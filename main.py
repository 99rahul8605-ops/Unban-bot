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
        self.owner_id = Config.OWNER_ID
        
    def is_owner(self, user_id: int) -> bool:
        """Check if user is the owner."""
        return user_id == self.owner_id
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        
        if not self.is_owner(user_id):
            await update.message.reply_text("❌ Access Denied: This bot is for owner only.")
            return
        
        await update.message.reply_html(
            f"👋 Welcome, Owner!\n\n"
            f"🤖 <b>Unban Bot Active</b>\n\n"
            f"📋 <b>Commands:</b>\n"
            f"• /start - Show this message\n"
            f"• /help - Show help\n"
            f"• /unban [ID] - Unban user\n\n"
            f"🎯 <b>How to use:</b>\n"
            f"1. Get user ID from @userinfobot\n"
            f"2. Send: <code>/unban USER_ID</code>\n\n"
            f"📢 Channel: <code>{self.channel_id}</code>\n"
            f"👑 Your ID: <code>{user_id}</code>"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        user_id = update.effective_user.id
        
        if not self.is_owner(user_id):
            await update.message.reply_text("❌ Access Denied")
            return
        
        await update.message.reply_html(
            "🆘 <b>Help Guide</b>\n\n"
            "📋 <b>Commands:</b>\n"
            "/start - Start bot\n"
            "/help - This help\n"
            "/unban [ID] - Unban user\n\n"
            "🎯 <b>How to unban:</b>\n"
            "1. Get user ID from @userinfobot\n"
            "2. Send: <code>/unban 123456789</code>\n\n"
            "⚠️ <b>Requirements:</b>\n"
            "• Bot must be admin in channel\n"
            "• Bot needs 'Ban Users' permission"
        )
    
    async def unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command."""
        user_id = update.effective_user.id
        
        if not self.is_owner(user_id):
            await update.message.reply_text("❌ Access Denied: Only owner can use this command.")
            return
        
        if not context.args:
            await update.message.reply_html(
                "❌ <b>Usage:</b>\n"
                "<code>/unban USER_ID</code>\n\n"
                "Example: <code>/unban 123456789</code>"
            )
            return
        
        target_user = context.args[0]
        
        # Validate user ID
        if not target_user.isdigit():
            await update.message.reply_text("❌ Invalid User ID. Must be numbers only.")
            return
        
        try:
            target_user_id = int(target_user)
            
            # Unban the user
            result = await context.bot.unban_chat_member(
                chat_id=self.channel_id,
                user_id=target_user_id,
                only_if_banned=True
            )
            
            if result:
                await update.message.reply_html(
                    f"✅ <b>Successfully Unbanned!</b>\n\n"
                    f"👤 User ID: <code>{target_user}</code>\n"
                    f"📢 Channel: <code>{self.channel_id}</code>\n"
                    f"👑 By: <code>{user_id}</code>"
                )
                logger.info(f"Unbanned user {target_user} from channel {self.channel_id}")
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
                    "Please make me admin first!"
                )
            elif "user not found" in error_msg.lower():
                await update.message.reply_text("❌ User not found or invalid ID.")
            elif "not in the chat" in error_msg.lower() or "not banned" in error_msg.lower():
                await update.message.reply_text("✅ User is not banned.")
            else:
                await update.message.reply_text(f"❌ Error: {error_msg[:100]}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct messages with user IDs."""
        user_id = update.effective_user.id
        
        if not self.is_owner(user_id):
            return  # Ignore messages from non-owners
        
        text = update.message.text.strip()
        
        # Check if it's a user ID (numeric)
        if text.isdigit() and len(text) >= 5:
            # Treat as unban request
            try:
                target_user_id = int(text)
                
                result = await context.bot.unban_chat_member(
                    chat_id=self.channel_id,
                    user_id=target_user_id,
                    only_if_banned=True
                )
                
                if result:
                    await update.message.reply_html(
                        f"✅ <b>Unbanned!</b>\n"
                        f"User: <code>{text}</code>"
                    )
                else:
                    await update.message.reply_text("✅ User is not banned.")
                    
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors."""
        logger.error(f"Error: {context.error}")
    
    def run(self):
        """Run the bot in polling mode."""
        # Create application
        app = Application.builder().token(self.token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help))
        app.add_handler(CommandHandler("unban", self.unban))
        
        # Handle numeric messages (user IDs)
        app.add_handler(MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE,
            self.handle_message
        ))
        
        # Error handler
        app.add_error_handler(self.error_handler)
        
        # Start polling
        logger.info("Starting bot in polling mode...")
        app.run_polling(
            drop_pending_updates=True,
            timeout=30,
            pool_timeout=30
        )

if __name__ == '__main__':
    bot = UnbanBot()
    bot.run()
