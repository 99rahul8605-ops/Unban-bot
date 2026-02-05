import logging
from flask import Flask, jsonify
import subprocess
import threading
import time
import os
from config import Config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable to track if bot is running
bot_process = None

def run_bot():
    """Run the bot in a separate process."""
    global bot_process
    
    try:
        logger.info("Starting Telegram bot...")
        
        # Run bot.py as a subprocess
        bot_process = subprocess.Popen(
            ["python", "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Log bot output
        def log_output(pipe, prefix):
            for line in pipe:
                if line.strip():
                    logger.info(f"{prefix}: {line.strip()}")
        
        # Start logging threads
        stdout_thread = threading.Thread(
            target=log_output,
            args=(bot_process.stdout, "BOT"),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=log_output,
            args=(bot_process.stderr, "BOT-ERROR"),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        logger.info(f"Bot process started with PID: {bot_process.pid}")
        
        # Wait for process to complete
        bot_process.wait()
        
    except Exception as e:
        logger.error(f"Error in bot process: {e}")
        bot_process = None

@app.route('/')
def home():
    """Home page."""
    return jsonify({
        "status": "online",
        "service": "Telegram Unban Bot",
        "owner_id": Config.OWNER_ID,
        "channel_id": Config.CHANNEL_ID,
        "bot_running": bot_process is not None and bot_process.poll() is None
    })

@app.route('/health')
def health():
    """Health check endpoint for Render."""
    bot_alive = bot_process is not None and bot_process.poll() is None
    
    status = {
        "status": "healthy" if bot_alive else "degraded",
        "bot": "running" if bot_alive else "not running",
        "owner_id": Config.OWNER_ID,
        "channel_id": Config.CHANNEL_ID,
        "port": Config.PORT
    }
    
    return jsonify(status), 200 if bot_alive else 503

@app.route('/restart')
def restart():
    """Restart the bot."""
    global bot_process
    
    if bot_process:
        bot_process.terminate()
        bot_process.wait()
        bot_process = None
    
    # Start bot in new thread
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    
    return jsonify({"status": "restarting", "message": "Bot restart initiated"}), 200

@app.route('/status')
def status():
    """Get detailed status."""
    bot_alive = bot_process is not None and bot_process.poll() is None
    
    return jsonify({
        "bot_process": {
            "pid": bot_process.pid if bot_process else None,
            "alive": bot_alive,
            "returncode": bot_process.poll() if bot_process else None
        },
        "config": {
            "bot_token": Config.BOT_TOKEN[:10] + "..." if Config.BOT_TOKEN else None,
            "channel_id": Config.CHANNEL_ID,
            "owner_id": Config.OWNER_ID
        },
        "server": {
            "port": Config.PORT
        }
    })

if __name__ == '__main__':
    # Start bot in background thread
    logger.info(f"Starting bot for owner {Config.OWNER_ID}")
    logger.info(f"Channel ID: {Config.CHANNEL_ID}")
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask server
    logger.info(f"Starting Flask server on port {Config.PORT}")
    
    # Use waitress for production
    from waitress import serve
    serve(app, host='0.0.0.0', port=Config.PORT)