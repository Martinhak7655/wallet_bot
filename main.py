import telebot
from telebot import types
import psycopg2

BOT_TOKEN = ""
bot = telebot.TeleBot(BOT_TOKEN)

connection = psycopg2.connect(
    host='localhost',
    database='walletbot',
    user='postgres',
    password='MH2012'
)
cursor = connection.cursor()

create_table = '''
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        telegram_id VARCHAR(100) NOT NULL,
        username VARCHAR(100) NOT NULL,
        balance INTEGER DEFAULT 0,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
'''
cursor.execute(create_table)
connection.commit()

def user_exists(telegram_id):
    select = '''
        SELECT * FROM users WHERE telegram_id = %s;
    '''
    cursor.execute(select, (str(telegram_id),))
    connection.commit()
def add_user(telegram_id, username):
    insert = '''
        INSERT INTO users (telegram_id, username) VALUES (%s, %s);
    '''
    cursor.execute(insert, (str(telegram_id), username,))
    connection.commit()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if not user_exists(user_id):
        bot.reply_to(message, "Դուք արդեն գրանցվացեք!")
    else:
        add_user(user_id, user_name)
        bot.reply_to(message, "Շնորգավորում եմ դուք գրանցվեցիք")

bot.polling()