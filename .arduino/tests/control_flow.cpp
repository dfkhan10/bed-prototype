#include "Servo.h"
#include <cassert>
#include <iostream>
#include SKETCH
int main(int argc,char**argv){
 assert(argc==2);std::string kind=argv[1];setup();
 if(kind=="vendor-auto"){
  assert(virtualMs==48000);assert(!writes.empty());
  // First 8-second phase, interpreted using the NEW phase-bank pin map.
  auto phase=delayedLevels.front();
  assert(phase[2]==180&&phase[3]==180&&phase[4]==0);
  assert(phase[8]==0&&phase[10]==180&&phase[11]==180);
  assert(phase[6]==180&&phase[7]==180); // both fill-valve pins
  for(auto kv:levels)assert(kv.second==0);
  std::cout<<"{\"test\":\"vendor-auto\",\"autostart\":true,\"virtual_duration_ms\":"<<virtualMs<<",\"inflate_bank_pins_on\":2,\"extraction_bank_pins_on\":2,\"all_off_at_end\":true}\n";
 }else if(kind=="phase-idle"){
  for(auto e:writes)assert(e.angle==0);
  auto before=writes.size();Serial.incoming="GO\n";
  for(int i=0;i<1000;i++)loop();
  assert(before==writes.size());assert(Serial.incoming=="GO\n");
  std::cout<<"{\"test\":\"phase-idle\",\"on_commands\":0,\"loop_iterations\":1000,\"go_consumed\":false}\n";
 }else if(kind=="vendor-stop"){
  assert(virtualMs==0);Serial.incoming="GO\n";injectStop=true;loop();
  assert(virtualMs==48000);assert(Serial.incoming=="OFF\n");
  for(auto kv:levels)assert(kv.second==0);
  auto ended=virtualMs;loop(); // OFF is unknown, not an implemented stop command.
  std::cout<<"{\"test\":\"vendor-stop\",\"off_unread_during_cycle\":true,\"virtual_cycle_ms\":"<<ended<<",\"off_handler_present\":false}\n";
 }else if(kind=="pair-stop"){
  assert(virtualMs==0);Serial.incoming="IN\n";injectStop=true;loop();
  assert(Serial.incoming=="OFF\n");assert(virtualMs-stopQueuedAt>=3000);
  auto pending=virtualMs-stopQueuedAt;loop();assert(Serial.incoming.empty());
  std::cout<<"{\"test\":\"pair-stop\",\"off_unread_during_inflate\":true,\"virtual_time_before_next_command_ms\":"<<pending<<"}\n";
 }else return 2;
}
