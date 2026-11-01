#pragma once
#include "Arduino.h"
#include <map>
struct WebServer {
  std::map<std::string, std::function<void()>> routes;
  std::map<std::string, std::string> args;
  int lastCode = 0; std::string lastBody;
  explicit WebServer(int) {}
  void on(const char* p, std::function<void()> f) { routes[p] = f; }
  void begin() {}
  void handleClient() {}
  bool hasArg(const char* a) { return args.count(a) > 0; }
  String arg(const char* a) { return String(args[a]); }
  void send(int code, const char*, const String& body) { lastCode = code; lastBody = body.s; }
  void send(int code, const char* t, const char* body) { send(code, t, String(body)); }
  // test helper
  int request(const std::string& path, std::map<std::string, std::string> a = {}) {
    args = a; lastCode = 404; if (routes.count(path)) routes[path](); return lastCode; }
};
