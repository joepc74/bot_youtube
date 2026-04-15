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
superuser,superuserid = os.getenv('superuser').split(",")

app = Client("video_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

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
    if str(message.from_user.id) != superuserid:
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
            'outtmpl': 'video.%(ext)s',
            'max_filesize': 1900 * 1024 * 1024, # Límite de 1900 MB
        }
        # si existe el archivo de cookies, lo añadimos a las opciones de yt-dlp para manejar sesiones autenticadas
        if os.path.exists("cookie.txt"):
            ydl_opts['cookies'] = 'cookie.txt'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        await client.edit_message_text(message.chat.id, message_status.id, text="Subiendo el vídeo a Telegram...")
        await client.send_video(message.chat.id, filename, caption=f"{info.get('title', 'Sin título')}")
        await client.delete_messages(message.chat.id, message_status.id)
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

if __name__ == "__main__":
    if os.path.exists("video.mp4"):
        os.remove("video.mp4")
    app.run(start_bot())
