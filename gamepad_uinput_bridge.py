#!/usr/bin/env python3
"""
================================================================================
🎮 PUENTE UNIVERSAL DE MANDOS Y PERIFÉRICOS (HTML5 GAMEPAD API -> LINUX UINPUT)
================================================================================
Convierte cualquier mando conectado por Bluetooth o Cable USB en el celular/PC
en un mando físico nativo virtual de Microsoft Xbox 360 en el kernel de Linux.
- Cero milisegundos de retraso (comunicación directa binaria WebSocket).
- Detección instantánea Plug & Play automática al conectar o abrir la app/web.
- Compatible con 100% de mandos: Xbox, PlayStation, Switch, 8BitDo, genéricos.
================================================================================
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path

try:
    import websockets
except ImportError:
    import subprocess
    subprocess.run("pip install --no-cache-dir websockets >/dev/null 2>&1 || true", shell=True)
    import websockets

try:
    import evdev
    from evdev import UInput, ecodes as e
except ImportError:
    print("⚠️ Módulo evdev no encontrado. Instalando python3-evdev...", flush=True)
    import subprocess
    subprocess.run("apt-get update -qq && apt-get install -y -qq python3-evdev >/dev/null 2>&1", shell=True)
    import evdev
    from evdev import UInput, ecodes as e

# Definición del mando virtual Xbox 360 (Estándar Kernel Linux & Steam Input)
GAMEPAD_CAPABILITIES = {
    e.EV_KEY: [
        e.BTN_A, e.BTN_B, e.BTN_X, e.BTN_Y,
        e.BTN_TL, e.BTN_TR, e.BTN_TL2, e.BTN_TR2,
        e.BTN_SELECT, e.BTN_START,
        e.BTN_MODE, e.BTN_THUMBL, e.BTN_THUMBR
    ],
    e.EV_ABS: [
        (e.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RX, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_RY, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (e.ABS_Z, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),   # Gatillo LT Analógico
        (e.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),  # Gatillo RT Analógico
        (e.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)), # Cruceta X
        (e.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))  # Cruceta Y
    ]
}

# Mapeo de botones estándar HTML5 Gamepad a Linux UInput
BUTTON_MAP = {
    0: e.BTN_A,        # A / Cruz
    1: e.BTN_B,        # B / Círculo
    2: e.BTN_X,        # X / Cuadrado
    3: e.BTN_Y,        # Y / Triángulo
    4: e.BTN_TL,       # LB / L1
    5: e.BTN_TR,       # RB / R1
    8: e.BTN_SELECT,   # Select / Back / Share
    9: e.BTN_START,    # Start / Options
    10: e.BTN_THUMBL,  # L3 (Click Stick Izq)
    11: e.BTN_THUMBR,  # R3 (Click Stick Der)
    16: e.BTN_MODE     # Botón Xbox / Guía / PS
}

virtual_pad = None

def get_virtual_pad():
    global virtual_pad
    if virtual_pad is None:
        try:
            if not os.path.exists("/dev/uinput"):
                import subprocess
                subprocess.run("mknod /dev/uinput c 10 223 2>/dev/null || true", shell=True)
                subprocess.run("chmod 0666 /dev/uinput 2>/dev/null || true", shell=True)
            virtual_pad = UInput(
                events=GAMEPAD_CAPABILITIES,
                name="Microsoft X-Box 360 pad",
                vendor=0x045e,
                product=0x028e,
                version=0x0114,
                bustype=e.BUS_USB
            )
            print("🎮 [✓] Mando Virtual Xbox 360 instanciado en el kernel (/dev/uinput, BUS_USB)!", flush=True)
        except Exception as err:
            print(f"⚠️ Error creando uinput: {err}. Asegúrate de que /dev/uinput tenga permisos 0666.", flush=True)
    return virtual_pad

async def gamepad_handler(websocket):
    print("🎮 [Plug & Play] Dispositivo conectado desde cliente web/móvil.", flush=True)
    pad = get_virtual_pad()
    if not pad:
        return

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                    continue

                # Formato esperado: {"axes": [x1, y1, x2, y2], "buttons": [b0, b1, ...]}
                axes = data.get("axes", [])
                buttons = data.get("buttons", [])

                # 1. Procesar Sticks Analógicos (-32768 a 32767) con saturación segura
                if len(axes) >= 2:
                    pad.write(e.EV_ABS, e.ABS_X, int(max(-1.0, min(1.0, float(axes[0]))) * 32767))
                    pad.write(e.EV_ABS, e.ABS_Y, int(max(-1.0, min(1.0, float(axes[1]))) * 32767))
                if len(axes) >= 4:
                    pad.write(e.EV_ABS, e.ABS_RX, int(max(-1.0, min(1.0, float(axes[2]))) * 32767))
                    pad.write(e.EV_ABS, e.ABS_RY, int(max(-1.0, min(1.0, float(axes[3]))) * 32767))

                # 2. Procesar Botones y Gatillos Analógicos Continuos (0..255)
                for idx, raw_val in enumerate(buttons):
                    val = float(raw_val) if isinstance(raw_val, (int, float)) else (1.0 if raw_val else 0.0)
                    is_pressed = val > 0.15

                    # Gatillo L2 / LT (Botón 6)
                    if idx == 6:
                        pad.write(e.EV_ABS, e.ABS_Z, int(val * 255))
                        pad.write(e.EV_KEY, e.BTN_TL2, 1 if is_pressed else 0)
                    # Gatillo R2 / RT (Botón 7)
                    elif idx == 7:
                        pad.write(e.EV_ABS, e.ABS_RZ, int(val * 255))
                        pad.write(e.EV_KEY, e.BTN_TR2, 1 if is_pressed else 0)
                    # Cruceta (D-Pad)
                    elif idx == 12: # Arriba
                        if is_pressed: pad.write(e.EV_ABS, e.ABS_HAT0Y, -1)
                        elif not (len(buttons) > 13 and float(buttons[13]) > 0.15): pad.write(e.EV_ABS, e.ABS_HAT0Y, 0)
                    elif idx == 13: # Abajo
                        if is_pressed: pad.write(e.EV_ABS, e.ABS_HAT0Y, 1)
                        elif not (len(buttons) > 12 and float(buttons[12]) > 0.15): pad.write(e.EV_ABS, e.ABS_HAT0Y, 0)
                    elif idx == 14: # Izquierda
                        if is_pressed: pad.write(e.EV_ABS, e.ABS_HAT0X, -1)
                        elif not (len(buttons) > 15 and float(buttons[15]) > 0.15): pad.write(e.EV_ABS, e.ABS_HAT0X, 0)
                    elif idx == 15: # Derecha
                        if is_pressed: pad.write(e.EV_ABS, e.ABS_HAT0X, 1)
                        elif not (len(buttons) > 14 and float(buttons[14]) > 0.15): pad.write(e.EV_ABS, e.ABS_HAT0X, 0)
                    # Botones de Acción
                    elif idx in BUTTON_MAP:
                        pad.write(e.EV_KEY, BUTTON_MAP[idx], 1 if is_pressed else 0)

                # Sincronizar todos los eventos en un solo frame (< 1ms)
                pad.syn()

            except Exception:
                pass
    except websockets.exceptions.ConnectionClosed:
        print("🎮 [Plug & Play] Mando desconectado del cliente. Liberando controles...", flush=True)
        # Centrado y liberación segura de controles para evitar movimiento fantasma
        try:
            pad.write(e.EV_ABS, e.ABS_X, 0)
            pad.write(e.EV_ABS, e.ABS_Y, 0)
            pad.write(e.EV_ABS, e.ABS_RX, 0)
            pad.write(e.EV_ABS, e.ABS_RY, 0)
            pad.write(e.EV_ABS, e.ABS_Z, 0)
            pad.write(e.EV_ABS, e.ABS_RZ, 0)
            pad.write(e.EV_ABS, e.ABS_HAT0X, 0)
            pad.write(e.EV_ABS, e.ABS_HAT0Y, 0)
            for btn in BUTTON_MAP.values():
                pad.write(e.EV_KEY, btn, 0)
            pad.write(e.EV_KEY, e.BTN_TL2, 0)
            pad.write(e.EV_KEY, e.BTN_TR2, 0)
            pad.syn()
        except Exception:
            pass

async def main():
    print("🚀 [Gamepad Daemon] Escuchando mandos en ws://0.0.0.0:6081...", flush=True)
    async with websockets.serve(gamepad_handler, "0.0.0.0", 6081):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
