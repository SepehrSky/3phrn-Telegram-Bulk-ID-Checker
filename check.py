from telethon.sync import TelegramClient, functions, errors
import configparser
import os
import time
import random

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('default', 'api_id')
api_hash = config.get('default', 'api_hash')

if api_id == 'UPDATE ME' or api_hash == 'UPDATE ME':
    print("Please read the config.ini and README.md")
    input()
    exit()
else:
    api_id = int(api_id)

# Load Telegram accounts from accounts.txt
accounts_file = config.get('default', 'accounts_file', fallback="accounts.txt")
with open(accounts_file, 'r') as accounts_file:
    accounts = [line.strip() for line in accounts_file]

client = None

class RateLimiter:
    def __init__(self, limit_per_second):
        self.limit_per_second = limit_per_second
        self.last_request_time = time.time()

    def delay_request(self):
        current_time = time.time()
        time_difference = current_time - self.last_request_time
        if time_difference < 1 / self.limit_per_second:
            delay = 1 / self.limit_per_second - time_difference
            time.sleep(delay)
        self.last_request_time = time.time()

def get_random_proxy():
    # Load proxy list from proxylist.txt
    proxy_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proxylist.txt')
    with open(proxy_file_path, 'r') as proxy_file:
        proxies = [line.strip() for line in proxy_file]

    # Select a random proxy
    return random.choice(proxies)

def init_client(account):
    global client
    phone_number, _, _ = account.split(':')
    client = TelegramClient(phone_number, api_id, api_hash, proxy=get_random_proxy())
    client.connect()

def user_lookup(account, rate_limiter):
    try:
        rate_limiter.delay_request()
        result = client(functions.account.CheckUsernameRequest(username=account))
        if result:
            print("The telegram", account, "is available")
            file = open(output(), 'a')
            file.write("%s\n" % (account))
            file.close()
        else:
            print("The telegram", account, "is not available")
    except errors.FloodWaitError as fW:
        print("Hit the rate limit, waiting", fW.seconds, "seconds")
        time.sleep(fW.seconds)
    except errors.UsernameInvalidError as uI:
        print("Username is invalid")
    except errors.rpcbaseerrors.BadRequestError as bR:
        print("Error:", bR.message)

def get_words(rate_limiter):
    words = []
    delay = config.get('default', 'delay')
    path = os.path.join("word_lists", config.get('default', 'wordList'))
    if path is not None:
        file = open(path, 'r', encoding='utf-8-sig')
        words = file.read().split('\n')
        file.close()
    else:
        print("Word list not found.")

    for i in range(len(words)):
        name = words[i]
        user_lookup(name, rate_limiter)
        time.sleep(int(delay))
    print("All done")
    input("Press enter to exit...")

def output():
    return config.get('default', 'outPut', fallback="AVAILABLE.txt")

def main():
    print('''
    ▄▄▄█████▓▓█████  ██▓    ▓█████   ▄████  ██▀███   ▄▄▄       ███▄ ▄███▓
    ▓  ██▒ ▓▒▓█   ▀ ▓██▒    ▓█   ▀  ██▒ ▀█▒▓██ ▒ ██▒▒████▄    ▓██▒▀█▀ ██▒
    ▒ ▓██░ ▒░▒███   ▒██░    ▒███   ▒██░▄▄▄░▓██ ░▄█ ▒▒██  ▀█▄  ▓██    ▓██░
    ░ ▓██▓ ░ ▒▓█  ▄ ▒██░    ▒▓█  ▄ ░▓█  ██▓▒██▀▀█▄  ░██▄▄▄▄██ ▒██    ▒██
      ▒██▒ ░ ░▒████▒░██████▒░▒████▒░▒▓███▀▒░██▓ ▒██▒ ▓█   ▓██▒▒██▒   ░██▒
      ▒ ░░   ░░ ▒░ ░░ ▒░▓  ░░░ ▒░ ░ ░▒   ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ░  ░
        ░     ░ ░  ░░ ░ ▒  ░ ░ ░  ░  ░   ░   ░▒ ░ ▒░  ▒   ▒▒ ░░  ░      ░
      ░         ░     ░ ░      ░   ░ ░   ░   ░░   ░   ░   ▒   ░      ░
                  ░  ░    ░  ░   ░  ░      ░    ░           ░  ░       ░
                                                                         
                                - Username Checker -
                                       3phrn
            ''')
    print("1 = Enter username manually\n2 = Read a list of usernames from the word_lists folder")
    set = ["1", "2"]
    option = input("Select your option: ")
    rate_limiter = RateLimiter(0.2)  # Adjust the rate limit as needed

    while True:
        if str(option) in set:
            if option == set[0]:
                name = input("Enter a username: ")
                for account in accounts:
                    init_client(account)
                    user_lookup(name, rate_limiter)
                    client.disconnect()
            else:
                for account in accounts:
                    init_client(account)
                    get_words(rate_limiter)
                    client.disconnect()
                break
        else:
            option = input("1 or 2 ... Please!: ")

if __name__ == "__main__":
    main()
