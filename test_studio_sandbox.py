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
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "test_touch_telemetry.log"
SOURCE_FILE = BASE_DIR / "run_kaggle_vnc_studio.py"
PORT = 8080

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

    anomaly_tag = f"⚠️ [ANOMALÍA: {anomaly}]" if anomaly else "✓ [OK: CALIBRADO]"

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
            gap: 8px;
            margin-top: 6px;
        }}
        .tel-btn {{
            flex: 1;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 8px;
            color: #e2e8f0;
            padding: 4px 8px;
            font-size: 10px;
            cursor: pointer;
            text-align: center;
            font-weight: 600;
        }}
        .tel-btn:active {{
            background: rgba(0,255,200,0.3);
            color: #00ffc8;
        }}
    </style>
</head>
<body>

    <!-- Contenedor Base noVNC -->
    <div id="noVNC_screen">
        <canvas id="noVNC_canvas" width="1920" height="1080"></canvas>
    </div>

    <!-- HUD de Telemetría Centrado e No Invasivo -->
    <div id="telemetry-hud-box" class="collapsed">
        <div class="tel-header" id="tel-toggle-btn">
            <span style="display:flex; align-items:center; gap:6px;">
                <span class="tel-indicator"></span>
                <span style="font-weight:800; letter-spacing:0.5px;">TELEMETRÍA EN VIVO</span>
            </span>
            <span class="tel-live-ticker" id="tel-ticker-text">Listo. Desliza o pulsa mandos</span>
            <span id="tel-collapse-icon" style="font-size:10px; color:#94a3b8;">▲ EXPANDIR</span>
        </div>
        <div class="tel-body">
            <div class="tel-log-stream" id="tel-stream-list">
                <div class="tel-log-item highlight">[LISTO] Esperando movimientos...</div>
            </div>
            <div class="tel-actions">
                <button class="tel-btn" id="tel-clear-btn">Limpiar Registro</button>
                <button class="tel-btn" id="tel-reset-avatar-btn">Centrar Todo</button>
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
                {{ id: "icon_term", x: 490, y: 530, label: "Terminal X11", icon: "⌨️", color: "#38bdf8" }},
                {{ id: "icon_game", x: 620, y: 530, label: "Juegos Cloud", icon: "🎮", color: "#10b981" }},
                {{ id: "icon_files", x: 750, y: 530, label: "Archivos", icon: "📁", color: "#f59e0b" }},
                {{ id: "icon_settings", x: 880, y: 530, label: "Ajustes", icon: "⚙️", color: "#94a3b8" }}
            ],
            dropTarget: {{ x: 1060, y: 510, w: 380, h: 180, label: "Zona de Arrastre Libre (Drop Zone)", isOver: false }}
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
                const anomAlert = anomaly ? `⚠️ [${{anomaly}}] ` : "";
                ticker.textContent = `${{anomAlert}}[${{type}}] Dedo:${{item.finger}} -> Puntero:${{item.coords}} | ${{action}}`;
            }}

            const stream = document.getElementById("tel-stream-list");
            if (stream) {{
                const el = document.createElement("div");
                el.className = anomaly ? "tel-log-item" : "tel-log-item highlight";
                if (anomaly) el.style.color = "#f43f5e";
                el.textContent = `${{anomaly ? '⚠️ ' : ''}}[${{type}}] D:${{item.finger}} -> P:${{item.coords}} | ${{action}} | ${{details}}`;
                stream.insertBefore(el, stream.firstChild);
                while (stream.children.length > 8) {{
                    stream.removeChild(stream.lastChild);
                }}
            }}

            // Enviar en ráfagas al servidor cada 100ms
            const now = Date.now();
            if (now - lastSendTime > 100 || telemetryBuffer.length >= 8) {{
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
            ctx.fillText("✦ AETHER CLOUD PC — LABORATORIO TÁCTIL Y TELEMETRÍA", 460, 27);

            ctx.fillStyle = "#94a3b8";
            ctx.font = "13px monospace";
            ctx.fillText("Espacio Virtual: 1920x1080 | Telemetría: Activa | Sin Lag", 1080, 27);

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
            ctx.strokeStyle = "rgba(0, 255, 200, 0.3)";
            ctx.lineWidth = 2;
            ctx.setLineDash([6, 6]);
            ctx.beginPath();
            ctx.arc(1260, 280, 160, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = "rgba(0, 255, 200, 0.5)";
            ctx.font = "bold 14px monospace";
            ctx.fillText("🎮 ARENA DE MANDO", 1190, 105);
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

            // 4. Zona Inferior de Prueba de Escritorio (Iconos y Zona de Arrastre)
            // Iconos
            state.desktopIcons.forEach(ic => {{
                ctx.fillStyle = "rgba(15, 23, 42, 0.7)";
                ctx.beginPath();
                ctx.roundRect(ic.x, ic.y, 90, 80, 10);
                ctx.fill();
                ctx.strokeStyle = "rgba(255,255,255,0.12)";
                ctx.stroke();

                ctx.font = "28px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText(ic.icon, ic.x + 45, ic.y + 40);

                ctx.fillStyle = ic.color;
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

            // 5. Unificación Total: El puntero oficial es #cloud-virtual-cursor (DOM SVG calibrado a 60/120Hz).
            // La superficie canvas nunca dibuja un segundo cursor redundante.

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

                    // Comprobar arrastre de cabecera de ventana
                    if (cur.x >= win.x && cur.x <= win.x + win.w &&
                        cur.y >= win.y && cur.y <= win.y + 42) {{
                        win.isDragging = true;
                        win.dragOffX = cur.x - win.x;
                        win.dragOffY = cur.y - win.y;
                        recordTelemetry("WIN_DRAG", cur, "WindowHeader", "StartDrag", "Ventana enganchada con éxito", "", activeFinger);
                    }}

                    // Comprobar botones dentro de la ventana
                    state.buttons.forEach(b => {{
                        if (cur.x >= b.x && cur.x <= b.x + b.w &&
                            cur.y >= b.y && cur.y <= b.y + b.h) {{
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
                    state.desktopIcons.forEach(ic => {{
                        if (cur.x >= ic.x && cur.x <= ic.x + 90 &&
                            cur.y >= ic.y && cur.y <= ic.y + 80) {{
                            win.terminalLines.push(`[LANZADOR] Abriendo ${{ic.label}}...`);
                            if (win.terminalLines.length > 7) win.terminalLines.shift();
                            recordTelemetry("ICON_LAUNCH", cur, ic.label, "Launch", "Acceso directo ejecutado", "", activeFinger);
                        }}
                    }});
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

                // Click Derecho presionado (Toque sostenido o 2 dedos)
                if (mask === 4 && oldMask !== 4) {{
                    recordTelemetry("CLICK_RIGHT", cur, "Canvas", "Down", `Menu Contextual activado en (${{Math.round(cur.x)}}, ${{Math.round(cur.y)}})`, "", activeFinger);
                    win.terminalLines.push(`[CLICK DERECHO] en X:${{Math.round(cur.x)}} Y:${{Math.round(cur.y)}}`);
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

                if (keysym === 65288) {{ // Backspace
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

        // Escucha y control del Avatar mediante Mandos Táctiles con Telemetría de Ejes
        let lastLoggedAxesTime = 0;
        window.updateAvatarFromGamepad = function(axes, buttons) {{
            const av = state.avatar;

            // Stick Izquierdo: Locomoción
            const lx = axes[0] || 0;
            const ly = axes[1] || 0;
            const speed = av.isSprinting ? 9.5 : 5.2;

            if (Math.hypot(lx, ly) > 0.06) {{
                av.vx = lx * speed;
                av.vy = ly * speed;

                const now = Date.now();
                if (now - lastLoggedAxesTime > 120) {{
                    lastLoggedAxesTime = now;
                    recordTelemetry("STICK_L_SLIDE", {{ x: av.x, y: av.y }}, "StickLeft", "Slide", `Vector: (X:${{lx.toFixed(2)}}, Y:${{ly.toFixed(2)}}) => Avatar Move (Vel:${{speed}}px)`);
                }}
            }}

            // Stick Derecho: Mira / Ángulo
            const rx = axes[2] || 0;
            const ry = axes[3] || 0;
            if (Math.hypot(rx, ry) > 0.12) {{
                av.angle = Math.atan2(ry, rx);
            }}

            // Botón A (0): Salto
            if (buttons[0] && !av.isJumping) {{
                av.isJumping = true;
                av.jumpScale = 1.45;
                setTimeout(() => {{ av.isJumping = false; av.jumpScale = 1.0; }}, 280);
                recordTelemetry("GAMEPAD_A", {{ x: av.x, y: av.y }}, "BtnA", "Jump", "Salto ejecutado");
            }}

            // Botón B (1): Dash
            if (buttons[1]) {{
                av.vx += Math.cos(av.angle) * 15;
                av.vy += Math.sin(av.angle) * 15;
                recordTelemetry("GAMEPAD_B", {{ x: av.x, y: av.y }}, "BtnB", "Dash", "Dash rápido hacia adelante");
            }}

            // Botón X (2): Ataque
            if (buttons[2] && av.attackEffect <= 0) {{
                av.attackEffect = 1.0;
                recordTelemetry("GAMEPAD_X", {{ x: av.x, y: av.y }}, "BtnX", "Attack", "Onda expansiva generada");
            }}

            // Botón Y (3): Escudo
            av.shieldActive = !!buttons[3];

            // Botón L3 (10): Sprint
            av.isSprinting = !!buttons[10];

            // D-Pad (12, 13, 14, 15)
            let dpadMoveX = 0;
            let dpadMoveY = 0;
            if (buttons[12]) dpadMoveY -= 1; // Up
            if (buttons[13]) dpadMoveY += 1; // Down
            if (buttons[14]) dpadMoveX -= 1; // Left
            if (buttons[15]) dpadMoveX += 1; // Right

            if (dpadMoveX !== 0 || dpadMoveY !== 0) {{
                av.vx = dpadMoveX * 5.0;
                av.vy = dpadMoveY * 5.0;
            }}

            // Gatillos LT (6) / RT (7): Cambio de Color
            if (buttons[6]) av.color = "#38bdf8";
            if (buttons[7]) av.color = "#ff2a85";
            if (buttons[4]) av.color = "#00ffc8";
            if (buttons[5]) av.color = "#f59e0b";
        }};

        // Botones del HUD de Telemetría
        document.addEventListener("DOMContentLoaded", () => {{
            const toggleBtn = document.getElementById("tel-toggle-btn");
            const box = document.getElementById("telemetry-hud-box");
            const clearBtn = document.getElementById("tel-clear-btn");
            const resetBtn = document.getElementById("tel-reset-avatar-btn");

            if (toggleBtn && box) {{
                toggleBtn.addEventListener("click", () => {{
                    box.classList.toggle("collapsed");
                    document.getElementById("tel-collapse-icon").textContent = box.classList.contains("collapsed") ? "▲ EXPANDIR" : "▼ COLAPSAR";
                }});
            }}
            if (clearBtn) {{
                clearBtn.addEventListener("click", () => {{
                    fetch("/api/clear_log", {{ method: "POST" }}).then(() => {{
                        document.getElementById("tel-stream-list").innerHTML = '<div class="tel-log-item highlight">[REGISTRO LIMPIADO]</div>';
                    }});
                }});
            }}
            if (resetBtn) {{
                resetBtn.addEventListener("click", () => {{
                    state.avatar.x = 1260;
                    state.avatar.y = 280;
                    state.avatar.vx = 0;
                    state.avatar.vy = 0;
                    state.window.x = 460;
                    state.window.y = 110;
                    recordTelemetry("RESET_ALL", {{ x: 960, y: 540 }}, "UI", "Reset", "Avatar y ventana centrados");
                }});
            }}
        }});
    }})();
    </script>

    <!-- INYECCIÓN DEL CÓDIGO DE PRODUCCIÓN (HUD, MANDOS TAK, TECLADO Y TRACKPAD) -->
    {hud_code}

    <!-- PUENTE DE TELEMETRÍA Y REGISTRO DE DESLIZAMIENTO FÍSICO CONTINUO -->
    <script>
    (function() {{
        // Conectar emitGamepadState para que mueva el Avatar localmente
        setInterval(() => {{
            if (typeof gpAxesState !== "undefined" && typeof gpButtonsState !== "undefined") {{
                if (window.updateAvatarFromGamepad) {{
                    window.updateAvatarFromGamepad(gpAxesState, gpButtonsState);
                }}
            }}
        }}, 16);

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
    print(f"🚀 Laboratorio de Pruebas v2 iniciado en http://localhost:{PORT}")
    print(f"📄 Guardando telemetría en vivo en: {LOG_FILE}")
    sys.stdout.flush()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        httpd.server_close()

if __name__ == "__main__":
    main()
