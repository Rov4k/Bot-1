import os
import telebot
from telebot import types

 
BOT_TOKEN = '7605794688:AAFGg_sAK2BpEb_dQmdelWekqBTD28cWrFU'
ADMIN_CHAT_ID = -1002444590988
BOT_TOKEN = os.getenv('BOT_TOKEN') or '7605794688:AAFGg_sAK2BpEb_dQmdelWekqBTD28cWrFU'
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID') or '-1002444590988')


bot = telebot.TeleBot(BOT_TOKEN)
# Словарь: ID пересланного сообщения в админ-чат -> ID чата пользователя
forward_map: dict[int, int] = {}

@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message):
    """Приветствие при /start"""
    bot.send_message(message.chat.id,
                     "Привет! Пришли мне своё предложение (текст, фото, видео или документ), и я передам его администрации.")

@bot.message_handler(func=lambda m: m.chat.type == 'private',
                     content_types=['text', 'photo', 'audio', 'video', 'document', 'sticker', 'voice'])
def handle_private(message: types.Message):
    """Пересылает текст и медиа из приватного чата в админ-чат"""
    try:
        # Для медиа лучше использовать forward_message
        forwarded = bot.forward_message(
            ADMIN_CHAT_ID,
            message.chat.id,
            message.message_id
        )
        # Сохраняем связь для ответа
        forward_map[forwarded.message_id] = message.chat.id
        bot.send_message(message.chat.id,
                         "Ваше предложение отправлено администрации. Спасибо!")
    except Exception as e:
        bot.send_message(message.chat.id, "Не удалось отправить предложение. Попробуйте позже.")
        print(f"Error forwarding message: {e}")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_CHAT_ID and m.reply_to_message,
                     content_types=['text', 'photo', 'audio', 'video', 'document', 'sticker', 'voice'])
def handle_admin_reply(message: types.Message):
    """Пересылает ответ администрации обратно пользователю (текст + медиа)"""
    reply_to_id = message.reply_to_message.message_id
    user_chat_id = forward_map.get(reply_to_id)
    if not user_chat_id:
        return
    try:
        # Если ответ содержит медиа, форвардим, иначе шлём текст
        if message.content_type == 'text':
            bot.send_message(user_chat_id,
                             f"💬 Ответ администрации на ваше предложение:\n{message.text}")
        else:
            bot.forward_message(
                user_chat_id,
                ADMIN_CHAT_ID,
                message.message_id
            )
        bot.send_message(ADMIN_CHAT_ID, "Ответ отправлен автору предложения.")
    except Exception as e:
        bot.send_message(ADMIN_CHAT_ID, "Не удалось отправить ответ автору.")
        print(f"Error sending reply: {e}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)
