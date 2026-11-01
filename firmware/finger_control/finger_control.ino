/*
  RoboHand - wireless finger control (ESP32)
  ------------------------------------------
  Step 1 of the robot-hand project: drive ONE finger servo from your phone.
  Built so that adding more fingers later is just one extra line in FINGERS[].

  How it works
    * The ESP32 creates its own WiFi network (no router needed):
        name:     RoboHand
        password: robohand123
    * Join that network on your phone, open http://192.168.4.1
      and move the slider (0% = finger open, 100% = finger closed).
    * You can also type commands in the Arduino Serial Monitor (115200 baud):
        f 0 50     -> finger 0 to 50% closed
        a 0 90     -> finger 0 servo to raw angle 90 (used for calibration)
        open | close | help

  Libraries (Arduino IDE -> Tools -> Manage Libraries):
    * "ESP32Servo" by Kevin Harrington / John K. Bennett
  Board: Tools -> Board -> esp32 -> "ESP32 Dev Module"
*/

#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// ----------------------------------------------------------------- SETTINGS
const char* WIFI_NAME = "RoboHand";
const char* WIFI_PASSWORD = "robohand123";   // at least 8 characters

struct FingerConfig {
  const char* name;
  int pin;          // ESP32 GPIO the servo's ORANGE (signal) wire goes to
  int openAngle;    // servo angle when the finger is straight   (calibrate!)
  int closedAngle;  // servo angle when the finger is fully bent (calibrate!)
};

// Add more fingers here later. Good pins: 13, 14, 27, 26, 25, 33, 32.
// (Avoid 0, 2, 12, 15 - they affect booting. 34-39 are input-only.)
FingerConfig FINGERS[] = {
  {"Index", 13, 20, 160},
};

const float SPEED_DEG_PER_STEP = 2.0;  // smaller = smoother/slower movement
const unsigned long STEP_MS = 15;      // how often the servo position is updated
// ---------------------------------------------------------------------------

const int NUM_FINGERS = sizeof(FINGERS) / sizeof(FINGERS[0]);
Servo servos[NUM_FINGERS];
float currentAngle[NUM_FINGERS];
float targetAngle[NUM_FINGERS];
int targetPercent[NUM_FINGERS];

WebServer server(80);

int percentToAngle(int i, int percent) {
  percent = constrain(percent, 0, 100);
  const FingerConfig& f = FINGERS[i];
  return f.openAngle + (f.closedAngle - f.openAngle) * percent / 100;
}

void setFingerPercent(int i, int percent) {
  if (i < 0 || i >= NUM_FINGERS) return;
  targetPercent[i] = constrain(percent, 0, 100);
  targetAngle[i] = percentToAngle(i, targetPercent[i]);
}

void setFingerRawAngle(int i, int angle) {
  if (i < 0 || i >= NUM_FINGERS) return;
  targetAngle[i] = constrain(angle, 0, 180);
}

// Move every servo a small step toward its target (smooth motion, less current spikes)
void updateServos() {
  static unsigned long last = 0;
  if (millis() - last < STEP_MS) return;
  last = millis();
  for (int i = 0; i < NUM_FINGERS; i++) {
    float diff = targetAngle[i] - currentAngle[i];
    if (fabs(diff) < 0.01) continue;
    if (fabs(diff) <= SPEED_DEG_PER_STEP) currentAngle[i] = targetAngle[i];
    else currentAngle[i] += (diff > 0 ? SPEED_DEG_PER_STEP : -SPEED_DEG_PER_STEP);
    servos[i].write((int)round(currentAngle[i]));
  }
}

// ------------------------------------------------------------------ web page
String buildPage() {
  String html = F(
    "<!doctype html><html><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>RoboHand</title><style>"
    "body{font-family:sans-serif;margin:16px;background:#111;color:#eee}"
    "h1{font-size:22px}.f{background:#222;border-radius:12px;padding:12px;margin:12px 0}"
    "input[type=range]{width:100%;height:40px}"
    "button{font-size:18px;padding:12px 18px;margin:4px;border-radius:10px;border:0}"
    "</style></head><body><h1>RoboHand</h1>"
    "<div><button onclick=\"all(0)\">Open all</button>"
    "<button onclick=\"all(100)\">Close all</button></div>");
  for (int i = 0; i < NUM_FINGERS; i++) {
    html += "<div class='f'><b>" + String(FINGERS[i].name) + "</b> <span id='v" + i + "'>" +
            targetPercent[i] + "</span>%<br><input type='range' min='0' max='100' value='" +
            targetPercent[i] + "' id='s" + i + "' oninput='mv(" + i + ",this.value)'></div>";
  }
  html += F(
    "<script>"
    "let t={};"
    "function mv(i,v){document.getElementById('v'+i).textContent=v;"
    "clearTimeout(t[i]);t[i]=setTimeout(()=>fetch('/set?f='+i+'&v='+v),30);}"
    "function all(v){fetch('/all?v='+v);document.querySelectorAll('input').forEach((s,i)=>{"
    "s.value=v;document.getElementById('v'+i).textContent=v;});}"
    "</script></body></html>");
  return html;
}

void handleRoot() { server.send(200, "text/html", buildPage()); }

void handleSet() {
  if (!server.hasArg("f") || !server.hasArg("v")) { server.send(400, "text/plain", "need f and v"); return; }
  setFingerPercent(server.arg("f").toInt(), server.arg("v").toInt());
  server.send(200, "text/plain", "ok");
}

void handleAll() {
  int v = server.hasArg("v") ? server.arg("v").toInt() : 0;
  for (int i = 0; i < NUM_FINGERS; i++) setFingerPercent(i, v);
  server.send(200, "text/plain", "ok");
}

// ------------------------------------------------------------ serial commands
void printHelp() {
  Serial.println(F("Commands:"));
  Serial.println(F("  f <finger> <0-100>   set finger % closed   e.g. f 0 50"));
  Serial.println(F("  a <finger> <0-180>   raw servo angle       e.g. a 0 90  (calibration)"));
  Serial.println(F("  open | close         all fingers"));
}

void handleSerial() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;
  char cmd = line.charAt(0);
  int a = -1, b = -1;
  sscanf(line.c_str() + 1, "%d %d", &a, &b);
  if (line == "open")       { for (int i = 0; i < NUM_FINGERS; i++) setFingerPercent(i, 0); }
  else if (line == "close") { for (int i = 0; i < NUM_FINGERS; i++) setFingerPercent(i, 100); }
  else if (cmd == 'f' && b >= 0) { setFingerPercent(a, b); }
  else if (cmd == 'a' && b >= 0) { setFingerRawAngle(a, b); }
  else { printHelp(); return; }
  Serial.print(F("OK -> "));
  Serial.println(line);
}

// ------------------------------------------------------------------- setup
void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println(F("\nRoboHand starting"));

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  for (int i = 0; i < NUM_FINGERS; i++) {
    servos[i].setPeriodHertz(50);                 // standard hobby servo
    servos[i].attach(FINGERS[i].pin, 500, 2400);  // pulse range in microseconds
    targetPercent[i] = 0;
    currentAngle[i] = targetAngle[i] = FINGERS[i].openAngle;
    servos[i].write(FINGERS[i].openAngle);
  }

  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_NAME, WIFI_PASSWORD);
  Serial.print(F("WiFi network: "));
  Serial.print(WIFI_NAME);
  Serial.print(F("   open http://"));
  Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/set", handleSet);
  server.on("/all", handleAll);
  server.begin();
  printHelp();
}

void loop() {
  server.handleClient();
  handleSerial();
  updateServos();
}
