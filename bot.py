#!/usr/bin/env python3
"""
بوت قبول طلبات الانضمام - Telegram Join Request Bot
Bot for accepting join requests for channels and groups
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    filters
)

from config import BOT_TOKEN

from handlers import (
    start_command,
    button_callback,
    handle_message,
    handle_chat_join_request,
    handle_activation_command,
    handle_claim_callback
)
import database

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    print("🤖 Starting Join Request Bot...")
    
    # Initialize database
    database.init_db()
    print("✅ Database initialized")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_claim_callback, pattern="^claim_"))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Handle activation command (groups & channels)
    application.add_handler(MessageHandler(filters.Regex(r"\.تفعيل"), handle_activation_command))
    
    # Handle normal messages (private chat state machine)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_message))
    
    application.add_handler(ChatJoinRequestHandler(handle_chat_join_request))
    
    print("✅ Handlers registered")
    print("🚀 Bot is running! Press Ctrl+C to stop.")
    
    # Run the bot
    application.run_polling(allowed_updates=["message", "channel_post", "callback_query", "chat_join_request"])

if __name__ == "__main__":
    main()
