import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
    
    # Channel ID
    CHANNEL_ID = os.getenv('CHANNEL_ID', '').strip()
    if CHANNEL_ID:
        try:
            CHANNEL_ID = int(CHANNEL_ID)
        except ValueError:
            CHANNEL_ID = 0
    
    # Owner ID
    OWNER_ID = os.getenv('OWNER_ID', '').strip()
    if OWNER_ID:
        try:
            OWNER_ID = int(OWNER_ID)
        except ValueError:
            OWNER_ID = 0
    
    # Server Configuration
    PORT = int(os.getenv('PORT', '10000'))
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not cls.CHANNEL_ID:
            errors.append("CHANNEL_ID is required")
        
        if not cls.OWNER_ID:
            errors.append("OWNER_ID is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        print("✅ Configuration validated!")
        print(f"🤖 Bot Token: {cls.BOT_TOKEN[:10]}...")
        print(f"📢 Channel ID: {cls.CHANNEL_ID}")
        print(f"👑 Owner ID: {cls.OWNER_ID}")
        print(f"🌐 Port: {cls.PORT}")
        return True

# Validate on import
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")