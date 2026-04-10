# Bot de YouTube

Un bot de Telegram simple que permite descargar vídeos de YouTube y enviarlos directamente al chat.

## Descripción

Este bot utiliza la biblioteca `yt-dlp` para descargar vídeos de YouTube y `Pyrogram` para interactuar con Telegram. Solo usuarios autorizados pueden usar el bot, y hay un superusuario que puede detenerlo.

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/bot_youtube.git
   cd bot_youtube
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   api_id=TU_API_ID
   api_hash=TU_API_HASH
   bot_token=TU_BOT_TOKEN
   valid_users=ID_USUARIO1,ID_USUARIO2
   superuser=ID_SUPERUSUARIO
   ```

   - `api_id` y `api_hash`: Obténlos de [my.telegram.org](https://my.telegram.org).
   - `bot_token`: Crea un bot con [@BotFather](https://t.me/botfather) en Telegram.
   - `valid_users`: Lista de IDs de usuarios separados por comas que pueden usar el bot.
   - `superuser`: ID del usuario que puede detener el bot.

## Uso

1. Ejecuta el bot:
   ```
   python bot_youtube.py
   ```

2. En Telegram, envía `/start` para iniciar.
3. Envía una URL de YouTube para descargar el vídeo.
4. El bot descargará el vídeo (hasta 1900 MB) y lo enviará como archivo de vídeo.

### Comandos

- `/start`: Inicia el bot.
- `/stop`: Detiene el bot (solo para el superusuario).

## Requisitos

- Python 3.7+
- Las dependencias listadas en `requirements.txt`.

## Notas

- Asegúrate de que el vídeo no exceda los 1900 MB.
- El bot elimina el archivo después de enviarlo para ahorrar espacio.

## Licencia

Este proyecto está bajo la Licencia MIT.