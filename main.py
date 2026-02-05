import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL.upper())
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
            f"<b>Commands:</b>\n"
            f"/start - Start the bot\n"
            f"/help - Show help message\n"
            f"/unban [user_id] - Unban a user\n\n"
            f"<b>How to unban:</b>\n"
            f"1. Get user ID from @userinfobot\n"
            f"2. Send: <code>/unban 123456789</code>\n"
            f"OR just send the user ID\n\n"
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
            "1. Get the user's ID (use @userinfobot)\n"
            "2. Send: <code>/unban 123456789</code>\n"
            "OR\n"
            "Simply send the user ID: <code>123456789</code>\n\n"
            "<b>Note:</b> I must be an admin in the channel with ban permissions!"
        )
        await update.message.reply_html(help_text)
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command."""
        if not context.args:
            await update.message.reply_html(
                "❌ Please provide a User ID\n"
                "Usage: <code>/unban 123456789</code>"
            )
            return
        
        user_id = context.args[0]
        await self.process_unban(update, context, user_id)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct messages containing user IDs."""
        text = update.message.text.strip()
        
        # Check if it's a user ID (numeric)
        if text.isdigit():
            await self.process_unban(update, context, text)
        else:
            await update.message.reply_html(
                "❌ Please send a valid User ID (numbers only)\n"
                "Example: <code>123456789</code>\n"
                "Or use: <code>/unban 123456789</code>"
            )
    
    async def process_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
        """Process unban request."""
        try:
            user_id_int = int(user_id)
            
            # Check if it's a valid Telegram ID
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
            logger.error(f"Error unbanning user {user_id}: {e}")
            
            error_msg = str(e).lower()
            if "not enough rights" in error_msg or "admin" in error_msg:
                await update.message.reply_html(
                    "❌ <b>Permission Error!</b>\n"
                    "I need to be an admin with ban permissions in the channel!"
                )
            elif "user not found" in error_msg:
                await update.message.reply_html("❌ User not found or invalid ID!")
            elif "not in the chat" in error_msg or "not banned" in error_msg:
                await update.message.reply_html("✅ User is not banned in the channel!")
            else:
                await update.message.reply_html("❌ Failed to unban user! Please try again.")
    
    def run(self):
        """Start the bot in polling mode."""
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("unban", self.unban_command))
        
        # Handle direct user ID messages
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            self.handle_message
        ))
        
        # Start polling
        logger.info("Starting bot in polling mode...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

if __name__ == '__main__':
    bot = UnbanBot()
    bot.run()
