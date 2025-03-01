import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import sqlite3
from typing import Dict

# 存储活跃用户
active_users: Dict[int, Update] = {}

# 初始化日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 连接数据库
def get_db():
    conn = sqlite3.connect('bot_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS buttons
                     (id INTEGER PRIMARY KEY, 
                      text TEXT UNIQUE NOT NULL,
                      response TEXT NOT NULL)''')
        # 添加默认按钮（如果表为空）
        c.execute("SELECT COUNT(*) FROM buttons")
        if c.fetchone()[0] == 0:
            default_buttons = [
                ("按钮1", "这是按钮1的回复"),
                ("按钮2", "这是按钮2的回复")
            ]
            c.executemany("INSERT INTO buttons (text, response) VALUES (?, ?)", default_buttons)
        conn.commit()

# 初始化数据库
init_db()

async def start(update: Update, context: CallbackContext):
    # 记录活跃用户
    active_users[update.message.from_user.id] = update
    
    with get_db() as conn:
        c = conn.cursor()
        # 获取所有按钮
        c.execute("SELECT text FROM buttons")
        buttons = [row[0] for row in c.fetchall()]
        
        # 创建键盘
        if buttons:
            keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text('请选择一个按钮:', reply_markup=reply_markup)
        else:
            await update.message.reply_text('当前没有可用按钮，请通过后台添加')

async def update_all_keyboards():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT text FROM buttons")
        buttons = [row[0] for row in c.fetchall()]
        
        if buttons:
            keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            # 更新所有活跃用户的键盘
            for user_id, update in active_users.items():
                try:
                    await update.message.reply_text('按钮已更新:', reply_markup=reply_markup)
                except Exception as e:
                    logging.error(f"Failed to update keyboard for user {user_id}: {e}")

async def handle_message(update: Update, context):
    # 获取消息文本
    text = update.message.text
    
    with get_db() as conn:
        c = conn.cursor()
        # 查找对应的回复和媒体文件
        c.execute("SELECT response, media_type, media_url FROM buttons WHERE text=?", (text,))
        result = c.fetchone()
    
    if result:
        response, media_type, media_url = result
        if media_type == 'text':
            await update.message.reply_text(response)
        elif media_type == 'photo':
            await update.message.reply_photo(media_url, caption=response)
        elif media_type == 'video':
            await update.message.reply_video(media_url, caption=response)
        elif media_type == 'document':
            await update.message.reply_document(media_url, caption=response)
    else:
        await update.message.reply_text("未找到对应的回复")

from config import config

# 获取应用实例
def get_application():
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return application

if __name__ == '__main__':
    # 创建应用
    application = get_application()
    
    # 启动机器人
    application.run_polling()
