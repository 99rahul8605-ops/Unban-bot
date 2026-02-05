import logging
from flask import Flask, jsonify
import threading
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def run_bot():
    """Run the Telegram bot."""
    try:
        logger.info("Importing and starting Telegram bot...")
        # Import inside function to avoid circular imports
        from main import UnbanBot
        
        logger.info("Bot class imported, creating instance...")
        bot = UnbanBot()
        logger.info(f"Bot instance created for owner: {bot.owner_id}")
        bot.run()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()
        # Try to restart after delay
        import time
        time.sleep(5)
        run_bot()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot",
        "owner_id": Config.OWNER_ID,
        "channel_id": Config.CHANNEL_ID,
        "endpoints": {
            "health": "/health",
            "status": "/status"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "owner": Config.OWNER_ID
    }), 200

@app.route('/status')
def status():
    """Status endpoint."""
    return jsonify({
        "bot_token_valid": bool(Config.BOT_TOKEN),
        "channel_id": Config.CHANNEL_ID,
        "owner_id": Config.OWNER_ID,
        "port": Config.PORT
    }), 200

@app.route('/check')
def check():
    """Quick check endpoint."""
    return "Bot is running!", 200

if __name__ == '__main__':
    # Start bot in background thread
    logger.info("Starting bot thread...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    logger.info(f"Bot thread started. Owner ID: {Config.OWNER_ID}")
    logger.info(f"Channel ID: {Config.CHANNEL_ID}")
    logger.info(f"Bot Token: {Config.BOT_TOKEN[:10]}...")
    
    # Start Flask server
    logger.info(f"Starting Flask server on port {Config.PORT}")
    
    # Use waitress for production
    from waitress import serve
    serve(app, host='0.0.0.0', port=Config.PORT)
