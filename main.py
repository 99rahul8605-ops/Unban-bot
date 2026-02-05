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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(f"Start command from user {user.id}")
    
    message = (
        f"👋 Hi {user.mention_html()}!\n\n"
        f"🤖 <b>Unban Bot Active</b>\n\n"
        f"📋 <b>Commands:</b>\n"
        f"• /start - Start bot\n"
        f"• /help - Help guide\n"
        f"• /unban [ID] - Unban user\n\n"
        f"🎯 <b>How to use:</b>\n"
        f"1. Get user ID from @userinfobot\n"
        f"2. Send me the ID\n"
        f"3. I'll unban them\n\n"
        f"⚡ <b>Quick unban:</b>\n"
        f"Just send: <code>123456789</code>\n\n"
        f"📢 Channel ID: <code>{Config.CHANNEL_ID}</code>"
    )
    
    await update.message.reply_html(message)
    logger.info(f"Sent welcome to user {user.id}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    help_text = (
        "🆘 <b>HELP GUIDE</b>\n\n"
        "📋 <b>Commands:</b>\n"
        "/start - Start the bot\n"
        "/help - Show this guide\n"
        "/unban [ID] - Unban a user\n\n"
        "🎯 <b>How to unban:</b>\n"
        "1. Get user ID from @userinfobot\n"
        "2. Send: <code>/unban 123456789</code>\n"
        "OR just send the ID\n\n"
        "⚠️ <b>Note:</b> I must be an admin in your channel!"
    )
    await update.message.reply_html(help_text)

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unban command."""
    if not context.args:
        await update.message.reply_html(
            "❌ <b>Usage:</b> <code>/unban USER_ID</code>\n"
            "Example: <code>/unban 123456789</code>"
        )
        return
    
    user_id = context.args[0]
    await process_unban(update, context, user_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct messages."""
    text = update.message.text.strip()
    
    if not text:
        return
    
    # Check if message is numeric (user ID)
    if text.isdigit() and len(text) >= 5:
        await process_unban(update, context, text)
    elif not text.startswith('/'):
        await update.message.reply_html(
            "❌ Send a valid User ID (numbers only)\n"
            "Example: <code>123456789</code>\n"
            "Get ID from @userinfobot"
        )

async def process_unban(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
    """Process unban request."""
    try:
        user_id_int = int(user_id)
        logger.info(f"Unbanning user {user_id_int} from {Config.CHANNEL_ID}")
        
        # Unban the user
        await context.bot.unban_chat_member(
            chat_id=Config.CHANNEL_ID,
            user_id=user_id_int,
            only_if_banned=True
        )
        
        await update.message.reply_html(
            f"✅ <b>Successfully Unbanned!</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"📢 Channel: <code>{Config.CHANNEL_ID}</code>"
        )
        logger.info(f"Success: Unbanned user {user_id_int}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unban error: {error_msg}")
        
        if "not enough rights" in error_msg.lower():
            await update.message.reply_html(
                "❌ <b>Permission Error!</b>\n\n"
                "Make me an ADMIN in the channel with:\n"
                "• Ban Users permission\n\n"
                "Then try again!"
            )
        elif "user not found" in error_msg.lower():
            await update.message.reply_html("❌ User not found!")
        elif "not banned" in error_msg.lower():
            await update.message.reply_html("✅ User is not banned!")
        else:
            await update.message.reply_html("❌ Failed to unban. Try again!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Error: {context.error}")

# Create application instance
def create_application():
    """Create and configure the bot application."""
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("unban", unban_command))
    
    # Handle direct messages
    application.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE,
        handle_message
    ))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application

# Global application instance
application = create_application()