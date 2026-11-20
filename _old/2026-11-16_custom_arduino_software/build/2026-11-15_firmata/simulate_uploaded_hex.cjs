// Offline only: execute the retained AVR HEX and observe simulated D3 edges.
// No serial port or hardware access. External driver and power are NOT modeled.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../..');
const avr = require(path.join(root, '.cache/2026-11-15_avr-diagnostic/node_modules/avr8js'));
const diagnostic = process.argv.includes('--diagnostic');
const forcePadLow = process.argv.includes('--force-pad-low');
const hexPath = path.join(root, diagnostic ? 'build/2026-11-15_firmata/diagnostic-compiled/DiagnosticFirmata.ino.hex' : '.arduino/evidence/build/2026-11-15_StandardFirmata-uploaded.hex');
const hex = fs.readFileSync(hexPath, 'utf8');
const program = new Uint8Array(32768);
let upper = 0;
for (const line of hex.trim().split(/\r?\n/)) {
  if (!line.startsWith(':')) throw new Error('Invalid HEX record');
  const record = Buffer.from(line.slice(1), 'hex');
  if (record.length !== record[0] + 5 || record.reduce((a,b) => a+b,0) % 256) throw new Error('Invalid HEX checksum/length');
  const address = (record[1] << 8) | record[2];
  const type = record[3];
  if (type === 4) upper = ((record[4] << 8) | record[5]) * 65536;
  if (type === 0) {
    if (upper + address + record[0] > program.length) throw new Error('HEX outside UNO flash');
    program.set(record.subarray(4, 4+record[0]), upper+address);
  }
}
const hz = 16000000;
const cpu = new avr.CPU(new Uint16Array(program.buffer), 2048);
const portB = new avr.AVRIOPort(cpu, avr.portBConfig);
const portC = new avr.AVRIOPort(cpu, avr.portCConfig);
const portD = new avr.AVRIOPort(cpu, avr.portDConfig);
const timer0 = new avr.AVRTimer(cpu, avr.timer0Config);
const timer1 = new avr.AVRTimer(cpu, avr.timer1Config);
const timer2 = new avr.AVRTimer(cpu, avr.timer2Config);
const uart = new avr.AVRUSART(cpu, avr.usart0Config, hz);
if (forcePadLow) {
  if (!diagnostic) throw new Error('Fault injection only applies to diagnostic test');
  const oldRead = cpu.readHooks[avr.portDConfig.PIN];
  cpu.readHooks[avr.portDConfig.PIN] = addr => (oldRead ? oldRead(addr) : cpu.data[addr]) & ~8;
}
const tx = [];
uart.onByteTransmit = value => tx.push({us: cpu.cycles/16, value});
const edges = [];
portD.addListener((value,old) => {
  if ((value ^ old) & 8) edges.push({us: cpu.cycles/16, level: (value >> 3)&1});
});
const schedule = [];
const commands = diagnostic ? [
  [5.8, 'diagnostic_status', 'f00e42440100f7'],
  [5.9, 'wrong_key_negative_control', 'f00e424401020329f7'],
  [6.0, 'passive_capture_negative_control', 'f00e42440101f7'],
  [6.3, 'bounded_D3_probe', 'f00e42440102032af7'],
  [7.4, 'duplicate_probe_rejected', 'f00e42440102032af7'],
] : [
  // The first command deliberately lacks Servo configuration: negative control.
  [6.0, 'unconfigured_180_negative_control', 'e33401'],
  [6.2, 'configure_servo_and_candidate_OFF', 'f0700320046012f7e30000'],
  [6.6, 'candidate_ON', 'e33401'],
  [6.65, 'pin_state_during_ON', 'f06d03f7'],
  [7.2, 'candidate_OFF', 'e30000'],
  [7.25, 'pin_state_after_OFF', 'f06d03f7'],
];
for (const [seconds, label, data] of commands) {
  let c = seconds * hz;
  for (const value of Buffer.from(data,'hex')) {
    schedule.push({cycles:c,value,label});
    c += 4000; // 250 us, slower than the actual 57600-baud character interval.
  }
}
let index=0;
const start=Date.now();
while (cpu.cycles < 7.6 * hz) {
  if (index < schedule.length && cpu.cycles >= schedule[index].cycles && !uart.rxBusy) {
    if (!uart.writeByte(schedule[index].value)) throw new Error('UART injection failed');
    index++;
  }
  avr.avrInstruction(cpu);
  cpu.tick();
}
const pulses = [];
for(let i=0; i+1<edges.length; i++) {
  if(edges[i].level === 1 && edges[i+1].level === 0) {
    const nextRise=edges.slice(i+2).find(e=>e.level===1);
    pulses.push({start_us:edges[i].us, width_us:edges[i+1].us-edges[i].us, period_us:nextRise?nextRise.us-edges[i].us:null});
  }
}
function stats(startSec,endSec) {
  const p=pulses.filter(p=>p.start_us>=startSec*1e6 && p.start_us<endSec*1e6);
  const w=p.map(p=>p.width_us);
  const periods=p.map(p=>p.period_us).filter(x=>x!==null);
  return {count:p.length,min_width_us:w.length?Math.min(...w):null,max_width_us:w.length?Math.max(...w):null,min_period_us:periods.length?Math.min(...periods):null,max_period_us:periods.length?Math.max(...periods):null};
}
const diagnostics = [];
let frame=[];
for (const {value} of tx) {
  if(value===0xf0) frame=[value];
  else if(frame.length) {
    frame.push(value);
    if(value===0xf7) {
      if(frame[1]===0x0e) {
        const values=[];
        for(let j=6;j+4<frame.length-1;j+=5) values.push(frame.slice(j,j+5).reduce((a,b,k)=>a+b*2**(7*k),0));
        diagnostics.push({version:frame[2],op:frame[3],phase:frame[4],error:frame[5],values});
      }
      frame=[];
    }
  }
}
const result={
  proof_stage:'OFFLINE SIMULATION ONLY; not measured at the driver',
  simulator:'avr8js@0.21.1',clock_hz:hz,hex_path:hexPath,
  hex_sha256:crypto.createHash('sha256').update(hex).digest('hex'),
  wall_ms:Date.now()-start,commands,force_pad_read_low:forcePadLow,diagnostics,
  negative_control:stats(6.01,6.19),off_before:stats(6.3,6.59),on:stats(6.7,7.19),off_after:stats(7.3,7.59),
  uart_tx_hex:Buffer.from(tx.map(x=>x.value)).toString('hex'),edges,pulses,
};
if(diagnostic) {
  const phases=diagnostics.filter(x=>x.op===2 && x.error===0);
  const phaseCounts=phases.length===3 && phases.every(x=>x.values.length===6 && x.values[5]<100);
  const rejectionChecks=diagnostics.some(x=>x.op===2 && x.error===1) && diagnostics.some(x=>x.op===2 && x.error===2);
  const noAutomaticStart=edges.every(e=>e.us>=6.3e6);
  const initialOff=stats(6.31,6.54);
  const noDefault1500us=initialOff.count>=10 && initialOff.min_width_us>530 && initialOff.max_width_us<560;
  const recognizedFault=forcePadLow && phases.every(x=>x.values[0]===0);
  const accurateCapture=!forcePadLow && phases.every(x=>x.values[0]>=10 && x.values[3]>19950 && x.values[4]<20050) && phases[0].values[1]>500 && phases[0].values[2]<590 && phases[1].values[1]>2350 && phases[1].values[2]<2450 && phases[2].values[1]>500 && phases[2].values[2]<590;
  result.diagnostic_checks={phaseCounts,rejectionChecks,noAutomaticStart,noDefault1500us,recognizedFault,accurateCapture};
  result.off_before=initialOff;
  result.on=stats(6.6,7.04);
  result.off_after=stats(7.1,7.35);
  result.pass=phaseCounts && rejectionChecks && noAutomaticStart && noDefault1500us && (recognizedFault || accurateCapture);
} else {
  result.pass = result.negative_control.count===0 && result.off_before.count>=10 && result.on.count>=20 && result.off_after.count>=10 && result.on.min_width_us>2390 && result.on.max_width_us<2415 && result.off_after.min_width_us>534 && result.off_after.max_width_us<560;
}
const output=path.join(root,`.arduino/evidence/build/2026-11-15_${diagnostic?'DiagnosticFirmata'+(forcePadLow?'-pad-low-fault':''):'Firmata'}-hex-waveform-simulation.json`);
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({pass:result.pass,output,negative_control:result.negative_control,off_before:result.off_before,on:result.on,off_after:result.off_after,diagnostics,wall_ms:result.wall_ms}));
if(!result.pass)process.exitCode=1;
