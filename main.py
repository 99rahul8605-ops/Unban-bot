import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UnbanBot:
    def __init__(self):
        self.token = Config.BOT_TOKEN
        self.channel_id = Config.CHANNEL_ID
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            f"Hi {user.mention_html()}! 👋\n\n"
            f"Welcome to the Unban Bot!\n\n"
            f"To unban a user, simply send me their User ID.\n"
            f"You can get a user's ID by forwarding their message to @userinfobot\n\n"
            f"📌 <b>How to use:</b>\n"
            f"1. Get the user's ID\n"
            f"2. Send it to me in this chat\n"
            f"3. I'll unban them from the channel\n\n"
            f"Channel ID: <code>{self.channel_id}</code>"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a help message."""
        help_text = (
            "🆘 <b>Help Guide</b>\n\n"
            "<b>Commands:</b>\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/unban [user_id] - Unban a user\n\n"
            "<b>How to unban:</b>\n"
            "1. Get the user's ID (you can use @userinfobot)\n"
            "2. Send: <code>/unban 123456789</code>\n"
            "OR\n"
            "Simply send the user ID directly: <code>123456789</code>\n\n"
            "<b>Note:</b> I must be an admin in the channel with ban permissions!"
        )
        await update.message.reply_html(help_text)
    
    async def unban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command and direct user ID messages."""
        user_id = None
        
        # Check if it's a command with argument
        if update.message.text.startswith('/unban'):
            if context.args:
                user_id = context.args[0]
            else:
                await update.message.reply_html(
                    "❌ Please provide a User ID\n"
                    "Usage: <code>/unban 123456789</code>"
                )
                return
        # Check if it's just a user ID (numeric message)
        elif update.message.text.isdigit():
            user_id = update.message.text
        
        if not user_id:
            await update.message.reply_html(
                "❌ Please send a valid User ID (numbers only)\n"
                "Example: <code>123456789</code>"
            )
            return
        
        try:
            # Convert to integer
            user_id_int = int(user_id)
            
            # Check if it's a valid Telegram ID (usually positive)
            if user_id_int <= 0:
                await update.message.reply_html("❌ Invalid User ID format!")
                return
            
            # Try to unban the user
            await context.bot.unban_chat_member(
                chat_id=self.channel_id,
                user_id=user_id_int,
                only_if_banned=True
            )
            
            await update.message.reply_html(
                f"✅ Successfully unbanned user!\n"
                f"User ID: <code>{user_id}</code>\n"
                f"From Channel: <code>{self.channel_id}</code>"
            )
            logger.info(f"Unbanned user {user_id} from channel {self.channel_id}")
            
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            
            error_message = str(e).lower()
            if "not enough rights" in error_message or "admin" in error_message:
                await update.message.reply_html(
                    "❌ <b>Permission Error!</b>\n"
                    "I need to be an admin with ban permissions in the channel!"
                )
            elif "user not found" in error_message or "invalid" in error_message:
                await update.message.reply_html(
                    "❌ User not found or invalid ID!\n"
                    "Make sure:\n"
                    "1. The ID is correct\n"
                    "2. The user exists"
                )
            elif "not in the chat" in error_message or "not banned" in error_message:
                await update.message.reply_html(
                    "✅ User is not banned in the channel!"
                )
            else:
                await update.message.reply_html(
                    "❌ Failed to unban user!\n"
                    f"Error: {str(e)[:100]}..."
                )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors."""
        logger.error(f"Update {update} caused error {context.error}")
    
    def run(self):
        """Start the bot."""
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("unban", self.unban_user))
        
        # Handle direct user ID messages
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            self.unban_user
        ))
        
        # Error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        if Config.WEBHOOK_URL:
            # Webhook mode for production
            webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
            application.run_webhook(
                listen="0.0.0.0",
                port=Config.PORT,
                url_path=Config.BOT_TOKEN,
                webhook_url=webhook_url
            )
        else:
            # Polling mode for development
            application.run_polling()

if __name__ == '__main__':
    bot = UnbanBot()
    bot.run()
