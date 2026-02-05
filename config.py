import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
    
    # Channel ID
    CHANNEL_ID = os.getenv('CHANNEL_ID', '').strip()
    
    # Convert CHANNEL_ID to int
    if CHANNEL_ID:
        CHANNEL_ID = int(CHANNEL_ID)
    
    # Webhook URL
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '').strip()
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 10000))
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        
        if not cls.CHANNEL_ID:
            raise ValueError("CHANNEL_ID is required")
        
        print("✅ Configuration validated!")
        print(f"🤖 Bot Token: {cls.BOT_TOKEN[:10]}...")
        print(f"📢 Channel ID: {cls.CHANNEL_ID}")
        print(f"🌐 Port: {cls.PORT}")
        
        return True

# Validate
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Error: {e}")