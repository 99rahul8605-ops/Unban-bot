import logging
from flask import Flask, request, jsonify
from waitress import serve
import asyncio
import threading

from main import application, bot_instance
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize bot webhook
def init_bot():
    """Initialize bot with webhook."""
    logger.info("Initializing bot...")
    
    # Create event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Initialize application
        loop.run_until_complete(application.initialize())
        logger.info("Application initialized")
        
        # Set webhook if URL is provided
        if Config.WEBHOOK_URL:
            webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
            logger.info(f"Setting webhook to: {webhook_url}")
            
            loop.run_until_complete(application.bot.set_webhook(webhook_url))
            logger.info("Webhook set successfully!")
        else:
            logger.info("Running in polling mode")
            
    except Exception as e:
        logger.error(f"Bot initialization failed: {e}")
    finally:
        loop.close()

# Start bot initialization
init_thread = threading.Thread(target=init_bot, daemon=True)
init_thread.start()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot (Owner Only)",
        "owner_id": Config.OWNER_ID,
        "channel_id": Config.CHANNEL_ID,
        "authorized_users": [Config.OWNER_ID] + Config.ADMIN_IDS
    })

@app.route('/health')
def health():
    """Health check for Render."""
    return jsonify({"status": "healthy", "owner_id": Config.OWNER_ID}), 200

@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates."""
    try:
        # Parse update
        update_data = request.get_json()
        
        # Process update asynchronously
        async def process():
            from telegram import Update
            update = Update.de_json(update_data, application.bot)
            await application.process_update(update)
        
        # Run in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process())
        loop.close()
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/set_webhook')
def set_webhook():
    """Manually set webhook."""
    if not Config.WEBHOOK_URL:
        return jsonify({"error": "WEBHOOK_URL not set"}), 400
    
    webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.bot.set_webhook(webhook_url))
        loop.close()
        
        return jsonify({
            "success": True,
            "webhook_url": webhook_url
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting server on port {Config.PORT}")
    logger.info(f"Owner ID: {Config.OWNER_ID}")
    
    # Start server
    serve(app, host='0.0.0.0', port=Config.PORT)
