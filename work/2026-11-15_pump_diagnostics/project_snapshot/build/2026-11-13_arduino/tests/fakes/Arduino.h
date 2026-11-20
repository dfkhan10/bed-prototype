#pragma once
#include <cstdint>
#include <deque>
#include <string>
#define INPUT 0
#define OUTPUT 1
#define LOW 0
#define F(value) value
extern uint32_t fakeNow;
extern int pinModes[20];
inline uint32_t millis() { return fakeNow; }
inline void pinMode(int pin, int mode) { pinModes[pin] = mode; }
inline void digitalWrite(int, int) {}
struct FakeSerial {
  std::deque<unsigned char> incoming;
  std::string output;
  void begin(unsigned long) {}
  int available() { return static_cast<int>(incoming.size()); }
  int read() { auto c = incoming.front(); incoming.pop_front(); return c; }
  void print(const char *s) { output += s; }
  template<class T> void print(T n) { output += std::to_string(static_cast<long long>(n)); }
  template<class T> void println(T x) { print(x); output += '\n'; }
};
extern FakeSerial Serial;
