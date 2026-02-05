import logging
from flask import Flask, request, jsonify
from waitress import serve
import asyncio
import threading

from main import application
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global event loop for async operations
loop = None

def init_bot():
    """Initialize the bot with webhook."""
    global loop
    
    logger.info("Initializing bot...")
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Initialize application in the event loop
    loop.run_until_complete(application.initialize())
    logger.info("Application initialized")
    
    # Set webhook if URL is provided
    if Config.WEBHOOK_URL:
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
        logger.info(f"Setting webhook to: {webhook_url}")
        
        try:
            loop.run_until_complete(application.bot.set_webhook(webhook_url))
            logger.info("Webhook set successfully!")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")

# Initialize bot in a thread
def start_bot():
    """Start bot initialization in background."""
    thread = threading.Thread(target=init_bot, daemon=True)
    thread.start()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot",
        "endpoints": {
            "health": "/health",
            "webhook": f"/{Config.BOT_TOKEN}",
            "info": "/info"
        }
    })

@app.route('/health')
def health():
    """Health check for Render."""
    return jsonify({"status": "healthy", "bot": "ready"}), 200

@app.route('/info')
def info():
    """Get bot info."""
    return jsonify({
        "bot_token": Config.BOT_TOKEN[:10] + "..." if Config.BOT_TOKEN else "not_set",
        "channel_id": Config.CHANNEL_ID,
        "webhook": Config.WEBHOOK_URL
    })

@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates."""
    try:
        # Get update from request
        json_data = request.get_json()
        
        # Create update object
        from telegram import Update
        update = Update.de_json(json_data, application.bot)
        
        # Process update in event loop
        if loop and loop.is_running():
            # Use run_coroutine_threadsafe for thread safety
            future = asyncio.run_coroutine_threadsafe(
                application.process_update(update),
                loop
            )
            future.result(timeout=5)  # Wait for completion
        else:
            # Create new event loop if needed
            asyncio.run(application.process_update(update))
        
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
        # Use existing loop or create new one
        if loop and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                application.bot.set_webhook(webhook_url),
                loop
            )
            future.result(timeout=5)
        else:
            asyncio.run(application.bot.set_webhook(webhook_url))
        
        return jsonify({
            "success": True,
            "webhook_url": webhook_url
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_webhook')
def delete_webhook():
    """Delete webhook."""
    try:
        if loop and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                application.bot.delete_webhook(),
                loop
            )
            future.result(timeout=5)
        else:
            asyncio.run(application.bot.delete_webhook())
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting server on port {Config.PORT}")
    
    # Start bot initialization
    start_bot()
    
    # Start Flask server
    serve(app, host='0.0.0.0', port=Config.PORT)