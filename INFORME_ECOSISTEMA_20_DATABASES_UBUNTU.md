# 🐧 REPORTE OFICIAL: ECOSISTEMA DE 20 DATABASES MODULARES UBUNTU (2,000 GB)

Este documento detalla la arquitectura modular oficial del ecosistema de **Ubuntu Cloud PC**. Cada base de datos está diseñada como un cartucho independiente de hasta 100GB que se puede conectar o descargar a demanda con 1 solo clic desde el escritorio, sin tocar ni saturar el límite de 20GB local.

---

## 📋 ESTADO GENERAL DEL CATÁLOGO DE 20 DATABASES

| # | Nombre de la Database | Slug Oficial | Categoría | Estado Actual |
| :-: | :--- | :--- | :--- | :---: |
| **1** | **Ubuntu - Core Desktop & Social Hub** | `ubuntu-core-os-social` | **Sistema Base & Redes** | **[✅ HECHO / LISTO]** |
| **2** | **Ubuntu - Emuladores PS2 & PS1** | `ubuntu-ps2-ps1-vault` | **Gaming Retro** | **[⚙️ EN COMPILACIÓN / LISTO]** |
| **3** | **Ubuntu - Emuladores PSP & Nintendo DS/GBA** | `ubuntu-psp-ds-gba-vault` | Gaming Portátil | [⏳ Planificado] |
| **4** | **Ubuntu - Emuladores Switch & Wii/GameCube** | `ubuntu-switch-wii-vault` | Gaming Nintendo | [⏳ Planificado] |
| **5** | **Ubuntu - Arcade Retro & Clásicos** | `ubuntu-arcade-retro-classics` | Gaming Arcade | [⏳ Planificado] |
| **6** | **Ubuntu - PC Gaming & Launchers** | `ubuntu-pc-gaming-launchers` | PC Gaming | [⏳ Planificado] |
| **7** | **Ubuntu - 3D Avatar & VTuber Studio** | `ubuntu-3d-avatar-studio` | Creadores & 3D | [⏳ Planificado] |
| **8** | **Ubuntu - Suite Streamer OBS Pro** | `ubuntu-streamer-obs-pro` | Streaming & Video | [⏳ Planificado] |
| **9** | **Ubuntu - Diseño Gráfico & Ilustración** | `ubuntu-graphic-design-art` | Arte 2D | [⏳ Planificado] |
| **10** | **Ubuntu - Modelado 3D Blender & VFX** | `ubuntu-3d-blender-vfx` | 3D & VFX | [⏳ Planificado] |
| **11** | **Ubuntu - Cerebro IA Ollama & Llama** | `ubuntu-ai-brains-ollama` | Inteligencia Artificial | [⏳ Planificado] |
| **12** | **Ubuntu - Laboratorio de Voz & Audio IA** | `ubuntu-ai-voice-audio-lab` | Inteligencia Artificial | [⏳ Planificado] |
| **13** | **Ubuntu - Generador de Arte ComfyUI SDXL** | `ubuntu-ai-image-comfyui` | Inteligencia Artificial | [⏳ Planificado] |
| **14** | **Ubuntu - Producción Musical LMMS Studio** | `ubuntu-music-audio-studio` | Música & Audio | [⏳ Planificado] |
| **15** | **Ubuntu - Suite Desarrollador & VSCode** | `ubuntu-developer-code-hub` | Programación | [⏳ Planificado] |
| **16** | **Ubuntu - Laboratorio Ciberseguridad Pentesting** | `ubuntu-cybersecurity-lab` | Seguridad & Redes | [⏳ Planificado] |
| **17** | **Ubuntu - Trading Cripto & Finanzas** | `ubuntu-crypto-trading-desk` | Finanzas & Cripto | [⏳ Planificado] |
| **18** | **Ubuntu - Universidad & Ciencia Hub** | `ubuntu-student-university-hub` | Educación & Ciencia | [⏳ Planificado] |
| **19** | **Ubuntu - Anime Manga & Entretenimiento** | `ubuntu-anime-manga-media` | Entretenimiento | [⏳ Planificado] |
| **20** | **Ubuntu - Herramientas de Rescate & Diagnóstico** | `ubuntu-sysadmin-rescue-tools` | Mantenimiento | [⏳ Planificado] |

---

## 🔍 DETALLE TÉCNICO DE CADA DATABASE

---

### 🌟 DATABASE 1: `Ubuntu - Core Desktop & Social Hub` **[✅ HECHO / LISTO]**
* **Slug:** `ubuntu-core-os-social`
* **Tamaño:** ~1.2 GB
* **Tiempo de Arranque:** **< 10 segundos**
* **Propósito:** El sistema operativo base limpio, universal y sin marcas de avatares. Todo usuario o cliente arranca desde aquí.
* **Contenido Completo:**
  - **Entorno Gráfico:** XFCE 4.18 optimizado con tema oscuro oficial Ubuntu Yaru-Dark e iconos Papirus.
  - **Servidor VNC & noVNC:** Puerto 5900 (TCP binario) y Puerto 6080 (Web) con **Motor de Trackpad Táctil de Laptop integrado** (deslizar dedo para mover el ratón).
  - **Servidor Sunshine (Moonlight):** Streaming H.264/HEVC acelerado por hardware GPU a 60/120 FPS.
  - **Redes Sociales & Comunicación:**
    - **Discord:** Cliente oficial para llamadas y comunidades.
    - **Telegram Desktop:** Mensajería instantánea y canales.
    - **WhatsApp Web (PWA):** Acceso directo como app nativa.
    - **Spotify & YouTube Music (PWA):** Música en segundo plano.
    - **Twitter / X & Instagram (PWA):** Redes sociales con ventana independiente.
    - **Google Meet & Zoom:** Videollamadas y reuniones.
    - **Google Chrome Oficial:** Navegador con aceleración GPU.
  - **Productividad & Utilidades Diarias:**
    - **Flameshot:** Capturas de pantalla profesionales con flechas, texto y pixelado.
    - **CopyQ:** Historial avanzado de portapapeles.
    - **LibreOffice Suite:** Writer (Word), Calc (Excel), Impress (PowerPoint).
    - **Evince / Xreader:** Visor ligero de PDFs y documentos.
    - **PeaZip / 7-Zip / Unrar:** Gestor total de archivos comprimidos.
    - **qBittorrent:** Descargas P2P ultrarrápidas a tus 5TB de Google Drive.
    - **VLC Media Player:** Reproductor multimedia con códecs universales.
    - **FileZilla:** Cliente FTP/SFTP.
    - **Google Drive 5TB FUSE:** Montaje automático en `/root/gdrive/PC_Kaggle`.
  - **Control, Móvil & Calidad de Vida:**
    - **Onboard:** Teclado virtual en pantalla para escribir desde móviles y tablets.
    - **AntiMicroX:** Calibrador y mapeador de mandos y controles Bluetooth/USB.
    - **Pavucontrol:** Mezclador de audio profesional para regular volúmenes independientes.
    - **Redshift:** Filtro de luz azul y modo noche para cuidar la vista.
  - **Centro de Software 1-Clic:** Acceso directo en el escritorio para instalar cualquiera de los otros 19 módulos con 1 clic.

---

### 🕹️ DATABASE 2: `Ubuntu - Emuladores PS2 & PS1` **[⚙️ EN COMPILACIÓN / LISTO]**
* **Slug:** `ubuntu-ps2-ps1-vault` | **Capacidad:** 100 GB
* **Propósito:** Consola PlayStation 2 y PlayStation 1 definitiva con resolución escalada a 1080p 60FPS, BIOS oficiales completas, Memory Cards 100% y catálogo curado en formato ultra-comprimido CHD/PBP.
* **Emuladores & Mejoras Gráficas:**
  - **PCSX2 (Qt 64-bit v2.0):** Emulador oficial de PS2 con renderizado Vulkan/OpenGL, reescalado interno 1080p/4K, filtro anisotrópico 16x y parches panorámicos 16:9 automáticos.
  - **DuckStation (PS1 PGXP HD):** Emulador de PS1 con eliminación total de temblores poligonales (PGXP Geometry Correction), texturas suavizadas y audio sincronizado.
  - **Pack Maestro de BIOS Oficiales:** SCPH-70012 (USA), SCPH-70004 (EUR), SCPH-70000 (JAP), SCPH-1001 y SCPH-5501.
  - **Memory Cards Virtuales:** Tarjetas de 8MB y 128KB con partidas completadas al 100% para desbloquear todos los personajes y pistas.
  - **Compatibilidad de Mandos:** Perfiles preconfigurados para mandos de PS4, PS5, Xbox One/Series y genéricos USB/Bluetooth.
* **Catálogo de Juegos de PlayStation 2 (Formato CHD/ISO):**
  - *Dragon Ball Z: Budokai Tenkaichi 3 (Versión Latino con voces en español)*
  - *God of War (1 & 2)*
  - *Grand Theft Auto: San Andreas & Vice City*
  - *Def Jam: Fight for NY*
  - *Resident Evil 4 & Silent Hill 2*
  - *Need for Speed: Underground 2 & Most Wanted (Black Edition)*
  - *Black & Shadow of the Colossus*
  - *Devil May Cry 3: Dante's Awakening (Special Edition)*
  - *Mortal Kombat: Shaolin Monks & Tekken 5*
  - *Bully (Canis Canem Edit) & Burnout 3: Takedown*
  - *Kingdom Hearts II & Naruto Shippuden: Ultimate Ninja 5*
  - *Marvel vs Capcom 2*
* **Catálogo de Juegos de PlayStation 1 (Formato CHD/PBP):**
  - *Crash Bandicoot 1, 2, 3 Warped & Crash Team Racing (CTR)*
  - *Resident Evil 1, 2 & 3 Nemesis*
  - *Silent Hill & Metal Gear Solid*
  - *Castlevania: Symphony of the Night & Tekken 3*
  - *Pepsiman, Gran Turismo 2 & Dino Crisis 2*
  - *Yu-Gi-Oh! Forbidden Memories (Mod 15 Drop)*
  - *Jackie Chan Stuntmaster & Tony Hawk's Pro Skater 2*
  - *Spider-Man (2000) & Marvel Super Heroes vs Street Fighter*
* **Activación 1-Clic (`setup.py`):**
  - Al conectarse a Kaggle o descargarse desde el escritorio, crea automáticamente los accesos directos:
    - `🎮 PlayStation 2 (PCSX2 1080p HD).desktop`
    - `🎮 PlayStation 1 (DuckStation PGXP).desktop`
    - `📂 Carpeta de Juegos PS2 & PS1 (ROMs).desktop`

---

### 📱 DATABASE 3: `Ubuntu - Emuladores PSP & Nintendo DS/GBA`
* **Slug:** `ubuntu-psp-ds-gba-vault` | **Capacidad:** 100 GB
* **Propósito:** Bóveda de consolas portátiles retro con más de 200 títulos legendarios.
* **Contenido:**
  - **PPSSPP (PSP):** Escalado a 4K con texturas HD.
  - **melonDS & DeSmuME (Nintendo DS):** Soporte de doble pantalla táctil.
  - **mGBA (Game Boy Advance):** Emulación perfecta a 60 FPS.
  - **Colección de Juegos:** *God of War Ghost of Sparta, Tekken 6, Monster Hunter Freedom Unite, Saga Pokémon (Esmeralda, FuegoRojo, Blanco/Negro, HeartGold), Castlevania Aria of Sorrow, GTA Vice City Stories.*

---

### 🍄 DATABASE 4: `Ubuntu - Emuladores Switch & Wii/GameCube`
* **Slug:** `ubuntu-switch-wii-vault` | **Capacidad:** 100 GB
* **Propósito:** Emulación de consolas modernas y clásicas de Nintendo.
* **Contenido:**
  - **Dolphin Emulator (GameCube & Wii):** Soporte de mandos clásicos y Wiimote emulado.
  - **Ryujinx (Nintendo Switch):** Con soporte para Vulkan en las GPUs NVIDIA Tesla T4.
  - **Colección de Juegos:** *Super Smash Bros Melee, Mario Kart Wii, Zelda Twilight Princess, Super Mario Odyssey, Mario Party, Metroid Prime, Animal Crossing.*

---

### 👾 DATABASE 5: `Ubuntu - Arcade Retro & Clásicos`
* **Slug:** `ubuntu-arcade-retro-classics` | **Capacidad:** 100 GB
* **Propósito:** La sala arcade de los años 90 y 2000 en tu bolsillo con más de 1,500 juegos.
* **Contenido:**
  - **MAME & FinalBurn Neo (Arcade):** *The King of Fighters 98/2002, Metal Slug 1 al X, Street Fighter III 3rd Strike, Cadillacs and Dinosaurs, Marvel vs Capcom.*
  - **RetroArch:** Núcleos de SNES (*Super Mario World, Chrono Trigger*), Sega Genesis (*Sonic 3*), NeoGeo y NES.

---

### 🏆 DATABASE 6: `Ubuntu - PC Gaming & Launchers`
* **Slug:** `ubuntu-pc-gaming-launchers` | **Capacidad:** 100 GB
* **Propósito:** Plataforma integral para jugar títulos de PC nativos de Steam y Epic Games.
* **Contenido:**
  - **Steam Oficial:** Pre-configurado con Proton-GE para máxima compatibilidad de juegos de Windows en Linux.
  - **Heroic Games Launcher:** Acceso directo a tu biblioteca de Epic Games Store y GOG.
  - **Lutris:** Instalador universal de juegos independientes.
  - **GameMode & MangoHud:** Optimizador de rendimiento de CPU y overlay de FPS en pantalla.

---

### 🌸 DATABASE 7: `Ubuntu - 3D Avatar & VTuber Studio`
* **Slug:** `ubuntu-3d-avatar-studio` | **Capacidad:** 100 GB
* **Propósito:** El estudio completo de VTubers y creadores de avatares 3D (extraído de la base para que cada usuario use el modelo que quiera).
* **Contenido:**
  - **VRoid Studio Oficial:** Para diseñar, vestir y exportar avatares 3D estilo anime en formato `.vrm`.
  - **VSeeFace & OpenSeeFace:** Software de tracking facial por cámara web para mover el avatar en vivo.
  - **Colección de 50+ Modelos VRM:** Avatares masculinos, femeninos y fantásticos listos para transmitir.
  - **Panel Web de Control 3D:** Renderizador WebGL en pantalla para interactuar en tiempo real.

---

### 🎬 DATABASE 8: `Ubuntu - Suite Streamer OBS Pro`
* **Slug:** `ubuntu-streamer-obs-pro` | **Capacidad:** 100 GB
* **Propósito:** Estudio de transmisión y grabación profesional para Twitch, Kick, YouTube y TikTok.
* **Contenido:**
  - **OBS Studio:** Con plugins avanzados (*Move Transition, StreamElements, DroidCam, V4L2loopback virtual cam*).
  - **Kdenlive & Shotcut:** Editores de video multipista con efectos de corte rápido y renderizado por GPU.
  - **Paquete de Overlays & Alertas:** Pantallas de "Iniciando Stream", "Ya volvemos" y marcos de cámara.
  - **Bóveda de 1,000+ Pistas de Música sin Copyright (DMCA Safe).**

---

### 🖌️ DATABASE 9: `Ubuntu - Diseño Gráfico & Ilustración`
* **Slug:** `ubuntu-graphic-design-art` | **Capacidad:** 100 GB
* **Propósito:** Suite creativa de ilustración digital, diseño vectorial y retoque fotográfico.
* **Contenido:**
  - **GIMP Studio:** Con interfaz y atajos estilo Photoshop + 2,000 pinceles de pintura digital.
  - **Krita Pro:** El estándar mundial de dibujo e ilustración digital y animación 2D cuadro por cuadro.
  - **Inkscape:** Editor de gráficos vectoriales (alternativa a Adobe Illustrator).
  - **Colección de 3,000+ Fuentes Tipográficas:** Tipografías para cartelería, logos y miniaturas.

---

### 🏛️ DATABASE 10: `Ubuntu - Modelado 3D Blender & VFX`
* **Slug:** `ubuntu-3d-blender-vfx` | **Capacidad:** 100 GB
* **Propósito:** Estudio de renderizado 3D, animación, arquitectura y efectos visuales.
* **Contenido:**
  - **Blender 4.x:** Con aceleración OptiX y CUDA activadas en las GPUs NVIDIA Tesla T4.
  - **FreeCAD:** Modelado paramétrico para ingeniería y diseño de piezas mecánicas.
  - **MeshLab:** Procesamiento y limpieza de mallas 3D y escaneos.
  - **Bóveda de Texturas PBR 4K & Materiales:** Madera, metal, piedra, piel y luces HDRI.

---

### 🤖 DATABASE 11: `Ubuntu - Cerebro IA Ollama & Llama`
* **Slug:** `ubuntu-ai-brains-ollama` | **Capacidad:** 100 GB
* **Propósito:** Modelos de lenguaje masivo (LLMs) ejecutados de forma local sin conexión a internet y 100% gratuitos.
* **Contenido:**
  - **Ollama Engine:** Servidor de inferencia ultrarrápido para GPUs Tesla T4.
  - **Modelos Cuantizados Incluidos:**
    - `Gemma 2 9B` (El potente modelo de Google).
    - `Llama 3.1 8B` (El modelo insignia de Meta).
    - `Mistral Nemo 12B` (Especializado en razonamiento y conversación).
    - `DeepSeek Coder 6.7B` (Asistente de programación y desarrollo de código).
  - **Open-WebUI:** Interfaz web idéntica a ChatGPT para chatear con los modelos en privado.

---

### 🎙️ DATABASE 12: `Ubuntu - Laboratorio de Voz & Audio IA`
* **Slug:** `ubuntu-ai-voice-audio-lab` | **Capacidad:** 100 GB
* **Propósito:** Síntesis de voz ultra-realista, clonación de voces y reconocimiento de audio.
* **Contenido:**
  - **Whisper Large-v3 (OpenAI):** Transcripción de audio y voz en tiempo real con precisión del 99%.
  - **Kokoro-TTS & XTTS-v2:** Generación de voz humana femenina/masculina con entonación natural y emociones.
  - **RVC (Retrieval-based Voice Conversion):** Modificador de voz en tiempo real para hablar con voz de personajes de anime o celebridades por micrófono.

---

### 🎨 DATABASE 13: `Ubuntu - Generador de Arte ComfyUI SDXL`
* **Slug:** `ubuntu-ai-image-comfyui` | **Capacidad:** 100 GB
* **Propósito:** Generación de imágenes y arte digital por Inteligencia Artificial con aceleración GPU.
* **Contenido:**
  - **ComfyUI & Automatic1111:** Interfaces profesionales basadas en nodos para Stable Diffusion.
  - **Modelos SDXL:** Checkpoints de estilo anime, fotorrealismo, arte conceptual y 3D.
  - **ControlNet & LoRAs:** Para controlar poses exactas, manos perfectas y estilos artísticos.

---

### 🎵 DATABASE 14: `Ubuntu - Producción Musical LMMS Studio`
* **Slug:** `ubuntu-music-audio-studio` | **Capacidad:** 100 GB
* **Propósito:** Estación de trabajo de audio digital (DAW) para compositores y productores de música.
* **Contenido:**
  - **LMMS (Linux MultiMedia Studio):** Alternativa completa a FL Studio con sintetizadores y secuenciador de ritmos.
  - **Audacity:** Editor de ondas de audio con suite completa de efectos VST.
  - **Ardour DAW:** Grabación multipista profesional para bandas e instrumentos reales.
  - **Soundfonts & Sample Packs:** Miles de sonidos de baterías, bajos, pianos y sintetizadores Synthwave/Lo-Fi.

---

### 💻 DATABASE 15: `Ubuntu - Suite Desarrollador & VSCode`
* **Slug:** `ubuntu-developer-code-hub` | **Capacidad:** 100 GB
* **Propósito:** Entorno integral para programadores de software, web, IA y aplicaciones móviles.
* **Contenido:**
  - **Visual Studio Code:** Pre-configurado con extensiones de Python, JavaScript, TypeScript, Go, Rust, C++ y Docker.
  - **Runtimes:** Python 3.10/3.12, Node.js 20 LTS, Go, Rust (cargo), GCC/G++.
  - **Herramientas de Datos:** DBeaver (Cliente gráfico para PostgreSQL, MySQL, SQLite, MongoDB), Postman (Pruebas de API REST).
  - **GitKraken & Lazygit:** Control de versiones gráfico.

---

### 🛡️ DATABASE 16: `Ubuntu - Laboratorio Ciberseguridad Pentesting`
* **Slug:** `ubuntu-cybersecurity-lab` | **Capacidad:** 100 GB
* **Propósito:** Laboratorio de auditoría de seguridad informática y hacking ético.
* **Contenido:**
  - **Análisis de Red:** Wireshark, Nmap, Zenmap, TCPdump.
  - **Auditoría Web:** Burp Suite Community Edition, OWASP ZAP, Nikto.
  - **Ingeniería Inversa:** Ghidra (Herramienta de la NSA para desensamblar binarios), Radare2, GDB.
  - **Fuerza Bruta & Auditoría:** Metasploit Framework, John the Ripper, Hashcat con soporte CUDA.

---

### 📈 DATABASE 17: `Ubuntu - Trading Cripto & Finanzas`
* **Slug:** `ubuntu-crypto-trading-desk` | **Capacidad:** 100 GB
* **Propósito:** Estación de trading financiero, seguimiento de mercados y gestión de carteras de criptomonedas.
* **Contenido:**
  - **TradingView Desktop:** Plataforma de análisis técnico con gráficos en tiempo real.
  - **Carteras Frías de Cripto:** Electrum (Bitcoin), Sparrow Wallet, Monero GUI.
  - **Herramientas de Análisis:** Librerías de Python (*ccxt, pandas_ta, backtrader*) para crear y probar bots de trading algorítmico.

---

### 🎓 DATABASE 18: `Ubuntu - Universidad & Ciencia Hub`
* **Slug:** `ubuntu-student-university-hub` | **Capacidad:** 100 GB
* **Propósito:** Centro de herramientas académicas para estudiantes universitarios, científicos e investigadores.
* **Contenido:**
  - **Anki:** Software de repetición espaciada con tarjetas de memoria para medicina, leyes e idiomas.
  - **GNU Octave:** Entorno de cálculo numérico y matrices (compatible con scripts de MATLAB).
  - **GeoGebra:** Geometría dinámica, álgebra y cálculo visual.
  - **Zotero:** Gestor de bibliografía y citas para tesis y artículos científicos.
  - **TeXstudio & Kile:** Editores profesionales de documentos LaTeX.
  - **Calibre:** Biblioteca y lector de libros electrónicos (EPUB, PDF, MOBI).

---

### ⛩️ DATABASE 19: `Ubuntu - Anime Manga & Entretenimiento`
* **Slug:** `ubuntu-anime-manga-media` | **Capacidad:** 100 GB
* **Propósito:** Mediateca multimedia de entretenimiento, cine y lectura de cómics/manga.
* **Contenido:**
  - **Stremio:** Cine y series en streaming 1080p/4K con subtítulos automáticos.
  - **Mihon / Tachiyomi Desktop:** Lector de manga, manhua y cómics con descarga para lectura offline.
  - **Aniyomi:** Reproductor especializado de anime con sincronización de listas (MyAnimeList / AniList).
  - **Kodi Media Center:** Centro multimedia completo para TV y música.

---

### 🔧 DATABASE 20: `Ubuntu - Herramientas de Rescate & Diagnóstico`
* **Slug:** `ubuntu-sysadmin-rescue-tools` | **Capacidad:** 100 GB
* **Propósito:** Herramientas de administración de sistemas, recuperación de datos y diagnóstico profundo.
* **Contenido:**
  - **GParted:** Gestor visual de particiones y discos.
  - **TestDisk & PhotoRec:** Recuperación de archivos y particiones borradas por accidente.
  - **Rclone Browser / GUI:** Gestor gráfico para transferir archivos entre Google Drive, Dropbox, OneDrive y Mega.
  - **Monitores de Rendimiento:** HTop, Glances, NVTop (Monitoreo de GPUs NVIDIA), IOTop (Velocidad de disco).

---

## 🖱️ CÓMO FUNCIONA EL CENTRO DE SOFTWARE 1-CLIC EN EL ESCRITORIO

En el escritorio de Ubuntu aparecerá el ícono **`🛍️ Centro de Software Ubuntu (1-Clic)`**:

1. **Doble Clic:** El usuario hace doble clic en el ícono del escritorio.
2. **Menú Visual:** Se abre una ventana limpia con las categorías (Gaming, IA, 3D, Programación, etc.).
3. **Activación Inteligente:**
   - Si el Dataset ya está conectado a Kaggle, se activa en **1 segundo**.
   - Si no está conectado, el script lo descarga en segundo plano a la carpeta `/tmp` con una barra gráfica de progreso.
4. **Cero Límite de 20GB:** Toda descarga se aloja en `/tmp` (más de 1,000 GB libres), dejando el disco de 20GB intacto.

---

## 🚀 RESUMEN Y PRÓXIMOS PASOS

1. **Dataset 1 (`ubuntu-core-os-social`)** ha sido desvinculado de marcas de avatares y queda listo como el **Sistema Base Universal** con arranque de 10 segundos.
2. Cada database futura comenzará estrictamente con el nombre **`Ubuntu - [Categoría]`**.
3. El archivo `ubuntu_store.py` ya está listo en el repositorio para servir como el motor de descarga y activación de los 19 módulos adicionales.
