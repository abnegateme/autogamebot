import requests
import telebot
import time
import json
from os.path import dirname, realpath, exists, join
from os import makedirs

from tesser import get_letters_from_image

class TBotWrapper:
  def __init__(self):
    self._proxy_url = ''
    self._TOKEN = ''
    self._bot_request_base_url = f'https://api.telegram.org/bot{self._TOKEN}/'


# SELF BOT
  def bot_run(self):
    telebot.apihelper.proxy = {'http': self._proxy_url, 'https': self._proxy_url}
    bot = telebot.TeleBot(self._TOKEN)

    try:
      bot_info = bot.get_me()
    except:
      print('Could not connect to proxy: is the Tor running?')
      return

    print(bot_info)

    image_directory = join(dirname(realpath(__file__)), 'data')
    if not exists(image_directory):
      makedirs(image_directory)

    @bot.message_handler(content_types=["photo"])
    def handle_command(message):
      """
      message.photo -> array of PhotoSize object (ascending)
      bot.get_file(file_id) -> File object
      bot.download_file(file_info.file_path) -> image bit string
      """
      file_id = message.photo[-1].file_id
      file_info = bot.get_file(file_id)
      downloaded_file = bot.download_file(file_info.file_path)
      image_path = join(image_directory, file_id + '.png')
      with open(image_path,'wb') as new_file:
        new_file.write(downloaded_file)

      letters = get_letters_from_image(image_path)
      bot.send_message(message.chat.id, letters)

    bot.polling()


# BOT TUTORIAL RUN
  def bot_tutorial_run(self):
    telebot.apihelper.proxy = {'http': self._proxy_url, 'https': self._proxy_url}
    bot = telebot.TeleBot(self._TOKEN)

    print(bot.get_me())

    def log(message, answer):
      print('\n ------')
      from datetime import datetime
      print(datetime.now())
      print('Message from {0} {1}. (id = {2}) \n Text - {3}'.format(
        message.from_user.first_name,
        message.from_user.last_name,
        str(message.from_user.id),
        message.text
      ))

    @bot.message_handler(commands=['help'])
    def handle_command(message):
      bot.send_message(message.chat.id, 'test help message')

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
      if message.text == 'a':
        answer = 'b'
        bot.send_message(message.chat.id, answer)
        log(message, answer)
      elif message.text == 'b':
        answer = 'c'
        bot.send_message(message.chat.id, answer)
        log(message, answer)
      else:
        answer = 'what is it?'
        bot.send_message(message.chat.id, 'what is it?')
        log(message, answer)

    bot.polling()


# BOT TEST RUN (from documentation)
  def bot_test_run(self):
    telebot.apihelper.proxy = {'http': self._proxy_url, 'https': self._proxy_url}
    bot = telebot.TeleBot(self._TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
      bot.reply_to(message, "Howdy, how are you doing?")

    @bot.message_handler(func=lambda m: True)
    def echo_all(message):
      bot.reply_to(message, message.text)

    @bot.message_handler(commands=['photo'])
    def image_handler(message):
      bot.reply_to(message, 'get image')
      print(message)

    bot.polling()


  def manual_request(self):
    session = requests.session()
    session.proxies = {'http': self._proxy_url, 'https': self._proxy_url}
    get_updates_url = self._bot_request_base_url + 'getUpdates'
    send_message_url = self._bot_request_base_url + 'sendmessage?chat_id=<chat-id>&text=success'
    r = session.get(get_updates_url)
    print('getUpdates response:', r.text)
    print('-'*20)
    r = session.get(send_message_url)
    print('sendmessage response:', r.text)


  def check_proxies(self):
    proxies = {'http': self._proxy_url, 'https': self._proxy_url}
    check_ip_url = 'http://httpbin.org/ip'
    print(requests.get(check_ip_url, proxies=proxies).text)
    print('-'*20)
    print(requests.get(check_ip_url).text)


if __name__ == "__main__":
    tbot = TBotWrapper()
    tbot.bot_run()