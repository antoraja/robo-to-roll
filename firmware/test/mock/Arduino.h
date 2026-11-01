// Minimal Arduino/ESP32 stand-ins so the sketch can be compiled and exercised on a PC.
#pragma once
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <functional>
#include <algorithm>
using std::round; using std::fabs;

class __FlashStringHelper;
#define F(s) (reinterpret_cast<const __FlashStringHelper*>(s))

class String {
 public:
  std::string s;
  String() {}
  String(const char* c) : s(c ? c : "") {}
  String(const __FlashStringHelper* f) : s(reinterpret_cast<const char*>(f)) {}
  String(const std::string& x) : s(x) {}
  explicit String(int v) : s(std::to_string(v)) {}
  explicit String(unsigned v) : s(std::to_string(v)) {}
  explicit String(long v) : s(std::to_string(v)) {}
  String& operator+=(const String& o) { s += o.s; return *this; }
  String& operator+=(const char* o) { s += o; return *this; }
  String& operator+=(const __FlashStringHelper* f) { s += reinterpret_cast<const char*>(f); return *this; }
  String& operator+=(int v) { s += std::to_string(v); return *this; }
  bool operator==(const char* o) const { return s == o; }
  int toInt() const { return atoi(s.c_str()); }
  void trim() { size_t a = s.find_first_not_of(" \r\n\t"); size_t b = s.find_last_not_of(" \r\n\t");
                s = (a == std::string::npos) ? "" : s.substr(a, b - a + 1); }
  unsigned length() const { return s.size(); }
  char charAt(unsigned i) const { return i < s.size() ? s[i] : 0; }
  const char* c_str() const { return s.c_str(); }
};
// Arduino's StringSumHelper lets "literal" + String + int chains work; mimic that.
inline String operator+(const String& a, const String& b) { return String(a.s + b.s); }
inline String operator+(const String& a, const char* b) { return String(a.s + b); }
inline String operator+(const char* a, const String& b) { return String(std::string(a) + b.s); }
inline String operator+(const String& a, int b) { return String(a.s + std::to_string(b)); }

inline unsigned long& __millis() { static unsigned long m = 0; return m; }
inline unsigned long millis() { return __millis(); }
inline void delay(unsigned long ms) { __millis() += ms; }
template <class T, class L, class H> T constrain(T x, L lo, H hi) { return x < lo ? lo : (x > hi ? hi : x); }

struct IPAddress { const char* toString() const { return "192.168.4.1"; } };
struct HardwareSerial {
  std::string in;
  void begin(long) {}
  int available() { return in.size(); }
  String readStringUntil(char c) { size_t p = in.find(c); std::string r = in.substr(0, p); in = (p == std::string::npos) ? "" : in.substr(p + 1); return String(r); }
  void print(const char* s) { printf("%s", s); }
  void print(const __FlashStringHelper* s) { printf("%s", reinterpret_cast<const char*>(s)); }
  void print(const String& s) { printf("%s", s.c_str()); }
  void println(const char* s = "") { printf("%s\n", s); }
  void println(const __FlashStringHelper* s) { printf("%s\n", reinterpret_cast<const char*>(s)); }
  void println(const String& s) { printf("%s\n", s.c_str()); }
  void println(const IPAddress& ip) { printf("%s\n", ip.toString()); }
};
extern HardwareSerial Serial;
