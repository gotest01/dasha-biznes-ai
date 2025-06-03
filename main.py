import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import openai
import aiohttp

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
GPT_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

openai.api_key = GPT_KEY
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def gpt_reply(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}],
            max_tokens=500,
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Ошибка GPT: {e}"

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("Привет! Я Даша — бизнес-бот.\nВот что я умею:\n/ask — задать вопрос GPT\n/btc — курс биткоина\n/stocks — фондовый рынок\n/news — рыночные новости")

@dp.message_handler(commands=['ask'])
async def ask_cmd(message: types.Message):
    await message.reply("Напиши мне свой вопрос.")

@dp.message_handler(commands=['btc'])
async def btc_cmd(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json") as resp:
                data = await resp.json()
                price = data['bpi']['USD']['rate']
                await message.reply(f"Курс BTC: ${price}")
    except Exception as e:
        await message.reply(f"Ошибка при получении данных: {e}")

@dp.message_handler(commands=['stocks'])
async def stocks_cmd(message: types.Message):
    await message.reply("📈 Индексы: S&P 500 — ~5200, Nasdaq — ~16500")

@dp.message_handler(commands=['news'])
async def news_cmd(message: types.Message):
    await message.reply("🗞️ Новости: 📉 Рынки ждут отчётов. BTC стабилен. Индексы растут.")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def text_handler(message: types.Message):
    await message.chat.do("typing")
    reply = await gpt_reply(message.text)
    await message.reply(reply)

    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        username = message.from_user.username or message.from_user.first_name
        alert = f"📩 Вопрос от @{username}:\n{message.text}"
        await bot.send_message(ADMIN_ID, alert)

if __name__ == '__main__':
    print("✅ Dasha-Biznes.AI готова к работе.")
    executor.start_polling(dp, skip_updates=True)
