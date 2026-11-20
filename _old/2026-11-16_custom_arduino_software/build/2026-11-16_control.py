#!/usr/bin/env python3
"""Управление UNO + shield через StandardFirmata. Меняем только этот файл.

Без аргументов: показать сценарий, USB не открывается.
--status: проверить плату, без команд выходам. --run: выполнить сценарий.
--stop: послать OFF выходам, которые уже настроены как Servo.
Запускать проектным .venv/bin/python; зависимость pyserial уже установлена.

Время выдерживает компьютер. При обрыве USB/зависании процесса StandardFirmata
может сохранить ON: аппаратного watchdog/отключения питания здесь нет.
Ctrl+C отправляет OFF, если связь работает. Ответ UNO не доказывает остановку.
При настройке Servo возможен краткий стартовый импульс 1500 мкс.
USB + внешний адаптер запрещены продавцом для непроверенной схемы питания.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Device:
    pin: int
    kind: str                     # pump или valve; оба через электронный ключ Servo
    role: str                     # inflate, deflate или valve
    group: int                    # одна пневматическая группа
    on: int = 180                 # команды из примера продавца
    off: int = 0                  # физическое выключение ещё требует наблюдения


@dataclass(frozen=True)
class Step:
    seconds: float
    on: tuple[str, ...] = ()       # имя устройства либо роль inflate/deflate/valve


# ==================== ЗДЕСЬ МЕНЯЕМ УСТРОЙСТВА И СЦЕНАРИЙ ====================
# Это ПРЕДЛАГАЕМАЯ НОВАЯ разводка, не установленная карта старых проводов.
# До подключения: сверить контакты, направление насосов и поведение клапанов.
DEVICES = {
    "inflate_1": Device(pin=3, kind="pump", role="inflate", group=1),
    "inflate_2": Device(pin=4, kind="pump", role="inflate", group=2),
    "inflate_3": Device(pin=5, kind="pump", role="inflate", group=3),
    "deflate_1": Device(pin=6, kind="pump", role="deflate", group=1),
    "deflate_2": Device(pin=7, kind="pump", role="deflate", group=2),
    "deflate_3": Device(pin=8, kind="pump", role="deflate", group=3),
    "valve_1": Device(pin=10, kind="valve", role="valve", group=1),
    "valve_2": Device(pin=11, kind="valve", role="valve", group=2),
    "valve_3": Device(pin=12, kind="valve", role="valve", group=3),
}

SCENARIO = [
    Step(seconds=10, on=("inflate",)),  # все три насоса на надув
    Step(seconds=10, on=("deflate",)),  # все три насоса на сдувание
    Step(seconds=1),                   # все использованные устройства OFF
]
REPEAT = 1                            # конечное число повторений
# Один насос: Step(seconds=2, on=("inflate_1",))
# Насос и клапан: Step(seconds=2, on=("deflate_1", "valve_1"))
# Клапаны не включаются автоматически при сдувании. Их роль ещё надо проверить.
# Для подключения другого электронного ключа добавляем Device и его имя в Step.

WIRING_CONFIRMED = False               # карта выше сверена с реальными проводами
USB_CONTROL_POWER_VERIFIED = False     # питание нагрузки развязано/проверено для USB
BOARD_SERIAL = "24238313635351910130"   # конкретная UNO, без привязки к номеру порта
SERVO_MIN_US, SERVO_MAX_US = 544, 2400
# ==================== НИЖЕ СЛУЖЕБНЫЙ КОД, ОБЫЧНО НЕ МЕНЯЕМ ==================


def validate_devices(devices):
    if not devices or len(devices) > 12:
        raise ValueError("Нужно от 1 до 12 устройств Servo")
    pins = set()
    for name, d in devices.items():
        if not name or name in {"inflate", "deflate", "valve"}:
            raise ValueError(f"Имя устройства совпадает с ролью: {name!r}")
        if type(d.pin) is not int or d.pin not in range(2, 13) or d.pin in pins:
            raise ValueError(f"{name}: нужен уникальный контакт D2–D12")
        pins.add(d.pin)
        if d.kind not in {"pump", "valve"} or d.role not in {"inflate", "deflate", "valve"}:
            raise ValueError(f"{name}: неизвестный тип или роль")
        if (d.kind == "valve") != (d.role == "valve"):
            raise ValueError(f"{name}: тип и роль не согласованы")
        if type(d.group) is not int or d.group < 1:
            raise ValueError(f"{name}: group должен быть положительным целым")
        if any(type(v) is not int or not 0 <= v <= 180 for v in (d.on, d.off)) or d.on == d.off:
            raise ValueError(f"{name}: ON и OFF должны отличаться, диапазон 0–180")


def compile_plan(devices=DEVICES, scenario=SCENARIO, repeat=REPEAT):
    """Проверка выполняется до открытия USB и любых команд выходам."""
    validate_devices(devices)
    if type(repeat) is not int or not 1 <= repeat <= 1000:
        raise ValueError("REPEAT должен быть целым числом от 1 до 1000")
    if not scenario:
        raise ValueError("SCENARIO пуст")
    plan = []
    for s in scenario:
        if isinstance(s.seconds, bool) or not isinstance(s.seconds, (int, float)) or not math.isfinite(s.seconds) or not 0 < s.seconds <= 3600:
            raise ValueError("Длительность шага должна быть от 0 до 3600 секунд, не включая 0")
        if not isinstance(s.on, tuple):
            raise ValueError('Используй кортеж имён: on=("inflate_1",)')
        active = set()
        for target in s.on:
            matches = {n for n, d in devices.items() if n == target or d.role == target}
            if not matches:
                raise ValueError(f"Устройство или роль не найдены: {target!r}")
            active.update(matches)
        for group in {devices[n].group for n in active}:
            roles = {devices[n].role for n in active if devices[n].group == group}
            if {"inflate", "deflate"} <= roles:
                raise ValueError(f"В группе {group} одновременно заданы надув и сдув")
        plan.append((float(s.seconds), tuple(n for n in devices if n in active)))
    return plan


def preview(plan):
    print("Предложенная карта контактов" if not WIRING_CONFIRMED else "Карта контактов")
    for name, d in DEVICES.items():
        print(f"  D{d.pin:<2} {name:<12} {d.kind:<5} группа {d.group}, ON={d.on}, OFF={d.off}")
    print(f"\nСценарий, повторений: {REPEAT}")
    for i, (seconds, names) in enumerate(plan, 1):
        print(f"  {i}. {seconds:g} с: {', '.join(names) if names else 'пауза'}")
    print("  На каждом шаге остальные использованные устройства получают OFF.")
    print("  Неиспользованные клапаны не настраиваются и не получают команд.")
    print(f"  Всего: {sum(s for s, _ in plan) * REPEAT:g} с + время обмена с UNO.")


class Firmata:
    def __init__(self):
        import serial
        from serial.tools import list_ports

        targets = [p for p in list_ports.comports()
                   if (p.vid, p.pid, p.serial_number) == (0x2341, 0x0043, BOARD_SERIAL)]
        if len(targets) != 1:
            raise RuntimeError("Нужна одна подключённая UNO с указанным BOARD_SERIAL")
        self.ser = serial.Serial(targets[0].device, 57600, timeout=0.02,
                                 write_timeout=0.5, exclusive=True)
        self.pending = bytearray()
        self.frames = []
        self.configured = []
        try:
            self.receive(6)  # UNO может сброситься при открытии USB
            fw = self.query(bytes((0xF0, 0x79, 0xF7)), 0x79)
            name = "".join(chr(fw[i] | fw[i + 1] << 7) for i in range(4, len(fw) - 1, 2))
            if name != "StandardFirmata.ino" or fw[2:4] != bytes((2, 5)):
                raise RuntimeError(f"Не та прошивка: {name!r}, {list(fw[2:4])}")
            caps = self.query(bytes((0xF0, 0x6B, 0xF7)), 0x6C)
            self.capabilities = []
            current = {}
            it = iter(caps[2:-1])
            for mode in it:
                if mode == 127:
                    self.capabilities.append(current)
                    current = {}
                else:
                    current[mode] = next(it)
            print(f"UNO {BOARD_SERIAL}, {targets[0].device}: {name}, 2.5")
        except BaseException:
            self.ser.close()
            raise

    def send(self, data):
        if self.ser.write(data) != len(data):
            raise RuntimeError("Неполная отправка в USB")

    def receive(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            for b in self.ser.read(self.ser.in_waiting or 1):
                if b == 0xF0:
                    self.pending = bytearray((b,))
                elif self.pending:
                    self.pending.append(b)
                    if b == 0xF7:
                        self.frames.append(bytes(self.pending))
                        self.pending.clear()
            self.frames = self.frames[-100:]

    def query(self, data, command, pin=None):
        self.frames.clear()
        self.send(data)
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline:
            self.receive(0.02)
            for f in self.frames:
                if len(f) >= 3 and f[1] == command and (pin is None or (len(f) > 3 and f[2] == pin)):
                    return f
        raise RuntimeError("UNO не ответила на запрос")

    def state(self, pin):
        f = self.query(bytes((0xF0, 0x6D, pin, 0xF7)), 0x6E, pin)
        if len(f) < 6:
            raise RuntimeError("Неполный ответ состояния контакта")
        return f[3], sum(b << (7 * i) for i, b in enumerate(f[4:-1]))

    def write(self, name, value):
        pin = DEVICES[name].pin
        self.send(bytes((0xE0 | pin, value & 127, value >> 7)))

    def prepare(self, names):
        for name in names:
            pin = DEVICES[name].pin
            if pin >= len(self.capabilities) or 4 not in self.capabilities[pin]:
                raise RuntimeError(f"D{pin}: прошивка не сообщает поддержку Servo")
        for name in names:
            d = DEVICES[name]
            self.configured.append(name)  # cleanup и при ошибке посреди настройки
            self.send(bytes((0xF0, 0x70, d.pin, SERVO_MIN_US & 127,
                             SERVO_MIN_US >> 7, SERVO_MAX_US & 127,
                             SERVO_MAX_US >> 7, 0xF7)))
            self.write(name, d.off)
            if self.state(d.pin) != (4, d.off):
                raise RuntimeError(f"D{d.pin}: OFF не отражён в состоянии прошивки")

    def off(self, names):
        failed = []
        for name in names:
            try:
                self.write(name, DEVICES[name].off)
            except Exception as e:
                failed.append(f"{name}: {e}")
        if failed:
            raise RuntimeError("Не удалось отправить OFF: " + "; ".join(failed))

    def close(self):
        try:
            self.off(self.configured)
        finally:
            self.ser.close()


def execute(board, plan):
    used = tuple(n for n in DEVICES if any(n in active for _, active in plan))
    board.prepare(used)
    for cycle in range(REPEAT):
        for seconds, active in plan:
            # Сначала выключаем предыдущую фазу, затем включаем новую.
            board.off(used)
            for name in active:
                board.write(name, DEVICES[name].on)
            print(f"{cycle + 1}/{REPEAT}: {seconds:g} с, {', '.join(active) or 'пауза'}", flush=True)
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                time.sleep(min(0.02, max(0, deadline - time.monotonic())))
            board.off(used)
    for name in used:
        if board.state(DEVICES[name].pin) != (4, DEVICES[name].off):
            raise RuntimeError(f"{name}: итоговый OFF не подтверждён прошивкой")
    print("Сценарий завершён. UNO сообщает OFF; физическая остановка требует наблюдения.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--preview", action="store_true", help="показать сценарий без USB (по умолчанию)")
    modes.add_argument("--status", action="store_true", help="только запросить состояние UNO")
    modes.add_argument("--run", action="store_true", help="выполнить сценарий")
    modes.add_argument("--stop", action="store_true", help="послать OFF уже настроенным выходам Servo")
    args = parser.parse_args()
    board = None
    try:
        # Ошибка сценария не должна мешать запросу состояния или команде OFF.
        validate_devices(DEVICES)
        plan = None if args.status or args.stop else compile_plan()
        if not (args.status or args.run or args.stop):
            preview(plan)
            return 0
        if args.run and not (WIRING_CONFIRMED and USB_CONTROL_POWER_VERIFIED):
            raise ValueError("Запуск закрыт: нужно подтвердить карту проводов и питание для USB-управления")
        board = Firmata()
        if args.status:
            for name, d in DEVICES.items():
                mode, value = board.state(d.pin)
                print(f"D{d.pin}: {name}, mode={mode}, stored={value}")
            print("Это состояние UNO, не обратная связь от насоса или клапана. Команд выходам не отправлено.")
        elif args.stop:
            names = [n for n, d in DEVICES.items() if board.state(d.pin)[0] == 4]
            board.configured = names
            board.off(names)
            for name in names:
                if board.state(DEVICES[name].pin) != (4, DEVICES[name].off):
                    raise RuntimeError(f"{name}: UNO не подтвердила OFF")
            if names:
                print(f"UNO подтвердила OFF на {len(names)} выходах Servo. Проверь физическую остановку.")
            else:
                print("Настроенных выходов Servo нет; команды OFF не отправлялись.")
        else:
            execute(board, plan)
        result = 0
    except KeyboardInterrupt:
        print("Прервано. Отправляю OFF при доступной связи.", file=sys.stderr)
        result = 130
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        result = 1
    finally:
        if board is not None:
            try:
                board.close()
            except Exception as e:
                print(f"OFF/USB: {e}. При продолжающейся работе сними питание нагрузки.", file=sys.stderr)
                result = 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
