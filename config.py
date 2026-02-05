import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # Channel ID (with minus sign for public channels)
    CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1001234567890'))
    
    # Webhook Configuration (for production)
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 8080))
    
    # Admin Configuration (optional, for restricting commands)
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not cls.CHANNEL_ID:
            errors.append("CHANNEL_ID is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        print("✅ Configuration validated successfully!")
        print(f"🤖 Bot Token: {cls.BOT_TOKEN[:10]}...")
        print(f"📢 Channel ID: {cls.CHANNEL_ID}")
        print(f"🌐 Port: {cls.PORT}")
        print(f"🔗 Webhook URL: {cls.WEBHOOK_URL if cls.WEBHOOK_URL else 'Disabled (Polling)'}")

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
