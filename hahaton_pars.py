import telebot
from telebot import types
import asyncio
import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup

bot = telebot.TeleBot('6019386505:AAFZcdkry75sTkZ-ZE9pgdMsFFWFc7PU3_o')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(types.KeyboardButton('Ввести запрос'))
messageChatId = None
websites = [
    "https://www.sport-express.ru/",
    "https://sportarena.com/",
    "https://rsport.ria.ru/",
    "https://www.sovsport.ru/",
    "https://sportrbc.ru/",
    "https://www.sports.ru/",
    "https://yandex.ru/sport/",
    "https://www.championat.com/",
    "https://news.sportbox.ru/",
    "https://matchtv.ru/news",
    "https://sport24.ru/",
    "https://sport.rambler.ru/",
    "https://lenta.ru/rubrics/sport/"
]
blacklist = []
###########################START################################
@bot.message_handler(commands=['start'])
def start(message):
	global messageChatId
	print("new session test")
	messageChatId = int(message.chat.id)
	print(f"user_id: {messageChatId}")

	reg1 = bot.send_message(message.chat.id, 'Выбери нужное действие :)', reply_markup=markup)
	bot.register_next_step_handler(reg1, function1)

@bot.message_handler(content_types=['text'])
def function1(message):
	global messageChatId
	messageChatId = int(message.chat.id)
	if message.text == "Ввести запрос":
		reg2 = bot.send_message(message.chat.id, "Введите запрос...", reply_markup=types.ReplyKeyboardRemove())
		bot.register_next_step_handler(reg2, function2)

	elif message.text == "/start":
		test = bot.send_message(message.chat.id, "Что?)")
		bot.register_next_step_handler(test, start)

	else:
		reg3 = bot.send_message(message.chat.id, "А больше функционала то нет", reply_markup=markup)
		bot.register_next_step_handler(reg3, start)

def function2(message):
	if message.text not in ["start","/start","Ввести запрос"]:
		messageChatId = int(message.chat.id)
		bot.send_message(message.chat.id, "Произвожу поиск..")

		loop = asyncio.new_event_loop()
		loop.run_until_complete(search_word_on_websites(message.text, websites))
		reg4 =  bot.send_message(message.chat.id, "Завершено!", reply_markup=markup)
		bot.register_next_step_handler(reg4, start)

async def process_website(session, site, word):
	global messageChatId
	try:
		async with session.get(site) as response:
			if response.status == 200:
				soup = BeautifulSoup(await response.text(), 'html.parser')
				text_blocks = soup.find_all(text=lambda text: text and word.lower() in text.lower())
				if text_blocks:
					printed_sentences = set()
					for block in text_blocks:
						sentence = block.strip()
						if sentence and sentence not in printed_sentences and '{"@' not in sentence:
							if len(sentence) <25:
								printed_sentences.add(sentence)
								bot.send_message(messageChatId, f"'{word}' найдено на\n{site}\n{sentence}")
								break
			else:
				print("")
				blacklist.append(site)
	except aiohttp.ClientError as e:
		print("")
		blacklist.append(site)

async def search_word_on_websites(word, websites):
	global messageChatId
	async with aiohttp.ClientSession() as session:
		tasks = []
		for site in websites:
			tasks.append(process_website(session, site, word))
		await asyncio.gather(*tasks)
##########################STARTING###############################
async def startpoling():
    try:
        print("started")
        bot.polling(non_stop=True)
    finally:
        print("stopped")
        bot.stop_polling()


if __name__ == "__main__":
    asyncio.run(startpoling())
