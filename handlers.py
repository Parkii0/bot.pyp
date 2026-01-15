from telegram import Update, ChatMemberAdministrator, ChatMemberOwner, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TelegramError
import database as db
from keyboards import (
    get_main_keyboard, 
    get_channels_keyboard, 
    get_accept_count_keyboard,
    get_back_keyboard,
    get_channel_actions_keyboard
)

# Store user states for conversation flow
user_states = {}


async def handle_activation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .تفعيل command in groups and channels"""
    message = update.message or update.channel_post
    if not message or not message.text:
        return

    if ".تفعيل" not in message.text:
        return

    chat = message.chat
    chat_type = chat.type
    
    try:
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if not isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner)):
            await message.reply_text("❌ البوت يحتاج صلاحيات أدمن للتفعيل (مع صلاحية دعوة المستخدمين).")
            return
    except TelegramError:
        return

    if chat_type in ['group', 'supergroup']:
        user = message.from_user
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
            await message.reply_text("❌ هذا الأمر للمشرفين فقط.")
            return

        if db.add_channel(user.id, chat.id, chat.title, "group"):
            await message.reply_text("✅ تم تفعيل المجموعه بنجاح! وربطها بحسابك.\nيمكنك الآن إدارتها من البوت.")
        else:
            await message.reply_text("✅ المجموعه مفعلة مسبقاً.")

    elif chat_type == 'channel':
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ أنا مالك القناة (اضغط للتفعيل)", callback_data=f"claim_{chat.id}")
        ]])
        await message.reply_text(
            "🔒 لتأكيد تفعيل القناة وربطها بحسابك، اضغط على الزر أدناه:",
            reply_markup=keyboard
        )

async def handle_claim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle channel ownership claim"""
    query = update.callback_query
    user = query.from_user
    chat_id = int(query.data.split("_")[1])
    
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if not isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
            await query.answer("❌ لست مشرفاً في هذه القناة!", show_alert=True)
            return
            
        chat = await context.bot.get_chat(chat_id)
        
        if db.add_channel(user.id, chat_id, chat.title, "channel"):
            await query.answer("✅ تم التفعيل بنجاح!")
            await query.edit_message_text(f"✅ تم تفعيل القناة بنجاح بواسطة {user.first_name}!")
        else:
            await query.answer("⚠️ القناة مفعلة مسبقاً", show_alert=True)
            await query.edit_message_text(f"✅ القناة مفعلة مسبقاً.")
            
    except TelegramError as e:
        await query.answer("❌ حدث خطأ، تأكد أن البوت لا يزال أدمن", show_alert=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""👋❤️ مرحبا {user.first_name}
• بوت قبول طلبات الانضمام الخاصة بالقنوات والكروبات✅.

لتفعيل البوت:
1. أضف البوت للقناة أو المجموعة كأدمن
2. أرسل كلمة `.تفعيل` في القناة أو المجموعة
3. ستظهر القناة في قائمة "قنواتي وكروباتي"

يمكنك قبول الطلبات بشكل تلقائي مباشرةً او تخزينها لقبولها لاحقاً بنقرة زر من خلال البوت 🤖"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "add_channel" or data == "add_group":
        await query.edit_message_text(
            "📢 لإضافة قناة أو كروب:\n\n"
            "1. أضف البوت كأدمن في القناة/الكروب\n"
            "2. أرسل `.تفعيل` في القناة/الكروب\n\n"
            "سيتم ربطها بحسابك تلقائياً!",
            reply_markup=get_back_keyboard()
        )
    
    elif data == "my_channels":
        channels = db.get_user_channels(user_id)
        if not channels:
            await query.edit_message_text(
                "❌ لا توجد قنوات أو مجموعات مضافة\n\n"
                "أضف البوت لقناة/كروب وأرسل `.تفعيل`",
                reply_markup=get_main_keyboard()
            )
        else:
            text = "📋 قنواتي وكروباتي:\n\n"
            for ch in channels:
                ch_type = "📢" if ch['chat_type'] == 'channel' else "👥"
                auto = "✅ تلقائي" if ch['auto_accept'] else ""
                text += f"{ch_type} {ch['title']} {auto}\n"
            
            await query.edit_message_text(
                text,
                reply_markup=get_channels_keyboard(channels, "manage")
            )
    
    elif data == "accept_requests":
        channels = db.get_user_channels(user_id)
        if not channels:
            await query.edit_message_text(
                "❌ لا توجد قنوات أو مجموعات\n\n"
                "أضف قناة أو كروب أولاً",
                reply_markup=get_main_keyboard()
            )
        else:
            await query.edit_message_text(
                "✅ اختر القناة أو الكروب لقبول طلبات الانضمام:",
                reply_markup=get_channels_keyboard(channels, "choose")
            )
    
    elif data.startswith("choose_"):
        chat_id = int(data.split("_")[1])
        channel = db.get_channel(user_id, chat_id)
        if channel:
            await query.edit_message_text(
                f"📊 {channel['title']}\n\n"
                "كم عدد طلبات الانضمام الذي تريد قبوله؟ اختر العدد\n"
                "او يمكنك قبول جميع الطلبات",
                reply_markup=get_accept_count_keyboard(chat_id)
            )
    
    elif data.startswith("manage_"):
        chat_id = int(data.split("_")[1])
        channel = db.get_channel(user_id, chat_id)
        if channel:
            ch_type = "قناة" if channel['chat_type'] == 'channel' else "كروب"
            auto_status = "مفعل ✅" if channel['auto_accept'] else "معطل ❌"
            await query.edit_message_text(
                f"📋 {channel['title']}\n"
                f"النوع: {ch_type}\n"
                f"القبول التلقائي: {auto_status}",
                reply_markup=get_channel_actions_keyboard(chat_id)
            )
    
    elif data.startswith("channel_accept_"):
        chat_id = int(data.split("_")[2])
        channel = db.get_channel(user_id, chat_id)
        if channel:
            await query.edit_message_text(
                f"📊 {channel['title']}\n\n"
                "كم عدد طلبات الانضمام الذي تريد قبوله؟ اختر العدد\n"
                "او يمكنك قبول جميع الطلبات",
                reply_markup=get_accept_count_keyboard(chat_id)
            )
    
    elif data.startswith("auto_accept_"):
        chat_id = int(data.split("_")[2])
        new_status = db.toggle_auto_accept(user_id, chat_id)
        status_text = "مفعل ✅" if new_status else "معطل ❌"
        await query.answer(f"القبول التلقائي: {status_text}", show_alert=True)
        
        channel = db.get_channel(user_id, chat_id)
        if channel:
            ch_type = "قناة" if channel['chat_type'] == 'channel' else "كروب"
            await query.edit_message_text(
                f"📋 {channel['title']}\n"
                f"النوع: {ch_type}\n"
                f"القبول التلقائي: {status_text}",
                reply_markup=get_channel_actions_keyboard(chat_id)
            )
    
    elif data.startswith("delete_channel_"):
        chat_id = int(data.split("_")[2])
        db.delete_channel(user_id, chat_id)
        await query.answer("✅ تم الحذف بنجاح", show_alert=True)
        
        channels = db.get_user_channels(user_id)
        if not channels:
            await query.edit_message_text(
                "❌ لا توجد قنوات أو مجموعات مضافة",
                reply_markup=get_main_keyboard()
            )
        else:
            text = "📋 قنواتي وكروباتي:\n\n"
            for ch in channels:
                ch_type = "📢" if ch['chat_type'] == 'channel' else "👥"
                text += f"{ch_type} {ch['title']}\n"
            await query.edit_message_text(
                text,
                reply_markup=get_channels_keyboard(channels, "manage")
            )
    
    elif data.startswith("accept_"):
        parts = data.split("_")
        if parts[1] == "all":
            count = None
            chat_id = int(parts[2])
        else:
            count = int(parts[1])
            chat_id = int(parts[2])
        
        await query.edit_message_text("⏳ جاري قبول الطلبات...")
        
        accepted = await accept_join_requests(context.bot, chat_id, count)
        
        await query.edit_message_text(
            f"✅ تم قبول {accepted} طلب انضمام بنجاح!",
            reply_markup=get_main_keyboard()
        )
    
    elif data == "back_main":
        user_states.pop(user_id, None)
        user = update.effective_user
        welcome_text = f"""👋❤️ مرحبا {user.first_name}
• بوت قبول طلبات الانضمام الخاصة بالقنوات والكروبات✅.

لتفعيل البوت:
1. أضف البوت للقناة أو المجموعة كأدمن
2. أرسل كلمة `.تفعيل` في القناة أو المجموعة
3. ستظهر القناة في قائمة "قنواتي وكروباتي"

يمكنك قبول الطلبات بشكل تلقائي مباشرةً او تخزينها لقبولها لاحقاً بنقرة زر من خلال البوت 🤖"""
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages in private chat"""
    pass

async def handle_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming join requests - auto accept if enabled, otherwise store"""
    request = update.chat_join_request
    chat_id = request.chat.id
    user_id = request.from_user.id
    first_name = request.from_user.first_name
    username = request.from_user.username
    
    auto_channels = db.get_auto_accept_channels()
    
    auto_accepted = False
    for channel in auto_channels:
        if channel['chat_id'] == chat_id:
            try:
                await context.bot.approve_chat_join_request(chat_id, user_id)
                auto_accepted = True
            except TelegramError:
                pass
            break
    
    if not auto_accepted:
        db.add_pending_request(chat_id, user_id, first_name, username)

async def accept_join_requests(bot, chat_id, count=None):
    """Accept pending join requests for a chat"""
    accepted = 0
    
    pending = db.get_pending_requests(chat_id, limit=count)
    
    for req in pending:
        try:
            await bot.approve_chat_join_request(chat_id, req['user_id'])
            db.delete_pending_request(chat_id, req['user_id'])
            accepted += 1
        except TelegramError:
            db.delete_pending_request(chat_id, req['user_id'])
            pass
    
    return accepted
