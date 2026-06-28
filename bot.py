import os
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

ALLOWED = {'PNG', 'JPEG', 'JPG', 'WEBP', 'BMP', 'GIF'}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Send me an image, then use:\n/convert FORMAT\n\nExample: /convert PNG"
    )

async def store_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo_id'] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ Image received! Now type /convert <format>")

async def convert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        fmt = context.args[0].upper()
        if fmt == 'JPG':
            pil_fmt = 'JPEG'
        else:
            pil_fmt = fmt if fmt in ALLOWED else None
        if pil_fmt is None:
            await update.message.reply_text(f"❌ Unsupported format. Use: {', '.join(ALLOWED)}")
            return
    except (IndexError, AttributeError):
        await update.message.reply_text("Usage: /convert FORMAT")
        return

    photo_id = context.user_data.get('photo_id')
    if not photo_id:
        await update.message.reply_text("Send me an image first.")
        return

    # Download
    file = await context.bot.get_file(photo_id)
    img_bytes = await file.download_as_bytearray()
    img = Image.open(io.BytesIO(img_bytes))

    # Convert
    out = io.BytesIO()
    if pil_fmt == 'GIF' and img.format != 'GIF':
        # Convert to RGB for GIF
        img = img.convert('RGB')
    img.save(out, format=pil_fmt)
    out.seek(0)
    ext = 'jpg' if fmt == 'JPG' else fmt.lower()
    await update.message.reply_document(
        document=out,
        filename=f"converted.{ext}",
        caption=f"✅ Converted to {fmt}"
    )

def main():
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, store_photo))
    app.add_handler(CommandHandler("convert", convert_cmd))
    app.run_polling()

if __name__ == '__main__':
    main()
