import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
    
    # Channel ID (with minus sign for public channels)
    CHANNEL_ID = os.getenv('CHANNEL_ID', '').strip()
    
    # Convert CHANNEL_ID to int if it's not empty
    if CHANNEL_ID:
        try:
            CHANNEL_ID = int(CHANNEL_ID)
        except ValueError:
            CHANNEL_ID = 0
    
    # Webhook URL (for production)
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '').strip()
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 10000))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required (get from @BotFather)")
        elif len(cls.BOT_TOKEN) < 20:
            errors.append("BOT_TOKEN seems too short")
        
        if not cls.CHANNEL_ID:
            errors.append("CHANNEL_ID is required")
        elif cls.CHANNEL_ID > 0:
            errors.append("CHANNEL_ID should be negative for channels (e.g., -1001234567890)")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        print("✅ Configuration validated successfully!")
        print(f"🤖 Bot Token: {cls.BOT_TOKEN[:15]}...")
        print(f"📢 Channel ID: {cls.CHANNEL_ID}")
        print(f"🌐 Port: {cls.PORT}")
        print(f"🔗 Webhook: {cls.WEBHOOK_URL if cls.WEBHOOK_URL else 'Disabled'}")
        return True

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("\nPlease set these environment variables:")
    print("BOT_TOKEN=your_bot_token_from_botfather")
    print("CHANNEL_ID=-1001234567890")
    print("PORT=10000")
    print("WEBHOOK_URL=https://your-app.onrender.com")
