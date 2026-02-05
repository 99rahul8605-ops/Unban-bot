import os
import logging
from flask import Flask, jsonify
import threading

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def run_bot():
    """Run the Telegram bot."""
    try:
        logger.info("Starting Telegram bot...")
        from bot import main
        main()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot",
        "owner_id": os.getenv('OWNER_ID', '7456681709')
    })

@app.route('/health')
def health():
    """Health check for Render."""
    return jsonify({"status": "healthy"}), 200

@app.route('/test')
def test():
    """Test endpoint."""
    return jsonify({
        "bot_token": os.getenv('BOT_TOKEN', '')[:5] + '...' if os.getenv('BOT_TOKEN') else 'not_set',
        "channel_id": os.getenv('CHANNEL_ID', 'not_set'),
        "owner_id": os.getenv('OWNER_ID', 'not_set')
    })

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    logger.info("🤖 Bot thread started")
    logger.info("🌐 Flask server starting...")
    
    # Get port from environment (Render sets this)
    port = int(os.getenv('PORT', 10000))
    
    # Run Flask
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)