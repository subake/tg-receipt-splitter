import yaml

from my_bot import ReceiptSplitterBot



if __name__ == '__main__':

    # open config file
    try:
        print('Opening config file...')
        CONFIG = yaml.safe_load(open('config.yaml', 'r'))
    except Exception as e:
        print(e)
        print('Error opening config file.')
        quit()

    print('Starting bot...')
    bot = ReceiptSplitterBot(CONFIG)