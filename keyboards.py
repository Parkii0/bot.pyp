from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    """Main menu keyboard - القائمة الرئيسية"""
    keyboard = [
        [
            InlineKeyboardButton("• إضافة قناة •", callback_data="add_channel"),
            InlineKeyboardButton("• إضافة كروب •", callback_data="add_group")
        ],
        [
            InlineKeyboardButton("• قنواتي وكروباتي •", callback_data="my_channels")
        ],
        [
            InlineKeyboardButton("✅ موافق على الانضمام", callback_data="accept_requests")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_channels_keyboard(channels, action="select"):
    """Keyboard to display user's channels/groups"""
    keyboard = []
    for channel in channels:
        channel_name = channel['title']
        channel_id = channel['chat_id']
        keyboard.append([InlineKeyboardButton(
            f"✅ {channel_name}", 
            callback_data=f"{action}_{channel_id}"
        )])
    keyboard.append([InlineKeyboardButton("• رجوع •", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def get_accept_count_keyboard(chat_id):
    """Keyboard for selecting number of requests to accept"""
    keyboard = [
        [
            InlineKeyboardButton("10", callback_data=f"accept_10_{chat_id}"),
            InlineKeyboardButton("50", callback_data=f"accept_50_{chat_id}"),
            InlineKeyboardButton("100", callback_data=f"accept_100_{chat_id}"),
            InlineKeyboardButton("250", callback_data=f"accept_250_{chat_id}"),
            InlineKeyboardButton("500", callback_data=f"accept_500_{chat_id}")
        ],
        [
            InlineKeyboardButton("1000", callback_data=f"accept_1000_{chat_id}"),
            InlineKeyboardButton("5000", callback_data=f"accept_5000_{chat_id}"),
            InlineKeyboardButton("10000", callback_data=f"accept_10000_{chat_id}"),
            InlineKeyboardButton("50000", callback_data=f"accept_50000_{chat_id}"),
            InlineKeyboardButton("100000", callback_data=f"accept_100000_{chat_id}")
        ],
        [
            InlineKeyboardButton("• قبول كل الطلبات المعلقة", callback_data=f"accept_all_{chat_id}")
        ],
        [
            InlineKeyboardButton("• رجوع •", callback_data="accept_requests")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Simple back button"""
    keyboard = [[InlineKeyboardButton("• رجوع •", callback_data="back_main")]]
    return InlineKeyboardMarkup(keyboard)

def get_channel_actions_keyboard(chat_id):
    """Actions for a specific channel"""
    keyboard = [
        [InlineKeyboardButton("✅ قبول الطلبات", callback_data=f"channel_accept_{chat_id}")],
        [InlineKeyboardButton("🔄 تفعيل القبول التلقائي", callback_data=f"auto_accept_{chat_id}")],
        [InlineKeyboardButton("🗑 حذف", callback_data=f"delete_channel_{chat_id}")],
        [InlineKeyboardButton("• رجوع •", callback_data="my_channels")]
    ]
    return InlineKeyboardMarkup(keyboard)
