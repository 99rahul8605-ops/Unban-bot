import logging
from flask import Flask, request, jsonify
from waitress import serve
from telegram import Update
from telegram.ext import Application
import asyncio
import threading

from main import application, bot_instance
from config import Config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize bot
def init_bot():
    """Initialize the bot application."""
    logger.info("Initializing bot...")
    
    # Initialize the application
    application.initialize()
    
    # Set webhook if WEBHOOK_URL is configured
    if Config.WEBHOOK_URL:
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
        logger.info(f"Setting webhook to: {webhook_url}")
        
        # Run async function in new thread
        async def set_webhook_async():
            await application.bot.set_webhook(webhook_url)
            logger.info("Webhook set successfully!")
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(set_webhook_async())
        loop.close()
    else:
        logger.info("Running in polling mode (for development)")
        # Start polling in background thread
        def start_polling():
            application.run_polling(
                drop_pending_updates=True,
                timeout=30,
                pool_timeout=30
            )
        
        thread = threading.Thread(target=start_polling, daemon=True)
        thread.start()

# Initialize bot on startup
init_bot()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot",
        "channel_id": Config.CHANNEL_ID,
        "webhook": bool(Config.WEBHOOK_URL),
        "endpoints": {
            "health": "/health",
            "webhook": f"/{Config.BOT_TOKEN}",
            "set_webhook": "/set_webhook"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "channel": Config.CHANNEL_ID
    }), 200

@app.route('/set_webhook')
def set_webhook():
    """Manually set webhook."""
    if not Config.WEBHOOK_URL:
        return jsonify({"error": "WEBHOOK_URL not configured"}), 400
    
    webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
    
    async def set_wh():
        await application.bot.set_webhook(webhook_url)
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_wh())
    loop.close()
    
    return jsonify({
        "success": True,
        "webhook_url": webhook_url
    }), 200

@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle webhook updates from Telegram."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        # Process update asynchronously
        async def process_update():
            await application.process_update(update)
        
        # Run in thread
        thread = threading.Thread(
            target=lambda: asyncio.run(process_update()),
            daemon=True
        )
        thread.start()
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    """Test endpoint."""
    return jsonify({
        "message": "Bot is running",
        "bot_token": Config.BOT_TOKEN[:10] + "..." if Config.BOT_TOKEN else "not_set",
        "channel_id": Config.CHANNEL_ID
    }), 200

if __name__ == '__main__':
    logger.info(f"Starting server on port {Config.PORT}")
    logger.info(f"Bot token: {Config.BOT_TOKEN[:10]}...")
    logger.info(f"Channel ID: {Config.CHANNEL_ID}")
    
    if Config.WEBHOOK_URL:
        logger.info(f"Webhook mode: {Config.WEBHOOK_URL}")
    else:
        logger.info("Polling mode (development)")
    
    serve(app, host='0.0.0.0', port=Config.PORT)
