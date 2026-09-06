#!/usr/bin/env python3
"""
Aether Cloud PC - Laboratorio de Pruebas Táctiles y Telemetría en Vivo (v2 - Equilibrado y Registro de Deslizamiento)
Servidor HTTP local para probar el 100% de la interfaz sin encender Kaggle.
Registra cada toque, deslizamiento continuo (touchmove), coordenadas y consecuencias en 'test_touch_telemetry.log'.
"""

import os
import sys
import json
import time
import struct
import zlib
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "test_touch_telemetry.log"
SOURCE_FILE = BASE_DIR / "run_kaggle_vnc_studio.py"
PORT = 8080

def make_png_icon(size):
    width = height = size
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data
    ihdr += struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data))
    raw = b''.join([b'\x00' + bytes([0, 255, 200] * width) for _ in range(height)])
    compressed = zlib.compress(raw)
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed
    idat += struct.pack('>I', zlib.crc32(b'IDAT' + compressed))
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND'))
    return sig + ihdr + idat + iend

ICON_192 = make_png_icon(192)
ICON_512 = make_png_icon(512)

def get_hud_code():
    """Extrae el bloque exacto de CSS, HTML y JS de producción de run_kaggle_vnc_studio.py"""
    if not SOURCE_FILE.exists():
        return ""
    text = SOURCE_FILE.read_text(encoding="utf-8")
    start_marker = 'hud_code = """'
    end_marker = '"""\n            if "<meta charset=" not in content.lower():'
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start != -1 and end != -1:
        return text[start + len(start_marker):end]
    return ""

def log_telemetry_entry(entry):
    """Guarda una entrada formateada y auditada en test_touch_telemetry.log"""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    millis = int((time.time() % 1) * 1000)
    ts = f"[{now}.{millis:03d}]"
    
    evt_type = entry.get("type", "EVENT")
    details = entry.get("details", "")
    coords = entry.get("coords", "")
    finger = entry.get("finger", "--")
    action = entry.get("action", "")
    target = entry.get("target", "")
    anomaly = entry.get("anomaly", "")

    anomaly_tag = f"[ANOMALIA: {anomaly}]" if anomaly else "[OK: CALIBRADO]"

    line = f"{ts} {evt_type:<16} | Dedo: {finger:<14} | PunteroVirt: {coords:<14} | Target: {target:<16} | Acción: {action:<10} | {anomaly_tag:<30} | {details}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    return line

def build_sandbox_html():
    hud_code = get_hud_code()

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Aether Studio - Laboratorio de Pruebas Táctiles v2</title>
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
    <link rel="apple-touch-icon" href="/icon-192.png">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0a0f1a">
    <script>
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('/sw.js').catch(() => {{}});
        }}
    </script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-user-select: none;
            -webkit-touch-callout: none;
        }}
        html, body {{
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background: #060913;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #f1f5f9;
        }}
        #noVNC_screen {{
            position: absolute;
            top: 0; left: 0; width: 100vw; height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #080d1a;
            overflow: hidden;
            touch-action: none;
        }}
        #noVNC_canvas {{
            max-width: 100vw;
            max-height: 100vh;
            aspect-ratio: 16 / 9;
            width: auto;
            height: auto;
            background: #090e1a;
            display: block;
            touch-action: none;
            box-shadow: 0 0 32px rgba(0,0,0,0.85);
            will-change: transform;
        }}

        /* HUD DE TELEMETRÍA EN VIVO: Centrado Inferior para no tapar los botones ni los mandos */
        #telemetry-hud-box {{
            position: fixed;
            bottom: calc(10px + var(--safe-bottom, 0px));
            left: 50%;
            transform: translateX(-50%);
            width: 480px;
            max-width: 92vw;
            background: rgba(10, 15, 26, 0.90);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1.5px solid rgba(0, 255, 200, 0.4);
            border-radius: 16px;
            padding: 8px 14px;
            font-family: monospace;
            font-size: 11px;
            z-index: 9999999;
            box-shadow: 0 8px 32px rgba(0,0,0,0.75);
            pointer-events: auto;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        #telemetry-hud-box.collapsed {{
            width: auto;
            padding: 6px 14px;
            border-radius: 20px;
            opacity: 0.85;
        }}
        #telemetry-hud-box.collapsed .tel-body {{
            display: none;
        }}
        .tel-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--aether-cyan, #00ffc8);
            font-weight: bold;
            font-size: 11px;
            cursor: pointer;
            gap: 12px;
        }}
        .tel-indicator {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ffc8;
            box-shadow: 0 0 10px #00ffc8;
            animation: telPulse 1.2s infinite;
        }}
        @keyframes telPulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.35; transform: scale(0.75); }}
        }}
        .tel-live-ticker {{
            color: #38bdf8;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 320px;
        }}
        .tel-body {{
            margin-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.12);
            padding-top: 8px;
        }}
        .tel-log-stream {{
            display: flex;
            flex-direction: column;
            gap: 3px;
            max-height: 90px;
            overflow: hidden;
        }}
        .tel-log-item {{
            color: #cbd5e1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.25;
            font-size: 10px;
        }}
        .tel-log-item.highlight {{
            color: #00ffc8;
            font-weight: bold;
        }}
        .tel-actions {{
            display: flex;
            gap: 6px;
            margin-top: 6px;
        }}
        .tel-btn {{
            flex: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 8px;
            color: #e2e8f0;
            padding: 5px 8px;
            font-size: 10px;
            cursor: pointer;
            text-align: center;
            font-weight: 600;
            transition: all 0.15s ease;
        }}
        .tel-btn svg {{
            width: 12px;
            height: 12px;
            stroke-width: 2;
            flex-shrink: 0;
        }}
        .tel-btn:active {{
            background: rgba(0,255,200,0.25);
            color: #00ffc8;
            border-color: rgba(0,255,200,0.5);
        }}
        .tel-status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
            flex-shrink: 0;
            box-shadow: 0 0 8px currentColor;
            transition: background-color 0.25s ease, box-shadow 0.25s ease;
        }}
        .tel-status-dot.online {{
            background: #10b981;
            color: #10b981;
        }}
        .tel-status-dot.offline {{
            background: #f43f5e;
            color: #f43f5e;
        }}
        .tel-status-dot.waiting {{
            background: #f59e0b;
            color: #f59e0b;
        }}
        .floating-bumper-btn {{
            position: fixed;
            top: 16px;
            z-index: 999999;
            width: 96px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-family: monospace;
            font-size: 14px;
            user-select: none;
            touch-action: none;
            transition: transform 0.08s ease, background 0.08s ease;
        }}
        .floating-bumper-btn.pressed {{
            transform: scale(0.92) !important;
            background: rgba(255, 255, 255, 0.4) !important;
            box-shadow: 0 0 25px currentColor !important;
        }}
        .floating-bumper-btn.hidden {{
            display: none !important;
        }}
    </style>
</head>
<body>

    <!-- Bumpers Flotantes Híbridos (Desactivados por defecto estilo BigTech para pantalla limpia) -->
    <div id="floating-bumper-lb" class="floating-bumper-btn hidden" style="left:16px; border:2px solid #00ffc8; background:rgba(0,255,200,0.18); backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px); color:#00ffc8; box-shadow:0 0 15px rgba(0,255,200,0.3); display:none !important;">
        LB (L1)
    </div>
    <div id="floating-bumper-rb" class="floating-bumper-btn hidden" style="right:16px; border:2px solid #f59e0b; background:rgba(245,158,11,0.18); backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px); color:#f59e0b; box-shadow:0 0 15px rgba(245,158,11,0.3); display:none !important;">
        RB (R1)
    </div>

    <!-- Contenedor Base noVNC -->
    <div id="noVNC_screen" tabindex="0" style="outline:none;">
        <canvas id="noVNC_canvas" width="1920" height="1080" tabindex="0" style="outline:none;"></canvas>
    </div>

    <!-- Banner Flotante de Notificación de Modo (Juego vs PC) -->
    <div id="tel-mode-toast" style="position:fixed; top:20px; left:50%; transform:translateX(-50%); background:rgba(10,15,26,0.94); border:1.5px solid #00ffc8; box-shadow:0 0 25px rgba(0,255,200,0.45); color:#00ffc8; padding:8px 22px; border-radius:24px; font-family:monospace; font-size:12px; font-weight:bold; letter-spacing:0.8px; z-index:999999; pointer-events:none; opacity:0; transition:opacity 0.25s ease, transform 0.25s ease;">
        MODO JUEGO XINPUT ACTIVADO
    </div>

    <!-- HUD de Telemetría Centrado e No Invasivo -->
    <div id="telemetry-hud-box" class="collapsed">
        <div class="tel-header" id="tel-toggle-btn">
            <span style="display:flex; align-items:center; gap:6px;">
                <span class="tel-indicator"></span>
                <span style="font-weight:800; letter-spacing:0.5px;">TELEMETRÍA EN VIVO</span>
            </span>
            <span class="tel-live-ticker" id="tel-ticker-text">Listo. Desliza o pulsa mandos</span>
            <span id="tel-collapse-btn-wrapper" style="display:flex; align-items:center; gap:4px; font-size:10px; color:#94a3b8;">
                <span id="tel-collapse-text">EXPANDIR</span>
                <svg id="tel-collapse-svg" viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="transition:transform 0.25s ease;"><polyline points="6 9 12 15 18 9"/></svg>
            </span>
        </div>
        <div class="tel-body">
            <!-- Barra de Estado del Mando Físico y Modo de Control -->
            <div id="tel-gp-status-bar" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; padding:4px 8px; background:rgba(255,255,255,0.05); border-radius:8px; font-size:10px;">
                <span style="display:flex; align-items:center;">
                    <span class="tel-status-dot waiting" id="tel-gp-dot"></span>
                    <span id="tel-gp-name" style="color:#f59e0b; font-weight:bold;">Mando: Esperando señal (Pulsa cualquier botón)</span>
                </span>
                <span id="tel-gp-mode-badge" style="color:#00ffc8; font-weight:bold; background:rgba(0,255,200,0.12); padding:2px 6px; border-radius:6px; border:1px solid rgba(0,255,200,0.3);">Modo: JUEGO (XInput)</span>
            </div>

            <!-- Medidor Analógico de Gatillos LT / RT en Tiempo Real -->
            <div style="display:flex; gap:10px; margin-bottom:8px; font-size:9px;">
                <div style="flex:1; display:flex; align-items:center; gap:4px;">
                    <span style="color:#38bdf8; font-weight:bold; width:22px;">LT:</span>
                    <div style="flex:1; height:6px; background:rgba(255,255,255,0.12); border-radius:3px; overflow:hidden;">
                        <div id="tel-gauge-lt" style="width:0%; height:100%; background:#38bdf8; transition:width 0.04s linear;"></div>
                    </div>
                    <span id="tel-val-lt" style="color:#38bdf8; width:28px; text-align:right;">0%</span>
                </div>
                <div style="flex:1; display:flex; align-items:center; gap:4px;">
                    <span style="color:#ff2a85; font-weight:bold; width:22px;">RT:</span>
                    <div style="flex:1; height:6px; background:rgba(255,255,255,0.12); border-radius:3px; overflow:hidden;">
                        <div id="tel-gauge-rt" style="width:0%; height:100%; background:#ff2a85; transition:width 0.04s linear;"></div>
                    </div>
                    <span id="tel-val-rt" style="color:#ff2a85; width:28px; text-align:right;">0%</span>
                </div>
            </div>

            <!-- Fila de Bumpers LB y RB y Sonda de Señal Raw en Tiempo Real -->
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; font-size:10px; gap:8px;">
                <div style="display:flex; gap:6px;">
                    <span id="tel-badge-lb" style="padding:2px 8px; border-radius:6px; border:1px solid rgba(0,255,200,0.3); background:rgba(0,255,200,0.08); color:#00ffc8; font-weight:bold; transition:all 0.1s ease;">LB: OFF</span>
                    <span id="tel-badge-rb" style="padding:2px 8px; border-radius:6px; border:1px solid rgba(245,158,11,0.3); background:rgba(245,158,11,0.08); color:#f59e0b; font-weight:bold; transition:all 0.1s ease;">RB: OFF</span>
                </div>
                <div style="flex:1; text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                    <span style="color:#64748b; font-size:9px;">SONDA RAW: </span>
                    <span id="tel-raw-probe-val" style="color:#38bdf8; font-family:monospace; font-weight:bold; font-size:9px;">Listo. Pulsa botones</span>
                </div>
            </div>

            <div class="tel-log-stream" id="tel-stream-list">
                <div class="tel-log-item highlight">[LISTO] Esperando movimientos...</div>
            </div>
            <div class="tel-actions" style="margin-top:6px; flex-wrap:wrap;">
                <button class="tel-btn" id="tel-sync-gp-btn" style="background:rgba(16,185,129,0.18); border-color:rgba(16,185,129,0.5); color:#10b981; font-weight:bold;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                    <span>Sincronizar Mando</span>
                </button>
                <button class="tel-btn" id="tel-game-lock-btn" style="background:rgba(239,68,68,0.18); border-color:rgba(239,68,68,0.5); color:#f87171; font-weight:bold;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                    <span id="tel-game-lock-text">Bloqueo Juego: OFF</span>
                </button>
                <button class="tel-btn" id="tel-remap-l3r3-btn" style="background:rgba(168,85,247,0.18); border-color:rgba(168,85,247,0.5); color:#c084fc; font-weight:bold;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/></svg>
                    <span id="tel-remap-l3r3-text">Mapeo L3/R3 a LB/RB: ON</span>
                </button>
                <button class="tel-btn" id="tel-float-bumpers-btn" style="background:rgba(0,255,200,0.18); border-color:rgba(0,255,200,0.5); color:#00ffc8; font-weight:bold;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/></svg>
                    <span id="tel-float-bumpers-text">Bumpers en Pantalla: ON</span>
                </button>
                <button class="tel-btn" id="tel-toggle-mouse-mode">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="7"/><line x1="12" y1="6" x2="12" y2="10"/></svg>
                    <span>Modo Ratón / PC (M)</span>
                </button>
                <button class="tel-btn" id="tel-toggle-touch-btn" style="background:rgba(56,189,248,0.12); border-color:rgba(56,189,248,0.4); color:#38bdf8;">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    <span id="tel-touch-btn-text">Ocultar Táctiles</span>
                </button>
                <button class="tel-btn" id="tel-rumble-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h2m16 0h2M5.6 5.6l1.4 1.4m10 10l1.4 1.4M5.6 18.4l1.4-1.4m10-10l1.4-1.4M9 9h6v6H9z"/></svg>
                    <span>Test Rumble</span>
                </button>
                <button class="tel-btn" id="tel-fullscreen-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
                    <span>Pantalla Completa</span>
                </button>
                <button class="tel-btn" id="tel-clear-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    <span>Limpiar Registro</span>
                </button>
                <button class="tel-btn" id="tel-reset-avatar-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                    <span>Centrar Todo</span>
                </button>
            </div>
        </div>
    </div>

    <!-- MOCK ENGINE noVNC & Canvas Simulator ANTES del HUD -->
    <script>
    (function() {{
        const canvas = document.getElementById("noVNC_canvas");
        const ctx = canvas.getContext("2d");

        // Estado del Escritorio Simulado 1080p (Perfectamente Equilibrado en el Corredor Central)
        // Corredor Central Libre: X de 440 a 1480 (Los pulgares izquierdo y derecho no tapan nada)
        const state = {{
            width: 1920,
            height: 1080,
            cursor: {{ x: 960, y: 540, mask: 0, trail: [] }},
            window: {{
                x: 460, y: 110, w: 560, h: 370,
                isDragging: false, dragOffX: 0, dragOffY: 0,
                title: "Consola X11 — Diagnóstico Táctil",
                terminalLines: [
                    "Aether Studio v3.2.0 [Ubuntu 22.04 LTS]",
                    "Banco de Pruebas Táctiles y Telemetría en Vivo",
                    "Prueba a escribir con el teclado virtual o arrastrar:"
                ],
                activeInput: ""
            }},
            avatar: {{
                x: 1260, y: 280,
                radius: 38,
                vx: 0, vy: 0,
                angle: 0,
                isSprinting: false,
                isJumping: false,
                jumpScale: 1.0,
                trail: [],
                color: "#00ffc8",
                shieldActive: false,
                attackEffect: 0,
                lastMoveDir: "Centro"
            }},
            buttons: [
                {{ id: "btn_test_left", x: 485, y: 415, w: 120, h: 42, label: "Click Izq", clicked: false, time: 0 }},
                {{ id: "btn_test_right", x: 620, y: 415, w: 120, h: 42, label: "Click Der", clicked: false, time: 0 }},
                {{ id: "btn_test_dbl", x: 755, y: 415, w: 130, h: 42, label: "Doble Click", clicked: false, time: 0 }},
                {{ id: "btn_test_clear", x: 895, y: 415, w: 105, h: 42, label: "Limpiar", clicked: false, time: 0 }}
            ],
            desktopIcons: [
                {{ id: "icon_term", x: 490, y: 530, label: "Terminal X11", icon: ">_", color: "#38bdf8" }},
                {{ id: "icon_game", x: 620, y: 530, label: "Juegos Cloud", icon: "GFN", color: "#10b981" }},
                {{ id: "icon_files", x: 750, y: 530, label: "Archivos", icon: "DIR", color: "#f59e0b" }},
                {{ id: "icon_settings", x: 880, y: 530, label: "Ajustes", icon: "SYS", color: "#94a3b8" }}
            ],
            dropTarget: {{ x: 1060, y: 510, w: 380, h: 180, label: "Zona de Arrastre Libre (Drop Zone)", isOver: false }},
            contextMenu: {{
                visible: false,
                x: 0,
                y: 0,
                w: 240,
                h: 215,
                items: [
                    {{ id: "new_folder", label: "📁 Nueva Carpeta" }},
                    {{ id: "terminal", label: "⚡ Terminal X11" }},
                    {{ id: "browser", label: "🌐 Navegador Web" }},
                    {{ id: "refresh", label: "🔄 Actualizar Escritorio" }},
                    {{ id: "properties", label: "⚙️ Propiedades del Sistema" }}
                ]
            }},
            ripples: [],
            scrollIndicator: {{ active: false, x: 0, y: 0, text: "", time: 0 }}
        }};

        // Sistema de Telemetría hacia el Servidor Local con Buffer Rápido
        let telemetryBuffer = [];
        let lastSendTime = 0;

        function recordTelemetry(type, coords, target, action, details, anomaly, finger) {{
            const item = {{
                time: Date.now(),
                type: type,
                coords: typeof coords === "object" ? `(${{Math.round(coords.x)}}, ${{Math.round(coords.y)}})` : String(coords),
                finger: finger ? (typeof finger === "object" ? `(${{Math.round(finger.x)}}, ${{Math.round(finger.y)}})` : String(finger)) : "--",
                target: target || "Screen",
                action: action || "",
                anomaly: anomaly || "",
                details: details || ""
            }};
            telemetryBuffer.push(item);

            // Actualizar Ticker y Stream en el HUD flotante
            const ticker = document.getElementById("tel-ticker-text");
            if (ticker) {{
                const anomAlert = anomaly ? `[ALERTA: ${{anomaly}}] ` : "";
                ticker.textContent = `${{anomAlert}}[${{type}}] Dedo:${{item.finger}} -> Puntero:${{item.coords}} | ${{action}}`;
            }}

            const stream = document.getElementById("tel-stream-list");
            if (stream) {{
                const el = document.createElement("div");
                el.className = anomaly ? "tel-log-item" : "tel-log-item highlight";
                if (anomaly) el.style.color = "#f43f5e";
                el.textContent = `${{anomaly ? '[ALERTA] ' : ''}}[${{type}}] D:${{item.finger}} -> P:${{item.coords}} | ${{action}} | ${{details}}`;
                stream.insertBefore(el, stream.firstChild);
                while (stream.children.length > 8) {{
                    stream.removeChild(stream.lastChild);
                }}
            }}

            // Enviar de inmediato si es evento físico/calibración, o en ráfagas cada 100ms
            const now = Date.now();
            if (type.startsWith("PHYSICAL") || type.startsWith("CALIBRATE") || type.startsWith("RAW") || type.startsWith("ENCAPSULATION") || (now - lastSendTime > 100) || telemetryBuffer.length >= 8) {{
                flushTelemetry();
            }}
        }}
        window.recordTelemetry = recordTelemetry;

        window.isControllerMouseMode = false;
        window.isGameModeLocked = false;

        window.toggleGameLock = function(forceVal) {{
            window.isGameModeLocked = (typeof forceVal === "boolean") ? forceVal : !window.isGameModeLocked;
            if (window.isGameModeLocked) {{
                // Si se activa el bloqueo de juego, forzar Modo Juego XInput de inmediato
                window.isControllerMouseMode = false;
            }}
            const lockBtn = document.getElementById("tel-game-lock-btn");
            const lockText = document.getElementById("tel-game-lock-text");
            if (lockText) {{
                lockText.textContent = window.isGameModeLocked ? "Bloqueo Juego: ON" : "Bloqueo Juego: OFF";
            }}
            if (lockBtn) {{
                lockBtn.style.background = window.isGameModeLocked ? "rgba(16,185,129,0.25)" : "rgba(239,68,68,0.18)";
                lockBtn.style.borderColor = window.isGameModeLocked ? "rgba(16,185,129,0.6)" : "rgba(239,68,68,0.5)";
                lockBtn.style.color = window.isGameModeLocked ? "#10b981" : "#f87171";
            }}
            const modeBadge = document.getElementById("tel-gp-mode-badge");
            if (modeBadge) {{
                modeBadge.textContent = window.isGameModeLocked ? "JUEGO BLINDADO (Sin Interrupciones)" : (window.isControllerMouseMode ? "Modo: RATÓN (Desktop PC)" : "Modo: JUEGO (XInput)");
                modeBadge.style.color = window.isGameModeLocked ? "#10b981" : (window.isControllerMouseMode ? "#38bdf8" : "#00ffc8");
                modeBadge.style.borderColor = window.isGameModeLocked ? "rgba(16,185,129,0.5)" : (window.isControllerMouseMode ? "rgba(56,189,248,0.4)" : "rgba(0,255,200,0.3)");
            }}
            // Al activar el Bloqueo de Juego, colapsar el HUD automáticamente para no tapar el juego
            const box = document.getElementById("telemetry-hud-box");
            if (window.isGameModeLocked && box) {{
                box.classList.add("collapsed");
                const colText = document.getElementById("tel-collapse-text");
                const colSvg = document.getElementById("tel-collapse-svg");
                if (colText) colText.textContent = "EXPANDIR";
                if (colSvg) colSvg.style.transform = "rotate(0deg)";
            }}
            // Ocultar cualquier toast inmediatamente
            const toast = document.getElementById("tel-mode-toast");
            if (toast) {{
                toast.style.opacity = "0";
                toast.style.transform = "translateX(-50%) translateY(0px)";
            }}
            if (navigator.vibrate) navigator.vibrate(window.isGameModeLocked ? [70, 50, 70] : 40);
            const cur = (typeof state !== "undefined" && state.cursor) ? state.cursor : {{ x: 960, y: 540 }};
            recordTelemetry("GAME_LOCK", cur, "Security", "Toggle", window.isGameModeLocked ? "Bloqueo de Juego ACTIVADO: 100% del mando blindado para el juego, atajos bloqueados, banners silenciados" : "Bloqueo de Juego DESACTIVADO");
        }};

        window.toggleMouseMode = function(forceVal) {{
            if (window.isGameModeLocked) {{
                // Si el juego está blindado, NUNCA cambiar a modo ratón ni mostrar interrupciones
                const cur = (typeof state !== "undefined" && state.cursor) ? state.cursor : {{ x: 960, y: 540 }};
                recordTelemetry("MODE_SWITCH_BLOCKED", cur, "Security", "Ignored", "Intento de conmutación bloqueado porque Bloqueo de Juego está activo");
                return;
            }}
            window.isControllerMouseMode = (typeof forceVal === "boolean") ? forceVal : !window.isControllerMouseMode;
            const modeBadge = document.getElementById("tel-gp-mode-badge");
            if (modeBadge) {{
                modeBadge.textContent = window.isControllerMouseMode ? "Modo: RATÓN (Desktop PC)" : "Modo: JUEGO (XInput)";
                modeBadge.style.color = window.isControllerMouseMode ? "#38bdf8" : "#00ffc8";
                modeBadge.style.borderColor = window.isControllerMouseMode ? "rgba(56,189,248,0.4)" : "rgba(0,255,200,0.3)";
            }}
            const toast = document.getElementById("tel-mode-toast");
            if (toast) {{
                toast.textContent = window.isControllerMouseMode ? "MODO RATÓN PC ACTIVADO (Stick: Cursor | RT/A: Clic Izq | LT/X: Clic Der)" : "MODO JUEGO XINPUT ACTIVADO (Avatar en Movimiento)";
                toast.style.borderColor = window.isControllerMouseMode ? "#38bdf8" : "#00ffc8";
                toast.style.boxShadow = window.isControllerMouseMode ? "0 0 25px rgba(56,189,248,0.5)" : "0 0 25px rgba(0,255,200,0.4)";
                toast.style.color = window.isControllerMouseMode ? "#38bdf8" : "#00ffc8";
                toast.style.opacity = "1";
                toast.style.transform = "translateX(-50%) translateY(12px)";
                clearTimeout(window._modeToastTimer);
                window._modeToastTimer = setTimeout(() => {{
                    toast.style.opacity = "0";
                    toast.style.transform = "translateX(-50%) translateY(0px)";
                }}, 2200);
            }}
            if (navigator.vibrate) {{
                navigator.vibrate(window.isControllerMouseMode ? [40, 50, 60] : [70, 30]);
            }}
            const cur = (typeof state !== "undefined" && state.cursor) ? state.cursor : {{ x: 960, y: 540 }};
            recordTelemetry("MODE_SWITCH", cur, "Input", "Toggle", window.isControllerMouseMode ? "Mando controla el ratón del PC (Stick = Cursor, RT/A = Clic Izq, LT/X = Clic Der)" : "Mando controla el Avatar de juego");
        }};

        function flushTelemetry() {{
            if (telemetryBuffer.length === 0) return;
            const payload = telemetryBuffer;
            telemetryBuffer = [];
            lastSendTime = Date.now();

            fetch("/api/log", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ entries: payload }})
            }}).catch(() => {{}});
        }}
        setInterval(flushTelemetry, 300);

        // Renderizado del Canvas de Prueba a 60 FPS
        function drawCanvas() {{
            ctx.clearRect(0, 0, state.width, state.height);

            // 1. Fondo de Escritorio Cyberpunk
            const bgGrad = ctx.createRadialGradient(960, 540, 150, 960, 540, 1150);
            bgGrad.addColorStop(0, "#0e182e");
            bgGrad.addColorStop(0.55, "#070c18");
            bgGrad.addColorStop(1, "#03060c");
            ctx.fillStyle = bgGrad;
            ctx.fillRect(0, 0, state.width, state.height);

            // Cuadrícula sutil
            ctx.strokeStyle = "rgba(56, 189, 248, 0.05)";
            ctx.lineWidth = 1;
            for (let x = 0; x < state.width; x += 80) {{
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, state.height); ctx.stroke();
            }}
            for (let y = 0; y < state.height; y += 80) {{
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(state.width, y); ctx.stroke();
            }}

            // Marcadores de Zona Segura Central (Corredor Libre de Pulgares)
            ctx.fillStyle = "rgba(0, 255, 200, 0.04)";
            ctx.fillRect(440, 50, 1040, 980);
            ctx.strokeStyle = "rgba(0, 255, 200, 0.12)";
            ctx.lineWidth = 1;
            ctx.strokeRect(440, 50, 1040, 980);

            // Barra Superior de Estado
            ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
            ctx.fillRect(0, 0, state.width, 42);
            ctx.fillStyle = "rgba(0, 255, 200, 0.4)";
            ctx.fillRect(0, 41, state.width, 1);

            ctx.fillStyle = "#00ffc8";
            ctx.font = "bold 16px monospace";
            ctx.fillText("// AETHER CLOUD PC — LABORATORIO TÁCTIL Y TELEMETRÍA", 460, 27);

            ctx.fillStyle = "#94a3b8";
            ctx.font = "13px monospace";
            ctx.fillText("Espacio Virtual: 1920x1080 | Telemetría: Activa", 1080, 27);

            // Indicador dinámico de modo en cabecera
            if (window.isGameModeLocked) {{
                ctx.fillStyle = "rgba(16, 185, 129, 0.22)";
                ctx.strokeStyle = "#10b981";
                ctx.beginPath();
                ctx.roundRect(1510, 7, 285, 28, 6);
                ctx.fill();
                ctx.stroke();
                ctx.fillStyle = "#10b981";
                ctx.font = "bold 12px monospace";
                ctx.fillText("JUEGO BLINDADO (SIN INTERRUPCIONES)", 1520, 26);
            }} else if (window.isControllerMouseMode) {{
                ctx.fillStyle = "rgba(56, 189, 248, 0.18)";
                ctx.strokeStyle = "#38bdf8";
                ctx.beginPath();
                ctx.roundRect(1530, 7, 265, 28, 6);
                ctx.fill();
                ctx.stroke();
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 12px monospace";
                ctx.fillText("MODO RATÓN PC (SELECT + R3)", 1538, 26);
            }} else {{
                ctx.fillStyle = "rgba(0, 255, 200, 0.14)";
                ctx.strokeStyle = "#00ffc8";
                ctx.beginPath();
                ctx.roundRect(1530, 7, 265, 28, 6);
                ctx.fill();
                ctx.stroke();
                ctx.fillStyle = "#00ffc8";
                ctx.font = "bold 12px monospace";
                ctx.fillText("MODO JUEGO XINPUT (SELECT + R3)", 1532, 26);
            }}

            // 2. Ventana Interactiva Arrastrable
            const win = state.window;
            ctx.save();
            ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
            ctx.shadowBlur = 28;
            ctx.shadowOffsetY = 10;
            ctx.fillStyle = "rgba(15, 23, 42, 0.96)";
            ctx.beginPath();
            ctx.roundRect(win.x, win.y, win.w, win.h, 14);
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.strokeStyle = win.isDragging ? "#00ffc8" : "rgba(56, 189, 248, 0.45)";
            ctx.lineWidth = win.isDragging ? 2.5 : 1.5;
            ctx.stroke();

            // Cabecera de la ventana
            ctx.fillStyle = win.isDragging ? "rgba(30, 58, 80, 0.95)" : "rgba(30, 41, 59, 0.95)";
            ctx.beginPath();
            ctx.roundRect(win.x, win.y, win.w, 42, [14, 14, 0, 0]);
            ctx.fill();

            // Botones semáforo
            ctx.fillStyle = "#ef4444"; ctx.beginPath(); ctx.arc(win.x + 22, win.y + 21, 6, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#f59e0b"; ctx.beginPath(); ctx.arc(win.x + 40, win.y + 21, 6, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#10b981"; ctx.beginPath(); ctx.arc(win.x + 58, win.y + 21, 6, 0, Math.PI*2); ctx.fill();

            ctx.fillStyle = "#e2e8f0";
            ctx.font = "bold 14px sans-serif";
            ctx.fillText(win.title + (win.isDragging ? " [ARRASTRANDO...]" : ""), win.x + 78, win.y + 26);

            // Terminal interior
            ctx.fillStyle = "#050811";
            ctx.beginPath();
            ctx.roundRect(win.x + 16, win.y + 52, win.w - 32, 230, 8);
            ctx.fill();
            ctx.strokeStyle = "rgba(255,255,255,0.08)";
            ctx.stroke();

            ctx.fillStyle = "#38bdf8";
            ctx.font = "13px monospace";
            let lineY = win.y + 78;
            win.terminalLines.forEach((l) => {{
                ctx.fillText(l, win.x + 28, lineY);
                lineY += 22;
            }});

            // Línea de entrada activa de teclado
            ctx.fillStyle = "#00ffc8";
            ctx.fillText("> " + win.activeInput + (Math.floor(Date.now() / 500) % 2 === 0 ? "█" : ""), win.x + 28, lineY + 12);

            // Botones de Prueba en la ventana
            state.buttons.forEach(b => {{
                const isLit = (Date.now() - b.time < 350);
                ctx.fillStyle = isLit ? "#00ffc8" : "rgba(30, 41, 59, 0.9)";
                ctx.beginPath();
                ctx.roundRect(b.x, b.y, b.w, b.h, 8);
                ctx.fill();
                ctx.strokeStyle = isLit ? "#ffffff" : "rgba(56, 189, 248, 0.4)";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                ctx.fillStyle = isLit ? "#0a0f1a" : "#f1f5f9";
                ctx.font = "bold 13px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText(b.label, b.x + b.w / 2, b.y + 26);
                ctx.textAlign = "left";
            }});
            ctx.restore();

            // 3. Gamepad Arena: Avatar en Posición Equilibrada (Columna Derecha Libre de Pulgares)
            const av = state.avatar;
            ctx.save();
            if (window.isControllerMouseMode) {{
                ctx.globalAlpha = 0.25;
            }}
            ctx.strokeStyle = "rgba(0, 255, 200, 0.3)";
            ctx.lineWidth = 2;
            ctx.setLineDash([6, 6]);
            ctx.beginPath();
            ctx.arc(1260, 280, 160, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = "rgba(0, 255, 200, 0.5)";
            ctx.font = "bold 14px monospace";
            ctx.fillText("ARENA XINPUT / GAMEPAD", 1180, 105);
            ctx.fillStyle = "#94a3b8";
            ctx.font = "11px monospace";
            ctx.fillText("Stick L: Mover | Stick R: Mirar", 1160, 125);
            ctx.fillText("L3: Sprint | A: Saltar | B: Dash", 1160, 142);
            ctx.fillText("D-Pad: 8-Way | X: Ataque | Y: Escudo", 1160, 159);

            // Actualizar posición del Avatar con fricción
            av.x += av.vx;
            av.y += av.vy;
            av.vx *= 0.88;
            av.vy *= 0.88;

            // Restricción dentro del área
            const dx = av.x - 1260;
            const dy = av.y - 280;
            const dist = Math.hypot(dx, dy);
            if (dist > 140) {{
                const angle = Math.atan2(dy, dx);
                av.x = 1260 + Math.cos(angle) * 140;
                av.y = 280 + Math.sin(angle) * 140;
            }}

            // Estela de Sprint
            if (av.isSprinting && Math.hypot(av.vx, av.vy) > 0.5) {{
                av.trail.push({{ x: av.x, y: av.y, alpha: 0.6 }});
            }}
            av.trail.forEach((t) => {{
                ctx.fillStyle = `rgba(0, 255, 200, ${{t.alpha}})`;
                ctx.beginPath();
                ctx.arc(t.x, t.y, av.radius * 0.7, 0, Math.PI * 2);
                ctx.fill();
                t.alpha *= 0.85;
            }});
            av.trail = av.trail.filter(t => t.alpha > 0.05);

            // Efecto de Ataque (Botón X)
            if (av.attackEffect > 0) {{
                ctx.strokeStyle = `rgba(59, 130, 246, ${{av.attackEffect}})`;
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.arc(av.x, av.y, av.radius * (2.2 - av.attackEffect), 0, Math.PI * 2);
                ctx.stroke();
                av.attackEffect -= 0.08;
            }}

            // Escudo (Botón Y)
            if (av.shieldActive) {{
                ctx.fillStyle = "rgba(245, 158, 11, 0.25)";
                ctx.strokeStyle = "#f59e0b";
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.arc(av.x, av.y, av.radius * 1.35, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            }}

            // Cuerpo del Avatar
            const renderRadius = av.radius * (av.isJumping ? av.jumpScale : 1.0);
            ctx.shadowColor = av.color;
            ctx.shadowBlur = 18;
            ctx.fillStyle = av.color;
            ctx.beginPath();
            ctx.arc(av.x, av.y, renderRadius, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.fillStyle = "#0a0f1a";
            ctx.beginPath();
            ctx.arc(av.x, av.y, renderRadius * 0.6, 0, Math.PI * 2);
            ctx.fill();

            // Puntero de orientación / mira (Stick Derecho)
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(av.x, av.y);
            ctx.lineTo(av.x + Math.cos(av.angle) * (renderRadius * 1.5), av.y + Math.sin(av.angle) * (renderRadius * 1.5));
            ctx.stroke();

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 13px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(av.isSprinting ? "SPRINT (L3)" : (av.isJumping ? "SALTO (A)" : "PILOTO"), av.x, av.y + renderRadius + 20);
            ctx.textAlign = "left";
            ctx.restore();

            if (window.isControllerMouseMode) {{
                ctx.save();
                ctx.fillStyle = "rgba(10, 15, 26, 0.92)";
                ctx.strokeStyle = "#38bdf8";
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.roundRect(1080, 185, 360, 190, 12);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 15px monospace";
                ctx.textAlign = "center";
                ctx.fillText("🖱️ MODO RATÓN PC ACTIVO", 1260, 212);
                ctx.fillStyle = "#e2e8f0";
                ctx.font = "11px monospace";
                ctx.fillText("Stick L: Puntero (L3: Precisión)", 1260, 235);
                ctx.fillText("Stick R: Scroll 2D Páginas (R3: Clic Central)", 1260, 255);
                ctx.fillText("A / RT: Clic Izq  |  X / LT: Clic Der", 1260, 275);
                ctx.fillText("B: Doble Clic  |  Y: Escape  |  START: Enter", 1260, 295);
                ctx.fillText("LB / RB: Atrás / Adelante  |  D-Pad: Flechas", 1260, 315);
                ctx.fillStyle = "#f59e0b";
                ctx.font = "bold 11px monospace";
                ctx.fillText("SELECT + R3: Volver a Modo Juego", 1260, 348);
                ctx.textAlign = "left";
                ctx.restore();
            }}

            // 4. Zona Inferior de Prueba de Escritorio (Iconos y Zona de Arrastre)
            // Iconos
            state.desktopIcons.forEach(ic => {{
                ctx.fillStyle = "rgba(15, 23, 42, 0.7)";
                ctx.beginPath();
                ctx.roundRect(ic.x, ic.y, 90, 80, 10);
                ctx.fill();
                ctx.strokeStyle = "rgba(255,255,255,0.12)";
                ctx.stroke();

                ctx.fillStyle = ic.color;
                ctx.font = "bold 22px monospace";
                ctx.textAlign = "center";
                ctx.fillText(ic.icon, ic.x + 45, ic.y + 42);

                ctx.fillStyle = "#cbd5e1";
                ctx.font = "bold 11px sans-serif";
                ctx.fillText(ic.label, ic.x + 45, ic.y + 68);
                ctx.textAlign = "left";
            }});

            // Zona de Soltado / Drop Target
            const dt = state.dropTarget;
            ctx.strokeStyle = dt.isOver ? "#00ffc8" : "rgba(56, 189, 248, 0.35)";
            ctx.lineWidth = dt.isOver ? 2.5 : 1.5;
            ctx.setLineDash([8, 8]);
            ctx.fillStyle = dt.isOver ? "rgba(0, 255, 200, 0.1)" : "rgba(15, 23, 42, 0.5)";
            ctx.beginPath();
            ctx.roundRect(dt.x, dt.y, dt.w, dt.h, 12);
            ctx.fill();
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = dt.isOver ? "#00ffc8" : "#94a3b8";
            ctx.font = "bold 13px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(dt.label, dt.x + dt.w / 2, dt.y + dt.h / 2 - 8);
            ctx.font = "11px monospace";
            ctx.fillText("Arrastra la ventana aquí para verificar precisión", dt.x + dt.w / 2, dt.y + dt.h / 2 + 14);
            ctx.textAlign = "left";

            // 4.5. Ondas de Impacto Visual por Clic (Ripples)
            if (state.ripples && state.ripples.length > 0) {{
                for (let i = state.ripples.length - 1; i >= 0; i--) {{
                    const r = state.ripples[i];
                    r.radius += (r.maxRadius - r.radius) * 0.25 + 1.5;
                    r.alpha *= 0.88;
                    if (r.alpha < 0.03 || r.radius >= r.maxRadius) {{
                        state.ripples.splice(i, 1);
                        continue;
                    }}
                    ctx.save();
                    ctx.beginPath();
                    ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
                    ctx.strokeStyle = r.color;
                    ctx.globalAlpha = r.alpha;
                    ctx.lineWidth = 3;
                    ctx.shadowColor = r.color;
                    ctx.shadowBlur = 16;
                    ctx.stroke();
                    ctx.restore();
                }}
            }}

            // 4.6. Menú Contextual Real de Escritorio (Clic Derecho X / LT)
            if (state.contextMenu && state.contextMenu.visible) {{
                const cm = state.contextMenu;
                ctx.save();
                ctx.shadowColor = "rgba(0, 0, 0, 0.85)";
                ctx.shadowBlur = 24;
                ctx.shadowOffsetX = 4;
                ctx.shadowOffsetY = 6;
                ctx.fillStyle = "rgba(15, 23, 42, 0.96)";
                ctx.strokeStyle = "#38bdf8";
                ctx.lineWidth = 1.8;
                ctx.beginPath();
                ctx.roundRect(cm.x, cm.y, cm.w, cm.h, 10);
                ctx.fill();
                ctx.stroke();
                ctx.shadowBlur = 0;

                // Cabecera de menú contextual
                ctx.fillStyle = "rgba(56, 189, 248, 0.18)";
                ctx.beginPath();
                ctx.roundRect(cm.x, cm.y, cm.w, 32, [10, 10, 0, 0]);
                ctx.fill();
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 11px monospace";
                ctx.fillText("MENÚ CONTEXTUAL PC", cm.x + 14, cm.y + 20);

                // Opciones del Menú con Resaltado Hover
                const itemH = 34;
                const curX = state.cursor.x;
                const curY = state.cursor.y;
                cm.items.forEach((item, idx) => {{
                    const iy = cm.y + 36 + (idx * itemH);
                    const isHovered = (curX >= cm.x && curX <= cm.x + cm.w && curY >= iy && curY < iy + itemH);
                    if (isHovered) {{
                        ctx.fillStyle = "rgba(56, 189, 248, 0.32)";
                        ctx.beginPath();
                        ctx.roundRect(cm.x + 6, iy + 2, cm.w - 12, itemH - 4, 6);
                        ctx.fill();
                    }}
                    ctx.fillStyle = isHovered ? "#ffffff" : "#cbd5e1";
                    ctx.font = isHovered ? "bold 13px sans-serif" : "12px sans-serif";
                    ctx.fillText(item.label, cm.x + 16, iy + 22);
                }});
                ctx.restore();
            }}

            // 4.7. Indicador Visual de Scroll 2D (Stick Derecho)
            if (state.scrollIndicator && state.scrollIndicator.active && (Date.now() - state.scrollIndicator.time < 750)) {{
                const si = state.scrollIndicator;
                ctx.save();
                ctx.fillStyle = "rgba(245, 158, 11, 0.95)";
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.roundRect(si.x + 15, si.y - 35, 135, 26, 13);
                ctx.fill();
                ctx.stroke();
                ctx.fillStyle = "#000000";
                ctx.font = "bold 11px monospace";
                ctx.textAlign = "center";
                ctx.fillText(si.text, si.x + 82, si.y - 18);
                ctx.textAlign = "left";
                ctx.restore();
            }}

            // 5. Renderizado del Puntero de Ratón Virtual del Escritorio (Hardware Accelerated)
            if (window.isControllerMouseMode || state.cursor.mask > 0 || (Date.now() - lastLoggedMove < 4000)) {{
                const cx = state.cursor.x;
                const cy = state.cursor.y;
                const isDownLeft = (state.cursor.mask === 1);
                const isDownRight = (state.cursor.mask === 4);

                ctx.save();
                // Halo de pulsación o arrastre
                if (isDownLeft) {{
                    ctx.beginPath();
                    ctx.arc(cx, cy, 26, 0, Math.PI * 2);
                    ctx.fillStyle = "rgba(56, 189, 248, 0.4)";
                    ctx.fill();
                    ctx.strokeStyle = "#38bdf8";
                    ctx.lineWidth = 2.5;
                    ctx.stroke();
                }} else if (isDownRight) {{
                    ctx.beginPath();
                    ctx.arc(cx, cy, 26, 0, Math.PI * 2);
                    ctx.fillStyle = "rgba(245, 158, 11, 0.4)";
                    ctx.fill();
                    ctx.strokeStyle = "#f59e0b";
                    ctx.lineWidth = 2.5;
                    ctx.stroke();
                }}

                // Sombra de puntero
                ctx.shadowColor = "rgba(0, 0, 0, 0.9)";
                ctx.shadowBlur = 12;
                ctx.shadowOffsetX = 3;
                ctx.shadowOffsetY = 4;

                // Flecha de puntero OS de alta visibilidad
                ctx.beginPath();
                ctx.moveTo(cx, cy);
                ctx.lineTo(cx, cy + 24);
                ctx.lineTo(cx + 6, cy + 18);
                ctx.lineTo(cx + 13, cy + 28);
                ctx.lineTo(cx + 17, cy + 25);
                ctx.lineTo(cx + 10, cy + 16);
                ctx.lineTo(cx + 19, cy + 16);
                ctx.closePath();

                ctx.fillStyle = isDownLeft ? "#38bdf8" : (isDownRight ? "#f59e0b" : "#ffffff");
                ctx.fill();
                ctx.strokeStyle = "#000000";
                ctx.lineWidth = 2;
                ctx.stroke();

                // Placa flotante de coordenadas y estado
                ctx.shadowBlur = 0;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;
                ctx.fillStyle = "rgba(10, 15, 26, 0.9)";
                ctx.strokeStyle = isDownLeft ? "#38bdf8" : "rgba(255, 255, 255, 0.35)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.roundRect(cx + 20, cy + 20, 125, 24, 6);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = isDownLeft ? "#38bdf8" : "#94a3b8";
                ctx.font = "bold 11px monospace";
                ctx.fillText(isDownLeft ? "CLIC / ARRASTRE" : `X:${{Math.round(cx)}} Y:${{Math.round(cy)}}`, cx + 26, cy + 36);

                ctx.restore();
            }}

            requestAnimationFrame(drawCanvas);
        }}
        requestAnimationFrame(drawCanvas);

        // Objeto RFB Simulado con Registro Exhaustivo de Deslizamiento y Consecuencias
        let lastLoggedMove = 0;
        let lastLoggedVx = 960;
        let lastLoggedVy = 540;

        const mockRFB = {{
            _rfbConnectionState: 'connected',
            _viewOnly: false,
            _canvas: canvas,
            _display: {{
                _scale: 1,
                _viewportLoc: {{ x: 0, y: 0 }}
            }},
            _sendMouse: function(vx, vy, mask) {{
                const oldMask = state.cursor.mask;
                const oldVx = state.cursor.x;
                const oldVy = state.cursor.y;

                state.cursor.x = Math.max(0, Math.min(1920, vx));
                state.cursor.y = Math.max(0, Math.min(1080, vy));
                state.cursor.mask = mask;

                const cur = state.cursor;
                const win = state.window;
                const dt = state.dropTarget;

                const deltaVirtX = cur.x - oldVx;
                const deltaVirtY = cur.y - oldVy;
                const moveDist = Math.hypot(deltaVirtX, deltaVirtY);

                let activeFinger = null;
                if (window.touchTrackMap && window.touchTrackMap.size > 0) {{
                    const ft = window.touchTrackMap.values().next().value;
                    if (ft) activeFinger = {{ x: ft.lastX, y: ft.lastY }};
                }}

                // Registro de Deslizamiento Continuo del Puntero (Cada 75ms o movimientos claros)
                const now = Date.now();
                if (moveDist > 2 && (now - lastLoggedMove > 75)) {{
                    lastLoggedMove = now;
                    const actionName = win.isDragging ? "WIN_DRAGGING" : (mask === 1 ? "MOUSE_DRAG" : "POINTER_MOVE");
                    const targetName = win.isDragging ? "WindowHeader" : "DesktopCanvas";
                    let anomaly = "";
                    if (cur.x <= 0 || cur.x >= 1920 || cur.y <= 0 || cur.y >= 1080) {{
                        anomaly = "BORDE_ESCRITORIO";
                    }}
                    recordTelemetry(actionName, cur, targetName, "Move", `Delta Virt: (dx:${{Math.round(deltaVirtX)}}, dy:${{Math.round(deltaVirtY)}}) | Puntero en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, anomaly, activeFinger);
                }}

                // Click Izquierdo presionado
                if (mask === 1 && oldMask !== 1) {{
                    recordTelemetry("CLICK_LEFT", cur, "Canvas", "Down", `Virtual(${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);

                    // Onda visual inmediata en cualquier parte de la pantalla
                    if (!state.ripples) state.ripples = [];
                    state.ripples.push({{ x: cur.x, y: cur.y, radius: 4, maxRadius: 44, color: "#38bdf8", alpha: 1.0 }});

                    // 1. Comprobar interacción con Menú Contextual si está abierto
                    if (state.contextMenu && state.contextMenu.visible) {{
                        const cm = state.contextMenu;
                        if (cur.x >= cm.x && cur.x <= cm.x + cm.w && cur.y >= cm.y + 36 && cur.y <= cm.y + cm.h) {{
                            const itemIdx = Math.floor((cur.y - (cm.y + 36)) / 34);
                            if (itemIdx >= 0 && itemIdx < cm.items.length) {{
                                const chosen = cm.items[itemIdx];
                                win.terminalLines.push(`[MENÚ PC] Ejecutando "${{chosen.label}}"...`);
                                if (win.terminalLines.length > 7) win.terminalLines.shift();
                                recordTelemetry("CONTEXT_MENU_CLICK", cur, chosen.label, "Execute", "Opción de menú contextual ejecutada", "", activeFinger);
                            }}
                        }}
                        state.contextMenu.visible = false;
                        return;
                    }}

                    // Comprobar arrastre de cabecera de ventana
                    if (cur.x >= win.x && cur.x <= win.x + win.w &&
                        cur.y >= win.y && cur.y <= win.y + 42) {{
                        win.isDragging = true;
                        win.dragOffX = cur.x - win.x;
                        win.dragOffY = cur.y - win.y;
                        recordTelemetry("WIN_DRAG", cur, "WindowHeader", "StartDrag", "Ventana enganchada con éxito", "", activeFinger);
                    }}

                    // Comprobar botones dentro de la ventana
                    let hitBtn = false;
                    state.buttons.forEach(b => {{
                        if (cur.x >= b.x && cur.x <= b.x + b.w &&
                            cur.y >= b.y && cur.y <= b.y + b.h) {{
                            hitBtn = true;
                            b.time = Date.now();
                            if (b.id === "btn_test_clear") {{
                                win.terminalLines = ["Consola limpiada."];
                                win.activeInput = "";
                            }} else {{
                                win.terminalLines.push(`[CLICK] ${{b.label}} activado en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`);
                                if (win.terminalLines.length > 7) win.terminalLines.shift();
                            }}
                            recordTelemetry("BTN_CLICK", cur, b.label, "Pressed", "Botón interior de ventana pulsado", "", activeFinger);
                        }}
                    }});

                    // Comprobar iconos de escritorio
                    let hitIcon = false;
                    state.desktopIcons.forEach(ic => {{
                        if (cur.x >= ic.x && cur.x <= ic.x + 90 &&
                            cur.y >= ic.y && cur.y <= ic.y + 80) {{
                            hitIcon = true;
                            win.terminalLines.push(`[LANZADOR] Abriendo ${{ic.label}}...`);
                            if (win.terminalLines.length > 7) win.terminalLines.shift();
                            recordTelemetry("ICON_LAUNCH", cur, ic.label, "Launch", "Acceso directo ejecutado", "", activeFinger);
                        }}
                    }});

                    // Clic en fondo de escritorio libre
                    if (!hitBtn && !hitIcon && !win.isDragging) {{
                        win.terminalLines.push(`[CLIC IZQ (RT / A)] en X:${{Math.round(cur.x)}} Y:${{Math.round(cur.y)}}`);
                        if (win.terminalLines.length > 7) win.terminalLines.shift();
                    }}
                }}

                // Movimiento mientras arrastra la ventana
                if (win.isDragging) {{
                    if (mask === 1) {{
                        win.x = Math.max(0, Math.min(1920 - win.w, cur.x - win.dragOffX));
                        win.y = Math.max(42, Math.min(1080 - win.h, cur.y - win.dragOffY));

                        // Verificar si está sobre la zona de soltado
                        dt.isOver = (win.x + win.w/2 >= dt.x && win.x + win.w/2 <= dt.x + dt.w &&
                                     win.y + win.h/2 >= dt.y && win.y + win.h/2 <= dt.y + dt.h);
                    }} else {{
                        win.isDragging = false;
                        dt.isOver = false;
                        recordTelemetry("WIN_DRAG", cur, "WindowHeader", "Drop", `Ventana soltada en (${{Math.round(win.x)}}, ${{Math.round(win.y)}})`, "", activeFinger);
                    }}
                }}

                // Click Derecho presionado (LT / Botón X)
                if (mask === 4 && oldMask !== 4) {{
                    recordTelemetry("CLICK_RIGHT", cur, "Canvas", "Down", `Menu Contextual activado en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);
                    if (!state.ripples) state.ripples = [];
                    state.ripples.push({{ x: cur.x, y: cur.y, radius: 4, maxRadius: 48, color: "#f59e0b", alpha: 1.0 }});

                    if (state.contextMenu) {{
                        state.contextMenu.visible = true;
                        state.contextMenu.x = Math.min(1920 - 250, Math.max(10, cur.x));
                        state.contextMenu.y = Math.min(1080 - 230, Math.max(10, cur.y));
                    }}
                    win.terminalLines.push(`[MENÚ CONTEXTUAL (LT/X)] Abierto en X:${{Math.round(cur.x)}} Y:${{Math.round(cur.y)}}`);
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }}

                // Click Central presionado (R3 Click o botón de rueda)
                if (mask === 2 && oldMask !== 2) {{
                    recordTelemetry("CLICK_MIDDLE", cur, "Canvas", "Down", `Clic Central (R3) en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);
                    if (!state.ripples) state.ripples = [];
                    state.ripples.push({{ x: cur.x, y: cur.y, radius: 4, maxRadius: 40, color: "#a855f7", alpha: 1.0 }});
                    win.terminalLines.push(`[CLIC CENTRAL R3] en X:${{Math.round(cur.x)}} Y:${{Math.round(cur.y)}}`);
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }}

                // Scroll 2D de Rueda (Stick R: Arriba/Abajo/Izq/Der)
                if ((mask === 8 || mask === 16 || mask === 32 || mask === 64) && oldMask === 0) {{
                    const sDesc = (mask === 8) ? "Scroll Arriba ▲" : ((mask === 16) ? "Scroll Abajo ▼" : ((mask === 32) ? "Scroll Izquierda ◀" : "Scroll Derecha ▶"));
                    recordTelemetry("MOUSE_SCROLL", cur, "DesktopCanvas", "Wheel", sDesc, "", activeFinger);
                    if (state.scrollIndicator) {{
                        state.scrollIndicator = {{ active: true, x: cur.x, y: cur.y, text: sDesc, time: Date.now() }};
                    }}
                    win.terminalLines.push(`[SCROLL STICK R] ${{sDesc}}`);
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }}

                if (mask === 0 && oldMask !== 0) {{
                    recordTelemetry("MOUSE_UP", cur, "Canvas", "Release", "Botones liberados", "", activeFinger);
                }}
            }},

            // Inyección de Teclado
            sendKey: function(keysym, down) {{
                if (!down) return;
                recordTelemetry("KEY_INPUT", "-", "VirtualKbd", "KeyDown", `Keysym: ${{keysym}}`);
                const win = state.window;

                if (keysym === 0xff1b || keysym === 27) {{ // Escape
                    if (state.contextMenu && state.contextMenu.visible) {{
                        state.contextMenu.visible = false;
                        win.terminalLines.push("[ESCAPE (Y)] Menú contextual cerrado.");
                        if (win.terminalLines.length > 7) win.terminalLines.shift();
                    }}
                }} else if (keysym === 65288) {{ // Backspace
                    win.activeInput = win.activeInput.slice(0, -1);
                }} else if (keysym === 65293) {{ // Enter
                    win.terminalLines.push("> " + win.activeInput);
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                    win.activeInput = "";
                }} else if (keysym >= 32 && keysym <= 126) {{
                    win.activeInput += String.fromCharCode(keysym);
                }}
            }},
            _sendKey: function(keysym, down) {{
                mockRFB.sendKey(keysym, down);
            }}
        }};

        window.UI = {{ rfb: mockRFB }};

        // Procesador Unificado de Control de PC por Mando (Desktop Mouse Mode)
        window.processDesktopMouseControls = function(axes, curBtns, prevBtns) {{
            if (typeof mockRFB === "undefined" || !state || !state.cursor) return;

            // 1. Stick Izquierdo (ax0, ax1): Movimiento Analógico del Cursor
            const ax0 = axes[0] || 0;
            const ax1 = axes[1] || 0;
            const magL = Math.hypot(ax0, ax1);
            if (magL > 0.08) {{
                // L3 (botón 10): Modo Precisión / Francotirador (35% velocidad para afinar clics)
                const isPrecision = !!curBtns[10];
                const baseSpeed = isPrecision ? 5.5 : 18.0;
                const factor = Math.pow(magL, 1.30) * baseSpeed;
                state.cursor.x = Math.max(10, Math.min(1910, state.cursor.x + (ax0 / magL) * factor));
                state.cursor.y = Math.max(10, Math.min(1070, state.cursor.y + (ax1 / magL) * factor));
                mockRFB._sendMouse(state.cursor.x, state.cursor.y, state.cursor.mask);
            }}

            // 2. Stick Derecho (ax2, ax3): Desplazamiento 2D de Páginas (Scroll Continuo)
            const ax2 = axes[2] || 0;
            const ax3 = axes[3] || 0;
            const scrollMag = Math.hypot(ax2, ax3);
            if (scrollMag > 0.18) {{
                const now = Date.now();
                const scrollInterval = Math.max(45, Math.round(180 - (scrollMag * 130)));
                if (!window._lastScrollTime || (now - window._lastScrollTime > scrollInterval)) {{
                    window._lastScrollTime = now;
                    if (Math.abs(ax3) >= Math.abs(ax2)) {{
                        // Scroll Vertical: Stick hacia arriba = Scroll Arriba (8) | Abajo = Scroll Abajo (16)
                        const scrollMask = (ax3 < 0) ? 8 : 16;
                        mockRFB._sendMouse(state.cursor.x, state.cursor.y, scrollMask);
                        setTimeout(() => mockRFB._sendMouse(state.cursor.x, state.cursor.y, 0), 20);
                    }} else {{
                        // Scroll Horizontal: Stick hacia la izq = Scroll Izq (32) | Der = Scroll Der (64)
                        const scrollMask = (ax2 < 0) ? 32 : 64;
                        mockRFB._sendMouse(state.cursor.x, state.cursor.y, scrollMask);
                        setTimeout(() => mockRFB._sendMouse(state.cursor.x, state.cursor.y, 0), 20);
                    }}
                }}
            }}

            // 3. Acciones del Puntero con Botones:
            // Botón A (0) o RT (7) = Clic Izquierdo Primario (Seleccionar / Arrastrar)
            const clickLeft = (curBtns[7] > 0.4) || !!curBtns[0];

            // Botón X (2) o LT (6) = Clic Derecho Secundario (Menú Contextual)
            const clickRight = (curBtns[6] > 0.4) || !!curBtns[2];

            // Botón R3 (11) = Clic Central de Ratón (Middle Click / botón de rueda)
            const clickMiddle = !!curBtns[11];

            const targetMask = clickRight ? 4 : (clickMiddle ? 2 : (clickLeft ? 1 : 0));
            if (targetMask !== state.cursor.mask) {{
                mockRFB._sendMouse(state.cursor.x, state.cursor.y, targetMask);
            }}

            // Botón B (1) = Doble Clic Izquierdo Instantáneo o Cerrar Menú Contextual
            if (curBtns[1] && !prevBtns[1]) {{
                if (state.contextMenu && state.contextMenu.visible) {{
                    state.contextMenu.visible = false;
                    state.window.terminalLines.push("[CANCELAR (B)] Menú contextual cerrado.");
                    if (state.window.terminalLines.length > 7) state.window.terminalLines.shift();
                }} else {{
                    if (!state.ripples) state.ripples = [];
                    state.ripples.push({{ x: state.cursor.x, y: state.cursor.y, radius: 4, maxRadius: 36, color: "#10b981", alpha: 1.0 }});
                    setTimeout(() => {{
                        state.ripples.push({{ x: state.cursor.x, y: state.cursor.y, radius: 4, maxRadius: 52, color: "#00ffc8", alpha: 1.0 }});
                    }}, 60);
                    state.window.terminalLines.push(`[DOBLE CLIC (B)] Ejecutado en (${{Math.round(state.cursor.x)}}, ${{Math.round(state.cursor.y)}})`);
                    if (state.window.terminalLines.length > 7) state.window.terminalLines.shift();

                    mockRFB._sendMouse(state.cursor.x, state.cursor.y, 1);
                    setTimeout(() => {{
                        mockRFB._sendMouse(state.cursor.x, state.cursor.y, 0);
                        setTimeout(() => {{
                            mockRFB._sendMouse(state.cursor.x, state.cursor.y, 1);
                            setTimeout(() => mockRFB._sendMouse(state.cursor.x, state.cursor.y, 0), 40);
                        }}, 50);
                    }}, 40);
                }}
            }}

            // Botón Y (3) = Tecla Escape (cierra diálogos, menús o ventanas activas)
            if (curBtns[3] && !prevBtns[3] && mockRFB.sendKey) {{
                mockRFB.sendKey(0xff1b, true);
                setTimeout(() => mockRFB.sendKey(0xff1b, false), 50);
            }}

            // LB (4) = Navegar Atrás (Browser Back / Historial)
            if (curBtns[4] && !prevBtns[4] && mockRFB.sendKey) {{
                mockRFB.sendKey(0xff51, true); // Alt + Left
                setTimeout(() => mockRFB.sendKey(0xff51, false), 50);
            }}

            // RB (5) = Navegar Adelante (Browser Forward)
            if (curBtns[5] && !prevBtns[5] && mockRFB.sendKey) {{
                mockRFB.sendKey(0xff53, true); // Alt + Right
                setTimeout(() => mockRFB.sendKey(0xff53, false), 50);
            }}

            // Cruceta D-Pad (12..15): Teclas de Flecha del Teclado (Arriba, Abajo, Izq, Der)
            if (curBtns[12] && !prevBtns[12] && mockRFB.sendKey) mockRFB.sendKey(0xff52, true);
            if (curBtns[13] && !prevBtns[13] && mockRFB.sendKey) mockRFB.sendKey(0xff54, true);
            if (curBtns[14] && !prevBtns[14] && mockRFB.sendKey) mockRFB.sendKey(0xff51, true);
            if (curBtns[15] && !prevBtns[15] && mockRFB.sendKey) mockRFB.sendKey(0xff53, true);

            // START (9) = Tecla Enter / Intro
            if (curBtns[9] && !prevBtns[9] && mockRFB.sendKey) {{
                mockRFB.sendKey(0xff0d, true);
                setTimeout(() => mockRFB.sendKey(0xff0d, false), 50);
            }}
        }};

        // -------------------------------------------------------------------------
        // MOCK WEBSOCKET: Emulador de Socket /gamepad para Mandos Táctiles (BigTech Test Harness)
        // -------------------------------------------------------------------------
        window._currentAxes = [0, 0, 0, 0];
        window._currentButtons = new Array(17).fill(0);

        (function() {{
            let prevBtns = new Array(17).fill(0);
            let lastAxesLogTime = 0;

            const BTN_LABELS = [
                "A (Salto)", "B (Dash)", "X (Ataque)", "Y (Escudo)",
                "LB (Bumper Izq)", "RB (Bumper Der)", "LT (Gatillo Izq)", "RT (Gatillo Der)",
                "VIEW (Compartir)", "MENU (Pausa)", "L3 (Sprint)", "R3 (Centrar)",
                "Cruceta ARRIBA", "Cruceta ABAJO", "Cruceta IZQUIERDA", "Cruceta DERECHA",
                "XBOX GUÍA"
            ];

            class MockGamepadSocket extends EventTarget {{
                constructor(url, protocols) {{
                    super();
                    this.url = url;
                    this.protocols = protocols;
                    this.readyState = 1; // WebSocket.OPEN
                    this.onopen = null;
                    this.onclose = null;
                    this.onerror = null;
                    this.onmessage = null;
                    window._mockGpSocket = this;

                    setTimeout(() => {{
                        if (typeof this.onopen === "function") this.onopen({{ type: "open" }});
                        this.dispatchEvent(new Event("open"));
                    }}, 25);
                }}

                send(data) {{
                    try {{
                        const pkg = (typeof data === "string") ? JSON.parse(data) : data;
                        if (!pkg || !pkg.buttons || !pkg.axes) return;

                        const btns = pkg.buttons;
                        const axes = pkg.axes;
                        window._currentAxes = axes;
                        window._currentButtons = btns;

                        // Conmutador táctil con SELECT + R3, SELECT + START o Botón 16 (Nexus / Guía)
                        const isTouchCombo = (btns[8] && btns[11]) || (btns[8] && btns[9]) || !!btns[16];
                        if (isTouchCombo && !window._touchComboLastDown) {{
                            window._touchComboLastDown = true;
                            if (!window.isGameModeLocked && typeof window.toggleMouseMode === "function") {{
                                window.toggleMouseMode();
                            }}
                        }} else if (!isTouchCombo) {{
                            window._touchComboLastDown = false;
                        }}

                        // Detección Instantánea de Cambios en Botones (Down / Up)
                        for (let i = 0; i < 17; i++) {{
                            const isDown = !!btns[i];
                            const wasDown = !!prevBtns[i];
                            const label = BTN_LABELS[i] || `Boton_${{i}}`;

                            if (isDown && !wasDown) {{
                                const cur = (typeof state !== "undefined") ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
                                if (window.recordTelemetry) {{
                                    window.recordTelemetry("GAMEPAD_DOWN", cur, label, "Down", `Pulsado botón ${{label}}`);
                                }}
                                const ticker = document.getElementById("tel-ticker-text");
                                if (ticker) ticker.textContent = `[MANDO TACTIL] ${{label}} ACTIVO`;
                            }} else if (!isDown && wasDown) {{
                                const cur = (typeof state !== "undefined") ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
                                if (window.recordTelemetry) {{
                                    window.recordTelemetry("GAMEPAD_UP", cur, label, "Release", `Liberado botón ${{label}}`);
                                }}
                            }}
                            prevBtns[i] = btns[i] ? 1 : 0;
                        }}

                        // Telemetría de Ejes Analógicos (Sticks)
                        const lx = axes[0] || 0, ly = axes[1] || 0;
                        const rx = axes[2] || 0, ry = axes[3] || 0;
                        const now = Date.now();

                        if ((Math.hypot(lx, ly) > 0.08 || Math.hypot(rx, ry) > 0.08) && (now - lastAxesLogTime > 140)) {{
                            lastAxesLogTime = now;
                            const cur = (typeof state !== "undefined") ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
                            if (window.recordTelemetry) {{
                                window.recordTelemetry("GAMEPAD_AXES", cur, "Sticks", "Move", `Stick L:(X:${{lx.toFixed(2)}}, Y:${{ly.toFixed(2)}}) | Stick R:(X:${{rx.toFixed(2)}}, Y:${{ry.toFixed(2)}})`);
                            }}
                        }}

                        if (window.isControllerMouseMode && typeof window.processDesktopMouseControls === "function") {{
                            window.processDesktopMouseControls(axes, btns, prevBtns);
                        }} else if (window.updateAvatarFromGamepad) {{
                            window.updateAvatarFromGamepad(axes, btns);
                        }}
                    }} catch(e) {{
                        console.error("[MOCK WS] Error:", e);
                    }}
                }}

                close() {{
                    this.readyState = 3;
                    if (typeof this.onclose === "function") this.onclose({{ type: "close" }});
                    this.dispatchEvent(new Event("close"));
                }}
            }}

            MockGamepadSocket.CONNECTING = 0;
            MockGamepadSocket.OPEN = 1;
            MockGamepadSocket.CLOSING = 2;
            MockGamepadSocket.CLOSED = 3;

            window.WebSocket = MockGamepadSocket;
        }})();

        // Escucha y control del Avatar mediante Mandos Táctiles con Telemetría de Ejes
        window.updateAvatarFromGamepad = function(axes, buttons) {{
            const av = state.avatar;

            // Stick Izquierdo: Locomoción Analógica 360°
            const lx = axes[0] || 0;
            const ly = axes[1] || 0;
            const speed = av.isSprinting ? 9.5 : 5.5;

            if (Math.hypot(lx, ly) > 0.08) {{
                av.vx = lx * speed;
                av.vy = ly * speed;
            }}

            // Stick Derecho: Mira / Rotación de Apuntado 360°
            const rx = axes[2] || 0;
            const ry = axes[3] || 0;
            if (Math.hypot(rx, ry) > 0.12) {{
                av.angle = Math.atan2(ry, rx);
            }}

            // Botón A (0): Salto Vertical Dinámico
            if (buttons[0] && !av.isJumping) {{
                av.isJumping = true;
                av.jumpScale = 1.55;
                setTimeout(() => {{ av.isJumping = false; av.jumpScale = 1.0; }}, 280);
            }}

            // Botón B (1): Dash Explosivo
            if (buttons[1] && !av.isDashing) {{
                av.isDashing = true;
                av.vx = Math.cos(av.angle) * 18;
                av.vy = Math.sin(av.angle) * 18;
                setTimeout(() => {{ av.isDashing = false; }}, 350);
            }}

            // Botón X (2): Onda Expansiva de Ataque
            if (buttons[2] && av.attackEffect <= 0) {{
                av.attackEffect = 1.0;
            }}

            // Botón Y (3): Escudo de Energía
            av.shieldActive = !!buttons[3];

            // Gatillos y Bumpers (LB, RB, LT, RT): Cambio de Color
            if (buttons[4]) av.color = "#00ffc8"; // LB: Verde Cian
            if (buttons[5]) av.color = "#f59e0b"; // RB: Ámbar Neón
            if (buttons[6]) av.color = "#38bdf8"; // LT: Azul Cielo
            if (buttons[7]) av.color = "#ff2a85"; // RT: Rosa Neón

            // Botón L3 (10): Sprint
            av.isSprinting = !!buttons[10];

            // Botón R3 (11): Centrado Instantáneo del Avatar
            if (buttons[11]) {{
                av.x = 1260; av.y = 280; av.vx = 0; av.vy = 0;
            }}

            // Botón View (8): Centrar Ventana
            if (buttons[8]) {{
                state.window.x = 460; state.window.y = 110;
            }}

            // Botón Menu (9): Registro en Consola
            if (buttons[9] && !av._menuTriggered) {{
                av._menuTriggered = true;
                state.window.terminalLines.push("[MENÚ PRINCIPAL ACTIVADO]");
                if (state.window.terminalLines.length > 7) state.window.terminalLines.shift();
                setTimeout(() => {{ av._menuTriggered = false; }}, 500);
            }}

            // Cruceta D-Pad (12, 13, 14, 15): Movimiento Direccional Fluido
            const dpadSpeed = av.isSprinting ? 7.5 : 4.8;
            if (buttons[12]) av.vy = -dpadSpeed; // Up
            if (buttons[13]) av.vy = dpadSpeed;  // Down
            if (buttons[14]) av.vx = -dpadSpeed; // Left
            if (buttons[15]) av.vx = dpadSpeed;  // Right
        }};

        // Bucle continuo para mantener locomoción física fluida cuando el stick está sostenido
        setInterval(() => {{
            if (window.updateAvatarFromGamepad && window._currentAxes && window._currentButtons) {{
                window.updateAvatarFromGamepad(window._currentAxes, window._currentButtons);
            }}
        }}, 16);

        // Aislamiento Táctil Absoluto del HUD de Telemetría (Estándar BigTech: stopImmediatePropagation)
        // Evita que tocar el panel del test active el trackpad o mueva el ratón en la pantalla
        ["touchstart", "touchmove", "touchend", "touchcancel"].forEach(evtName => {{
            window.addEventListener(evtName, function(e) {{
                if (e.target && e.target.closest && e.target.closest("#telemetry-hud-box")) {{
                    e.stopImmediatePropagation();
                }}
            }}, {{ capture: true, passive: false }});
        }});

        // Botones del HUD de Telemetría con Respuesta Táctil Instantánea y Encapsulación
        document.addEventListener("DOMContentLoaded", () => {{
            const toggleBtn = document.getElementById("tel-toggle-btn");
            const box = document.getElementById("telemetry-hud-box");
            const clearBtn = document.getElementById("tel-clear-btn");
            const resetBtn = document.getElementById("tel-reset-avatar-btn");
            const mouseModeBtn = document.getElementById("tel-toggle-mouse-mode");
            const toggleTouchBtn = document.getElementById("tel-toggle-touch-btn");
            const touchBtnText = document.getElementById("tel-touch-btn-text");
            const rumbleBtn = document.getElementById("tel-rumble-btn");
            const fullscreenBtn = document.getElementById("tel-fullscreen-btn");
            const syncGpBtn = document.getElementById("tel-sync-gp-btn");
            const modeBadge = document.getElementById("tel-gp-mode-badge");

            function attachFastTap(elem, callback) {{
                if (!elem) return;
                let tapMoved = false;
                elem.addEventListener("touchstart", (e) => {{ e.stopPropagation(); tapMoved = false; }}, {{ passive: true }});
                elem.addEventListener("touchmove", () => {{ tapMoved = true; }}, {{ passive: true }});
                elem.addEventListener("touchend", (e) => {{
                    e.stopPropagation();
                    if (!tapMoved) {{
                        e.preventDefault();
                        callback();
                    }}
                }}, {{ passive: false }});
                elem.addEventListener("click", (e) => {{
                    e.stopPropagation();
                    callback();
                }});
            }}

            // 0. Botón de Sincronización Inmediata de Mando Físico
            if (syncGpBtn) {{
                attachFastTap(syncGpBtn, () => {{
                    if (navigator.vibrate) navigator.vibrate(50);
                    if (window.syncPhysicalGamepad) {{
                        window.syncPhysicalGamepad(true);
                    }}
                }});
            }}

            // 0.1 Botón de Bloqueo de Juego (100% Inmersivo / Cero Interrupciones)
            const gameLockBtn = document.getElementById("tel-game-lock-btn");
            if (gameLockBtn) {{
                attachFastTap(gameLockBtn, () => {{
                    if (window.toggleGameLock) window.toggleGameLock();
                }});
            }}

            // 1. Alternador de Modo Ratón de PC vs Modo Juego en Mando
            if (mouseModeBtn) {{
                attachFastTap(mouseModeBtn, () => {{
                    if (window.toggleMouseMode) window.toggleMouseMode();
                }});
            }}
            if (modeBadge) {{
                attachFastTap(modeBadge, () => {{
                    if (window.toggleMouseMode) window.toggleMouseMode();
                }});
            }}

            // 1.1 Alternador Manual de Mandos Táctiles (Ocultar / Mostrar)
            if (toggleTouchBtn) {{
                attachFastTap(toggleTouchBtn, () => {{
                    const gpOverlay = document.getElementById("virtual-gamepad-overlay");
                    if (!gpOverlay) return;
                    const isHidden = gpOverlay.classList.contains("gp-phys-hidden");
                    if (isHidden) {{
                        gpOverlay.classList.remove("gp-phys-hidden");
                        if (typeof wakeGamepadOverlay === "function") wakeGamepadOverlay();
                        if (touchBtnText) touchBtnText.textContent = "Ocultar Táctiles";
                        recordTelemetry("TOUCH_TOGGLE", {{ x: 960, y: 540 }}, "UI", "Show", "Mandos táctiles restaurados manualmente");
                    }} else {{
                        gpOverlay.classList.add("gp-phys-hidden");
                        if (touchBtnText) touchBtnText.textContent = "Mostrar Táctiles";
                        recordTelemetry("TOUCH_TOGGLE", {{ x: 960, y: 540 }}, "UI", "Hide", "Mandos táctiles ocultados manualmente");
                    }}
                    if (navigator.vibrate) navigator.vibrate(40);
                }});
            }}

            // 2. Test de Vibración Háptica Dual (Rumble)
            if (rumbleBtn) {{
                attachFastTap(rumbleBtn, () => {{
                    const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
                    let vibrated = false;
                    for (let i = 0; i < gamepads.length; i++) {{
                        const gp = gamepads[i];
                        if (gp && gp.vibrationActuator && typeof gp.vibrationActuator.playEffect === "function") {{
                            try {{
                                gp.vibrationActuator.playEffect("dual-rumble", {{
                                    startDelay: 0, duration: 180, weakMagnitude: 0.85, strongMagnitude: 0.65
                                }});
                                vibrated = true;
                            }} catch(e) {{}}
                        }}
                    }}
                    if (!vibrated && navigator.vibrate) {{
                        navigator.vibrate([40, 80, 40]);
                    }}
                    recordTelemetry("RUMBLE_TEST", "-", "Gamepad", "Haptic", vibrated ? "Vibración enviada al mando físico con éxito" : "Vibración enviada a pantalla táctil");
                }});
            }}

            // 3. Encapsulación Total: Pantalla Completa + Keyboard Lock + Wake Lock + Anti-Atrás
            function enterImmersiveFullscreen() {{
                const el = document.documentElement;
                if (el.requestFullscreen) {{
                    el.requestFullscreen({{ navigationUI: "hide" }}).catch(() => {{}});
                }} else if (el.webkitRequestFullscreen) {{
                    el.webkitRequestFullscreen().catch(() => {{}});
                }}
                if (navigator.keyboard && typeof navigator.keyboard.lock === "function") {{
                    navigator.keyboard.lock(["Escape", "Tab", "AltLeft", "AltRight", "MetaLeft", "MetaRight"]).catch(() => {{}});
                }}
                if ("wakeLock" in navigator && typeof navigator.wakeLock.request === "function") {{
                    navigator.wakeLock.request("screen").catch(() => {{}});
                }}
                recordTelemetry("FULLSCREEN_LOCK", "-", "Window", "Encapsulated", "Pantalla completa inmersiva + Keyboard Lock + Wake Lock activados");
            }}

            if (fullscreenBtn) {{
                attachFastTap(fullscreenBtn, () => {{
                    enterImmersiveFullscreen();
                }});
            }}

            // 4. Trap de Historial Anti-Atrás (Previene que el botón 'B' del mando cierre la pestaña en Android)
            try {{
                window.history.pushState({{ aether: 1 }}, "", window.location.href);
                window.addEventListener("popstate", function(e) {{
                    window.history.pushState({{ aether: 1 }}, "", window.location.href);
                    recordTelemetry("TRAP_NAV_BACK", "-", "Navigation", "Blocked", "Gesto/Botón Atrás encapsulado dentro de la página");
                    if (typeof window.updateRawProbeDisplay === "function") {{
                        window.updateRawProbeDisplay("ANDROID_BACK", "Botón / Gesto Atrás capturado");
                    }}
                }});
            }} catch(e) {{}}

            if (toggleBtn && box) {{
                attachFastTap(toggleBtn, () => {{
                    box.classList.toggle("collapsed");
                    const isCol = box.classList.contains("collapsed");
                    const colText = document.getElementById("tel-collapse-text");
                    const colSvg = document.getElementById("tel-collapse-svg");
                    if (colText) colText.textContent = isCol ? "EXPANDIR" : "COLAPSAR";
                    if (colSvg) colSvg.style.transform = isCol ? "rotate(0deg)" : "rotate(180deg)";
                }});
            }}
            if (clearBtn) {{
                attachFastTap(clearBtn, () => {{
                    fetch("/api/clear_log", {{ method: "POST" }}).then(() => {{
                        document.getElementById("tel-stream-list").innerHTML = '<div class="tel-log-item highlight">[REGISTRO LIMPIADO]</div>';
                    }});
                }});
            }}
            if (resetBtn) {{
                attachFastTap(resetBtn, () => {{
                    state.avatar.x = 1260;
                    state.avatar.y = 280;
                    state.avatar.vx = 0;
                    state.avatar.vy = 0;
                    state.window.x = 460;
                    state.window.y = 110;
                    recordTelemetry("RESET_ALL", {{ x: 960, y: 540 }}, "UI", "Reset", "Avatar y ventana centrados");
                }});
            }}

            // Gestión de Bumpers Flotantes y Reasignación L3/R3 (Desactivados estilo BigTech)
            window.remapL3R3ToBumpers = false;
            window.floatingBumpersEnabled = false;

            const remapBtn = document.getElementById("tel-remap-l3r3-btn");
            const floatBtn = document.getElementById("tel-float-bumpers-btn");
            const btnLb = document.getElementById("floating-bumper-lb");
            const btnRb = document.getElementById("floating-bumper-rb");

            if (remapBtn) {{
                attachFastTap(remapBtn, () => {{
                    window.remapL3R3ToBumpers = !window.remapL3R3ToBumpers;
                    const text = document.getElementById("tel-remap-l3r3-text");
                    if (text) text.textContent = `Mapeo L3/R3 a LB/RB: ${{window.remapL3R3ToBumpers ? "ON" : "OFF"}}`;
                    remapBtn.style.color = window.remapL3R3ToBumpers ? "#c084fc" : "#64748b";
                    recordTelemetry("CONFIG_REMAP", "-", "Remap", "Toggle", `Reasignación L3/R3 -> LB/RB: ${{window.remapL3R3ToBumpers}}`);
                }});
            }}

            if (floatBtn) {{
                attachFastTap(floatBtn, () => {{
                    window.floatingBumpersEnabled = !window.floatingBumpersEnabled;
                    const text = document.getElementById("tel-float-bumpers-text");
                    if (text) text.textContent = `Bumpers en Pantalla: ${{window.floatingBumpersEnabled ? "ON" : "OFF"}}`;
                    floatBtn.style.color = window.floatingBumpersEnabled ? "#00ffc8" : "#64748b";
                    if (btnLb) btnLb.classList.toggle("hidden", !window.floatingBumpersEnabled);
                    if (btnRb) btnRb.classList.toggle("hidden", !window.floatingBumpersEnabled);
                    recordTelemetry("CONFIG_FLOAT_BUMPERS", "-", "UI", "Toggle", `Bumpers Flotantes en Pantalla: ${{window.floatingBumpersEnabled}}`);
                }});
            }}

            // Configurar pulsación táctil ultra-rápida en los bumpers flotantes
            if (btnLb) {{
                const onDownLb = (e) => {{
                    e.preventDefault();
                    e.stopPropagation();
                    btnLb.classList.add("pressed");
                    if (typeof window.setSoftwareBumper === "function") window.setSoftwareBumper(4, true, "Bumper Pantalla LB");
                    if (navigator.vibrate) navigator.vibrate(15);
                }};
                const onUpLb = (e) => {{
                    btnLb.classList.remove("pressed");
                    if (typeof window.setSoftwareBumper === "function") window.setSoftwareBumper(4, false, "Bumper Pantalla LB");
                }};
                btnLb.addEventListener("pointerdown", onDownLb, {{ capture: true, passive: false }});
                btnLb.addEventListener("pointerup", onUpLb, {{ capture: true, passive: false }});
                btnLb.addEventListener("pointercancel", onUpLb, {{ capture: true, passive: false }});
            }}

            if (btnRb) {{
                const onDownRb = (e) => {{
                    e.preventDefault();
                    e.stopPropagation();
                    btnRb.classList.add("pressed");
                    if (typeof window.setSoftwareBumper === "function") window.setSoftwareBumper(5, true, "Bumper Pantalla RB");
                    if (navigator.vibrate) navigator.vibrate(15);
                }};
                const onUpRb = (e) => {{
                    btnRb.classList.remove("pressed");
                    if (typeof window.setSoftwareBumper === "function") window.setSoftwareBumper(5, false, "Bumper Pantalla RB");
                }};
                btnRb.addEventListener("pointerdown", onDownRb, {{ capture: true, passive: false }});
                btnRb.addEventListener("pointerup", onUpRb, {{ capture: true, passive: false }});
                btnRb.addEventListener("pointercancel", onUpRb, {{ capture: true, passive: false }});
            }}
        }});
    }})();
    </script>

    <!-- INYECCIÓN DEL CÓDIGO DE PRODUCCIÓN (HUD, MANDOS TAK, TECLADO Y TRACKPAD) -->
    {hud_code}

    <!-- TEMA DE MANDOS TÁCTILES TRANSPARENTES (Fondo 100% transparente, líneas y colores intactos) -->
    <style id="theme-transparent-gamepad">
        /* 1. Botones de Acción ABXY */
        .gp-action-btn {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            box-shadow: none !important;
        }}
        .btn-xbox-a {{
            border: 2.5px solid #10b981 !important;
            color: #10b981 !important;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.9) !important;
            background: transparent !important;
        }}
        .btn-xbox-a.pressed, .btn-xbox-a:active {{
            background: rgba(16, 185, 129, 0.35) !important;
            border-color: #10b981 !important;
            box-shadow: 0 0 24px #10b981, inset 0 0 10px rgba(16, 185, 129, 0.4) !important;
            color: #ffffff !important;
        }}
        .btn-xbox-b {{
            border: 2.5px solid #ef4444 !important;
            color: #ef4444 !important;
            text-shadow: 0 0 10px rgba(239, 68, 68, 0.9) !important;
            background: transparent !important;
        }}
        .btn-xbox-b.pressed, .btn-xbox-b:active {{
            background: rgba(239, 68, 68, 0.35) !important;
            border-color: #ef4444 !important;
            box-shadow: 0 0 24px #ef4444, inset 0 0 10px rgba(239, 68, 68, 0.4) !important;
            color: #ffffff !important;
        }}
        .btn-xbox-x {{
            border: 2.5px solid #3b82f6 !important;
            color: #3b82f6 !important;
            text-shadow: 0 0 10px rgba(59, 130, 246, 0.9) !important;
            background: transparent !important;
        }}
        .btn-xbox-x.pressed, .btn-xbox-x:active {{
            background: rgba(59, 130, 246, 0.35) !important;
            border-color: #3b82f6 !important;
            box-shadow: 0 0 24px #3b82f6, inset 0 0 10px rgba(59, 130, 246, 0.4) !important;
            color: #ffffff !important;
        }}
        .btn-xbox-y {{
            border: 2.5px solid #f59e0b !important;
            color: #f59e0b !important;
            text-shadow: 0 0 10px rgba(245, 158, 11, 0.9) !important;
            background: transparent !important;
        }}
        .btn-xbox-y.pressed, .btn-xbox-y:active {{
            background: rgba(245, 158, 11, 0.35) !important;
            border-color: #f59e0b !important;
            box-shadow: 0 0 24px #f59e0b, inset 0 0 10px rgba(245, 158, 11, 0.4) !important;
            color: #ffffff !important;
        }}

        /* 2. Base y Thumbs de los Sticks Analógicos */
        .gp-stick-base {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: 2px solid rgba(0, 255, 200, 0.45) !important;
            box-shadow: 0 0 16px rgba(0, 255, 200, 0.15) !important;
        }}
        .gp-stick-base::before {{
            border: 1.5px dashed rgba(0, 255, 200, 0.35) !important;
        }}
        .gp-stick-thumb {{
            background: rgba(0, 255, 200, 0.08) !important;
            border: 2px solid var(--aether-cyan, #00ffc8) !important;
            box-shadow: 0 0 16px rgba(0, 255, 200, 0.45), inset 0 0 8px rgba(0, 255, 200, 0.3) !important;
        }}
        .gp-stick-thumb::after {{
            background: transparent !important;
            border: 1.5px solid rgba(0, 255, 200, 0.6) !important;
        }}
        .gp-stick-click-btn {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: 1.5px solid var(--aether-cyan, #00ffc8) !important;
            color: var(--aether-cyan, #00ffc8) !important;
            box-shadow: none !important;
        }}
        .gp-stick-click-btn.pressed, .gp-stick-click-btn:active {{
            background: rgba(0, 255, 200, 0.35) !important;
            color: #ffffff !important;
            box-shadow: 0 0 16px var(--aether-cyan, #00ffc8) !important;
        }}

        /* 3. Cruceta D-Pad */
        .gp-dpad-container {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: 2px solid rgba(56, 189, 248, 0.4) !important;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.15) !important;
        }}
        .gp-dpad-container::before {{
            background: transparent !important;
            border: 1.5px dashed rgba(56, 189, 248, 0.3) !important;
        }}
        .gp-dpad-btn {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: 1.5px solid rgba(56, 189, 248, 0.45) !important;
            color: var(--aether-blue, #38bdf8) !important;
        }}
        .gp-dpad-btn.pressed, .gp-dpad-btn:active {{
            background: rgba(56, 189, 248, 0.35) !important;
            border-color: #38bdf8 !important;
            color: #ffffff !important;
            box-shadow: 0 0 18px #38bdf8 !important;
        }}

        /* 4. Gatillos y Bumpers (LB, RB, LT, RT) con Iluminación Específica por Color de Avatar */
        .gp-shoulder-btn {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            box-shadow: none !important;
            transition: all 0.08s ease !important;
        }}

        /* LB (Bumper Izquierdo): Verde Cian Neón (#00ffc8) */
        [data-btn="4"], .gp-bumper-btn:not([data-btn="5"]) {{
            border: 2.2px solid #00ffc8 !important;
            color: #00ffc8 !important;
            text-shadow: 0 0 10px rgba(0, 255, 200, 0.9) !important;
            background: transparent !important;
        }}
        [data-btn="4"].pressed, [data-btn="4"]:active {{
            background: rgba(0, 255, 200, 0.48) !important;
            border-color: #00ffc8 !important;
            color: #ffffff !important;
            box-shadow: 0 0 28px #00ffc8, inset 0 0 14px rgba(0, 255, 200, 0.6) !important;
        }}

        /* RB (Bumper Derecho): Ámbar Dorado Neón (#f59e0b) */
        [data-btn="5"] {{
            border: 2.2px solid #f59e0b !important;
            color: #f59e0b !important;
            text-shadow: 0 0 10px rgba(245, 158, 11, 0.9) !important;
            background: transparent !important;
        }}
        [data-btn="5"].pressed, [data-btn="5"]:active {{
            background: rgba(245, 158, 11, 0.52) !important;
            border-color: #f59e0b !important;
            color: #ffffff !important;
            box-shadow: 0 0 28px #f59e0b, inset 0 0 14px rgba(245, 158, 11, 0.6) !important;
        }}

        /* LT (Gatillo Izquierdo): Azul Cielo Neón (#38bdf8) */
        [data-btn="6"], .gp-trigger-left {{
            border: 2.2px solid #38bdf8 !important;
            color: #38bdf8 !important;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.9) !important;
            background: transparent !important;
        }}
        [data-btn="6"].pressed, [data-btn="6"]:active, .gp-trigger-left.pressed, .gp-trigger-left:active {{
            background: rgba(56, 189, 248, 0.48) !important;
            border-color: #38bdf8 !important;
            color: #ffffff !important;
            box-shadow: 0 0 28px #38bdf8, inset 0 0 14px rgba(56, 189, 248, 0.6) !important;
        }}

        /* RT (Gatillo Derecho): Rosa Neón Carmesí (#ff2a85) */
        [data-btn="7"], .gp-trigger-right {{
            border: 2.2px solid #ff2a85 !important;
            color: #ff2a85 !important;
            text-shadow: 0 0 10px rgba(255, 42, 133, 0.9) !important;
            background: transparent !important;
        }}
        [data-btn="7"].pressed, [data-btn="7"]:active, .gp-trigger-right.pressed, .gp-trigger-right:active {{
            background: rgba(255, 42, 133, 0.52) !important;
            border-color: #ff2a85 !important;
            color: #ffffff !important;
            box-shadow: 0 0 28px #ff2a85, inset 0 0 14px rgba(255, 42, 133, 0.6) !important;
        }}

        /* 5. Barra Central de Sistema (View, Xbox Nexus, Menu) */
        .gp-center-container {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            box-shadow: none !important;
        }}
        .gp-center-btn {{
            background: transparent !important;
            color: #cbd5e1 !important;
            border: 1px solid rgba(255, 255, 255, 0.22) !important;
        }}
        .gp-center-btn.gp-guide-btn {{
            border-color: rgba(16, 185, 129, 0.65) !important;
            color: #10b981 !important;
        }}
        .gp-center-btn.pressed, .gp-center-btn:active {{
            background: rgba(255, 255, 255, 0.22) !important;
            color: #ffffff !important;
        }}
        .gp-guide-btn.pressed, .gp-guide-btn:active {{
            background: rgba(16, 185, 129, 0.35) !important;
            color: #ffffff !important;
            box-shadow: 0 0 20px #10b981 !important;
        }}

        /* 6. Auto-ocultamiento Inteligente al Conectar Mando Físico (Estándar TAK / RetroArch / GeForce NOW) */
        #virtual-gamepad-overlay {{
            transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s ease !important;
        }}
        #virtual-gamepad-overlay.gp-phys-hidden {{
            opacity: 0 !important;
            pointer-events: none !important;
            transform: scale(0.96) !important;
        }}
    </style>

    <!-- PUENTE DE TELEMETRÍA Y REGISTRO DE DESLIZAMIENTO FÍSICO CONTINUO -->
    <script>
    (function() {{
        // =========================================================================
        // ESCUDO TRIPLE BIGTECH DE ENCAPSULACIÓN TOTAL Y SONDA RAW UNIVERSAL
        // =========================================================================
        window.rawSoftwareLbDown = false;
        window.rawSoftwareRbDown = false;

        function updateRawProbeDisplay(src, detail) {{
            const probeEl = document.getElementById("tel-raw-probe-val");
            if (probeEl) {{
                probeEl.textContent = `${{src}}: ${{detail}}`;
                probeEl.style.color = "#00ffc8";
            }}
            if (window.recordTelemetry) {{
                window.recordTelemetry("RAW_PROBE", {{ x: 0, y: 0 }}, src, "Signal", detail);
            }}
        }}
        window.updateRawProbeDisplay = updateRawProbeDisplay;

        function setSoftwareBumper(btnIndex, isDown, label) {{
            if (btnIndex === 4) window.rawSoftwareLbDown = isDown;
            if (btnIndex === 5) window.rawSoftwareRbDown = isDown;

            const bLabel = (btnIndex === 4) ? "LB (Cian)" : "RB (Ámbar)";
            const cur = (typeof state !== "undefined" && state.avatar) ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
            if (isDown) {{
                if (window.recordTelemetry) {{
                    window.recordTelemetry("CALIBRATE_BTN_DOWN", cur, bLabel, "Press", `[BUMPER PUENTEADO] ${{label}} -> ${{bLabel}}`);
                }}
            }} else {{
                if (window.recordTelemetry) {{
                    window.recordTelemetry("CALIBRATE_BTN_UP", cur, bLabel, "Release", `[BUMPER LIBERADO] ${{label}} -> ${{bLabel}}`);
                }}
            }}
        }}

        function shieldKeyEvent(e) {{
            const code = e.keyCode || e.which;
            const key = e.key;
            const codeStr = e.code || "";

            // Actualizar sonda de diagnóstico en vivo en tiempo real para cualquier evento de teclado
            if (e.type === "keydown") {{
                updateRawProbeDisplay("KEY", `"${{key}}" (code:${{codeStr}}, keyCode:${{code}})`);
            }}

            // 1. Detección de teclas de Mando Físico reportadas por el kernel Android:
            // 96=A, 97=B, 98=C, 99=X, 100=Y, 101=Z, 102=L1(LB), 103=R1(RB),
            // 104=L2(LT), 105=R2(RT), 106=THUMBL, 107=THUMBR, 108=START, 109=SELECT, 110=MODE
            const isAndroidGamepadKey = (code >= 96 && code <= 110);

            // Detección exhaustiva de teclas que corresponden a LB / L1:
            const isLbKey = (code === 102 || code === 33 || key === "PageUp" || codeStr === "PageUp" ||
                             key === "MediaTrackPrevious" || codeStr === "MediaTrackPrevious" || code === 88 || code === 177 ||
                             key === "AudioVolumeDown" || code === 25 || code === 174 || (e.altKey && (key === "ArrowLeft" || code === 37)));

            // Detección exhaustiva de teclas que corresponden a RB / R1:
            const isRbKey = (code === 103 || code === 34 || key === "PageDown" || codeStr === "PageDown" ||
                             key === "MediaTrackNext" || codeStr === "MediaTrackNext" || code === 87 || code === 176 ||
                             key === "AudioVolumeUp" || code === 24 || code === 175 || (e.altKey && (key === "ArrowRight" || code === 39)));

            // 2. Bumpers LB/RB y Teclas que Android Chrome usa para cambiar de pestaña:
            const isBumperOrTabKey = (isLbKey || isRbKey || code === 9 || key === "Tab");

            // Si es pulsación de LB o RB por teclado/kernel:
            if (isLbKey) {{
                setSoftwareBumper(4, e.type === "keydown", `Key: "${{key || code}}"`);
            }}
            if (isRbKey) {{
                setSoftwareBumper(5, e.type === "keydown", `Key: "${{key || code}}"`);
            }}

            // 3. Atajos de Navegador para Conmutar Pestañas:
            const isTabSwitchCombo = (e.ctrlKey && (key === "Tab" || code === 9 || key === "PageUp" || key === "PageDown" || key === "w" || key === "W" || key === "t" || key === "T")) ||
                                     (e.altKey && (key === "ArrowLeft" || key === "ArrowRight" || key === "Left" || key === "Right" || key === "d" || key === "D"));

            // 4. Salida / Navegación Atrás (Botón B o Tecla Escape):
            const isBackNav = (code === 97 || code === 4 || key === "Back" || key === "Escape" || code === 27 || (e.altKey && key === "ArrowLeft"));

            // ATAJO TECLADO: Tecla 'M', 'F4' o '~' (Backquote) para Alternar Modo Ratón / Modo PC
            if ((key === "m" || key === "M" || key === "F4" || code === 77 || code === 115 || code === 192) && !e.ctrlKey && !e.altKey && !e.metaKey) {{
                e.preventDefault();
                e.stopImmediatePropagation();
                e.stopPropagation();
                if (e.type === "keydown") {{
                    if (!window.isGameModeLocked && typeof window.toggleMouseMode === "function") {{
                        window.toggleMouseMode();
                    }}
                }}
                return false;
            }}

            // AUTO-DETECCIÓN INSTANTÁNEA: Si el mando envía cualquier evento de hardware y aún no estaba marcado ON:
            if (isAndroidGamepadKey || isBumperOrTabKey) {{
                if (!isPhysicalGamepadOn) {{
                    const gp = scanActiveGamepad();
                    if (gp) {{
                        handleGamepadPowerOn(gp);
                    }} else {{
                        // Activación instantánea para ocultar los mandos táctiles en 0ms
                        handleGamepadPowerOn({{
                            id: "Mando Físico (Android Bluetooth/USB)",
                            index: 0,
                            connected: true,
                            buttons: new Array(17).fill({{ pressed: false, value: 0 }}),
                            axes: [0, 0, 0, 0]
                        }});
                    }}
                }}
            }}

            // SUPRESIÓN ACTIVA: Encapsula el evento dentro de la pestaña y evita que Chrome cambie de pestaña o retroceda
            if (isBumperOrTabKey || isTabSwitchCombo || isBackNav || isAndroidGamepadKey) {{
                e.preventDefault();
                e.stopImmediatePropagation();
                e.stopPropagation();

                if (e.type === "keydown" && window.recordTelemetry) {{
                    const desc = `Tecla/Código: "${{key || code}}" (keyCode:${{code}}, Ctrl:${{e.ctrlKey}}, Alt:${{e.altKey}})`;
                    window.recordTelemetry("ENCAPSULATION_SHIELD", {{ x: 0, y: 0 }}, "BrowserTab", "Encapsulated", desc);
                    if (isAndroidGamepadKey) {{
                        window.recordTelemetry("CALIBRATE_KEY_DOWN", {{ x: 0, y: 0 }}, `KeyCode_${{code}}`, "Press", `[CALIBRACIÓN ANDROID] Recibido KeyEvent de Mando: keyCode=${{code}}, key="${{key}}"`);
                    }}
                }}
                return false;
            }}
        }}

        window.addEventListener("keydown", shieldKeyEvent, {{ capture: true, passive: false }});
        window.addEventListener("keyup", shieldKeyEvent, {{ capture: true, passive: false }});
        window.addEventListener("keypress", shieldKeyEvent, {{ capture: true, passive: false }});
        document.addEventListener("keydown", shieldKeyEvent, {{ capture: true, passive: false }});
        document.addEventListener("keyup", shieldKeyEvent, {{ capture: true, passive: false }});

        // -------------------------------------------------------------------------
        // ESCUDO TOTAL DE EVENTOS WHEEL (RUEDA HORIZONTAL / TILT WHEEL / SWIPE)
        // Mandos como el X3 en Consumer Control envían Tilt Wheel para LB/RB
        // lo que en Chrome en Android hace que cambie de pestaña
        // -------------------------------------------------------------------------
        function shieldWheelEvent(e) {{
            e.preventDefault();
            e.stopImmediatePropagation();
            e.stopPropagation();

            const desc = `dx:${{e.deltaX.toFixed(1)}} dy:${{e.deltaY.toFixed(1)}} dz:${{e.deltaZ.toFixed(1)}} mode:${{e.deltaMode}}`;
            updateRawProbeDisplay("WHEEL", desc);

            if (e.deltaX < -5 || (Math.abs(e.deltaX) < 1 && e.deltaY < -5)) {{
                setSoftwareBumper(4, true, `Wheel Izq (${{desc}})`);
                setTimeout(() => setSoftwareBumper(4, false, `Wheel Izq`), 120);
            }} else if (e.deltaX > 5 || (Math.abs(e.deltaX) < 1 && e.deltaY > 5)) {{
                setSoftwareBumper(5, true, `Wheel Der (${{desc}})`);
                setTimeout(() => setSoftwareBumper(5, false, `Wheel Der`), 120);
            }}
            return false;
        }}

        window.addEventListener("wheel", shieldWheelEvent, {{ capture: true, passive: false }});
        document.addEventListener("wheel", shieldWheelEvent, {{ capture: true, passive: false }});

        // Asegurar foco en el canvas para recibir eventos de hardware
        function ensureHardwareFocus() {{
            const canvas = document.getElementById("noVNC_canvas");
            if (canvas && document.activeElement !== canvas) {{
                canvas.focus();
            }}
        }}
        window.addEventListener("pointerdown", ensureHardwareFocus, {{ capture: true }});
        window.addEventListener("click", ensureHardwareFocus, {{ capture: true }});

        // Captura de eventos Pointer / Ratón para mandos que reportan botones laterales como mouse
        window.addEventListener("pointerdown", function(e) {{
            if (e.pointerType === "mouse" || e.button > 0) {{
                updateRawProbeDisplay("POINTER", `btn:${{e.button}} btns:${{e.buttons}} tipo:${{e.pointerType}}`);
                if (e.button === 3 || e.button === 4) {{
                    e.preventDefault();
                    e.stopPropagation();
                    if (e.button === 3) setSoftwareBumper(4, true, "Pointer_3 (Atrás)");
                    if (e.button === 4) setSoftwareBumper(5, true, "Pointer_4 (Adelante)");
                }}
            }}
        }}, {{ capture: true, passive: false }});

        window.addEventListener("pointerup", function(e) {{
            if (e.button === 3) setSoftwareBumper(4, false, "Pointer_3 (Atrás)");
            if (e.button === 4) setSoftwareBumper(5, false, "Pointer_4 (Adelante)");
        }}, {{ capture: true, passive: false }});

        // Soporte unificado de Mouse / Puntero para pruebas de escritorio o clics
        document.querySelectorAll("[data-btn]:not(.gp-dpad-btn)").forEach(btn => {{
            const btnIndex = parseInt(btn.getAttribute("data-btn"), 10);
            btn.addEventListener("mousedown", (e) => {{
                e.preventDefault();
                e.stopPropagation();
                btn.classList.add("pressed");
                if (window._mockGpSocket) {{
                    const btns = window._currentButtons.slice();
                    btns[btnIndex] = 1;
                    window._mockGpSocket.send(JSON.stringify({{ axes: window._currentAxes, buttons: btns }}));
                }}
            }});
            const rel = (e) => {{
                btn.classList.remove("pressed");
                if (window._mockGpSocket) {{
                    const btns = window._currentButtons.slice();
                    btns[btnIndex] = 0;
                    window._mockGpSocket.send(JSON.stringify({{ axes: window._currentAxes, buttons: btns }}));
                }}
            }};
            btn.addEventListener("mouseup", rel);
            btn.addEventListener("mouseleave", rel);
        }});

        // -------------------------------------------------------------------------
        // GESTOR DEFINITIVO DE MANDOS FÍSICOS (BIGTECH DUAL ENGINE: EVENTOS + POLLING ACTIVO)
        // -------------------------------------------------------------------------
        let activePhysicalGamepad = null;
        let isPhysicalGamepadOn = false;
        let lastLoggedPhysicalBtns = new Array(17).fill(0);
        let lastRawProbeBtns = new Array(32).fill(0);
        let lastRawProbeAxes = new Array(16).fill(0);
        let lastPhysicalAxesLogTime = 0;
        let btn16LastDown = false;

        const GP_BTN_LABELS = [
            "A (Salto)", "B (Dash)", "X (Ataque)", "Y (Escudo)",
            "LB (Cian)", "RB (Ámbar)", "LT (Azul)", "RT (Rosa)",
            "VIEW (Compartir)", "MENU (Pausa)", "L3 (Sprint)", "R3 (Centrar)",
            "Cruceta ARRIBA", "Cruceta ABAJO", "Cruceta IZQUIERDA", "Cruceta DERECHA",
            "GUÍA / HOME (Nexus / PS)"
        ];

        // Función de descubrimiento directo de gamepad activo
        function scanActiveGamepad() {{
            if (!navigator.getGamepads) return null;
            const gamepads = navigator.getGamepads();
            for (let i = 0; i < gamepads.length; i++) {{
                const gp = gamepads[i];
                if (gp && (gp.connected !== false) && (gp.id || (gp.buttons && gp.buttons.length > 0))) {{
                    return gp;
                }}
            }}
            return null;
        }}

        // Sondeo rápido de inicio y recuperación de foco (sin esperar interacción)
        function checkPhysicalGamepadNow() {{
            if (!isPhysicalGamepadOn) {{
                const gp = scanActiveGamepad();
                if (gp) handleGamepadPowerOn(gp);
            }}
        }}
        window.addEventListener("focus", checkPhysicalGamepadNow);
        document.addEventListener("visibilitychange", function() {{
            if (document.visibilityState === "visible") checkPhysicalGamepadNow();
        }});
        let startupScanCount = 0;
        const startupScanInterval = setInterval(() => {{
            checkPhysicalGamepadNow();
            startupScanCount++;
            if (startupScanCount > 60 || isPhysicalGamepadOn) {{
                clearInterval(startupScanInterval);
            }}
        }}, 100);

        // Manejo unificado del Encendido / Conexión (Auto-oculta mandos táctiles)
        function handleGamepadPowerOn(gp) {{
            if (isPhysicalGamepadOn) return;
            isPhysicalGamepadOn = true;
            activePhysicalGamepad = gp;

            const cur = (typeof state !== "undefined" && state.avatar) ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
            const details = `ID: "${{gp.id}}" | Puerto:#${{gp.index}} | Mapeo:${{gp.mapping || 'standard'}} | Botones:${{gp.buttons.length}} | Ejes:${{gp.axes.length}} | Rumble:${{!!gp.vibrationActuator}}`;

            if (window.recordTelemetry) {{
                window.recordTelemetry("PHYSICAL_GP_ON", cur, "PhysicalGamepad", "Connected", details);
            }}

            const gpDot = document.getElementById("tel-gp-dot");
            if (gpDot) {{
                gpDot.className = "tel-status-dot online";
            }}

            const gpNameEl = document.getElementById("tel-gp-name");
            if (gpNameEl) {{
                const shortName = gp.id.length > 22 ? gp.id.substring(0, 22) + "..." : gp.id;
                gpNameEl.textContent = `Mando: ${{shortName}} (Conectado)`;
                gpNameEl.style.color = "#10b981";
            }}

            const ticker = document.getElementById("tel-ticker-text");
            if (ticker) ticker.textContent = `[CONECTADO] ${{gp.id.substring(0, 24)}}...`;

            const stream = document.getElementById("tel-stream-list");
            if (stream) {{
                const el = document.createElement("div");
                el.className = "tel-log-item highlight";
                el.style.color = "#10b981";
                el.textContent = `[CONECTADO] Mando Físico Detectado: ${{gp.id}}`;
                stream.insertBefore(el, stream.firstChild);
            }}

            // AUTO-OCULTAMIENTO: Al encender o detectar el mando físico, se quitan los mandos táctiles
            const gpOverlay = document.getElementById("virtual-gamepad-overlay");
            if (gpOverlay) {{
                gpOverlay.classList.add("gp-phys-hidden");
            }}
            const gpBadge = document.getElementById("badge-aether-gamepad");
            if (gpBadge) {{
                gpBadge.textContent = "MANDO FÍSICO";
                gpBadge.classList.add("active");
            }}
            const touchBtnText = document.getElementById("tel-touch-btn-text");
            if (touchBtnText) {{
                touchBtnText.textContent = "Mostrar Táctiles";
            }}

            // Haptic feedback en dispositivo
            if (navigator.vibrate) navigator.vibrate([40, 80, 40]);
        }}

        // Manejo unificado del Apagado / Desconexión (Auto-reaparición de mandos táctiles)
        function handleGamepadPowerOff(gp) {{
            if (!isPhysicalGamepadOn) return;
            isPhysicalGamepadOn = false;

            const cur = (typeof state !== "undefined" && state.avatar) ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
            const id = gp ? gp.id : (activePhysicalGamepad ? activePhysicalGamepad.id : "Desconocido");
            const details = `ID: "${{id}}" | Mando apagado o desconectado por el usuario`;

            if (window.recordTelemetry) {{
                window.recordTelemetry("PHYSICAL_GP_OFF", cur, "PhysicalGamepad", "Disconnected", details);
            }}

            const gpDot = document.getElementById("tel-gp-dot");
            if (gpDot) {{
                gpDot.className = "tel-status-dot waiting";
            }}

            const gpNameEl = document.getElementById("tel-gp-name");
            if (gpNameEl) {{
                gpNameEl.textContent = "Mando: Esperando señal (Pulsa cualquier botón)";
                gpNameEl.style.color = "#f59e0b";
            }}

            const ticker = document.getElementById("tel-ticker-text");
            if (ticker) ticker.textContent = `[DESCONECTADO] Mando apagado`;

            const stream = document.getElementById("tel-stream-list");
            if (stream) {{
                const el = document.createElement("div");
                el.className = "tel-log-item highlight";
                el.style.color = "#f43f5e";
                el.textContent = `[DESCONECTADO] Mando Físico: ${{id}}`;
                stream.insertBefore(el, stream.firstChild);
            }}

            // AUTO-REAPARICIÓN: Al apagar el mando físico, vuelven a aparecer los mandos táctiles
            const gpOverlay = document.getElementById("virtual-gamepad-overlay");
            if (gpOverlay) {{
                gpOverlay.classList.remove("gp-phys-hidden");
                if (typeof wakeGamepadOverlay === "function") {{
                    wakeGamepadOverlay();
                }}
            }}
            const gpBadge = document.getElementById("badge-aether-gamepad");
            if (gpBadge) {{
                gpBadge.textContent = (typeof isGamepadVisible !== "undefined" && isGamepadVisible) ? "ON" : "OFF";
                if (typeof isGamepadVisible !== "undefined" && !isGamepadVisible) {{
                    gpBadge.classList.remove("active");
                }}
            }}
            const touchBtnTextOff = document.getElementById("tel-touch-btn-text");
            if (touchBtnTextOff) {{
                touchBtnTextOff.textContent = "Ocultar Táctiles";
            }}

            // Limpieza de estados visuales
            document.querySelectorAll("[data-btn]").forEach(b => b.classList.remove("pressed"));
            const gaugeLt = document.getElementById("tel-gauge-lt");
            const gaugeRt = document.getElementById("tel-gauge-rt");
            const valLt = document.getElementById("tel-val-lt");
            const valRt = document.getElementById("tel-val-rt");
            if (gaugeLt) gaugeLt.style.width = "0%";
            if (valLt) valLt.textContent = "0%";
            if (gaugeRt) gaugeRt.style.width = "0%";
            if (valRt) valRt.textContent = "0%";

            lastLoggedPhysicalBtns.fill(0);
            activePhysicalGamepad = null;
        }}

        // Eventos nativos del navegador
        window.addEventListener("gamepadconnected", function(e) {{
            if (window.recordTelemetry) {{
                window.recordTelemetry("GAMEPAD_CONNECTED_EVENT", {{ x: 960, y: 540 }}, "ChromeEvent", "Connected", `Evento nativo gamepadconnected recibido: "${{e.gamepad.id}}" (index:${{e.gamepad.index}}, mapping:${{e.gamepad.mapping}})`);
            }}
            handleGamepadPowerOn(e.gamepad);
        }});

        window.addEventListener("gamepaddisconnected", function(e) {{
            if (window.recordTelemetry) {{
                window.recordTelemetry("GAMEPAD_DISCONNECTED_EVENT", {{ x: 960, y: 540 }}, "ChromeEvent", "Disconnected", `Evento nativo gamepaddisconnected recibido: "${{e.gamepad ? e.gamepad.id : 'desconocido'}}"`);
            }}
            handleGamepadPowerOff(e.gamepad);
        }});

        // Sincronización Manual y Wakeup con Diagnóstico Detallado
        window.syncPhysicalGamepad = function(fromUserBtn) {{
            let diagInfo = "";
            if (!navigator.getGamepads) {{
                diagInfo = "navigator.getGamepads NO es soportado en este navegador";
            }} else {{
                const gps = navigator.getGamepads();
                const items = [];
                for (let i = 0; i < (gps ? gps.length : 0); i++) {{
                    const g = gps[i];
                    if (g) {{
                        items.push(`[#${{i}}] "${{g.id}}" (Conn:${{g.connected}}, Btns:${{g.buttons ? g.buttons.length : 0}}, Axes:${{g.axes ? g.axes.length : 0}})`);
                    }} else {{
                        items.push(`[#${{i}}] null`);
                    }}
                }}
                diagInfo = items.length > 0 ? items.join(" | ") : "Array getGamepads() vacío (longitud 0)";
            }}

            if (window.recordTelemetry) {{
                window.recordTelemetry("DIAGNOSTIC_GP_SCAN", {{ x: 960, y: 540 }}, "BluetoothGamepad", "Scan", diagInfo);
            }}

            const gp = scanActiveGamepad();
            if (gp) {{
                handleGamepadPowerOn(gp);
            }} else if (fromUserBtn) {{
                const ticker = document.getElementById("tel-ticker-text");
                if (ticker) ticker.textContent = `[DIAGNÓSTICO] Chrome: ${{diagInfo}}`;
                const stream = document.getElementById("tel-stream-list");
                if (stream) {{
                    const el = document.createElement("div");
                    el.className = "tel-log-item";
                    el.style.color = "#f59e0b";
                    el.textContent = `[SINCRONIZACIÓN] Estado en Chrome: ${{diagInfo}}. Si todos son null, verifica que el mando esté en modo HOME+X y vinculado por Bluetooth.`;
                    stream.insertBefore(el, stream.firstChild);
                }}
            }}
        }};

        // Activación por interacción en pantalla (User Gesture Gate de Android/Chrome)
        ["touchstart", "pointerdown", "click"].forEach(evt => {{
            window.addEventListener(evt, () => {{
                if (!isPhysicalGamepadOn) {{
                    const gp = scanActiveGamepad();
                    if (gp) handleGamepadPowerOn(gp);
                }}
            }}, {{ passive: true }});
        }});

        // Bucle de sincronización de alta fidelidad (60Hz / 120Hz)
        function processPhysicalGamepadFrame() {{
            const activeGp = scanActiveGamepad();

            // 1. Detección continua de ciclo de vida (Encendido vs Apagado)
            if (activeGp && !isPhysicalGamepadOn) {{
                handleGamepadPowerOn(activeGp);
            }} else if (!activeGp && isPhysicalGamepadOn) {{
                handleGamepadPowerOff(null);
            }}

            if (activeGp) {{
                activePhysicalGamepad = activeGp;

                // 2. Medidores Analógicos de Gatillos LT y RT (Gauges en tiempo real)
                // Soporte universal híbrido: analógico continuo (0.0 a 1.0) o digital puro (0 o 1) como en mandos genéricos X3
                const rawLt = activeGp.buttons[6];
                const rawRt = activeGp.buttons[7];
                let ltVal = 0;
                if (typeof rawLt === "object" && rawLt !== null) {{
                    ltVal = (rawLt.value !== undefined && rawLt.value !== null) ? rawLt.value : (rawLt.pressed ? 1 : 0);
                }} else if (typeof rawLt === "number") {{
                    ltVal = rawLt;
                }} else if (rawLt) {{
                    ltVal = 1;
                }}

                let rtVal = 0;
                if (typeof rawRt === "object" && rawRt !== null) {{
                    rtVal = (rawRt.value !== undefined && rawRt.value !== null) ? rawRt.value : (rawRt.pressed ? 1 : 0);
                }} else if (typeof rawRt === "number") {{
                    rtVal = rawRt;
                }} else if (rawRt) {{
                    rtVal = 1;
                }}

                const gaugeLt = document.getElementById("tel-gauge-lt");
                const gaugeRt = document.getElementById("tel-gauge-rt");
                const valLt = document.getElementById("tel-val-lt");
                const valRt = document.getElementById("tel-val-rt");

                if (gaugeLt) gaugeLt.style.width = `${{Math.round(ltVal * 100)}}%`;
                if (valLt) valLt.textContent = `${{Math.round(ltVal * 100)}}%`;
                if (gaugeRt) gaugeRt.style.width = `${{Math.round(rtVal * 100)}}%`;
                if (valRt) valRt.textContent = `${{Math.round(rtVal * 100)}}%`;

                // 3. Normalización Universal de Cruceta (D-Pad)
                // En mandos estándar W3C son buttons[12..15].
                // En mandos genéricos (Wireless Controller X3, T3, ShanWan), Android reporta la cruceta como Hat Switch en axes[4..9].
                let dpadUp = !!(activeGp.buttons[12] && (activeGp.buttons[12].pressed || activeGp.buttons[12].value > 0.45));
                let dpadDown = !!(activeGp.buttons[13] && (activeGp.buttons[13].pressed || activeGp.buttons[13].value > 0.45));
                let dpadLeft = !!(activeGp.buttons[14] && (activeGp.buttons[14].pressed || activeGp.buttons[14].value > 0.45));
                let dpadRight = !!(activeGp.buttons[15] && (activeGp.buttons[15].pressed || activeGp.buttons[15].value > 0.45));

                if (!dpadUp && !dpadDown && !dpadLeft && !dpadRight && activeGp.axes && activeGp.axes.length > 4) {{
                    for (let ai = 4; ai < activeGp.axes.length; ai += 2) {{
                        const hx = activeGp.axes[ai] || 0;
                        const hy = (ai + 1 < activeGp.axes.length) ? (activeGp.axes[ai + 1] || 0) : 0;
                        if (Math.abs(hx) > 0.4 || Math.abs(hy) > 0.4) {{
                            if (hy < -0.4) dpadUp = true;
                            if (hy > 0.4) dpadDown = true;
                            if (hx < -0.4) dpadLeft = true;
                            if (hx > 0.4) dpadRight = true;
                            break;
                        }}
                    }}
                }}

                // Instantánea del frame anterior para detección de flancos limpia
                const prevBtns = [...lastLoggedPhysicalBtns];

                // Sincronización de Botones y Telemetría de Presión / Liberación
                const totalRawBtns = Math.max(17, (activeGp.buttons ? activeGp.buttons.length : 0));
                while (lastLoggedPhysicalBtns.length < totalRawBtns) lastLoggedPhysicalBtns.push(0);

                const curBtns = new Array(totalRawBtns).fill(0);
                for (let b = 0; b < totalRawBtns; b++) {{
                    let isDown = false;
                    let val = 0;
                    if (b >= 12 && b <= 15) {{
                        if (b === 12) isDown = dpadUp;
                        else if (b === 13) isDown = dpadDown;
                        else if (b === 14) isDown = dpadLeft;
                        else if (b === 15) isDown = dpadRight;
                        val = isDown ? 1 : 0;
                    }} else if (b === 6) {{
                        val = ltVal;
                        isDown = (typeof rawLt === "object" && rawLt ? (rawLt.pressed || (rawLt.value > 0.15)) : false) || val > 0.15;
                    }} else if (b === 7) {{
                        val = rtVal;
                        isDown = (typeof rawRt === "object" && rawRt ? (rawRt.pressed || (rawRt.value > 0.15)) : false) || val > 0.15;
                    }} else {{
                        const bObj = activeGp.buttons ? activeGp.buttons[b] : null;
                        if (bObj) {{
                            val = (typeof bObj === "object" && bObj !== null) ? (bObj.value !== undefined ? bObj.value : (bObj.pressed ? 1 : 0)) : (bObj ? 1 : 0);
                            isDown = (typeof bObj === "object" && bObj !== null) ? (bObj.pressed || (val > 0.45)) : (val > 0.45);
                        }}
                    }}
                    // Fusión con puente de software (LB/RB por teclado/pointer/kernel)
                    if (b === 4 && window.rawSoftwareLbDown) {{
                        isDown = true;
                        val = 1.0;
                    }}
                    if (b === 5 && window.rawSoftwareRbDown) {{
                        isDown = true;
                        val = 1.0;
                    }}
                    // Reasignación inteligente L3 / R3 a LB / RB cuando está habilitada
                    if (window.remapL3R3ToBumpers) {{
                        if (b === 4) {{
                            const bL3 = activeGp.buttons ? activeGp.buttons[10] : null;
                            const isL3 = bL3 ? ((typeof bL3 === "object" && bL3 !== null) ? (bL3.pressed || (bL3.value > 0.45)) : (bL3 > 0.45)) : false;
                            if (isL3) {{
                                isDown = true;
                                val = 1.0;
                            }}
                        }}
                        if (b === 5) {{
                            const bR3 = activeGp.buttons ? activeGp.buttons[11] : null;
                            const isR3 = bR3 ? ((typeof bR3 === "object" && bR3 !== null) ? (bR3.pressed || (bR3.value > 0.45)) : (bR3 > 0.45)) : false;
                            if (isR3) {{
                                isDown = true;
                                val = 1.0;
                            }}
                        }}
                    }}
                    curBtns[b] = (b === 6 || b === 7) ? val : (isDown ? 1 : 0);

                    // Iluminación visual de botones en pantalla
                    const scrBtn = document.querySelector(`[data-btn="${{b}}"]`);
                    if (scrBtn) scrBtn.classList.toggle("pressed", isDown);

                    // Registro de Telemetría Edge-Triggered
                    const wasDown = !!prevBtns[b];
                    if (isDown && !wasDown) {{
                        const cur = (typeof state !== "undefined" && state.avatar) ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
                        const bLabel = GP_BTN_LABELS[b] || `Btn_Raw_${{b}}`;
                        if (window.recordTelemetry) {{
                            window.recordTelemetry("CALIBRATE_BTN_DOWN", cur, bLabel, "Press", `[BOTÓN FÍSICO DETECTADO] Raw Index #${{b}} | Etiqueta: "${{bLabel}}" | Valor: ${{val.toFixed(2)}} | Mando: ${{activeGp.id}}`);
                        }}
                    }} else if (!isDown && wasDown) {{
                        const cur = (typeof state !== "undefined" && state.avatar) ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
                        const bLabel = GP_BTN_LABELS[b] || `Btn_Raw_${{b}}`;
                        if (window.recordTelemetry) {{
                            window.recordTelemetry("CALIBRATE_BTN_UP", cur, bLabel, "Release", `[BOTÓN LIBERADO] Raw Index #${{b}} | Etiqueta: "${{bLabel}}"`);
                        }}
                    }}
                }}

                // Actualizar badges visuales de LB y RB en el HUD
                const badgeLb = document.getElementById("tel-badge-lb");
                const badgeRb = document.getElementById("tel-badge-rb");
                if (badgeLb) {{
                    badgeLb.textContent = curBtns[4] ? "LB: ACTIVO" : "LB: OFF";
                    badgeLb.style.background = curBtns[4] ? "rgba(0,255,200,0.35)" : "rgba(0,255,200,0.08)";
                    badgeLb.style.boxShadow = curBtns[4] ? "0 0 12px #00ffc8" : "none";
                }}
                if (badgeRb) {{
                    badgeRb.textContent = curBtns[5] ? "RB: ACTIVO" : "RB: OFF";
                    badgeRb.style.background = curBtns[5] ? "rgba(245,158,11,0.35)" : "rgba(245,158,11,0.08)";
                    badgeRb.style.boxShadow = curBtns[5] ? "0 0 12px #f59e0b" : "none";
                }}

                // Sonda diagnóstica continua de todos los botones y ejes del Gamepad
                if (activeGp.buttons) {{
                    for (let rbi = 0; rbi < activeGp.buttons.length; rbi++) {{
                        const rawB = activeGp.buttons[rbi];
                        const rVal = (typeof rawB === "object" && rawB !== null) ? (rawB.value !== undefined ? rawB.value : (rawB.pressed ? 1 : 0)) : (rawB ? 1 : 0);
                        const rDown = (typeof rawB === "object" && rawB !== null) ? (rawB.pressed || (rVal > 0.35)) : (rVal > 0.35);
                        if (rDown && !lastRawProbeBtns[rbi]) {{
                            updateRawProbeDisplay("GP_BTN", `#${{rbi}} (${{GP_BTN_LABELS[rbi] || "Raw"}}) val:${{rVal.toFixed(2)}}`);
                        }}
                        lastRawProbeBtns[rbi] = rDown ? 1 : 0;
                    }}
                }}
                if (activeGp.axes) {{
                    for (let rai = 0; rai < activeGp.axes.length; rai++) {{
                        const aVal = activeGp.axes[rai] || 0;
                        if (Math.abs(aVal) > 0.4 && Math.abs(lastRawProbeAxes[rai] || 0) <= 0.4) {{
                            updateRawProbeDisplay("GP_AXIS", `#${{rai}} val:${{aVal.toFixed(2)}}`);
                        }}
                        lastRawProbeAxes[rai] = (Math.abs(aVal) > 0.4) ? aVal : 0;
                    }}
                }}

                // Conmutador de Modo Dual: SELECT + R3 (8+11), SELECT + START (8+9), L3 + R3 (10+11) o Botón 16 (Nexus / Guía)
                const isComboToggle = (curBtns[8] && curBtns[11]) ||
                                      (curBtns[8] && curBtns[9]) ||
                                      (curBtns[10] && curBtns[11]) ||
                                      !!curBtns[16];
                if (isComboToggle && !btn16LastDown) {{
                    btn16LastDown = true;
                    if (!window.isGameModeLocked && typeof window.toggleMouseMode === "function") {{
                        window.toggleMouseMode();
                    }}
                }} else if (!isComboToggle) {{
                    btn16LastDown = false;
                }}

                // 4. Sticks Analógicos con Deadzone Calibrada (0.10)
                let ax0 = activeGp.axes[0] || 0;
                let ax1 = activeGp.axes[1] || 0;
                let ax2 = (activeGp.axes.length >= 3) ? (activeGp.axes[2] || 0) : 0;
                let ax3 = (activeGp.axes.length >= 4) ? (activeGp.axes[3] || 0) : 0;

                const magL = Math.hypot(ax0, ax1);
                if (magL < 0.10) {{ ax0 = 0; ax1 = 0; }}
                else {{ const s = (magL - 0.10) / 0.90; ax0 = (ax0 / magL) * s; ax1 = (ax1 / magL) * s; }}

                const magR = Math.hypot(ax2, ax3);
                if (magR < 0.10) {{ ax2 = 0; ax3 = 0; }}
                else {{ const s = (magR - 0.10) / 0.90; ax2 = (ax2 / magR) * s; ax3 = (ax3 / magR) * s; }}

                const currentAxes = [ax0, ax1, ax2, ax3];

                // Sincronizar variables globales de estado para compatibilidad total
                if (typeof gpAxesState !== "undefined") {{
                    gpAxesState[0] = ax0; gpAxesState[1] = ax1;
                    gpAxesState[2] = ax2; gpAxesState[3] = ax3;
                }}
                if (typeof gpButtonsState !== "undefined") {{
                    for (let i = 0; i < 17; i++) gpButtonsState[i] = curBtns[i];
                }}
                window._currentAxes = currentAxes;
                window._currentButtons = curBtns;

                // Telemetría de Ejes Analógicos (con limitador de tasa a 130ms)
                const now = Date.now();
                if ((Math.abs(ax0) > 0.06 || Math.abs(ax1) > 0.06 || Math.abs(ax2) > 0.06 || Math.abs(ax3) > 0.06) && (now - lastPhysicalAxesLogTime > 130)) {{
                    lastPhysicalAxesLogTime = now;
                    const cur = (typeof state !== "undefined" && state.avatar) ? {{ x: state.avatar.x, y: state.avatar.y }} : {{ x: 960, y: 540 }};
                    if (window.recordTelemetry) {{
                        window.recordTelemetry("PHYSICAL_AXES", cur, "Sticks", "Move", `Stick L:(X:${{ax0.toFixed(2)}}, Y:${{ax1.toFixed(2)}}) | Stick R:${{ax2.toFixed(2)}}, Y:${{ax3.toFixed(2)}})`);
                    }}
                }}

                // 5. MODO RATÓN / ESCRITORIO O MODO JUEGO
                if (window.isControllerMouseMode && typeof window.processDesktopMouseControls === "function") {{
                    window.processDesktopMouseControls(currentAxes, curBtns, lastLoggedPhysicalBtns);
                }} else {{
                    // Modo Juego: Locomoción física fluida del Avatar
                    if (window.updateAvatarFromGamepad) {{
                        window.updateAvatarFromGamepad(currentAxes, curBtns);
                    }}
                }}

                // Persistir estado de botones para detección en el próximo ciclo
                for (let b = 0; b < totalRawBtns; b++) {{
                    lastLoggedPhysicalBtns[b] = curBtns[b] ? 1 : 0;
                }}
            }} else {{
                // Si no hay mando físico pero sí mandos táctiles en pantalla
                if (window._currentAxes && window._currentButtons) {{
                    if (window.isControllerMouseMode && typeof window.processDesktopMouseControls === "function") {{
                        window.processDesktopMouseControls(window._currentAxes, window._currentButtons, window._lastTouchBtns || new Array(17).fill(0));
                    }} else if (window.updateAvatarFromGamepad) {{
                        window.updateAvatarFromGamepad(window._currentAxes, window._currentButtons);
                    }}
                }}
            }}
        }}

        // Ejecutar bucle con doble garantía: requestAnimationFrame para fluidez nativa y setInterval como fallback
        function startSyncLoop() {{
            processPhysicalGamepadFrame();
            requestAnimationFrame(startSyncLoop);
        }}
        requestAnimationFrame(startSyncLoop);
        setInterval(processPhysicalGamepadFrame, 16);

        // Registro de Toques y Deslizamientos Físicos Continuos en Pantalla
        const touchTrackMap = window.touchTrackMap || (window.touchTrackMap = new Map());
        let lastLoggedSlideTime = 0;

        window.addEventListener("touchstart", function(e) {{
            for (let i = 0; i < e.changedTouches.length; i++) {{
                const t = e.changedTouches[i];
                const target = t.target.id || t.target.className || t.target.tagName;
                touchTrackMap.set(t.identifier, {{
                    startX: t.clientX, startY: t.clientY,
                    lastX: t.clientX, lastY: t.clientY,
                    target: target,
                    startTime: Date.now()
                }});
                if (window.recordTelemetry) {{
                    window.recordTelemetry("TOUCH_START", {{ x: t.clientX, y: t.clientY }}, target, "Down", `Dedo #${{t.identifier}} en pantalla física`);
                }}
            }}
        }}, {{ passive: true }});

        // REGISTRO DE DESLIZAMIENTO CONTINUO (TOUCHMOVE): Registra el desplazamiento exacto del dedo y el resultado
        window.addEventListener("touchmove", function(e) {{
            const now = Date.now();
            for (let i = 0; i < e.changedTouches.length; i++) {{
                const t = e.changedTouches[i];
                const track = touchTrackMap.get(t.identifier);
                if (track) {{
                    const dx = t.clientX - track.lastX;
                    const dy = t.clientY - track.lastY;
                    const dist = Math.hypot(dx, dy);

                    // Registrar si hubo desplazamiento físico
                    if (dist >= 2) {{
                        track.lastX = t.clientX;
                        track.lastY = t.clientY;

                        if (now - lastLoggedSlideTime > 75 && window.recordTelemetry) {{
                            lastLoggedSlideTime = now;
                            const totalDx = t.clientX - track.startX;
                            const totalDy = t.clientY - track.startY;

                            // Comprobación de Incongruencias y Anomalías en Tiempo Real
                            let anomaly = "";
                            const cur = (typeof state !== "undefined") ? state.cursor : {{ x: 960, y: 540, mask: 0 }};

                            // 1. Detección de cursores duplicados en el DOM
                            const cursorsFound = document.querySelectorAll("#cloud-virtual-cursor").length;
                            if (cursorsFound > 1) {{
                                anomaly = "PUNTERO_DUPLICADO (" + cursorsFound + ")";
                            }}

                            // 2. Detección de Drift/Desfase en Modo Táctil Directo
                            if (typeof currentMode !== "undefined" && currentMode === "TOUCH" && typeof virtualToScreen === "function") {{
                                const sPos = virtualToScreen(cur.x, cur.y);
                                const drift = Math.hypot(t.clientX - sPos.x, t.clientY - sPos.y);
                                if (drift > 28) {{
                                    anomaly = "DESFASE_TACTIL (" + Math.round(drift) + "px)";
                                }}
                            }}

                            // 3. Límite de Escritorio
                            if (cur.x <= 0 || cur.x >= 1920 || cur.y <= 0 || cur.y >= 1080) {{
                                if (!anomaly) anomaly = "LIMITE_ESCRITORIO";
                            }}

                            window.recordTelemetry(
                                "FINGER_SLIDE",
                                cur,
                                track.target,
                                "Slide",
                                `Dedo: (dx:${{Math.round(dx)}}, dy:${{Math.round(dy)}}) Total: (dx:${{Math.round(totalDx)}}, dy:${{Math.round(totalDy)}}) | PunteroVirt: (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`,
                                anomaly,
                                {{ x: t.clientX, y: t.clientY }}
                            );
                        }}
                    }}
                }}
            }}
        }}, {{ passive: true }});

        window.addEventListener("touchend", function(e) {{
            for (let i = 0; i < e.changedTouches.length; i++) {{
                const t = e.changedTouches[i];
                const track = touchTrackMap.get(t.identifier);
                const target = track ? track.target : (t.target.id || t.target.className || t.target.tagName);
                touchTrackMap.delete(t.identifier);
                if (window.recordTelemetry) {{
                    window.recordTelemetry("TOUCH_END", {{ x: t.clientX, y: t.clientY }}, target, "Release", `Dedo #${{t.identifier}} levantado`);
                }}
            }}
        }}, {{ passive: true }});

        window.addEventListener("touchcancel", function(e) {{
            for (let i = 0; i < e.changedTouches.length; i++) {{
                touchTrackMap.delete(e.changedTouches[i].identifier);
            }}
        }}, {{ passive: true }});
    }})();
    </script>
</body>
</html>
"""

class SandboxHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            html = build_sandbox_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(html)
        elif parsed.path == "/api/log":
            if LOG_FILE.exists():
                content = LOG_FILE.read_text(encoding="utf-8")
            else:
                content = "No logs yet.\n"
            data = content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif parsed.path == "/sw.js":
            sw_code = b"self.addEventListener('install', (e) => { self.skipWaiting(); }); self.addEventListener('activate', (e) => { e.waitUntil(self.clients.claim()); }); self.addEventListener('fetch', (e) => { e.respondWith(fetch(e.request)); });"
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(sw_code)))
            self.end_headers()
            self.wfile.write(sw_code)
        elif parsed.path == "/icon-192.png":
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(ICON_192)))
            self.end_headers()
            self.wfile.write(ICON_192)
        elif parsed.path == "/icon-512.png":
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(ICON_512)))
            self.end_headers()
            self.wfile.write(ICON_512)
        elif parsed.path == "/manifest.json":
            manifest = json.dumps({
                "name": "Aether Cloud Studio",
                "short_name": "AetherPC",
                "start_url": "/",
                "scope": "/",
                "display": "fullscreen",
                "orientation": "landscape",
                "background_color": "#0a0f1a",
                "theme_color": "#0a0f1a",
                "icons": [
                    {
                        "src": "/icon-192.png",
                        "sizes": "192x192",
                        "type": "image/png",
                        "purpose": "any maskable"
                    },
                    {
                        "src": "/icon-512.png",
                        "sizes": "512x512",
                        "type": "image/png",
                        "purpose": "any maskable"
                    }
                ]
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/manifest+json; charset=utf-8")
            self.send_header("Content-Length", str(len(manifest)))
            self.end_headers()
            self.wfile.write(manifest)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/log":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                entries = data.get("entries", [])
                for entry in entries:
                    log_telemetry_entry(entry)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        elif parsed.path == "/api/clear_log":
            if LOG_FILE.exists():
                LOG_FILE.unlink()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"cleared"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def main():
    # Inicializar archivo de log con cabecera
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "="*80 + "\n")
        f.write("=== AETHER STUDIO v2 - REGISTRO DE DESLIZAMIENTO FÍSICO Y TELEMETRÍA ===\n")
        f.write(f"Reanudado en: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Formato: [TIMESTAMP] EVENTO | COORDENADAS | ELEMENTO | ACCIÓN | DETALLES\n")
        f.write("="*80 + "\n\n")

    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, SandboxHandler)
    print(f"[AETHER] Laboratorio de Pruebas v2 iniciado en http://localhost:{PORT}")
    print(f"[AETHER] Guardando telemetría en vivo en: {LOG_FILE}")
    sys.stdout.flush()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        httpd.server_close()

if __name__ == "__main__":
    main()
