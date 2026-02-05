import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
    
    # Channel ID
    CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1003374353864'))
    
    # Owner ID
    OWNER_ID = int(os.getenv('OWNER_ID', '7456681709'))
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 10000))
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        
        if not cls.CHANNEL_ID:
            raise ValueError("CHANNEL_ID is required")
        
        if not cls.OWNER_ID:
            raise ValueError("OWNER_ID is required")
        
        print("✅ Configuration validated!")
        print(f"🤖 Bot Token: {cls.BOT_TOKEN[:10]}...")
        print(f"📢 Channel ID: {cls.CHANNEL_ID}")
        print(f"👑 Owner ID: {cls.OWNER_ID}")
        print(f"🌐 Port: {cls.PORT}")
        return True

# Validate
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Error: {e}")
