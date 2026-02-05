import os
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
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
        self.application = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        logger.info(f"Start command received from user {user.id}")
        
        welcome_message = (
            f"👋 Hi {user.mention_html()}!\n\n"
            f"🤖 <b>Unban Bot Active</b>\n\n"
            f"📝 <b>How to use:</b>\n"
            f"1. Get user's ID from @userinfobot\n"
            f"2. Send me their ID\n"
            f"3. I'll unban them from the channel\n\n"
            f"📌 <b>Example:</b>\n"
            f"• Send: <code>123456789</code>\n"
            f"• Or: <code>/unban 123456789</code>\n\n"
            f"📢 Channel: <code>{self.channel_id}</code>\n"
            f"✅ Bot is online!"
        )
        
        await update.message.reply_html(welcome_message)
        logger.info(f"Sent welcome message to user {user.id}")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a help message."""
        help_text = (
            "🆘 <b>HELP GUIDE</b>\n\n"
            "📋 <b>Commands:</b>\n"
            "• /start - Start the bot\n"
            "• /help - Show this guide\n"
            "• /unban [ID] - Unban a user\n\n"
            "🎯 <b>How to unban:</b>\n"
            "1. Get user ID from @userinfobot\n"
            "2. Send me the ID (numbers only)\n"
            "3. I'll unban them immediately\n\n"
            "⚡ <b>Quick unban:</b>\n"
            "Just send the user ID directly!\n"
            "Example: <code>123456789</code>\n\n"
            "⚠️ <b>Note:</b>\n"
            "I must be an admin in your channel with ban permissions!"
        )
        await update.message.reply_html(help_text)
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command."""
        if not context.args:
            await update.message.reply_html(
                "❌ <b>Usage:</b> <code>/unban USER_ID</code>\n"
                "Example: <code>/unban 123456789</code>"
            )
            return
        
        user_id = context.args[0]
        await self.process_unban(update, context, user_id)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct messages containing user IDs."""
        text = update.message.text.strip()
        
        if not text:
            return
            
        # Check if it's a user ID (numeric)
        if text.isdigit() and len(text) >= 6:
            await self.process_unban(update, context, text)
        elif text.startswith('/'):
            # Unknown command
            await update.message.reply_html(
                "❌ Unknown command. Try /help for available commands."
            )
        else:
            await update.message.reply_html(
                "❌ Please send a valid User ID (numbers only)\n"
                "Example: <code>123456789</code>\n"
                "Get ID from: @userinfobot"
            )
    
    async def process_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
        """Process unban request."""
        try:
            user_id_int = int(user_id)
            logger.info(f"Attempting to unban user {user_id_int} from channel {self.channel_id}")
            
            # Check if it's a valid Telegram ID
            if user_id_int <= 0:
                await update.message.reply_html("❌ Invalid User ID format!")
                return
            
            # Try to unban the user
            result = await context.bot.unban_chat_member(
                chat_id=self.channel_id,
                user_id=user_id_int,
                only_if_banned=True
            )
            
            if result:
                await update.message.reply_html(
                    f"✅ <b>Successfully Unbanned!</b>\n\n"
                    f"👤 User ID: <code>{user_id}</code>\n"
                    f"📢 Channel: <code>{self.channel_id}</code>\n\n"
                    f"🔄 User can now join the channel again."
                )
                logger.info(f"Successfully unbanned user {user_id_int}")
            else:
                await update.message.reply_html("✅ User is not banned in this channel!")
                
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {str(e)}")
            
            error_msg = str(e).lower()
            if "not enough rights" in error_msg or "admin" in error_msg:
                await update.message.reply_html(
                    "❌ <b>Permission Error!</b>\n\n"
                    "I need to be an ADMIN in the channel with:\n"
                    "• Ban Users permission\n"
                    "• Delete Messages permission\n\n"
                    "Please make me an admin first!"
                )
            elif "user not found" in error_msg or "invalid" in error_msg:
                await update.message.reply_html(
                    "❌ <b>User Not Found</b>\n\n"
                    "The User ID is invalid or the user doesn't exist.\n"
                    "Check the ID with @userinfobot."
                )
            elif "not in the chat" in error_msg or "not banned" in error_msg:
                await update.message.reply_html("✅ User is not banned in this channel!")
            else:
                await update.message.reply_html(
                    f"❌ <b>Error:</b> {str(e)[:100]}\n\n"
                    "Please check:\n"
                    "1. Channel ID is correct\n"
                    "2. I'm an admin\n"
                    "3. User ID is valid"
                )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors."""
        logger.error(f"Update {update} caused error {context.error}")

# Global bot instance
bot_instance = UnbanBot()

def setup_application():
    """Setup the bot application."""
    application = Application.builder().token(bot_instance.token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(CommandHandler("help", bot_instance.help))
    application.add_handler(CommandHandler("unban", bot_instance.unban_command))
    
    # Handle direct messages
    application.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE,
        bot_instance.handle_message
    ))
    
    # Error handler
    application.add_error_handler(bot_instance.error_handler)
    
    return application

# Create global application
application = setup_application()
