// Execute the exact uploaded HEX offline; no serial or physical device access.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../..');
const avr = require(path.join(root, '.cache/2026-11-15_avr-diagnostic/node_modules/avr8js'));
const upload = JSON.parse(fs.readFileSync(path.join(root, '.arduino/evidence/hardware/2026-11-15_SixPumps-upload.json')));
const hex = fs.readFileSync(path.join(root, upload.hex));
const sha256 = crypto.createHash('sha256').update(hex).digest('hex');
if (sha256 !== upload.hex_sha256) throw new Error('Uploaded HEX identity mismatch');
const program = new Uint8Array(32768);
let upper = 0;
for (const line of hex.toString().trim().split(/\r?\n/)) {
  const r = Buffer.from(line.slice(1), 'hex');
  if (!line.startsWith(':') || r.length !== r[0] + 5 || r.reduce((a,b) => a+b, 0) % 256) throw new Error('Invalid HEX record');
  const address = (r[1] << 8) | r[2];
  if (r[3] === 4) upper = ((r[4] << 8) | r[5]) * 65536;
  if (r[3] === 0) program.set(r.subarray(4, 4+r[0]), upper + address);
}
const cpu = new avr.CPU(new Uint16Array(program.buffer), 2048);
const portB = new avr.AVRIOPort(cpu, avr.portBConfig);
const portC = new avr.AVRIOPort(cpu, avr.portCConfig);
const portD = new avr.AVRIOPort(cpu, avr.portDConfig);
const timer0 = new avr.AVRTimer(cpu, avr.timer0Config);
const timer1 = new avr.AVRTimer(cpu, avr.timer1Config);
const timer2 = new avr.AVRTimer(cpu, avr.timer2Config);
const channels = Object.fromEntries([3,4,5,6,7,8].map(pin => [pin, {
  name: ({3:'B1',4:'A1',5:'A2',6:'B2',7:'A3',8:'A4'})[pin],
  rise: null, previousRise: null, state: null, transitions: [],
  on: {count:0,minWidthUs:Infinity,maxWidthUs:0},
  off: {count:0,minWidthUs:Infinity,maxWidthUs:0},
  minPeriodUs:Infinity,maxPeriodUs:0
}]));
function observe(pin, level) {
  const c = channels[pin], now = cpu.cycles / 16;
  if (level) {
    if (c.previousRise !== null) {
      const period = now - c.previousRise;
      c.minPeriodUs = Math.min(c.minPeriodUs, period);
      c.maxPeriodUs = Math.max(c.maxPeriodUs, period);
    }
    c.rise = c.previousRise = now;
  } else if (c.rise !== null) {
    const width = now - c.rise;
    const state = width > 1500 ? 'on' : 'off';
    const stats = c[state];
    stats.count++;
    stats.minWidthUs = Math.min(stats.minWidthUs, width);
    stats.maxWidthUs = Math.max(stats.maxWidthUs, width);
    if (c.state !== state) c.transitions.push({state,startSeconds:c.rise/1e6});
    c.state = state;
    c.rise = null;
  }
}
portD.addListener((value,old) => {
  for (let pin=3;pin<=7;pin++) if ((value ^ old) & (1 << pin)) observe(pin,(value >> pin)&1);
});
portB.addListener((value,old) => {
  if ((value ^ old)&1) observe(8,value&1);
});
const start = Date.now();
while (cpu.cycles < 49 * 16000000) {
  avr.avrInstruction(cpu);
  cpu.tick();
}
let pass = true;
for (const c of Object.values(channels)) {
  const firstOn = c.transitions.findIndex(t => t.state === 'on');
  const phases = c.transitions.slice(firstOn);
  c.phaseDurationsSeconds = phases.slice(0,-1).map((t,i) => phases[i+1].startSeconds-t.startSeconds);
  // Edges are complete Servo pulses, not the instant write() updates its value.
  // Allow startup/refresh quantization (up to two 20 ms frames plus channel
  // position changes). Preserve measured durations, rather than rounding to 8s.
  c.pass = firstOn >= 0 && phases.length === 6 && phases.every((t,i) => t.state === (i%2===0 ? 'on':'off'))
    && phases.every((t,i) => Math.abs(t.startSeconds-i*8)<0.060)
    && c.phaseDurationsSeconds.every(s => Math.abs(s-8)<0.060)
    && c.on.minWidthUs>2380 && c.on.maxWidthUs<2420 && c.off.minWidthUs>530 && c.off.maxWidthUs<560;
  pass &&= c.pass;
  delete c.rise;
  delete c.previousRise;
}
const result = {
  proof_stage:'OFFLINE AVR SIMULATION ONLY; power, physical clock, wiring, driver and motor response not modeled',
  clock_hz:16000000,simulator:'avr8js@0.21.1',hex_sha256:sha256,
  simulated_seconds:49,wall_ms:Date.now()-start,channels,pass
};
const output=path.join(root,'.arduino/evidence/build/2026-11-15_SixPumps-hex-waveform-simulation.json');
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
if (!pass) process.exitCode=1;
