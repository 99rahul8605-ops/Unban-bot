from flask import Flask, jsonify
import logging
import threading
from main import UnbanBot
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global bot thread
bot_thread = None

def run_bot():
    """Run the Telegram bot in a separate thread"""
    logger.info("Starting Telegram bot...")
    try:
        bot = UnbanBot()
        bot.run()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot",
        "channel_id": Config.CHANNEL_ID,
        "health": "/health"
    })

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "channel_id": Config.CHANNEL_ID
    }), 200

@app.route('/status')
def status():
    """Check bot status"""
    return jsonify({
        "bot_token": Config.BOT_TOKEN[:10] + "..." if Config.BOT_TOKEN else "not_set",
        "channel_id": Config.CHANNEL_ID,
        "port": Config.PORT
    })

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info(f"Bot thread started")
    
    # Start Flask server
    logger.info(f"Starting Flask server on port {Config.PORT}")
    from waitress import serve
    serve(app, host='0.0.0.0', port=Config.PORT)
