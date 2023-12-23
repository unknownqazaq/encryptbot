import telebot
from telebot import types
from modules.database_manager import DatabaseManager
from modules.encryption_utils import encrypt, decrypt
import mysql.connector
import logging


# Состояния для отслеживания контекста диалога
states = {}

# Настройка логирования
logging.basicConfig(filename='bot_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



# Создаем экземпляр DatabaseManager
db_manager = DatabaseManager(host="localhost", user="root", password="root", database="encbot2")

# Подключение к базе данных
try:
    db_manager.connect()
    db_manager.create_table()
    logging.info("Connected to the database and created table.")
except mysql.connector.Error as err:
    logging.error(f"Error: {err}")
finally:
    db_manager.disconnect()

# Создаем объект бота
TOKEN = '6323376518:AAHqdDLlJfhBxEos-yICy_wW8JDEy225qMk'
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_info = f"User ID: {message.from_user.id}, Username: {message.from_user.username}, " \
                f"First Name: {message.from_user.first_name}, Last Name: {message.from_user.last_name}"

    logging.info(user_info)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_enc = types.KeyboardButton('Encrypt text')
    btn_des = types.KeyboardButton('Decrypt text')

    markup.add(btn_enc, btn_des)
    bot.send_message(message.chat.id, 'SIS-2121 Amiruldayev Emil, Rakhmetuly Zhanserik, Nurpeisov Daniyar',
                     reply_markup=markup)

# Обработчик для кнопки "Encrypt text"
@bot.message_handler(func=lambda message: message.text == 'Encrypt text')
def handle_encrypt_start(message):
    global states
    # Устанавливаем состояние "ожидание текста для шифрования"
    states[message.chat.id] = 'encrypt_text'
    bot.send_message(message.chat.id, 'Enter the text that needs to be encrypted')

# Обработчик для ответа на текст для шифрования
@bot.message_handler(func=lambda message: states.get(message.chat.id) == 'encrypt_text')
def handle_encrypt_text(message):
    global states
    global text_to_encrypt
    # Получаем текст для шифрования из сообщения пользователя
    text_to_encrypt = message.text

    # Спрашиваем у пользователя ключ для шифрования
    bot.send_message(message.chat.id, 'Enter the key for encryption')

    # Устанавливаем состояние "ожидание ключа для шифрования"
    states[message.chat.id] = 'encrypt_key'

def save_to_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Обработчик для ответа на ключ для шифрования
@bot.message_handler(func=lambda message: states.get(message.chat.id) == 'encrypt_key')
def handle_encrypt_key(message):
    global states
    global encryption_key, text_to_encrypt

    encryption_key = message.text

    if not encryption_key.isdigit():
        bot.send_message(message.chat.id, 'Please enter a valid numeric key.')
        return

    # Зашифровываем текст
    encrypted_text = encrypt(text_to_encrypt, int(encryption_key))

    # Сохраняем зашифрованный текст в файл
    save_to_file('encrypted_text.txt', encrypted_text)

    # Сохраняем данные в базе данных
    db_manager.insert_data(encrypted_text, text_to_encrypt, int(encryption_key))

    # Отправляем файл пользователю
    with open('encrypted_text.txt', 'rb') as file:
        bot.send_document(message.chat.id, file)

    states[message.chat.id] = None

# Обработчик для кнопки "Decrypt text"
@bot.message_handler(func=lambda message: message.text == 'Decrypt text')
def handle_decrypt_start(message):
    global states
    # Устанавливаем состояние "ожидание текста для расшифрования"
    states[message.chat.id] = 'decrypt_text'
    bot.send_message(message.chat.id, 'Enter the text that needs to be decrypted')

# Обработчик для ответа на текст для расшифрования
@bot.message_handler(func=lambda message: states.get(message.chat.id) == 'decrypt_text')
def handle_decrypt_text(message):
    global states
    global text_to_encrypt
    try:
        # Получаем текст для расшифрования из сообщения пользователя
        text_to_encrypt = message.text

        # Спрашиваем у пользователя ключ для расшифрования
        bot.send_message(message.chat.id, 'Enter the key for decryption')

        # Устанавливаем состояние "ожидание ключа для расшифрования"
        states[message.chat.id] = 'decrypt_key'

    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла неожиданная ошибка: {str(e)}')

# Обработчик для ответа на ключ для расшифрования
@bot.message_handler(func=lambda message: states.get(message.chat.id) == 'decrypt_key')
def handle_decrypt_key(message):
    global states
    global text_to_encrypt

    try:
        decryption_key = message.text

        if not decryption_key.isdigit():
            logging.warning('Invalid numeric key entered.')
            bot.send_message(message.chat.id, 'Please enter a valid numeric key.')
            return

        # Retrieve encrypted data as a tuple
        encrypted_data_tuple = db_manager.fetch_data(int(decryption_key))

        if encrypted_data_tuple:
            encrypted_text = encrypted_data_tuple[0]  # Access the first element of the tuple
            decrypted_text = decrypt(encrypted_text, int(decryption_key))

            # Save decrypted text to file
            save_to_file('decrypted_text.txt', decrypted_text)

            # Send the file to the user
            with open('decrypted_text.txt', 'rb') as file:
                bot.send_document(message.chat.id, file)
        else:
            logging.info('No data found for the given key.')
            bot.send_message(message.chat.id, 'No data found for the given key.')

    except ValueError as e:
        logging.error(f'Error: {str(e)}')
        bot.send_message(message.chat.id, f'Error: {str(e)}')

    finally:
        states[message.chat.id] = None





# Запуск бота
bot.polling(none_stop=True, interval=0)
