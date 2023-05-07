import telebot


class ReceiptSplitterBot():
    '''
    ReceiptSplitterBot Description
    here
    are 
    my 
    commands
    '''
    def __init__(self, CONFIG):
        

        bot = telebot.TeleBot(CONFIG['BOT']['TOKEN'])

        self.chat_list = CONFIG['BOT']['CHAT_ID']
        print(self.chat_list)

        # TODO: подгрузить табличку
        # TODO: строка с балансом каждого

        # TODO: создание лог файлов для пользователей
        
        # Проверка чата на право использования бота
        def chek_group(msg):
            if msg.chat.id in self.chat_list:
                return True
            else:
                bot.send_message(msg.chat.id, f"Sorry, you can't use me in this chat!\nYour chat ID is: '{msg.chat.id}'")
                return False

        @bot.message_handler(commands=['start'])
        def send_guide(message):
            if chek_group(message):
                bot.send_message(message.chat.id, f'Hi! This is guide how to use me!{self.__doc__}')

        # TODO: написать функцию для выставления счета всем или между конкретными людьми
        @bot.message_handler(commands=['add'])
        def add_receipt(message):
            if chek_group(message):
                # TODO:выдавать сообщение: какая операция записана, 
                bot.reply_to(message, '')
            
        # TODO: написать функцию для вывода 'чья очередь платить'
        @bot.message_handler(commands=['turn'])
        def turn_to_pay(message):
            if chek_group(message):
                bot.reply_to(message, '')

        # TODO: написать функцию для вывода платежей
        @bot.message_handler(commands=['checkout'])
        def get_payments(message):
            if chek_group(message):
                # TODO: расчет минимального количества платежей
                bot.reply_to(message, '')

        # TODO: написать функцию для возвращения таблички (кто в каком плюсе/минусе)
        @bot.message_handler(commands=['balance'])
        def get_balance(message):
            if chek_group(message):
                bot.reply_to(message, '')

        # TODO: написать функцию для очистки истории долгов
        @bot.message_handler(commands=['clear'])
        def clear_history(message):
            if chek_group(message):
                # TODO: нужно получить дополнительное подтверждение
                bot.reply_to(message, '')

        print('Bot is running!')
        bot.infinity_polling()    
