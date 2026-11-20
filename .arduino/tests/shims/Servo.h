#pragma once
// Host-only control-flow shim. Does not simulate AVR timers, pulse widths,
// switch electronics, electrical power, air flow, or physical stopping.
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <map>
#include <string>
#include <vector>
using std::uint8_t;
#define F(x) x
#define OUTPUT 1
#define HIGH 1
#define LOW 0
#define LED_BUILTIN 13
class __FlashStringHelper {};
struct Event { unsigned long time; int pin; int angle; };
inline unsigned long virtualMs=0;
inline std::map<int,int> levels;
inline std::vector<Event> writes;
inline std::vector<std::map<int,int>> delayedLevels;
inline bool injectStop=false;
inline unsigned long stopQueuedAt=0;
class String {
 std::string value;
 public:
 String(std::string s=""):value(s){}
 void trim(){auto a=value.find_first_not_of(" \r\n\t"),b=value.find_last_not_of(" \r\n\t");value=a==std::string::npos?"":value.substr(a,b-a+1);}
 void toUpperCase(){for(char &c:value)c=static_cast<char>(std::toupper(static_cast<unsigned char>(c)));}
 std::size_t length()const{return value.size();}
 bool operator==(const char*s)const{return value==s;}
};
struct SerialShim {
 std::string incoming;
 void begin(unsigned long){}
 int available()const{return static_cast<int>(incoming.size());}
 String readStringUntil(char sep){auto n=incoming.find(sep);if(n==std::string::npos){auto s=incoming;incoming.clear();virtualMs+=1000;return String(s);}auto s=incoming.substr(0,n);incoming.erase(0,n+1);return String(s);}
 template<class T>void print(const T&){}
 template<class T>void println(const T&){}
 void println(){}
};
inline SerialShim Serial;
inline void delay(unsigned long ms){delayedLevels.push_back(levels);if(injectStop){Serial.incoming+="OFF\n";stopQueuedAt=virtualMs;injectStop=false;}virtualMs+=ms;}
inline void pinMode(int,int){}
inline void digitalWrite(int,int){}
class Servo{
 int pin=-1;
 public:
 int attach(int p){pin=p;return 1;}
 void write(int angle){levels[pin]=angle;writes.push_back({virtualMs,pin,angle});}
 void detach(){pin=-1;}
};
