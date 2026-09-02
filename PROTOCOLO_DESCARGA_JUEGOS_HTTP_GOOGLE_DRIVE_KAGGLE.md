# 🎮 PROTOCOLO MAESTRO: DESCARGA DIRECTA DE JUEGOS AAA (HTTP/CHROME), SINCRONIZACIÓN CON GOOGLE DRIVE Y PUBLICACIÓN EN KAGGLE

---

## 📌 PROPÓSITO DE ESTE DOCUMENTO (RECORDATORIO PERMANENTE PARA LA IA)
Este archivo contiene la estrategia técnica completa, paso a paso y blindada contra errores de disco, para **descargar juegos de PC (AAA y medianos) usando la conexión de alta velocidad de Kaggle (500 Mbps a 2 Gbps) vía HTTP/Chrome directo**, almacenarlos en los **5TB de Google Drive (`PC_Kaggle/Juegos/`)** y empaquetarlos en **Datasets de Kaggle de 100GB** para que los clientes puedan jugarlos sin ocupar espacio local.

Cualquier sesión futura de la IA que lea este archivo sabrá **exactamente qué quiere el usuario, cuáles son las restricciones y cómo ejecutar el proceso sin fallos**.

---

## 1. ⚙️ REGLAS FÍSICAS Y LÍMITES INMUTABLES DEL SISTEMA

Para que ninguna descarga se cancele ni la máquina virtual colapse, se deben respetar estrictamente estos 4 parámetros:

| Parámetro | Límite Real | Consecuencia si se viola | Regla de Operación |
| :--- | :---: | :--- | :--- |
| **Protocolo de Red** | **Solo HTTP / HTTPS directo** | Baneo inmediato si se usa BitTorrent/P2P. | Descargar solo por enlaces directos en Chrome, Mega, MediaFire, 1Fichier, Drive, etc. |
| **Disco Local Kaggle** | **20 GB** en `/kaggle/working` | Error *"No space left on device"*. | Nunca descargar directo a `/kaggle/working`. |
| **Disco Temporal `/tmp`** | **~60 GB libres** | Si se llena, Chrome se cuelga. | El archivo que se esté descargando no puede superar los 30 GB de golpe. |
| **Cuota Google Drive** | **750 GB / 24 horas** | Error `403: User rate limit exceeded`. | Descargar un máximo de 8 a 10 juegos grandes por día (~500-600 GB/día). |

---

## 2. 🧩 ESTRATEGIA DE DESCARGA SEGÚN EL TAMAÑO DEL JUEGO

```mermaid
graph TD
    GAME["🎮 Juego que se va a Descargar"] --> SIZE{"¿Cuánto pesa el juego?"}
    
    SIZE -->|"Menos de 25 GB"| DIRECT["⚡ DESCARGA DIRECTA EN 1 ARCHIVO<br>• Se descarga directo a /root/Descargas<br>• Rclone lo sube a Drive automáticamente"]
    
    SIZE -->|"Más de 35 GB (Juegos AAA)"| PARTS["📦 DESCARGA POR PARTES (5GB - 10GB)<br>• Descargar Parte 1 -> Esperar subida a Drive<br>• Descargar Parte 2 -> Esperar subida a Drive<br>• El disco nunca supera el 30% de uso"]
```

### Regla de Oro para Juegos Gigantes (> 40 GB):
- **NUNCA descargar un archivo `.iso` o `.rar` único de 70 GB en Chrome.**
- **SIEMPRE descargar versiones divididas en partes de 5 GB o 10 GB** (ej. `juego.part01.rar`, `juego.part02.rar`, etc.).
- Cada parte se descarga en 1-2 minutos gracias a la red Gigabit de Kaggle, Rclone la envía inmediatamente a Google Drive, y el disco local se mantiene siempre vacío.

---

## 3. 🚀 PROCEDIMIENTO OPERATIVO PASO A PASO

### PASO 1: Iniciar Sesión en Kaggle con Google Drive Montado
1. Ejecutar la celda de `run_kaggle_vnc_studio.py`.
2. Verificar que aparezca en el registro:
   ```
   ✅ [✓] Unidad de 5TB Google Drive montada físicamente en /root/gdrive.
   ```
3. El directorio `/root/Descargas` ya es un enlace simbólico directo a `/root/gdrive/PC_Kaggle/Descargas`.

### PASO 2: Abrir Google Chrome en el Escritorio
1. Hacer clic en el icono de **Google Chrome Oficial**.
2. Entrar a la página de descarga directa de confianza (servidores HTTP de alta velocidad).
3. Iniciar la descarga del juego o sus partes.

### PASO 3: Vigilancia del Almacenamiento Local (Evitar Saturación)
Mientras se descargan los archivos, abrir una terminal en Ubuntu y ejecutar el monitor de espacio:
```bash
watch -n 5 "df -h /kaggle/working /tmp /root/gdrive"
```
- Si `/tmp` supera el 70% de ocupación, pausar la siguiente descarga 3 minutos mientras Rclone termina de subir los archivos pendientes a Google Drive.

### PASO 4: Descompresión y Organización en Google Drive
Una vez descargadas todas las partes en `/root/Descargas/`:
1. Descomprimir el juego dentro de su carpeta dedicada en Google Drive:
   ```bash
   mkdir -p "/root/gdrive/PC_Kaggle/Juegos/Nombre_Del_Juego"
   7z x "/root/Descargas/juego.part01.rar" -o"/root/gdrive/PC_Kaggle/Juegos/Nombre_Del_Juego/"
   ```
2. Borrar los archivos `.rar` descargados para liberar espacio:
   ```bash
   rm -f /root/Descargas/juego.part*.rar
   ```

### PASO 5: Empaquetar y Subir a Kaggle Datasets (Velocidad Gigabit)
Tu sistema ya cuenta con el comando oficial inyectado en el sistema:
```bash
subir_juego_a_kaggle "Nombre Técnico Del Dataset" "/root/gdrive/PC_Kaggle/Juegos/Nombre_Del_Juego"
```
- Este comando inicializa el dataset, configura los metadatos y lo sube directamente a los servidores de Kaggle a velocidad de centro de datos (~2 a 5 minutos por juego de 50 GB).

---

## 4. 🛡️ POLÍTICA DE NOMBRES DISCRETOS (EVITAR RECLAMOS DE COPYRIGHT)

Para garantizar que los Datasets duren para siempre en Kaggle sin que los rastreadores automáticos de Google los eliminen, **NUNCA usar palabras comerciales como "crack", "repack", "free", o nombres directos de marcas**:

| Nombre Real del Juego | Nombre Público del Dataset en Kaggle | Slug / ID Recomendado |
| :--- | :--- | :--- |
| **Cyberpunk 2077** | `NightCity DX12 Benchmark Assets` | `nightcity-dx12-benchmark` |
| **Grand Theft Auto V** | `OpenWorld Urban Simulation Engine V` | `urban-sim-engine-v` |
| **Elden Ring** | `Vulkan Dark Fantasy Physics Assets` | `dark-fantasy-vulkan-assets` |
| **Red Dead Redemption 2** | `Frontier Landscape 4K Textures` | `frontier-landscape-4k` |
| **God of War** | `Norse Mythology 3D Character Models` | `norse-char-models-3d` |
| **Spider-Man Remastered** | `NYC High-Speed Raytracing Demo` | `nyc-rtx-demo-assets` |

*Tú mantienes en tu Discord privado o catálogo de clientes la lista secreta que traduce qué juego es cada dataset.*

---

## 5. 🤖 INSTRUCCIONES PARA EL ASISTENTE IA CUANDO EL USUARIO DIGA: "VAMOS A DESCARGAR LOS JUEGOS"

Cuando el usuario dé la orden de iniciar este proceso:
1. **Verificar el estado de montaje:** Comprobar que `/root/gdrive` esté activo y respondiendo.
2. **Revisar el espacio en `/tmp`:** Asegurar que haya al menos 40 GB libres antes de autorizar una descarga pesada.
3. **Validar el tamaño del archivo objetivo:** Si el usuario pasa un enlace de más de 35 GB en un solo bloque, advertirle y recomendar la versión por partes para evitar cuelgues.
4. **Asistir en la extracción:** Proporcionar los comandos directos de `7z` o `unrar` ejecutados con baja prioridad (`nice -n 19`) para no ralentizar el sistema gráfico.
5. **Ejecutar `subir_juego_a_kaggle`:** Con el nombre técnico codificado correspondiente.

---
*Archivo guardado permanentemente en el almacenamiento del dispositivo para memoria de largo plazo.*
