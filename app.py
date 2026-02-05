from flask import Flask, request, jsonify
import logging
from waitress import serve
from main import UnbanBot
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize bot
bot_app = None

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot",
        "endpoints": {
            "health": "/health",
            "webhook": f"/{Config.BOT_TOKEN}",
            "set_webhook": "/set_webhook",
            "delete_webhook": "/delete_webhook"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "bot": "Telegram Unban Bot",
        "channel_id": Config.CHANNEL_ID
    }), 200

@app.route('/set_webhook')
def set_webhook():
    """Manually set webhook (useful for debugging)"""
    if not Config.WEBHOOK_URL:
        return jsonify({"error": "WEBHOOK_URL not configured"}), 400
    
    from telegram import Bot
    bot = Bot(token=Config.BOT_TOKEN)
    
    webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
    result = bot.set_webhook(webhook_url)
    
    return jsonify({
        "success": result,
        "webhook_url": webhook_url
    }), 200

@app.route('/delete_webhook')
def delete_webhook():
    """Delete webhook (switch to polling)"""
    from telegram import Bot
    bot = Bot(token=Config.BOT_TOKEN)
    
    result = bot.delete_webhook()
    return jsonify({"success": result}), 200

@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    if bot_app is None:
        return jsonify({"error": "Bot not initialized"}), 500
    
    update = request.get_json()
    
    # Process update asynchronously
    import asyncio
    asyncio.run(bot_app.process_update(update))
    
    return jsonify({"status": "ok"}), 200

def init_bot():
    """Initialize the bot application"""
    global bot_app
    from telegram.ext import Application
    
    if Config.WEBHOOK_URL:
        logger.info("Starting in WEBHOOK mode")
        # Initialize bot for webhook mode
        bot_app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Set up handlers
        from main import UnbanBot
        temp_bot = UnbanBot()
        
        # Register handlers
        bot_app.add_handler(CommandHandler("start", temp_bot.start))
        bot_app.add_handler(CommandHandler("help", temp_bot.help))
        bot_app.add_handler(CommandHandler("unban", temp_bot.unban_user))
        
        from telegram.ext import MessageHandler, filters
        bot_app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            temp_bot.unban_user
        ))
        
        bot_app.add_error_handler(temp_bot.error_handler)
        
        # Initialize bot
        bot_app.initialize()
        
        # Set webhook
        from telegram import Bot
        bot = Bot(token=Config.BOT_TOKEN)
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
        bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
    else:
        logger.info("Starting in POLLING mode")
        # Start bot in polling mode
        bot = UnbanBot()
        import threading
        thread = threading.Thread(target=bot.run, daemon=True)
        thread.start()

if __name__ == '__main__':
    init_bot()
    
    # Start Flask server
    logger.info(f"Starting server on port {Config.PORT}")
    serve(app, host="0.0.0.0", port=Config.PORT)
