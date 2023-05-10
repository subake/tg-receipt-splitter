import os
import sys
import yaml
import re

import inspect

import telebot


class ReceiptSplitterBot():
    '''
/start -- инструкция к боту
/new -- добавить новых пользователей 
    /new @user1 @user2 ...
/rename -- переименовать существующего пользователя
    (не реализовано)
/remove -- удалить существующего пользователя
    (не реализовано)
/add -- внести информацию о новой покупке ([.] -- опциональные параметры)
    /add [@payer] TOTAL [notme] [@debtor1 @debtor2 ...]
    @payer -- тот, кто оплатил чек (по умолчанию отправитель)
    TOTAL -- сумма покупки
    notme -- флаг: входит ли плательщик в сделку (по умолчанию 'да')
    @debtor -- список должников (по умолчанию все пользователи)
/turn -- чья очередь платить (оплачивает главный должник)
/checkout -- выводит оптимальный список передовов для погашения долгов
    (не реализовано)
/balance -- выводит долги участников
/clear -- обнуляет долги участников
    '''
    def __init__(self):
        
        # open config file
        try:
            print('Opening config file...')
            CONFIG = yaml.safe_load(open('config.yaml', 'r'))
        except Exception as e:
            print(e)
            print('Error opening config file.')
            quit()
            
        print('Starting bot...')
        bot = telebot.TeleBot(CONFIG['BOT']['TOKEN'])

        self.chat_list = CONFIG['BOT']['CHAT_ID']
        print('Chat ID list: ', self.chat_list)

        # Opening cash data for all chats
        try:
            print('Opening cash data...')
            DATA = yaml.safe_load(open('cash_data.yaml', 'r'))
            if DATA is None:
                DATA = {}
        except Exception as e:
            print(e)
            print('Error opening cash data.')
            quit()
        print(DATA)

        # TODO: создание лог файлов для пользователей
        
        # Проверка чата на право использования бота
        def chek_group(msg):
            if msg.chat.id in self.chat_list:
                return True
            else:
                bot.send_message(msg.chat.id, f"Sorry, you can't use me in this chat!\nYour chat ID is: '{msg.chat.id}'")
                return False

        # Проверка на наличие страницы группы в yaml файле + проверка списка участников   
        def chek_group_users(msg, usr_list=None):
            # Добавление нового словаря под новый чат
            if msg.chat.id not in DATA.keys():
                DATA[msg.chat.id] = {}

            new_usrs = []
            # добавление автора сообщения
            if msg.from_user.username not in DATA[msg.chat.id].keys():
                DATA[msg.chat.id][msg.from_user.username] = 0
                new_usrs += [msg.from_user.username]

            # добавление нового списка участников
            if usr_list is not None:
                for usr in usr_list: 
                    if usr not in DATA[msg.chat.id].keys():
                        DATA[msg.chat.id][usr] = 0
                        new_usrs += [usr]

            if len(new_usrs):
                bot.send_message(msg.chat.id, f'Welcome new debtors: {", ".join(new_usrs)}')

        # Совершение платежа: кто заплатил, сумма, кто должен
        def make_payment(chat_id, payer, price, debtors):
            piece = price / len(debtors)
            for usr in debtors:
                DATA[chat_id][usr] -= piece
            DATA[chat_id][payer] += price

            save_data()

        def save_data():
            with open('cash_data.yaml', 'w') as outfile:
                yaml.dump(DATA, outfile, default_flow_style=False)

        # TODO: Описание бота и инструкции (дописать docstring)
        @bot.message_handler(commands=['start'])
        def send_guide(message):
            if not chek_group(message):
                return
            
            bot.send_message(message.chat.id, f'Hi! This is guide how to use me!{self.__doc__}')

        # Функция для добавления новых пользователей
        @bot.message_handler(commands=['new'])
        def add_user(message):
            if not chek_group(message):
                return

            # Список новых пользователей
            usr_list = [message.text[e.offset+1:e.offset+e.length] for e in message.entities if e.type == 'mention']
            
            print(usr_list)

            chek_group_users(message, usr_list)

            save_data()


        # TODO: написать функцию для добавления изменения ника пользователя
        @bot.message_handler(commands=['rename'])
        def rename_user(message):
            if not chek_group(message):
                return
            chek_group_users(message)

            save_data()
        
            bot.reply_to(message, '')

        # TODO: написать функцию для удаления пользователей
        @bot.message_handler(commands=['remove'])
        def remove_user(message):
            if not chek_group(message):
                return
            chek_group_users(message)

            save_data()
        
            # TODO:выдавать сообщение: кому должен удаленный пользователь перевести бабки
            bot.reply_to(message, '')

        # Функция для выставления счета всем или между конкретными людьми
        @bot.message_handler(commands=['add'])
        def add_receipt(message):
            if not chek_group(message):
                return
            
            usr_list = [message.text[e.offset+1:e.offset+e.length] for e in message.entities if e.type == 'mention']
            
            print(usr_list)

            chek_group_users(message, usr_list)

            # print(message.text)
            price = re.findall("([-+]?\d+(?:[.,]\d+)?)", message.text)[0]

            if len(price) == 0:
                bot.reply_to(message, 'No TOTAL found')
                return
            
            price_pos = message.text.find(price)
            price = float(price.replace(',', '.'))

            # определение плательщика
            payer = message.from_user.username
            debtors_n = 0
            if len(usr_list) > 0:
                for e in message.entities:
                    if e.type == 'mention':
                        if e.offset < price_pos:
                            payer = usr_list[0]
                            debtors_n = 1
                        break
            
            # определение должников
            notme = 'notme' in message.text.split()
            usrs = DATA[message.chat.id].keys()
            if len(usr_list) - debtors_n > 0:
                usrs = usr_list[debtors_n:]
                if payer not in usrs:
                    usrs += [payer]

            if notme:
                usrs = [usr for usr in usrs if usr != payer]
            
            # покупка конкретной группе
            make_payment(message.chat.id, payer, price, usrs)
        
            # TODO: реакция на сообщение
            bot.reply_to(message, u'\N{check mark}')

            # сообщение об операции
            bot.reply_to(message, f'{payer} paid {price:.2f} for the receipt splitted between: {", ".join(usrs)}')

            # get_balance(message)
            
        # Функция для вывода 'чья очередь платить'
        @bot.message_handler(commands=['turn'])
        def turn_to_pay(message):
            if not chek_group(message):
                return

            chat_balance = DATA[message.chat.id]

            min_bal = 10**10
            min_usr = ''
            for usr, bal in chat_balance.items():
                if bal < min_bal:
                    min_usr, min_bal = usr, bal

            bot.reply_to(message, f"It's @{min_usr} turn to pay!")

        # TODO: написать функцию для вывода платежей
        @bot.message_handler(commands=['checkout'])
        def get_payments(message):
            if not chek_group(message):
                return
        
            # TODO: расчет минимального количества платежей
            bot.reply_to(message, '')

        # Функция для возвращения баланса участников (кто в каком плюсе/минусе)
        @bot.message_handler(commands=['balance'])
        def get_balance(message):
            if not chek_group(message):
                return
        
            chat_balance = DATA[message.chat.id]
            chat_balance = {k: v for k, v in sorted(chat_balance.items(), key=lambda item: -item[1])}
            txt = ''.join([f'{usr} : {bal:.2f}\n' for usr, bal in chat_balance.items()])

            bot.send_message(message.chat.id, f'This is current balance:\n{txt}')

        # Функция для очистки истории долгов (обнуление баланса)
        @bot.message_handler(commands=['clear'])
        def clear_history(message):
            if not chek_group(message):
                return
        
            # TODO: нужно получить дополнительное подтверждение
            DATA[message.chat.id] = {usr: 0 for usr in DATA[message.chat.id].keys()}
            save_data()

            bot.reply_to(message, 'Cleared balance')

            get_balance(message)


        try:

            print('Bot is running!')
            bot.infinity_polling()
            
        except KeyboardInterrupt:

            print('Interrupted')
            with open('cash_data.yaml', 'w') as outfile:
                yaml.dump(DATA, outfile, default_flow_style=False)
            print('Cash data saved')

            try:
                sys.exit(130)
            except SystemExit:
                os._exit(130)    
