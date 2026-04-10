from pyrogram import Client, filters, types, idle
from dotenv import load_dotenv
import os,sys, asyncio
import yt_dlp
import time

rutas={}

last_update_time = 0

# Carga los valores del archivo .env
load_dotenv()
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
bot_token = os.getenv('bot_token')
valid_users = os.getenv('valid_users').split(",")
superuser = os.getenv('superuser')

app = Client("video_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Función que yt-dlp llamará durante la descarga
def progress_hook(d, context, chat_id, status_msg_id):
    if d['status'] == 'downloading':
        # Calculamos el porcentaje
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)

        if total_bytes:
            percentage = (downloaded_bytes / total_bytes) * 100
            # Creamos una barra visual sencilla
            bar_length = 10
            filled_length = int(bar_length * percentage // 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)

            progress_text = f"Descargando: {percentage:.1f}%\n[{bar}]"

            # Verificamos si han pasado al menos 30 segundos desde la última actualización
            global last_update_time
            if time.time() - last_update_time > 15:
                last_update_time = time.time()
                # Intentamos actualizar el mensaje de Telegram
                # Nota: Usamos loop.create_task porque el hook corre en un hilo aparte
                try:
                    loop = asyncio.get_event_loop()
                    # Para evitar el baneo por spam, podrías añadir un control de tiempo aquí
                    loop.create_task(context.edit_message_text(
                        chat_id=chat_id,
                        message_id=status_msg_id,
                        text=progress_text
                    ))
                except Exception:
                    pass # Ignoramos errores si el mensaje no ha cambiado o hay spam limit

# Manejador de inicio
@app.on_message(filters.command("start"))
async def start(client, message):
    if valid_users and str(message.from_user.id) not in valid_users:
        await message.reply("❌ No tienes permiso para usar este bot.")
        return
    await message.reply(
        "👋 ¡Hola! Soy un bot que descarga vídeos, dime la url del vídeo."
    )

# Manejador de fin para parar el bot
@app.on_message(filters.command("stop"))
async def stop(client, message):
    if str(message.from_user.id) != superuser:
        await message.reply("❌ No tienes permiso para realizar esta acción.")
        return
    await message.reply("👋 ¡Adiós! El bot se ha detenido.")
    # Detiene el cliente de Pyrogram
    sys.exit(0)

# Manejador de mensajes para recibir URLs
@app.on_message(filters.text & ~filters.command(["start", "stop"]))
async def handle_message(client, message):
    if valid_users and str(message.from_user.id) not in valid_users:
        await message.reply("❌ No tienes permiso para usar este bot.")
        return
    url = message.text.strip()
    print(f"Usuario {message.from_user.id} ha enviado la URL: {url}")
    # Aquí puedes agregar la lógica para procesar la URL y descargar el vídeo
    await message.reply(f"Recibí tu URL: {url}", disable_web_page_preview = True)
    message_status = await app.send_message(message.chat.id, "Descargando ...")

    filename=""
    try:
        """Descarga el video usando yt-dlp y devuelve el nombre del archivo."""
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Preferimos MP4 para compatibilidad directa
            'outtmpl': 'video_descargado.%(ext)s',
            'max_filesize': 1900 * 1024 * 1024, # Límite de 1900 MB
            'progress_hooks': [lambda d: progress_hook(d, app, message.chat.id, message_status.id)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        try:
            await client.edit_message_text(message.chat.id, message_status.id, text="Subiendo el vídeo a Telegram...")
        except Exception:
            pass # Ignoramos errores de edición, el mensaje podría haber sido eliminado o no actualizado
        await client.send_video(message.chat.id, filename, caption=f"{info.get('title', 'Sin título')}")
    except Exception as e:
        print(f"Error al descargar el vídeo: {e}")
        await message.reply("❌ Ocurrió un error al descargar el vídeo. Asegúrate de que la URL es válida y el vídeo no supera los 1900 MB.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)


async def start_bot():
    await app.start()

    try:
        await app.send_message(chat_id=superuser, text="El bot de descargas de vídeos ha iniciado correctamente.")
    except Exception as e:
        print(f"Error al enviar mensaje de inicio: {e}")
    await idle()
    # await app.stop()

app.run(start_bot())
