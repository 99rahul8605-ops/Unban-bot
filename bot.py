import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8595225498:AAHv95LLP9OZR9yG7y0rLw4hQ8x8tYs1abc')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1003374353864'))
OWNER_ID = int(os.getenv('OWNER_ID', '7456681709'))

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_owner(user_id: int) -> bool:
    """Check if user is the owner."""
    return user_id == OWNER_ID

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    
    if not is_owner(user.id):
        logger.warning(f"Unauthorized access attempt from {user.id}")
        await update.message.reply_text("❌ Access Denied. Owner only.")
        return
    
    logger.info(f"Owner {user.id} started the bot")
    
    await update.message.reply_html(
        f"👋 <b>Welcome Owner!</b>\n\n"
        f"🤖 Bot is working!\n"
        f"📢 Channel: <code>{CHANNEL_ID}</code>\n"
        f"👑 Your ID: <code>{user.id}</code>\n\n"
        f"📋 <b>Commands:</b>\n"
        f"• /start - This message\n"
        f"• /help - Help guide\n"
        f"• /unban [ID] - Unban user\n"
        f"• /test - Test connection\n\n"
        f"🎯 <b>Quick unban:</b>\n"
        f"Just send user ID like: <code>123456789</code>"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    if not is_owner(update.effective_user.id):
        return
    
    await update.message.reply_html(
        "🆘 <b>Help Guide</b>\n\n"
        "📋 <b>Commands:</b>\n"
        "/start - Start bot\n"
        "/help - Show help\n"
        "/unban [ID] - Unban user\n"
        "/test - Test connection\n\n"
        "🎯 <b>How to unban:</b>\n"
        "1. Get user ID from @userinfobot\n"
        "2. Send: <code>/unban USER_ID</code>\n"
        "OR send just the ID\n\n"
        "⚠️ <b>Requirements:</b>\n"
        "• Bot must be admin in channel\n"
        "• Bot needs 'Ban Users' permission\n\n"
        f"📢 Channel ID: <code>{CHANNEL_ID}</code>"
    )

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /test command."""
    if not is_owner(update.effective_user.id):
        return
    
    await update.message.reply_html(
        f"✅ <b>Bot is working!</b>\n\n"
        f"🤖 Bot: Active\n"
        f"👑 Owner: <code>{update.effective_user.id}</code>\n"
        f"📢 Channel: <code>{CHANNEL_ID}</code>\n"
        f"💬 Chat ID: <code>{update.message.chat.id}</code>"
    )

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unban command."""
    user = update.effective_user
    
    if not is_owner(user.id):
        logger.warning(f"Unauthorized unban attempt from {user.id}")
        await update.message.reply_text("❌ Access Denied. Owner only.")
        return
    
    # Check if user ID is provided
    if not context.args:
        await update.message.reply_html(
            "❌ <b>Usage:</b>\n"
            "<code>/unban USER_ID</code>\n\n"
            "Example: <code>/unban 123456789</code>\n\n"
            "Get user ID from @userinfobot"
        )
        return
    
    user_id = context.args[0]
    
    # Validate user ID
    if not user_id.isdigit():
        await update.message.reply_text("❌ Invalid User ID. Must be numbers only.")
        return
    
    try:
        target_user_id = int(user_id)
        logger.info(f"Owner {user.id} trying to unban {target_user_id} from {CHANNEL_ID}")
        
        # Try to unban
        result = await context.bot.unban_chat_member(
            chat_id=CHANNEL_ID,
            user_id=target_user_id,
            only_if_banned=True
        )
        
        if result:
            await update.message.reply_html(
                f"✅ <b>Successfully Unbanned!</b>\n\n"
                f"👤 User: <code>{user_id}</code>\n"
                f"📢 Channel: <code>{CHANNEL_ID}</code>\n"
                f"👑 By: <code>{user.id}</code>"
            )
            logger.info(f"Success: Unbanned {target_user_id}")
        else:
            await update.message.reply_text("✅ User is not banned in this channel.")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unban error: {error_msg}")
        
        if "not enough rights" in error_msg.lower():
            await update.message.reply_html(
                "❌ <b>Permission Error!</b>\n\n"
                "I need to be an ADMIN in the channel with:\n"
                "• Ban Users permission\n\n"
                "Please make me admin with ban rights!"
            )
        elif "user not found" in error_msg.lower() or "invalid" in error_msg.lower():
            await update.message.reply_text("❌ User not found or invalid ID.")
        elif "chat not found" in error_msg.lower():
            await update.message.reply_text("❌ Channel not found. Check CHANNEL_ID.")
        elif "not in the chat" in error_msg.lower():
            await update.message.reply_text("✅ User is not banned in this channel.")
        else:
            await update.message.reply_text(f"❌ Error: {error_msg[:100]}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct messages."""
    user = update.effective_user
    
    if not is_owner(user.id):
        return
    
    text = update.message.text.strip()
    
    # If it's just numbers (user ID), treat as unban request
    if text.isdigit() and len(text) >= 5:
        try:
            target_user_id = int(text)
            
            result = await context.bot.unban_chat_member(
                chat_id=CHANNEL_ID,
                user_id=target_user_id,
                only_if_banned=True
            )
            
            if result:
                await update.message.reply_html(f"✅ Unbanned user <code>{text}</code>")
            else:
                await update.message.reply_text("✅ User is not banned.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
    
    # If it's text but not a command, show help
    elif not text.startswith('/'):
        await update.message.reply_text(
            "Send a User ID (numbers only) to unban.\n"
            "Example: 123456789\n\n"
            "Or use /help for commands."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("test", test_command))
    
    # Handle messages
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_message
    ))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start polling
    logger.info("🤖 Bot starting in polling mode...")
    logger.info(f"👑 Owner ID: {OWNER_ID}")
    logger.info(f"📢 Channel ID: {CHANNEL_ID}")
    logger.info(f"🔑 Bot Token: {BOT_TOKEN[:10]}...")
    
    app.run_polling(
        drop_pending_updates=True,
        timeout=30,
        pool_timeout=30
    )

if __name__ == '__main__':
    main()