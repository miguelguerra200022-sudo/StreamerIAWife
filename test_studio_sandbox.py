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
    """Extrae el bloque exacto de CSS, HTML y JS de producción de run_kaggle_vnc_studio.py y adapta mejoras"""
    if not SOURCE_FILE.exists():
        return ""
    text = SOURCE_FILE.read_text(encoding="utf-8")
    start_marker = 'hud_code = """'
    end_marker = '"""\n            if "<meta charset=" not in content.lower():'
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start != -1 and end != -1:
        code = text[start + len(start_marker):end]

        # 1. Iniciar directamente en Modo Ratón PC sin desincronización
        code = code.replace(
            "let isControllerMouseMode = false;",
            "let isControllerMouseMode = true;\n    window.isControllerMouseMode = true;\n    window.setControllerMouseMode = function(v) { isControllerMouseMode = !!v; };"
        )

        # 2. Corregir arrastre en sendMouseMove() para mandos:
        #    Cuando el mando mueve Stick L mientras mantiene presionado A o RT,
        #    debe conservar la máscara activa (1) en vez de forzar 0.
        code = code.replace(
            "function sendMouseMove() {\n        sendPointer(virtX, virtY, isDragging ? 1 : 0);\n    }",
            """function sendMouseMove() {
        const isDown = isDragging || (isControllerMouseMode && ((lastMouseMask & 1) !== 0));
        sendPointer(virtX, virtY, isDown ? 1 : 0);
    }"""
        )

        # 3. Sincronizar el conmutador de modo SELECT + R3 con window.isControllerMouseMode y UI
        code = code.replace(
            'isControllerMouseMode = !isControllerMouseMode;\n                        showToast(isControllerMouseMode ? "Mando en Modo Ratón PC" : "Mando en Modo Juego XInput");',
            '''isControllerMouseMode = !isControllerMouseMode;
                        window.isControllerMouseMode = isControllerMouseMode;
                        if (typeof window.syncUIMouseMode === "function") window.syncUIMouseMode(isControllerMouseMode);
                        showToast(isControllerMouseMode ? "Mando en Modo Ratón PC" : "Mando en Modo Juego XInput");'''
        )

        # 4. Auto-iniciar bucle de mando físico de inmediato para mandos ya conectados
        code = code.replace(
            "startPhysicalGamepadLoop();\n    });",
            "startPhysicalGamepadLoop();\n    });\n    startPhysicalGamepadLoop();"
        )

        return code
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
    <title>Aether Studio — Ubuntu Desktop</title>
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
    </style>
</head>
<body class="tp-trackpad-mode">

    <!-- Contenedor Base noVNC Idéntico a Producción -->
    <div id="noVNC_screen" tabindex="0" style="outline:none;">
        <canvas id="noVNC_canvas" width="1920" height="1080" tabindex="0" style="outline:none;"></canvas>
    </div>

    <!-- MOCK ENGINE noVNC & Simulador de Escritorio 1080p con Telemetría Silenciosa -->
    <script>
    (function() {{
        const canvas = document.getElementById("noVNC_canvas");
        const ctx = canvas.getContext("2d");

        // Estado del Escritorio Simulado 1080p
        const state = {{
            width: 1920,
            height: 1080,
            cursor: {{ x: 960, y: 540, mask: 0 }},
            window: {{
                x: 460, y: 110, w: 560, h: 370,
                isDragging: false, dragOffX: 0, dragOffY: 0,
                title: "Consola X11 — Ubuntu 22.04 LTS",
                terminalLines: [
                    "Aether Studio v3.2.0 [Ubuntu 22.04 LTS]",
                    "Entorno Oficial Conectado — Modo Ratón PC Activo",
                    "Arrastra archivos o la ventana a la Zona de Arrastre:"
                ],
                activeInput: ""
            }},
            buttons: [
                {{ id: "btn_test_left", x: 485, y: 415, w: 120, h: 42, label: "Click Izq", clicked: false, time: 0 }},
                {{ id: "btn_test_right", x: 620, y: 415, w: 120, h: 42, label: "Click Der", clicked: false, time: 0 }},
                {{ id: "btn_test_dbl", x: 755, y: 415, w: 130, h: 42, label: "Doble Click", clicked: false, time: 0 }},
                {{ id: "btn_test_clear", x: 895, y: 415, w: 105, h: 42, label: "Limpiar", clicked: false, time: 0 }}
            ],
            desktopIcons: [
                {{ id: "icon_term", x: 490, y: 530, origX: 490, origY: 530, label: "Terminal X11", icon: ">_", color: "#38bdf8", isDragging: false, dragOffX: 0, dragOffY: 0 }},
                {{ id: "icon_game", x: 620, y: 530, origX: 620, origY: 530, label: "Juegos Cloud", icon: "GFN", color: "#10b981", isDragging: false, dragOffX: 0, dragOffY: 0 }},
                {{ id: "icon_files", x: 750, y: 530, origX: 750, origY: 530, label: "Archivos", icon: "DIR", color: "#f59e0b", isDragging: false, dragOffX: 0, dragOffY: 0 }},
                {{ id: "icon_settings", x: 880, y: 530, origX: 880, origY: 530, label: "Ajustes", icon: "SYS", color: "#94a3b8", isDragging: false, dragOffX: 0, dragOffY: 0 }}
            ],
            draggableFiles: [
                {{ id: "file_test", x: 920, y: 520, w: 120, h: 84, origX: 920, origY: 520, label: "Doc_Prueba.txt", icon: "📄", color: "#38bdf8", isDragging: false, dragOffX: 0, dragOffY: 0 }}
            ],
            selectionBox: {{ active: false, startX: 0, startY: 0, currentX: 0, currentY: 0 }},
            isAnyDragging: false,
            lastDragLabel: "",
            dropTarget: {{ x: 1080, y: 510, w: 370, h: 190, label: "Zona de Arrastre Libre (Drop Zone)", isOver: false, dropCount: 0, lastDropped: "" }},
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
            ripples: []
        }};

        // Sistema de Telemetría Silenciosa en Segundo Plano
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
            const now = Date.now();
            if (telemetryBuffer.length >= 10 || (now - lastSendTime > 150)) {{
                flushTelemetry();
            }}
        }}
        window.recordTelemetry = recordTelemetry;

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

        window.touchTrackMap = new Map();
        window.addEventListener("touchstart", (e) => {{
            for (let i = 0; i < e.changedTouches.length; i++) {{
                const t = e.changedTouches[i];
                window.touchTrackMap.set(t.identifier, {{ lastX: t.clientX, lastY: t.clientY }});
                recordTelemetry("TOUCH_DOWN", {{ x: t.clientX, y: t.clientY }}, "Screen", "Down", `Dedo #${{t.identifier}}`);
            }}
        }}, {{ passive: true }});
        window.addEventListener("touchmove", (e) => {{
            for (let i = 0; i < e.changedTouches.length; i++) {{
                const t = e.changedTouches[i];
                window.touchTrackMap.set(t.identifier, {{ lastX: t.clientX, lastY: t.clientY }});
            }}
        }}, {{ passive: true }});
        window.addEventListener("touchend", (e) => {{
            for (let i = 0; i < e.changedTouches.length; i++) {{
                const t = e.changedTouches[i];
                window.touchTrackMap.delete(t.identifier);
                recordTelemetry("TOUCH_UP", {{ x: t.clientX, y: t.clientY }}, "Screen", "Up", `Dedo #${{t.identifier}}`);
            }}
        }}, {{ passive: true }});
        window.addEventListener("touchcancel", (e) => {{
            for (let i = 0; i < e.changedTouches.length; i++) {{
                window.touchTrackMap.delete(e.changedTouches[i].identifier);
            }}
        }}, {{ passive: true }});

        // Dibujo del Canvas Simulado 1080p
        function drawCanvas() {{
            ctx.clearRect(0, 0, state.width, state.height);

            // 1. Fondo Cyberpunk
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

            // Marcador de zona de trabajo
            ctx.fillStyle = "rgba(0, 255, 200, 0.03)";
            ctx.fillRect(440, 50, 1040, 980);
            ctx.strokeStyle = "rgba(0, 255, 200, 0.10)";
            ctx.lineWidth = 1;
            ctx.strokeRect(440, 50, 1040, 980);

            // Barra Superior
            ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
            ctx.fillRect(0, 0, state.width, 42);
            ctx.fillStyle = "rgba(0, 255, 200, 0.4)";
            ctx.fillRect(0, 41, state.width, 1);

            ctx.fillStyle = "#00ffc8";
            ctx.font = "bold 15px monospace";
            ctx.fillText("// AETHER CLOUD PC — SISTEMA OFICIAL UBUNTU CORE", 460, 27);

            ctx.fillStyle = "#94a3b8";
            ctx.font = "13px monospace";
            ctx.fillText("Espacio Virtual: 1920x1080 | Telemetría en Vivo", 1120, 27);

            // 2. Ventana de Consola X11
            const win = state.window;
            ctx.save();
            ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
            ctx.shadowBlur = 24;
            ctx.shadowOffsetY = 8;
            ctx.fillStyle = "rgba(15, 23, 42, 0.96)";
            ctx.beginPath();
            ctx.roundRect(win.x, win.y, win.w, win.h, 12);
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.strokeStyle = win.isDragging ? "#00ffc8" : "rgba(56, 189, 248, 0.45)";
            ctx.lineWidth = win.isDragging ? 2.5 : 1.5;
            ctx.stroke();

            // Cabecera de la ventana
            ctx.fillStyle = win.isDragging ? "rgba(30, 58, 80, 0.95)" : "rgba(30, 41, 59, 0.95)";
            ctx.beginPath();
            ctx.roundRect(win.x, win.y, win.w, 40, [12, 12, 0, 0]);
            ctx.fill();

            // Botones semáforo
            ctx.fillStyle = "#ef4444"; ctx.beginPath(); ctx.arc(win.x + 22, win.y + 20, 6, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#f59e0b"; ctx.beginPath(); ctx.arc(win.x + 40, win.y + 20, 6, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#10b981"; ctx.beginPath(); ctx.arc(win.x + 58, win.y + 20, 6, 0, Math.PI*2); ctx.fill();

            ctx.fillStyle = "#e2e8f0";
            ctx.font = "bold 13px sans-serif";
            ctx.fillText(win.title + (win.isDragging ? " [ARRASTRANDO...]" : ""), win.x + 76, win.y + 25);

            // Terminal interior
            ctx.fillStyle = "#050811";
            ctx.beginPath();
            ctx.roundRect(win.x + 14, win.y + 48, win.w - 28, 230, 8);
            ctx.fill();
            ctx.strokeStyle = "rgba(255,255,255,0.08)";
            ctx.stroke();

            ctx.fillStyle = "#38bdf8";
            ctx.font = "13px monospace";
            let lineY = win.y + 74;
            win.terminalLines.forEach((l) => {{
                ctx.fillText(l, win.x + 24, lineY);
                lineY += 22;
            }});

            ctx.fillStyle = "#00ffc8";
            ctx.fillText("> " + win.activeInput + (Math.floor(Date.now() / 500) % 2 === 0 ? "█" : ""), win.x + 24, lineY + 12);

            // Botones interiores de prueba
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

            // 3. Zona de Arrastre Libre (Drop Target)
            const dt = state.dropTarget;
            ctx.save();
            ctx.lineWidth = dt.isOver ? 3 : 2;
            ctx.setLineDash([8, 6]);
            ctx.strokeStyle = dt.isOver ? "#00ffc8" : "rgba(0, 255, 200, 0.4)";
            ctx.fillStyle = dt.isOver ? "rgba(0, 255, 200, 0.16)" : "rgba(0, 255, 200, 0.04)";
            ctx.beginPath();
            ctx.roundRect(dt.x, dt.y, dt.w, dt.h, 14);
            ctx.fill();
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = dt.isOver ? "#00ffc8" : "rgba(0, 255, 200, 0.9)";
            ctx.font = "bold 15px monospace";
            ctx.textAlign = "center";
            ctx.fillText(dt.label, dt.x + dt.w / 2, dt.y + 36);

            ctx.fillStyle = "#cbd5e1";
            ctx.font = "12px sans-serif";
            ctx.fillText("Arrastra aquí Doc_Prueba.txt, iconos o la consola", dt.x + dt.w / 2, dt.y + 64);

            if (dt.dropCount > 0) {{
                ctx.fillStyle = "#10b981";
                ctx.font = "bold 14px monospace";
                ctx.fillText(`✓ Elementos soltados con éxito: ${{dt.dropCount}}`, dt.x + dt.w / 2, dt.y + 115);
                ctx.fillStyle = "#94a3b8";
                ctx.font = "11px monospace";
                ctx.fillText(`Último: "${{dt.lastDropped}}"`, dt.x + dt.w / 2, dt.y + 140);
            }}
            ctx.textAlign = "left";
            ctx.restore();

            // 4. Iconos de Escritorio Arrastrables
            state.desktopIcons.forEach(ic => {{
                ctx.save();
                ctx.shadowColor = ic.isDragging ? ic.color : "rgba(0,0,0,0.5)";
                ctx.shadowBlur = ic.isDragging ? 18 : 6;
                ctx.fillStyle = ic.isDragging ? "rgba(30, 41, 59, 0.95)" : "rgba(15, 23, 42, 0.85)";
                ctx.strokeStyle = ic.isDragging ? ic.color : "rgba(255, 255, 255, 0.15)";
                ctx.lineWidth = ic.isDragging ? 2.5 : 1.2;
                ctx.beginPath();
                ctx.roundRect(ic.x, ic.y, 90, 80, 10);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = ic.color;
                ctx.font = "bold 20px monospace";
                ctx.textAlign = "center";
                ctx.fillText(ic.icon, ic.x + 45, ic.y + 38);

                ctx.fillStyle = "#f1f5f9";
                ctx.font = "11px sans-serif";
                ctx.fillText(ic.label, ic.x + 45, ic.y + 62);
                ctx.textAlign = "left";
                ctx.restore();
            }});

            // 5. Archivo Arrastrable de Prueba (Doc_Prueba.txt)
            if (state.draggableFiles) {{
                state.draggableFiles.forEach(f => {{
                    ctx.save();
                    ctx.shadowColor = f.isDragging ? "#38bdf8" : "rgba(0, 0, 0, 0.6)";
                    ctx.shadowBlur = f.isDragging ? 22 : 8;
                    ctx.fillStyle = f.isDragging ? "rgba(56, 189, 248, 0.25)" : "rgba(30, 41, 59, 0.92)";
                    ctx.strokeStyle = f.isDragging ? "#38bdf8" : "rgba(56, 189, 248, 0.55)";
                    ctx.lineWidth = f.isDragging ? 2.5 : 1.5;
                    ctx.beginPath();
                    ctx.roundRect(f.x, f.y, f.w, f.h, 10);
                    ctx.fill();
                    ctx.stroke();

                    ctx.font = "26px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText(f.icon, f.x + f.w / 2, f.y + 38);

                    ctx.fillStyle = f.isDragging ? "#38bdf8" : "#e2e8f0";
                    ctx.font = "bold 12px sans-serif";
                    ctx.fillText(f.label, f.x + f.w / 2, f.y + 64);
                    ctx.textAlign = "left";
                    ctx.restore();
                }});
            }}

            // 6. Rectángulo de Selección Marquee
            if (state.selectionBox && state.selectionBox.active) {{
                const sb = state.selectionBox;
                const sx = Math.min(sb.startX, sb.currentX);
                const sy = Math.min(sb.startY, sb.currentY);
                const sw = Math.abs(sb.currentX - sb.startX);
                const sh = Math.abs(sb.currentY - sb.startY);

                ctx.save();
                ctx.fillStyle = "rgba(56, 189, 248, 0.16)";
                ctx.strokeStyle = "#38bdf8";
                ctx.lineWidth = 1.5;
                ctx.setLineDash([4, 4]);
                ctx.beginPath();
                ctx.rect(sx, sy, sw, sh);
                ctx.fill();
                ctx.stroke();
                ctx.restore();
            }}

            // 7. Menú Contextual (Clic Derecho)
            if (state.contextMenu && state.contextMenu.visible) {{
                const cm = state.contextMenu;
                ctx.save();
                ctx.shadowColor = "rgba(0, 0, 0, 0.85)";
                ctx.shadowBlur = 24;
                ctx.fillStyle = "rgba(15, 23, 42, 0.96)";
                ctx.strokeStyle = "#38bdf8";
                ctx.lineWidth = 1.8;
                ctx.beginPath();
                ctx.roundRect(cm.x, cm.y, cm.w, cm.h, 10);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = "rgba(56, 189, 248, 0.18)";
                ctx.beginPath();
                ctx.roundRect(cm.x, cm.y, cm.w, 32, [10, 10, 0, 0]);
                ctx.fill();
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 11px monospace";
                ctx.fillText("MENÚ CONTEXTUAL PC", cm.x + 14, cm.y + 20);

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

            // 8. Ondas Visuales de Clic (Ripples)
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
                    ctx.lineWidth = 2.5;
                    ctx.stroke();
                    ctx.restore();
                }}
            }}
        }}

        // Bucle de renderizado del Canvas a 60 FPS
        function renderLoop() {{
            drawCanvas();
            requestAnimationFrame(renderLoop);
        }}
        requestAnimationFrame(renderLoop);

        // MOCK RFB que recibe los eventos reales de hud_code
        let lastLoggedMove = 0;

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

                // Telemetría de movimiento
                const now = Date.now();
                if (moveDist > 2 && (now - lastLoggedMove > 75)) {{
                    lastLoggedMove = now;
                    let actionName = (mask === 1) ? "MOUSE_DRAG" : "POINTER_MOVE";
                    let targetName = "DesktopCanvas";
                    if (win.isDragging) {{ actionName = "WIN_DRAGGING"; targetName = "WindowHeader"; }}
                    else if (state.isAnyDragging) {{ actionName = "ITEM_DRAGGING"; targetName = state.lastDragLabel || "Item"; }}
                    else if (state.selectionBox && state.selectionBox.active) {{ actionName = "SELECTION_DRAG"; targetName = "SelectionMarquee"; }}

                    recordTelemetry(actionName, cur, targetName, "Move", `Delta: (dx:${{Math.round(deltaVirtX)}}, dy:${{Math.round(deltaVirtY)}}) | Puntero: (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);
                }}

                // 1. CLIC IZQUIERDO PRESIONADO (mask === 1 && oldMask !== 1)
                if (mask === 1 && oldMask !== 1) {{
                    recordTelemetry("CLICK_LEFT", cur, "Canvas", "Down", `Virtual(${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);
                    if (!state.ripples) state.ripples = [];
                    state.ripples.push({{ x: cur.x, y: cur.y, radius: 4, maxRadius: 40, color: "#38bdf8", alpha: 1.0 }});

                    // Context Menu
                    if (state.contextMenu && state.contextMenu.visible) {{
                        const cm = state.contextMenu;
                        if (cur.x >= cm.x && cur.x <= cm.x + cm.w && cur.y >= cm.y + 36 && cur.y <= cm.y + cm.h) {{
                            const itemIdx = Math.floor((cur.y - (cm.y + 36)) / 34);
                            if (itemIdx >= 0 && itemIdx < cm.items.length) {{
                                const chosen = cm.items[itemIdx];
                                win.terminalLines.push(`[MENÚ PC] ${{chosen.label}}`);
                                if (win.terminalLines.length > 7) win.terminalLines.shift();
                                recordTelemetry("CONTEXT_MENU_CLICK", cur, chosen.label, "Execute", chosen.label, "", activeFinger);
                            }}
                        }}
                        state.contextMenu.visible = false;
                        return;
                    }}

                    // Arrastre de Ventana
                    if (cur.x >= win.x && cur.x <= win.x + win.w &&
                        cur.y >= win.y && cur.y <= win.y + 40) {{
                        win.isDragging = true;
                        win.dragOffX = cur.x - win.x;
                        win.dragOffY = cur.y - win.y;
                        state.isAnyDragging = true;
                        state.lastDragLabel = "Ventana";
                        recordTelemetry("WIN_DRAG", cur, "WindowHeader", "StartDrag", "Ventana enganchada", "", activeFinger);
                        return;
                    }}

                    // Botones interiores
                    let hitBtn = false;
                    state.buttons.forEach(b => {{
                        if (cur.x >= b.x && cur.x <= b.x + b.w &&
                            cur.y >= b.y && cur.y <= b.y + b.h) {{
                            hitBtn = true;
                            b.time = Date.now();
                            b.clicked = true;
                            if (b.id === "btn_test_clear") {{
                                win.terminalLines = ["Consola limpiada. Listo."];
                                win.activeInput = "";
                            }} else {{
                                win.terminalLines.push(`[BOTÓN] ${{b.label}} pulsado`);
                                if (win.terminalLines.length > 7) win.terminalLines.shift();
                            }}
                            recordTelemetry("BTN_CLICK", cur, b.label, "Pressed", b.label, "", activeFinger);
                        }}
                    }});
                    if (hitBtn) return;

                    // Archivos arrastrables (Doc_Prueba.txt)
                    let hitFile = false;
                    if (state.draggableFiles) {{
                        state.draggableFiles.forEach(f => {{
                            if (cur.x >= f.x && cur.x <= f.x + f.w &&
                                cur.y >= f.y && cur.y <= f.y + f.h) {{
                                hitFile = true;
                                f.isDragging = true;
                                f.dragOffX = cur.x - f.x;
                                f.dragOffY = cur.y - f.y;
                                state.isAnyDragging = true;
                                state.lastDragLabel = f.label;
                                recordTelemetry("FILE_DRAG", cur, f.label, "StartDrag", f.label, "", activeFinger);
                            }}
                        }});
                    }}
                    if (hitFile) return;

                    // Iconos de escritorio
                    let hitIcon = false;
                    state.desktopIcons.forEach(ic => {{
                        if (cur.x >= ic.x && cur.x <= ic.x + 90 &&
                            cur.y >= ic.y && cur.y <= ic.y + 80) {{
                            hitIcon = true;
                            ic.isDragging = true;
                            ic.dragOffX = cur.x - ic.x;
                            ic.dragOffY = cur.y - ic.y;
                            state.isAnyDragging = true;
                            state.lastDragLabel = ic.label;
                            recordTelemetry("ICON_DRAG", cur, ic.label, "StartDrag", ic.label, "", activeFinger);
                        }}
                    }});
                    if (hitIcon) return;

                    // Clic en fondo -> Selección marquee
                    state.selectionBox = {{
                        active: true,
                        startX: cur.x,
                        startY: cur.y,
                        currentX: cur.x,
                        currentY: cur.y
                    }};
                }}

                // 2. MOVIMIENTO CON BOTÓN MANTENIDO (mask === 1)
                if (mask === 1) {{
                    if (win.isDragging) {{
                        win.x = Math.max(0, Math.min(1920 - win.w, cur.x - win.dragOffX));
                        win.y = Math.max(42, Math.min(1080 - win.h, cur.y - win.dragOffY));
                        dt.isOver = (win.x + win.w/2 >= dt.x && win.x + win.w/2 <= dt.x + dt.w &&
                                     win.y + win.h/2 >= dt.y && win.y + win.h/2 <= dt.y + dt.h);
                    }}
                    if (state.draggableFiles) {{
                        state.draggableFiles.forEach(f => {{
                            if (f.isDragging) {{
                                f.x = Math.max(0, Math.min(1920 - f.w, cur.x - f.dragOffX));
                                f.y = Math.max(42, Math.min(1080 - f.h, cur.y - f.dragOffY));
                                dt.isOver = (f.x + f.w/2 >= dt.x && f.x + f.w/2 <= dt.x + dt.w &&
                                             f.y + f.h/2 >= dt.y && f.y + f.h/2 <= dt.y + dt.h);
                            }}
                        }});
                    }}
                    state.desktopIcons.forEach(ic => {{
                        if (ic.isDragging) {{
                            ic.x = Math.max(0, Math.min(1920 - 90, cur.x - ic.dragOffX));
                            ic.y = Math.max(42, Math.min(1080 - 80, cur.y - ic.dragOffY));
                            dt.isOver = (ic.x + 45 >= dt.x && ic.x + 45 <= dt.x + dt.w &&
                                         ic.y + 40 >= dt.y && ic.y + 40 <= dt.y + dt.h);
                        }}
                    }});
                    if (state.selectionBox && state.selectionBox.active) {{
                        state.selectionBox.currentX = cur.x;
                        state.selectionBox.currentY = cur.y;
                    }}
                }}

                // 3. BOTÓN IZQUIERDO SOLTADO (mask === 0 && oldMask === 1)
                if (mask === 0 && oldMask === 1) {{
                    state.isAnyDragging = false;
                    state.lastDragLabel = "";

                    if (win.isDragging) {{
                        win.isDragging = false;
                        if (dt.isOver) {{
                            dt.dropCount = (dt.dropCount || 0) + 1;
                            dt.lastDropped = "Ventana de Consola";
                            win.terminalLines.push(`[ÉXITO DROP] Ventana soltada (#${{dt.dropCount}})`);
                            if (win.terminalLines.length > 7) win.terminalLines.shift();
                            recordTelemetry("WIN_DROP", cur, "DropTarget", "DropSuccess", `Ventana soltada (#${{dt.dropCount}})`, "", activeFinger);
                            if (navigator.vibrate) navigator.vibrate([30, 50, 30]);
                        }}
                        dt.isOver = false;
                    }}

                    if (state.draggableFiles) {{
                        state.draggableFiles.forEach(f => {{
                            if (f.isDragging) {{
                                f.isDragging = false;
                                if (dt.isOver) {{
                                    dt.dropCount = (dt.dropCount || 0) + 1;
                                    dt.lastDropped = f.label;
                                    win.terminalLines.push(`[ÉXITO DROP] "${{f.label}}" soltado (#${{dt.dropCount}})`);
                                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                                    recordTelemetry("FILE_DROP", cur, "DropTarget", "DropSuccess", `${{f.label}} soltado (#${{dt.dropCount}})`, "", activeFinger);
                                    if (navigator.vibrate) navigator.vibrate([30, 70, 30]);
                                    setTimeout(() => {{ f.x = f.origX; f.y = f.origY; }}, 1500);
                                }}
                                dt.isOver = false;
                            }}
                        }});
                    }}

                    state.desktopIcons.forEach(ic => {{
                        if (ic.isDragging) {{
                            ic.isDragging = false;
                            const movedDist = Math.hypot(ic.x - ic.origX, ic.y - ic.origY);
                            if (dt.isOver) {{
                                dt.dropCount = (dt.dropCount || 0) + 1;
                                dt.lastDropped = ic.label;
                                win.terminalLines.push(`[ÉXITO DROP] "${{ic.label}}" soltado (#${{dt.dropCount}})`);
                                if (win.terminalLines.length > 7) win.terminalLines.shift();
                                recordTelemetry("ICON_DROP", cur, "DropTarget", "DropSuccess", `${{ic.label}} soltado (#${{dt.dropCount}})`, "", activeFinger);
                                if (navigator.vibrate) navigator.vibrate([30, 70, 30]);
                                setTimeout(() => {{ ic.x = ic.origX; ic.y = ic.origY; }}, 1500);
                            }} else if (movedDist < 8) {{
                                win.terminalLines.push(`[LANZADOR] Abriendo ${{ic.label}}...`);
                                if (win.terminalLines.length > 7) win.terminalLines.shift();
                                recordTelemetry("ICON_LAUNCH", cur, ic.label, "Launch", ic.label, "", activeFinger);
                            }}
                            dt.isOver = false;
                        }}
                    }});

                    if (state.selectionBox && state.selectionBox.active) {{
                        const selW = Math.abs(state.selectionBox.currentX - state.selectionBox.startX);
                        const selH = Math.abs(state.selectionBox.currentY - state.selectionBox.startY);
                        state.selectionBox.active = false;
                        if (selW > 12 && selH > 12) {{
                            win.terminalLines.push(`[SELECCIÓN] Área: ${{Math.round(selW)}}x${{Math.round(selH)}} px`);
                            if (win.terminalLines.length > 7) win.terminalLines.shift();
                            recordTelemetry("SELECTION_MARQUEE", cur, "DesktopCanvas", "Select", `Área: ${{Math.round(selW)}}x${{Math.round(selH)}} px`, "", activeFinger);
                        }}
                    }}
                }}

                // 4. CLIC DERECHO (mask === 4 && oldMask !== 4)
                if (mask === 4 && oldMask !== 4) {{
                    recordTelemetry("CLICK_RIGHT", cur, "Canvas", "Down", `Menú contextual en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);
                    if (!state.ripples) state.ripples = [];
                    state.ripples.push({{ x: cur.x, y: cur.y, radius: 4, maxRadius: 36, color: "#f59e0b", alpha: 1.0 }});
                    state.contextMenu.visible = !state.contextMenu.visible;
                    state.contextMenu.x = Math.max(10, Math.min(1920 - state.contextMenu.w - 10, cur.x));
                    state.contextMenu.y = Math.max(42, Math.min(1080 - state.contextMenu.h - 10, cur.y));
                }}

                // 5. CLIC CENTRAL (mask === 2 && oldMask !== 2)
                if (mask === 2 && oldMask !== 2) {{
                    recordTelemetry("CLICK_MIDDLE", cur, "Canvas", "Down", `R3 en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);
                    if (!state.ripples) state.ripples = [];
                    state.ripples.push({{ x: cur.x, y: cur.y, radius: 4, maxRadius: 36, color: "#a855f7", alpha: 1.0 }});
                    win.terminalLines.push(`[CLIC CENTRAL R3] en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`);
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }}

                // 6. SCROLL 2D DE RUEDA (Stick R o 2 dedos)
                const scrollBits = mask & (8 | 16 | 32 | 64);
                if (scrollBits && (scrollBits !== (oldMask & (8 | 16 | 32 | 64)))) {{
                    let dirStr = "";
                    if (scrollBits & 8) dirStr = "Arriba ▲";
                    else if (scrollBits & 16) dirStr = "Abajo ▼";
                    else if (scrollBits & 32) dirStr = "Izquierda ◀";
                    else if (scrollBits & 64) dirStr = "Derecha ▶";

                    win.terminalLines.push(`[SCROLL] ${{dirStr}}`);
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                    recordTelemetry("MOUSE_SCROLL", cur, "DesktopCanvas", "Wheel", `Scroll: ${{dirStr}}`, "", activeFinger);
                }}
            }},

            sendKey: function(keysym, down) {{
                if (!down) return;
                recordTelemetry("KEY_INPUT", "-", "VirtualKbd", "KeyDown", `Keysym: ${{keysym}}`);
                const win = state.window;

                if (keysym === 0xff1b || keysym === 27) {{ // Escape
                    if (state.contextMenu && state.contextMenu.visible) {{
                        state.contextMenu.visible = false;
                        win.terminalLines.push("[ESCAPE] Menú contextual cerrado.");
                    }}
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }} else if (keysym === 0xff52) {{ // Flecha Arriba
                    win.terminalLines.push("[CRUCETA ▲] Arriba");
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }} else if (keysym === 0xff54) {{ // Flecha Abajo
                    win.terminalLines.push("[CRUCETA ▼] Abajo");
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }} else if (keysym === 0xff51) {{ // Flecha Izquierda
                    win.terminalLines.push("[CRUCETA ◀ / LB] Izquierda");
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }} else if (keysym === 0xff53) {{ // Flecha Derecha
                    win.terminalLines.push("[CRUCETA ▶ / RB] Derecha");
                    if (win.terminalLines.length > 7) win.terminalLines.shift();
                }} else if (keysym === 65288) {{ // Backspace
                    win.activeInput = win.activeInput.slice(0, -1);
                }} else if (keysym === 65293 || keysym === 0xff0d) {{ // Enter
                    win.terminalLines.push("> " + (win.activeInput || "comando ejecutado [OK]"));
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
        window.rfb = mockRFB;
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
        .gp-dpad-btn {{
            background: transparent !important;
            color: #38bdf8 !important;
        }}
        .gp-dpad-btn.pressed, .gp-dpad-btn:active {{
            background: rgba(56, 189, 248, 0.4) !important;
            box-shadow: 0 0 12px #38bdf8 !important;
        }}

        /* 4. Gatillos y Bumpers */
        .gp-shoulder-btn, .gp-trigger-btn {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: 2px solid rgba(0, 255, 200, 0.45) !important;
            color: var(--aether-cyan, #00ffc8) !important;
            box-shadow: none !important;
        }}
        .gp-shoulder-btn.pressed, .gp-shoulder-btn:active,
        .gp-trigger-btn.pressed, .gp-trigger-btn:active {{
            background: rgba(0, 255, 200, 0.35) !important;
            color: #ffffff !important;
            box-shadow: 0 0 20px var(--aether-cyan, #00ffc8) !important;
        }}

        /* 5. Botones Centrales */
        .gp-center-btn {{
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: 1.5px solid rgba(255, 255, 255, 0.3) !important;
            color: #cbd5e1 !important;
            box-shadow: none !important;
        }}
        .gp-center-btn.pressed, .gp-center-btn:active {{
            background: rgba(255, 255, 255, 0.35) !important;
            color: #ffffff !important;
        }}

        /* 6. Ocultación al detectar mando físico */
        #virtual-gamepad-overlay.gp-phys-hidden {{
            opacity: 0 !important;
            pointer-events: none !important;
            transform: scale(0.96) !important;
        }}
    </style>
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
