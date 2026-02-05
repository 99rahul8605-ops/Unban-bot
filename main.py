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
        self.admin_ids = Config.ADMIN_IDS
        
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized (owner or admin)."""
        if user_id == self.owner_id:
            return True
        if user_id in self.admin_ids:
            return True
        return False
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        user_id = user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_html(
                "🚫 <b>Access Denied</b>\n\n"
                "This bot is restricted to the owner only.\n"
                "If you are the owner, please check your configuration."
            )
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            return
        
        logger.info(f"Start command from owner/admin {user_id}")
        
        message = (
            f"👋 Welcome back, {user.mention_html()}!\n\n"
            f"🤖 <b>Unban Bot - Owner Mode</b>\n\n"
            f"📋 <b>Available Commands:</b>\n"
            f"• /start - Show this message\n"
            f"• /help - Show help guide\n"
            f"• /unban [ID] - Unban a user\n"
            f"• /users - Show authorized users\n\n"
            f"🎯 <b>How to unban:</b>\n"
            f"1. Get user ID from @userinfobot\n"
            f"2. Send me the ID\n"
            f"3. I'll unban them immediately\n\n"
            f"📢 Channel ID: <code>{self.channel_id}</code>\n"
            f"👑 Owner ID: <code>{self.owner_id}</code>"
        )
        
        await update.message.reply_html(message)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a help message."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_html("🚫 Access Denied")
            return
        
        help_text = (
            "🆘 <b>OWNER HELP GUIDE</b>\n\n"
            "📋 <b>Commands:</b>\n"
            "/start - Start the bot\n"
            "/help - Show this guide\n"
            "/unban [ID] - Unban a user\n"
            "/users - Show authorized users\n\n"
            "🎯 <b>How to unban:</b>\n"
            "1. Get user ID from @userinfobot\n"
            f"2. Send: <code>/unban 123456789</code>\n"
            "OR just send the ID directly\n\n"
            "📢 <b>Channel:</b>\n"
            f"ID: <code>{self.channel_id}</code>\n\n"
            "👑 <b>Authorized Users:</b>\n"
            f"Owner: <code>{self.owner_id}</code>\n"
            f"Admins: {len(self.admin_ids)} user(s)"
        )
        await update.message.reply_html(help_text)
    
    async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show authorized users."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_html("🚫 Access Denied")
            return
        
        admins_text = "\n".join([f"• <code>{admin_id}</code>" for admin_id in self.admin_ids])
        if not admins_text:
            admins_text = "• No additional admins"
        
        message = (
            "👥 <b>Authorized Users</b>\n\n"
            f"👑 Owner: <code>{self.owner_id}</code>\n\n"
            f"🛡️ Admins ({len(self.admin_ids)}):\n"
            f"{admins_text}\n\n"
            f"📢 Channel: <code>{self.channel_id}</code>"
        )
        
        await update.message.reply_html(message)
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_html(
                "🚫 <b>Access Denied</b>\n\n"
                "Only the owner and authorized admins can use this command."
            )
            logger.warning(f"Unauthorized unban attempt from user {user_id}")
            return
        
        if not context.args:
            await update.message.reply_html(
                "❌ <b>Usage:</b> <code>/unban USER_ID</code>\n"
                "Example: <code>/unban 123456789</code>"
            )
            return
        
        target_user_id = context.args[0]
        await self.process_unban(update, context, target_user_id)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct messages."""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            await update.message.reply_html(
                "🚫 <b>Access Denied</b>\n\n"
                "This bot is restricted to authorized users only."
            )
            return
        
        text = update.message.text.strip()
        
        if not text:
            return
        
        # Check if message is numeric (user ID)
        if text.isdigit() and len(text) >= 5:
            await self.process_unban(update, context, text)
        elif not text.startswith('/'):
            await update.message.reply_html(
                "❌ Send a valid User ID (numbers only)\n"
                "Example: <code>123456789</code>\n"
                "Get ID from @userinfobot"
            )
    
    async def process_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE, target_user_id: str):
        """Process unban request."""
        try:
            user_id_int = int(target_user_id)
            requester_id = update.effective_user.id
            
            logger.info(f"Owner/Admin {requester_id} unbanning user {user_id_int} from {self.channel_id}")
            
            # Unban the user
            result = await context.bot.unban_chat_member(
                chat_id=self.channel_id,
                user_id=user_id_int,
                only_if_banned=True
            )
            
            if result:
                await update.message.reply_html(
                    f"✅ <b>Successfully Unbanned!</b>\n\n"
                    f"👤 User ID: <code>{target_user_id}</code>\n"
                    f"📢 Channel: <code>{self.channel_id}</code>\n"
                    f"👑 By: <code>{requester_id}</code>"
                )
                logger.info(f"Success: Unbanned user {user_id_int} by {requester_id}")
            else:
                await update.message.reply_html("✅ User is not banned!")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unban error by {update.effective_user.id}: {error_msg}")
            
            if "not enough rights" in error_msg.lower():
                await update.message.reply_html(
                    "❌ <b>Permission Error!</b>\n\n"
                    "I need to be an ADMIN in the channel with:\n"
                    "• Ban Users permission\n\n"
                    "Please check my admin status!"
                )
            elif "user not found" in error_msg.lower():
                await update.message.reply_html("❌ User not found!")
            elif "not banned" in error_msg.lower():
                await update.message.reply_html("✅ User is not banned!")
            else:
                await update.message.reply_html("❌ Failed to unban. Please try again!")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors."""
        logger.error(f"Error: {context.error}")
    
    def create_application(self):
        """Create and configure the bot application."""
        application = Application.builder().token(self.token).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("unban", self.unban_command))
        application.add_handler(CommandHandler("users", self.show_users))
        
        # Handle direct messages
        application.add_handler(MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE,
            self.handle_message
        ))
        
        # Error handler
        application.add_error_handler(self.error_handler)
        
        return application

# Create bot instance
bot_instance = UnbanBot()

# Create application
application = bot_instance.create_application()
