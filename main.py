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

user_balance = [0]
user_data = {}

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

def getbalance(user_id):
    select = '''
        SELECT * FROM users WHERE telegram_id = %s;
    '''
    cursor.execute(select, (str(user_id),))
    users = cursor.fetchone()
    return users[3]

def user_exists(telegram_id):
    select = '''
        SELECT * FROM users WHERE telegram_id = %s;
    '''
    cursor.execute(select, (str(telegram_id),))
    users = cursor.fetchone()
    connection.commit()
    if users:
        return True
def add_user(telegram_id, username):
    insert = '''
        INSERT INTO users (telegram_id, username, balance) VALUES (%s, %s, %s);
    '''
    cursor.execute(insert, (str(telegram_id), username, user_balance[0],))
    connection.commit()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if user_exists(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Ցույց Տալ Իմ Հաշիվը", callback_data="balance")
        btn2 = types.InlineKeyboardButton("Ավելացնել Իմ Հաշվին", callback_data="cashim")
        btn3 = types.InlineKeyboardButton("Հանել Իմ հաշվից", callback_data="cashout")
        btn4 = types.InlineKeyboardButton("Փոխանցում Կատարել", callback_data="poxancum")
        markup.add(btn1, btn2, btn3, btn4)
        bot.reply_to(message, "Ընտրեք կոճակներից որևէ մեկը", reply_markup=markup)
    else:
        add_user(user_id, user_name)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Ցույց Տալ Իմ Հաշիվը", callback_data="balance")
        btn2 = types.InlineKeyboardButton("Ավելացնել Իմ Հաշվին", callback_data="cashim")
        btn3 = types.InlineKeyboardButton("Հանել Իմ հաշվից", callback_data="cashout")
        btn4 = types.InlineKeyboardButton("Փոխանցում Կատարել", callback_data="poxancum")
        markup.add(btn1, btn2, btn3, btn4)
        bot.reply_to(message, "Շնորգավորում եմ դուք գրանցվեցիք", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    if call.data == "balance":
        bot.send_message(call.message.chat.id, (getbalance(user_id)))
    elif call.data == "cashim":
        bot.send_message(call.message.chat.id, "Գրեք թե որքանեք ուզում ավելացնել")
        @bot.message_handler(content_types=["text"])
        def cashim(message):
            sum = message.text
            update = '''
                UPDATE users SET balance = %s WHERE telegram_id = %s;
            '''
            cursor.execute(update, (getbalance(user_id) + int(sum), str(user_id),))
            connection.commit()
            bot.reply_to(message, "Ձեր հաշիվը ավելացվեց")
    elif call.data == "cashout":
        bot.send_message(call.message.chat.id, "Գրեք թե որքանեք ուզում հանել")
        @bot.message_handler(content_types=["text"])
        def cashout(message):
            sum = message.text
            update = '''
                UPDATE users SET balance = %s WHERE telegram_id = %s;
            '''
            cursor.execute(update, (getbalance(user_id) - int(sum), str(user_id),))
            connection.commit()
            bot.reply_to(message, "Ձեր հաշիվը հանվեց")
    elif call.data == "poxancum":
        bot.send_message(call.message.chat.id, "Գրեք Փոխղանցման գումարր")
        @bot.message_handler(content_types=["text"])
        def poxancum(message):
            if "sum" not in user_data:
                sum = message.text
                user_data["sum"] = int(sum)
                bot.reply_to(message, "Հիմա Գրեք այդ Մարդու այդին")
            else:
                user_id2 = message.text
                user_data["id"] = user_id2
                update = '''
                    UPDATE users SET balance = (%s) WHERE telegram_id = (%s);
                '''
                cursor.execute(update, (getbalance(user_id2) + int(user_data["sum"]), str(user_data["id"]),))
                connection.commit()
                update = '''
                    UPDATE users SET balance = (%s) WHERE telegram_id = (%s);
                '''
                cursor.execute(update, (getbalance(user_id) - int(user_data["sum"]), str(user_id),))
                connection.commit()
                bot.reply_to(message, "Փոխանցումը հաջոցությամբ կատարվեց")
bot.polling()