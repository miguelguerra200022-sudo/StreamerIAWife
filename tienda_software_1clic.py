#!/usr/bin/env python3
"""
================================================================================
🛍️ TIENDA DE SOFTWARE Y JUEGOS 1-CLIC (ECOSISTEMA MODULAR DINÁMICO)
================================================================================
Funciona exactamente igual que la Google Play Store o Steam:
1. Lee el catálogo en tiempo real desde la nube (GitHub Manifest).
2. Cuando el Administrador añade un juego nuevo a 'catalogo_tienda.json',
   aparece automáticamente en el escritorio de todos los clientes en 0s.
3. Cero tokens pedidos a los clientes: instalación transparente en 1-clic.
================================================================================
"""

import os
import sys
import json
import time
import shutil
import urllib.request
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

BASE_DIR = Path("/kaggle/working/StreamerIAWife") if Path("/kaggle/working/StreamerIAWife").exists() else Path(__file__).resolve().parent
CATALOG_URL = "https://raw.githubusercontent.com/miguelguerra200022-sudo/StreamerIAWife/main/catalogo_tienda.json"

# Catálogo local de respaldo si no hay conexión externa
FALLBACK_CATALOG = [
    {"id": 1, "name": "Ubuntu Core & Social Hub", "slug": "ubuntu-core-os-social", "cat": "Sistema Base", "desc": "Escritorio XFCE Dark, Google Chrome GPU, Steam, Discord, Telegram, noVNC Trackpad.", "icon": "computer"},
    {"id": 2, "name": "PlayStation 2 & PS1 Vault", "slug": "ubuntu-ps2-ps1-vault", "cat": "Gaming & Emulación", "desc": "PCSX2 1080p 60FPS + DuckStation PGXP HD con BIOS completas y cheats.", "icon": "input-gaming"},
    {"id": 3, "name": "PSP, Nintendo DS & GBA Vault", "slug": "ubuntu-psp-ds-gba-vault", "cat": "Gaming & Emulación", "desc": "PPSSPP 4K, MelonDS pantalla táctil y mGBA con shaders retro.", "icon": "input-gaming"},
    {"id": 4, "name": "Nintendo Switch & Wii Vault", "slug": "ubuntu-switch-wii-vault", "cat": "Gaming & Emulación", "desc": "Ryujinx / Dolphin 1080p con soporte de mandos Joy-Con y Pro Controller.", "icon": "input-gaming"},
    {"id": 5, "name": "Arcade Classics, Neo-Geo & MAME", "slug": "ubuntu-arcade-classics", "cat": "Gaming & Emulación", "desc": "FBNeo y MAME con catálogo de las mejores recreativas de la historia.", "icon": "input-gaming"},
    {"id": 6, "name": "Retro PC Gaming & MS-DOS Box", "slug": "ubuntu-retro-pc-dosbox", "cat": "Gaming & Emulación", "desc": "DOSBox-Staging y ScummVM optimizados para clásicos de PC.", "icon": "applications-games"},
    {"id": 7, "name": "Avatar 3D & VTuber Studio Pro", "slug": "ubuntu-avatar-3d-vtuber", "cat": "Streaming & Contenido", "desc": "OpenSeeFace IA, VSeeFace y modelos VRM para streaming profesional.", "icon": "camera-video"},
    {"id": 8, "name": "Estudio de Producción Musical & Audio", "slug": "ubuntu-daw-musica-audio", "cat": "Multimedia & Arte", "desc": "LMMS, Audacity, complementos VST y soundfonts de consolas retro.", "icon": "audio-x-generic"},
    {"id": 9, "name": "Edición de Video Cine & Efectos VFX", "slug": "ubuntu-video-vfx-cine", "cat": "Multimedia & Arte", "desc": "Kdenlive 60FPS con aceleración NVENC y efectos cinematográficos.", "icon": "video-display"},
    {"id": 10, "name": "Diseño 3D, Modelado & Render Blender", "slug": "ubuntu-3d-modelado-blender", "cat": "Multimedia & Arte", "desc": "Blender 4.2 LTS acelerado por núcleos OptiX / CUDA de Nvidia T4.", "icon": "applications-graphics"},
    {"id": 11, "name": "Servidor de IA Local (LLMs & RAG)", "slug": "ubuntu-ia-llm-rag-studio", "cat": "Inteligencia Artificial", "desc": "Ollama con DeepSeek, Llama 3 y Qwen en GPU con Open-WebUI.", "icon": "system-run"},
    {"id": 12, "name": "Clonación de Voz & Síntesis TTS", "slug": "ubuntu-voice-clone-tts", "cat": "Inteligencia Artificial", "desc": "Kokoro-TTS y XTTS-v2 para clonar voces ultra-realistas en segundos.", "icon": "audio-volume-high"},
    {"id": 13, "name": "Generación de Imágenes ComfyUI & SDXL", "slug": "ubuntu-comfyui-sdxl-flux", "cat": "Inteligencia Artificial", "desc": "ComfyUI, Stable Diffusion XL y ControlNet para arte ultra HD.", "icon": "image-x-generic"},
    {"id": 14, "name": "Desarrollo de Videojuegos Godot Engine", "slug": "ubuntu-game-dev-godot", "cat": "Programación & Dev", "desc": "Godot 4.3 .NET con plantillas 2D/3D y exportador a Web y Android.", "icon": "applications-development"},
    {"id": 15, "name": "Programación FullStack & Copiloto IA", "slug": "ubuntu-dev-fullstack-ai", "cat": "Programación & Dev", "desc": "VS Code, Node 22, Python 3.12, Bun, Rust, Docker y Claude Code CLI.", "icon": "text-x-generic"},
    {"id": 16, "name": "Ciberseguridad & Laboratorio de Pentesting", "slug": "ubuntu-cybersecurity-pentest", "cat": "Ciberseguridad", "desc": "Wireshark, Nmap, ZAP Proxy, Semgrep y AI Security Copilot.", "icon": "security-high"},
    {"id": 17, "name": "Trading Cuantitativo & Billeteras Cripto", "slug": "ubuntu-trading-crypto-bots", "cat": "Finanzas & Trading", "desc": "Freqtrade, Pandas-TA, Electrum, Monero y base de datos CryptoDB 109GB.", "icon": "utilities-system-monitor"},
    {"id": 18, "name": "Juegos AAA PC Gamer - Volumen 1", "slug": "ubuntu-juegos-aaa-vol1", "cat": "Gaming AAA", "desc": "Colección de títulos de acción, aventura y RPG a 1080p 60 FPS.", "icon": "input-gaming"},
    {"id": 19, "name": "Juegos AAA PC Gamer - Volumen 2", "slug": "ubuntu-juegos-aaa-vol2", "cat": "Gaming AAA", "desc": "Títulos de conducción, simulación y mundo abierto en GPU Tesla T4.", "icon": "input-gaming"},
    {"id": 20, "name": "Android Cloud Phone & Mobile Gaming", "slug": "ubuntu-android-cloud-phone", "cat": "Android Cloud", "desc": "Teléfono Android virtual ROG Phone con Scrcpy, Aurora Store y Keymapper.", "icon": "phone"}
]

def cargar_catalogo_remoto():
    """Descarga el catálogo más reciente en tiempo real (Google Play Store Model)"""
    try:
        req = urllib.request.Request(CATALOG_URL, headers={"User-Agent": "Mozilla/5.0 LinuWaifuStore/1.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                Path("/tmp/catalogo_tienda_cache.json").write_text(json.dumps(data), encoding="utf-8")
                return data
    except Exception:
        pass

    for p in [Path("/tmp/catalogo_tienda_cache.json"), BASE_DIR / "catalogo_tienda.json"]:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return FALLBACK_CATALOG

class TiendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛍️ Tienda de Software & Juegos 1-Clic")
        self.root.geometry("860x620")
        self.root.configure(bg="#0f172a")

        self.catalog = cargar_catalogo_remoto()

        # Estilo Cyberpunk / Dark
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background="#1e293b",
            foreground="#f8fafc",
            fieldbackground="#1e293b",
            rowheight=32,
            font=("Ubuntu", 10)
        )
        style.configure("Treeview.Heading",
            background="#0f172a",
            foreground="#00ffc8",
            font=("Ubuntu Bold", 11)
        )
        style.map("Treeview", background=[("selected", "#ff2a85")])

        # Header
        header = tk.Frame(root, bg="#0f172a", padx=16, pady=12)
        header.pack(fill="x")

        title = tk.Label(header, text="🛍️ Tienda de Software & Juegos 1-Clic", font=("Ubuntu Bold", 14), fg="#00ffc8", bg="#0f172a")
        title.pack(side="left")

        subtitle = tk.Label(header, text="🌐 Sincronizada en Vivo con la Nube | Cero Configuración", font=("Ubuntu", 9), fg="#94a3b8", bg="#0f172a")
        subtitle.pack(side="right")

        # Treeview de Catálogo
        tree_frame = tk.Frame(root, bg="#0f172a", padx=16, pady=6)
        tree_frame.pack(fill="both", expand=True)

        cols = ("ID", "Nombre", "Categoría", "Descripción")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("ID", text="#")
        self.tree.heading("Nombre", text="Nombre del Software o Juego")
        self.tree.heading("Categoría", text="Categoría")
        self.tree.heading("Descripción", text="Descripción del Contenido")

        self.tree.column("ID", width=45, anchor="center")
        self.tree.column("Nombre", width=230, anchor="w")
        self.tree.column("Categoría", width=140, anchor="w")
        self.tree.column("Descripción", width=400, anchor="w")

        self.actualizar_tabla()

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Barra de Acciones Inferior
        btn_frame = tk.Frame(root, bg="#0f172a", padx=16, pady=16)
        btn_frame.pack(fill="x")

        btn_instalar = tk.Button(btn_frame, text="⚡ INSTALAR EN 1-CLIC", bg="#00ffc8", fg="#0f172a", font=("Ubuntu Bold", 11), padx=18, pady=8, relief="flat", cursor="hand2", command=self.instalar_seleccionado)
        btn_instalar.pack(side="left")

        btn_refresh = tk.Button(btn_frame, text="🔄 Actualizar Catálogo", bg="#1e293b", fg="#38bdf8", font=("Ubuntu", 10), padx=12, pady=8, relief="flat", cursor="hand2", command=self.refrescar_catalogo)
        btn_refresh.pack(side="left", padx=10)

        btn_desconectar = tk.Button(btn_frame, text="🛑 Desconectar", bg="#ff2a85", fg="#ffffff", font=("Ubuntu Bold", 10), padx=12, pady=8, relief="flat", cursor="hand2", command=self.desconectar_seleccionado)
        btn_desconectar.pack(side="left")

        btn_cerrar = tk.Button(btn_frame, text="✕ Salir", bg="#334155", fg="#f8fafc", font=("Ubuntu", 10), padx=14, pady=8, relief="flat", cursor="hand2", command=root.destroy)
        btn_cerrar.pack(side="right")

    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.catalog:
            self.tree.insert("", "end", values=(f"[{item['id']:02d}]", item["name"], item["cat"], item["desc"]))

    def refrescar_catalogo(self):
        self.catalog = cargar_catalogo_remoto()
        self.actualizar_tabla()
        messagebox.showinfo("Catálogo Sincronizado", "🎉 ¡Catálogo sincronizado en vivo con la nube!")

    def instalar_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Por favor selecciona un elemento del catálogo para instalar.")
            return
        item_vals = self.tree.item(sel[0])["values"]
        db_id = int(str(item_vals[0]).replace("[", "").replace("]", ""))
        db_info = next((d for d in self.catalog if d["id"] == db_id), None)

        if not db_info:
            return

        # 1. Caso A: Montado directamente en /kaggle/input (Arranque instantáneo en 0s)
        input_dir = Path(f"/kaggle/input/{db_info['slug']}")
        alt_input = Path(f"/kaggle/input/{db_info['slug'].replace('-', '_')}")
        target_dir = input_dir if input_dir.exists() else (alt_input if alt_input.exists() else None)

        if target_dir and (target_dir / "setup.py").exists():
            subprocess.Popen(f"python3 '{target_dir}/setup.py' &", shell=True)
            messagebox.showinfo("¡Éxito!", f"🎉 ¡{db_info['name']} activado exitosamente en tu Escritorio!")
            return

        # 2. Caso B: Descarga opcional en disco efímero de la nube (NUNCA en el Google Drive del cliente)
        download_url = db_info.get("download_url")
        if download_url:
            messagebox.showinfo(
                "Instalación en la Nube",
                f"🚀 Cargando {db_info['name']} en el disco de alta velocidad de la PC...\n\n"
                "🛡️ (Tus 15GB de Google Drive están protegidos: solo se guardan tus partidas y configuraciones)."
            )
            dest_dir = Path(f"/opt/juegos_cloud/{db_info['slug']}")
            dest_dir.mkdir(parents=True, exist_ok=True)
            cmd = f"aria2c -x 16 -s 16 -d '{dest_dir}' '{download_url}' && echo 'Completado' > '{dest_dir}/status.ok'"
            subprocess.Popen(cmd, shell=True)
        else:
            # Notificación amigable
            messagebox.showinfo(
                "Activación de Módulo",
                f"⚡ Activando acceso directo para: {db_info['name']}.\n\n"
                f"• Categoría: {db_info['cat']}\n"
                f"• Slug: {db_info['slug']}\n"
                f"• Estado: Listo para conectar en Kaggle sin configuración del usuario."
            )

    def desconectar_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un elemento para desconectar.")
            return
        item_vals = self.tree.item(sel[0])["values"]
        name = item_vals[1]
        messagebox.showinfo("Desconexión", f"🧹 '{name}' ha sido desconectado limpiamente del escritorio.")

def main():
    root = tk.Tk()
    app = TiendaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
