import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
    
    # Channel ID
    CHANNEL_ID = os.getenv('CHANNEL_ID', '').strip()
    
    # Owner ID (required - your Telegram user ID)
    OWNER_ID = int(os.getenv('OWNER_ID', '0'))
    
    # Admin IDs (optional, comma-separated)
    ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '').strip()
    ADMIN_IDS = []
    if ADMIN_IDS_STR:
        try:
            ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(',') if admin_id.strip()]
        except ValueError:
            print("⚠️ Warning: Invalid ADMIN_IDS format. Should be comma-separated numbers.")
    
    # Convert CHANNEL_ID to int
    if CHANNEL_ID:
        try:
            CHANNEL_ID = int(CHANNEL_ID)
        except ValueError:
            CHANNEL_ID = 0
    
    # Webhook URL
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '').strip()
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 10000))
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not cls.CHANNEL_ID:
            errors.append("CHANNEL_ID is required")
        
        if cls.OWNER_ID == 0:
            errors.append("OWNER_ID is required (your Telegram user ID)")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        print("✅ Configuration validated!")
        print(f"🤖 Bot Token: {cls.BOT_TOKEN[:10]}...")
        print(f"📢 Channel ID: {cls.CHANNEL_ID}")
        print(f"👑 Owner ID: {cls.OWNER_ID}")
        print(f"🛡️ Admin IDs: {cls.ADMIN_IDS}")
        print(f"🌐 Port: {cls.PORT}")
        
        return True

# Validate
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Error: {e}")
    print("\n📝 Please set these environment variables:")
    print("BOT_TOKEN=your_bot_token")
    print("CHANNEL_ID=-1001234567890")
    print("OWNER_ID=your_telegram_user_id")
    print("ADMIN_IDS=123456789,987654321 (optional)")
    print("PORT=10000")
    print("WEBHOOK_URL=https://your-app.onrender.com")
