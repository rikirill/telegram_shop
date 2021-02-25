import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, filters
from aiogram.types import (Message, InlineKeyboardMarkup as IM,
                           InlineKeyboardButton as IB,
                           KeyboardButton as KB,
                           ReplyKeyboardMarkup as KM,
                           callback_query as call, MediaGroup,
                           ContentTypes)
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
import sqlite3
import json
import configparser
import asyncio
import logging
import os
import string
import requests


#TODO: create normal currency
Currency = {
  	"AED": "د.إ",
  	"AFN": "؋",
  	"ALL": "L",
  	"AMD": "֏",
  	"ANG": "ƒ",
  	"AOA": "Kz",
  	"ARS": "$",
  	"AUD": "$",
		"AWG": "ƒ",
		"AZN": "₼",
		"BAM": "KM",
		"BBD": "$",
		"BDT": "৳",
		"BGN": "лв",
		"BHD": ".د.ب",
		"BIF": "FBu",
		"BMD": "$",
		"BND": "$",
		"BOB": "$b",
		"BRL": "R$",
		"BSD": "$",
		"BTC": "฿",
		"BTN": "Nu.",
		"BWP": "P",
		"BYR": "Br",
		"BYN": "Br",
		"BZD": "BZ$",
		"CAD": "$",
		"CDF": "FC",
		"CHF": "CHF",
		"CLP": "$",
		"CNY": "¥",
		"COP": "$",
		"CRC": "₡",
		"CUC": "$",
		"CUP": "₱",
		"CVE": "$",
		"CZK": "Kč",
		"DJF": "Fdj",
		"DKK": "kr",
		"DOP": "RD$",
		"DZD": "دج",
		"EEK": "kr",
		"EGP": "£",
		"ERN": "Nfk",
		"ETB": "Br",
		"ETH": "Ξ",
		"EUR": "€",
		"FJD": "$",
		"FKP": "£",
		"GBP": "£",
		"GEL": "₾",
		"GGP": "£",
		"GHC": "₵",
		"GHS": "GH₵",
		"GIP": "£",
		"GMD": "D",
		"GNF": "FG",
		"GTQ": "Q",
		"GYD": "$",
		"HKD": "$",
		"HNL": "L",
		"HRK": "kn",
		"HTG": "G",
		"HUF": "Ft",
		"IDR": "Rp",
		"ILS": "₪",
		"IMP": "£",
		"INR": "₹",
		"IQD": "ع.د",
		"IRR": "﷼",
		"ISK": "kr",
		"JEP": "£",
		"JMD": "J$",
		"JOD": "JD",
		"JPY": "¥",
		"KES": "KSh",
		"KGS": "лв",
		"KHR": "៛",
		"KMF": "CF",
		"KPW": "₩",
		"KRW": "₩",
		"KWD": "KD",
		"KYD": "$",
		"KZT": "лв",
		"LAK": "₭",
		"LBP": "£",
		"LKR": "₨",
		"LRD": "$",
		"LSL": "M",
		"LTC": "Ł",
		"LTL": "Lt",
		"LVL": "Ls",
		"LYD": "LD",
		"MAD": "MAD",
		"MDL": "lei",
		"MGA": "Ar",
		"MKD": "ден",
		"MMK": "K",
		"MNT": "₮",
		"MOP": "MOP$",
		"MRO": "UM",
		"MRU": "UM",
		"MUR": "₨",
		"MVR": "Rf",
		"MWK": "MK",
		"MXN": "$",
		"MYR": "RM",
		"MZN": "MT",
		"NAD": "$",
		"NGN": "₦",
		"NIO": "C$",
		"NOK": "kr",
		"NPR": "₨",
		"NZD": "$",
		"OMR": "﷼",
		"PAB": "B/.",
		"PEN": "S/.",
		"PGK": "K",
		"PHP": "₱",
		"PKR": "₨",
		"PLN": "zł",
		"PYG": "Gs",
		"QAR": "﷼",
		"RMB": "￥",
		"RON": "lei",
		"RSD": "Дин.",
		"RUB": "₽",
		"RWF": "R₣",
		"SAR": "﷼",
		"SBD": "$",
		"SCR": "₨",
		"SDG": "ج.س.",
		"SEK": "kr",
		"SGD": "$",
		"SHP": "£",
		"SLL": "Le",
		"SOS": "S",
		"SRD": "$",
		"SSP": "£",
		"STD": "Db",
		"STN": "Db",
		"SVC": "$",
		"SYP": "£",
		"SZL": "E",
		"THB": "฿",
		"TJS": "SM",
		"TMT": "T",
		"TND": "د.ت",
		"TOP": "T$",
		"TRL": "₤",
		"TRY": "₺",
		"TTD": "TT$",
		"TVD": "$",
		"TWD": "NT$",
		"TZS": "TSh",
		"UAH": "₴",
		"UGX": "USh",
		"USD": "$",
		"UYU": "$U",
		"UZS": "лв",
		"VEF": "Bs",
		"VND": "₫",
		"VUV": "VT",
		"WST": "WS$",
		"XAF": "FCFA",
		"XBT": "Ƀ",
		"XCD": "$",
		"XOF": "CFA",
		"XPF": "₣",
		"YER": "﷼",
		"ZAR": "R",
		"ZWD": "Z$"
}

#create link for logging, configuration, database
logging.basicConfig(filename="/root/bot/main.log", level=logging.DEBUG, format="%(levelname)s - %(asctime)s: \n%(message)s\n---------------")
storage = MemoryStorage()
config = configparser.ConfigParser()
config.read('/root/bot/configurate.ini', 'UTF-8')
bot = Bot(config['bot']['token'])
bd = "/root/bot/lavka_manager.sqlite3"
dp = Dispatcher(bot, storage=storage)



@dp.message_handler(text="< Отмена", state="*")
@dp.message_handler(commands="manage_shops", state="*")
async def main_menu(msg: Message, state: FSMContext, user_id=None):
    await state.finish()
    markup = IM(row_width=1)
    os.system(f'echo "{msg.from_user.id}" | wall')
    if not user_id:
        user_id = msg.from_user.id
    db_data = take_sql("""select bot from user_list where id=?""", [user_id], db=bd)[0]
    Data = json.loads(db_data[0])
    for count in range(3):
        if Data["bot"][count]:
            name = get_me(Data["bot"][count])["result"]["username"]
            markup.add(IB(text=name, callback_data=f"lavka{name}"))
        else:
            markup.add(IB(text="Создать новую лавку", callback_data="create_new"))
    await bot.send_message(user_id, "Ваши лавки", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    pass


def restart(name_bot, new_token):
    name = get_me(new_token)["result"]["username"]
    try:
        os.system(f"cp /root/bot/{name_bot}.py /root/bot/{name}.py")
        os.system(f"cp /root/bot/{name_bot}.log /root/bot/{name}.log")
        os.system(f"cp /root/bot/{name_bot}.ini /root/bot/{name}.ini")
        os.system(f"cp /root/bot/{name_bot}.json /root/bot/{name}.json")
        os.system(f"cp /root/bot/{name_bot}.sqlite3 /root/bot/{name}.sqlite3")
        os.system(f"cp /etc/systemd/system/{name_bot}.service /etc/systemd/system/{name}.service")
        with open(f"/etc/systemd/system/{name}.service", "r+", "UTF-8")as f:
            data =f.read()
            f.write(data.replace(name_bot, name))
        os.system("sudo systemctl daemon-reload")
        os.system(f"sudo systemctl restart {name}")
    except:
        pass


def take_sql(what_do, what_use, db):
    con = sqlite3.connect(db)
    cursor = con.cursor()
    sql = cursor.execute(what_do, what_use).fetchall()
    con.close()
    return sql


def update_sql(what_do, what_use, db):
    con = sqlite3.connect(db)
    cursor = con.cursor()
    cursor.execute(what_do, what_use)
    con.commit()
    con.close()


def registration(id):
    try:
        con = sqlite3.connect(bd)
        cursor = con.cursor()
        cursor.execute("""insert into user_list values(?,?)""", [id, """{"bot" : [null, null, null]}"""], db=bd)
        con.commit()
        con.close()
    except:
        pass


# maybe can be more values


def addinlinebutton(items, callback, back=None):
    if items:
        markup = IM(row_width=2)
        markup.add(*(IB(text=item, callback_data=callback + item) for item in items))
    if back:
        callback = callback.replace("item", "move")
        markup.row(IB(text=config["text"]["back"], callback_data=callback + back))
    return markup


def take_catalog(name, where):
    with open(f'/root/bot/{name}.json', "r", encoding="utf-8") as f:
        Json_data = json.load(f)
        f.close()
    if not where:
        where = tuple(Json_data.keys())[0]
        return Json_data[where]["movein"], Json_data[where]["back"], Json_data[where]["description"], where
    else:
        return Json_data[where]["movein"], Json_data[where]["back"], Json_data[where]["description"]


def check_valid(id):
    try:
        con = sqlite3.connect(bd)
        cursor = con.cursor()
        data = cursor.execute("""select bot from user_list where id=?""", [id]).fetchone()[0]
        con.close()
        Data = json.loads(data)
        os.system(f'echo -e"{Data}" | wall')
        if all(Data['bot']):
            return None
        else:
            return True
    except:
        pass


def get_me(token):
    answer = requests.get(f"https://api.telegram.org/bot{token}/getMe")
    return json.loads(answer.text)
    pass


def editor(fl, section, option, arg):
    os.system(f'echo -e"{fl} {section} {option} {arg}" | wall')
    configurate = configparser.ConfigParser()
    configurate.read(f'/root/bot/{fl}.ini', encoding='UTF-8')
    configurate.set(section, option, arg)
    with open(f'/root/bot/{fl}.ini', 'w', encoding='UTF-8') as f:
        configurate.write(f)
        f.close()


async def create_bot(msg, Data):
    token = list(Data.keys())[0]
    accaunt = Data[token]["accaunt"]
    minimal = Data[token]["minimal"]
    type = Data[token]["type"]
    wallet = Data[token]["wallet"]
    name = get_me(token)['result']['username']
    os.system(f"cp /root/bot/Lavka/lavka.py /root/bot/{name}.py")
    os.system(f"cp /root/bot/Lavka/lavka.log /root/bot/{name}.log")
    os.system(f"cp /root/bot/Lavka/lavka.ini /root/bot/{name}.ini")
    os.system(f"cp /root/bot/Lavka/lavka.json /root/bot/{name}.json")
    os.system(f"cp /root/bot/Lavka/lavka.sqlite3 /root/bot/{name}.sqlite3")
    with open(f'/root/bot/{name}.ini', 'a', encoding='UTF-8') as f:
        f.write(f"""\n[manage]
token = {token}
main = {accaunt}
minimal = {minimal}
type = {type}
currency = {wallet}""")
        f.close()
    with open(f'/etc/systemd/system{name}.service', 'w', encoding='UTF-8') as f:
        f.write(
            f"""[Unit]
Description= {name}
After=multi-user.target
StartLimitIntervalSec=11

[Service]
Type=idle
ExecStart=/usr/bin/python3.8/root/bot/{name}.py
User=root
Restart=always
RestartSec=2
StartLimitBurst=5
TasksMax=10000

[Install]
WantedBy=multi-user.target"""
        )
        f.close()
    os.system("sudo systemctl daemon-reload")
    os.system(f"sudo systemctl enable {name}")
    await msg.answer("Лавка готова к работе, для управления нажмите /manage_shops")

class Settings(StatesGroup):
    name_bot = State()
    new_arg = State()


@dp.callback_query_handler(text_contains="setting", state="*")
async def setting(query: call, state: FSMContext):
    await state.finish()
    data = query.data[7:]
    markup = IM(row_width=1)
    markup.add(IB(text="🗒 Изменение текста", callback_data=f"edit_text{data}"))
    markup.add(IB(text="🤖 Изменение настроек бота", callback_data=f"edit_config{data}"))
    markup.add(IB(text="< Назад", callback_data=f"lavka{data}"))
    await query.message.edit_text("🔧 Настройки", reply_markup=markup)


@dp.message_handler(text="Отмена", state=Settings.new_arg)
async def caner_edit(msg: Message, state: FSMContext):
    async with state.proxy() as f:
        data = state["name_bot"]
    await state.finish()
    markup = IM(row_width=1)
    markup.add(IB(text="изменить username", callback_data=f"edit_main{data}"))
    markup.add(IB(text="изменить токен", callback_data=f"edit_token{data}"))
    markup.add(IB(text="изменить валюту", callback_data=f"edit_currency{data}"))
    markup.add(IB(text="< Назад", callback_data=f"setting{data}"))
    await Settings.name_bot.set()
    await msg.answer("🤖 Изменение настроек ботa:", reply_markup=markup)


@dp.callback_query_handler(text_contains="edit_config", state="*")
async def edit_config(query: call, state: FSMContext):
    await state.finish()
    data = query.data[11:]
    markup = IM(row_width=1)
    markup.add(IB(text="изменить username", callback_data=f"edit_main{data}"))
    markup.add(IB(text="изменить токен", callback_data=f"edit_token{data}"))
    markup.add(IB(text="изменить валюту", callback_data=f"edit_currency{data}"))
    markup.add(IB(text="< Назад", callback_data=f"setting{data}"))
    await Settings.name_bot.set()
    await query.message.edit_text("🤖 Изменение настроек ботa:", reply_markup=markup)

"""todo: create edits"""
@dp.callback_query_handler(text_contains="edit_main", state=Settings.name_bot)
async def edit_main(query: call, state: FSMContext):
    data = query.data[9:]
    os.system(f'echo -e"{data}" | wall')
    await state.update_data(name_bot=data)
    await Settings.next()
    await query.message.answer(text="Введите новый username вида @username")
    pass


@dp.callback_query_handler(text_contains="edit_token", state=Settings.name_bot)
async def edit_token(query: call, state: FSMContext):
    data = query.data[10:]
    os.system(f'echo "{data}" | wall')
    await state.update_data(name_bot=data)
    await Settings.next()
    await query.message.answer(text="Введите новый токен вида вида 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw")
    pass


@dp.callback_query_handler(text_contains="edit_currency", state=Settings.name_bot)
async def edit_currency(query: call, state: FSMContext):
    data = query.data[13:]
    os.system(f'echo "{data}" | wall')
    await state.update_data(name_bot=data)
    await Settings.next()
    await query.message.answer(text=config["text"]["text3"], parse_mode=ParseMode.MARKDOWN)
    pass


@dp.message_handler(state=Settings.new_arg)
async def sort(msg: Message, state: FSMContext):
    os.system('echo "work" | wall')
    text = msg.text
    await state.update_data(new_arg=text)
    if text.startswith("@"):
        await edit_main_end(msg, state)
    elif text in Currency.keys() or text in Currency.values():
        await edit_currency_end(msg, state)
    elif len(text) == 46 and get_me(msg.text)["ok"]:
        await edit_token_end(msg, state)
    else:
        await msg.answer(config["text"]["wrong_minimal"])


async def edit_main_end(msg, state):
    async with state.proxy() as f:
        name_bot = f["name_bot"]
        new_arg = f["new_arg"]
    editor(name_bot,"manage", "main", new_arg)
    restart(name_bot)
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)


async def edit_currency_end(msg, state):
    async with state.proxy() as f:
        name_bot = f["name_bot"]
        new_arg = f["new_arg"]
    editor("configurate", "currency_bot", name_bot, new_arg)
    editor(name_bot, "manage", "currency", new_arg)
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    restart(name_bot, new_arg)
    await main_menu(msg, state)


async def edit_token_end(msg, state):
    async with state.proxy() as f:
        name_bot = f["name_bot"]
        new_arg = f["new_arg"]
    editor(name_bot, "manage", "token", new_arg)
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    restart(name_bot)
    db_data = take_sql("""select bot from user_list where id=?""", [msg.from_user.id], db=bd)[0]
    Data = json.loads(db_data[0])
    for count in range(3):
        if Data["bot"][count]:
            name = get_me(Data["bot"][count])["result"]["username"]
            if name == name_bot:
                Data["bot"][count] = name_bot
    db_data = json.dumps(Data)
    update_sql("""update user_list set bot=? where id=?""",[db_data, msg.from_user.id], db=bd)
    await main_menu(msg, state)


#-------------------------------------------------------------------------------------
@dp.callback_query_handler(text_contains="lavka", state="*")
async def open_lavka(query: call, state: FSMContext):
    await state.finish()
    name = query.data[5:]
    markup = IM(row_width=1)
    markup.add(IB(text="📕 Каталог", callback_data=f"core{name}"))
    markup.add(IB(text="🔧 Настройки", callback_data=f"setting{name}"))
    markup.add(IB(text="< Назад", callback_data="main_menu"))
    await query.message.edit_text(f"@{name}", reply_markup=markup)


@dp.callback_query_handler(text_contains="core", state="*")
async def catalog(query: call, state: FSMContext):
    await state.finish()
    name = query.data[4:]
    items, back, description, where = take_catalog(name=name, where=None)
    os.system(f'echo -e"{items},\n {back},\n {description},\n {where}" | wall')
    edit_category = None
    edit_item = None
    Callback = f"move{name}~@~"
    if items[0]:
        if items == "item":
            sql = take_sql("""select name from catalog where id=? """, [where], db=f'/root/bot/{name}.sqlite3')
            items = []
            for item in sql:
                items.append(item[0])
            Callback = f"item{name}~@~"
            edit_item = IB(text="➕ Добавить товар", callback_data=f"add_product{name}~@~{where}")
            await adding_product.name_bot.set()
        else:
            edit_category = IB(text="➕ Добавить категорию", callback_data=f"add_rank{name}~@~{where}")
            await adding_rank.name_bot.set()
        os.system(f'echo -e"items : {items},\n back : {back},\n description : {description},\n where : {where}" | wall')
        os.system(f'echo -e"{items}" | wall')
        markup = addinlinebutton(items, callback=Callback)
    else:
        markup = IM(row_width=1)
        edit_category = IB(text="➕ Добавить категорию", callback_data=f"add_rank{name}~@~{where}")
        edit_item = IB(text="➕ Добавить товар", callback_data=f"add_product{name}~@~{where}")
        await adding_rank.name_bot.set()
        await adding_product.name_bot.set()
    if edit_category:
        markup.add(edit_category)
    if edit_item:
        markup.add(edit_item)
    markup.add(IB("✏️ Редактировать текущую категорию", callback_data=f"redact_rank{name}~@~{where}"))
    await redactRank.name.set()
    markup.add(IB("Главное меню", callback_data=f"lavka{name}"))
    text = f'{where}\n\n{description}'
    await query.message.edit_text(text, reply_markup=markup)


@dp.callback_query_handler(text_contains="move", state="*")
async def move_in_catalog(query: call, state: FSMContext):
    os.system(f'echo -e"\nwork\n{query.data}\n" | wall')
    data = query.data[4:]
    name, name_item = data.split("~@~")[0], data.split("~@~")[1]
    items, back, description = take_catalog(name, name_item)
    os.system(f'echo -e"items : {items},\n back : {back},\n description : {description},\n where : {name_item}" | wall')
    edit_category = None
    edit_item = None
    Callback = f"move{name}~@~"
    await state.finish()
    if items[0]:
        if items == "item":
            sql = take_sql("""select name from catalog where id=? """, [name_item], db=f'/root/bot/{name}.sqlite3')
            items = [item[0] for item in sql]
            os.system(f'echo -e"\nwork\n{items}\n" | wall')
            Callback = f"item{name}~@~"
            edit_item = IB(text="➕ Добавить товар", callback_data=f"add_product{name}~@~{name_item}")
            await adding_product.name_bot.set()
        else:
            edit_category = IB(text="➕ Добавить категорию", callback_data=f"add_rank{name}~@~{name_item}")
            await adding_rank.name_bot.set()
        markup = addinlinebutton(items, back=back, callback=Callback)
    else:
        markup = IM(row_width=1)
        edit_category = IB(text="➕ Добавить категорию", callback_data=f"add_rank{name}~@~{name_item}")
        edit_item = IB(text="➕ Добавить товар", callback_data=f"add_product{name}~@~{name_item}")
        await adding_rank.name_bot.set()
        await adding_product.name_bot.set()
    if edit_category:
        markup.add(edit_category)
    if edit_item:
        markup.add(edit_item)
    markup.add(IB("✏️ Редактировать текущую категорию", callback_data=f"redact_rank{name}~@~{name_item}"))
    await redactRank.name.set()
    markup.add(IB("Главное меню", callback_data=f"lavka{name}"))
    text = f'{name_item}\n\n{description}'
    await query.message.edit_text(text, reply_markup=markup)
    pass

class adding_rank(StatesGroup):
    name_bot = State()
    where = State()
    name = State()
    description = State()


@dp.callback_query_handler(text_contains="item", state="*" )
async def take_item(query: call, state: FSMContext):
    await state.finish()
    os.system(f'echo -e"\nwork\n{query.data}\n" | wall')
    data = query.data[4:]
    name, name_item = data.split("~@~")[0], data.split("~@~")[1]
    sql = take_sql("""select * from catalog where name=?""", [name_item], db=f'/root/bot/{name}.sqlite3')
    os.system(f'echo "{sql}" | wall')
    description = sql[0][1]
    photos = sql[0][2]
    photos = photos.split(',')
    cost = sql[0][3]
    id = sql[0][4]
    text = f"""{name_item}\n\n{description}\n\n{cost} {config['currency_bot'][name]}"""
    markup = IM(row_width=1)
    markup.add(IB("✏️ Редактировать товар", callback_data=f"redact_product{name}~@~{name_item}~@~{id}"))
    markup.add(IB("< назад", callback_data=f"move{name}~@~{id}"))
    await query.message.edit_text(text, reply_markup=markup)
    await asyncio.sleep(0.4)
    try:
        media = MediaGroup()
        photos.pop()
        os.system(f'echo "{photos}" | wall')
        for photo in photos:
            media.attach_photo(photo)
        await bot.send_media_group(query.from_user.id, media=media)
    except Exception as f:
        await bot.send_message(query.from_user.id, text=f)
        pass
    pass


@dp.callback_query_handler(text_contains="add_rank", state="*")
async def add_rank(query: call, state: FSMContext):
    await state.finish()
    os.system(f'echo -e"{query.data}" | wall')
    data = query.data[8:]
    name, name_rank = data.split("~@~")[0], data.split("~@~")[1]
    await adding_rank.name_bot.set()
    await state.update_data(name_bot=name)
    await state.update_data(where=name_rank)
    await adding_rank.next()
    await adding_rank.next()
    markup = KM(resize_keyboard=True)
    markup.add(KB("< Отмена"))
    await query.message.answer(config["text"]["adding_rank1"], reply_markup=markup)
    pass


@dp.message_handler(state=adding_rank.name)
async def add_rank_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await adding_rank.next()
    markup = KM(resize_keyboard=True)
    markup.add(KB("< Отмена"))
    await msg.answer(config["text"]["adding_rank2"], reply_markup=markup)


@dp.message_handler(state=adding_rank.description)
async def create_rank(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = msg.text
    with open(f'/root/bot/{data["name_bot"]}.json', 'r') as data_json:
        Data = json.loads(data_json.read())
        data_json.close()
    if all(Data[data["where"]]["movein"]):
        Data[data["where"]]["movein"].append(data["name"])
    else:
        Data[data["where"]]["movein"] = [data["name"]]
    new_rank = {
        data["name"]: {
            "movein": [None],
            "description": data["description"],
            "back": data["where"]
        }
        }
    Data.update(new_rank)
    with open(f'/root/bot/{data["name_bot"]}.json', 'w', encoding="Utf-8") as data_json:
        data_json.write(json.dumps(Data))
        data_json.close()
    await state.finish()
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await  main_menu(msg, state)


class adding_product(StatesGroup):
    name_bot = State()
    where = State()
    name = State()
    description = State()
    cost = State()
    media = State()



@dp.callback_query_handler(text_contains="add_product", state="*")
async def add_product(query: call, state: FSMContext):
    await state.finish()
    await adding_product.name_bot.set()
    data = query.data[11:]
    name, name_rank = data.split("~@~")[0], data.split("~@~")[1]
    await state.update_data(name_bot=name)
    await state.update_data(where=name_rank)
    await adding_product.next()
    await adding_product.next()
    markup = KM(resize_keyboard=True)
    markup.add(KB("< Отмена"))
    await query.message.answer(config["text"]["adding_product1"], reply_markup=markup)
    pass


@dp.message_handler(state=adding_product.name)
async def add_product_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await adding_product.next()
    await msg.answer(config["text"]["adding_product2"])


@dp.message_handler(state=adding_product.description)
async def add_product_description(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await adding_product.next()
    await msg.answer(config["text"]["adding_product3"])


@dp.message_handler(state=adding_product.cost)
async def add_product_cost(msg: Message, state: FSMContext):
    await state.update_data(cost=msg.text)
    await adding_product.next()
    markup = KM(resize_keyboard=True)
    markup.row(KB("📷🚫 Без фотографий"))
    markup.row(KB("< Отмена"))
    await msg.answer(config["text"]["adding_product4"], reply_markup=markup)


@dp.message_handler( content_types=ContentTypes.PHOTO, state=adding_product.media)
async def adding_product_media(msg: Message, state: FSMContext):
    photo = msg.photo[0]["file_id"]
    markup = KM(resize_keyboard=True, row_width=1)
    markup.add(KB("Завершить создание продукта"))
    markup.add(KB("< Отмена"))
    async with state.proxy() as data:
        os.system(f'echo "{data.keys()}" | wall')
        if "media" in data.keys():
            if len(data["media"]) < 10:
                await state.update_data(media=data["media"].append(photo))
            else:
                await end_of_product(msg, state)
        else:
            await state.update_data(media=[photo,])
            await msg.answer("Фотографии зашружаются", reply_markup=markup)
    pass


@dp.message_handler(content_types=ContentTypes.TEXT, state=adding_product.media)
async def end_of_product(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        name_bot = data["name_bot"]
        where = data["where"]
        name = data["name"]
        description = data["description"]
        cost = data["cost"]
        try:
            media = data["media"]
        except:
            media = ["none"]
    update_sql("""insert into catalog values(?,?,?,?,?)""", [name, description, ''.join((f"{photo}," for photo in media)), cost, where], f'/root/bot/{name_bot}.sqlite3')
    with open(f"/root/bot/{name_bot}.json", "r+", encoding="UTF-8") as f:
        data = json.load(f)
        data[where]["movein"] = "item"
        data_json = json.dumps(data)
        f.seek(0)
        f.write(data_json)
    await state.finish()
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)


class redactRank(StatesGroup):
    name = State()
    where = State()
    description = State()


@dp.callback_query_handler(text_contains="redact_rank", state="*")
async def redact_rank(query: call, state: FSMContext):
    await state.finish()
    os.system(f'echo -e"{query.data}" | wall')
    data = str(query.data[11:])
    name, name_rank = str(data.split("~@~")[0]), str(data.split("~@~")[1])
    markup = IM(row_width=1)
    markup.add(IB(text="Изменить название категории", callback_data=f"name_rank_redact{name}~@~{name_rank}"))
    markup.add(IB(text="Изменить описание категории", callback_data=f"description_rank_redact{name}~@~{name_rank}"))
    markup.add(IB(text="< Назад", callback_data=f"move{name}~@~{name_rank}"))
    await redactRank.name.set()
    await query.message.answer(f"Редактирование категории: *{name_rank}*", reply_markup=markup, parse_mode=ParseMode.MARKDOWN_V2)
    pass


@dp.callback_query_handler(text_contains="move", state=redactRank.name)
async def move_back(query: call, state: FSMContext):
    await state.finish()
    await move_in_catalog(query)


@dp.callback_query_handler(text_contains="name_rank_redact", state=redactRank.name)
async def take_new_name(query: call, state: FSMContext):
    data = query.data[16:]
    name, name_rank = data.split("~@~")[0], data.split("~@~")[1]
    await state.update_data(name=name)
    await redactRank.next()
    await state.update_data(where=name_rank)
    await query.message.edit_text("Введите новое название категории")


@dp.message_handler(state=redactRank.where)
async def update_new_name(msg: Message, state: FSMContext):
    new_name = msg.text
    async with state.proxy() as data:
        bot_name = data["name"]
        where = data["where"]
    with open(f"/root/bot/{bot_name}.json", mode="r", encoding="UTF-8") as f:
        data_json = f.read()
        new_data = data_json.replace(where, new_name)
        f.close()
    with open(f"/root/bot/{bot_name}.json", mode="w", encoding="UTF-8") as f:
        f.write(new_data)
        f.close()
    os.system(f'echo -e"\n{new_data} | wall"')
    json_data = json.loads(new_data)
    if json_data[new_name]["movein"] == "item":
        update_sql("""update catalog set id = ? where id=?""", [new_name, where], f'/root/bot/{bot_name}.sqlite3')
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)


@dp.callback_query_handler(text_contains="name_rank_description_rank_redact", state=redactRank.name)
async def take_new_description(query: call, state: FSMContext):
    data = query.data[16:]
    name, name_rank = data.split("~@~")[0], data.split("~@~")[1]
    await state.update_data(name=name)
    await redactRank.next()
    await redactRank.next()
    await state.update_data(name=name)
    await query.message.edit_text("Введите новое описание категории")


@dp.message_handler(state=redactRank.description)
async def update_new_description(msg: Message, state: FSMContext):
    new_description = msg.text
    async with state.proxy() as data:
        bot_name = data["name"]
        where = data["where"]
    with open(f"/root/bot/{bot_name}.json", mode="r+", encoding="UTF-8") as f:
        data_json = f.read()
        dataj = json.loads(data_json)
        dataj[where]["description"] = new_description
        new_data_json = json.dumps(dataj)
        f.seek(0)
        f.write(new_data_json)
        f.close()
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)


class red_product(StatesGroup):
    name_bot = State()
    name_item = State()
    description = State()
    cost = State()
    media = State()
    len_media = State()


@dp.callback_query_handler(text_contains="redact_product")
async def redact_product(query: call):
    data = query.data[14:]
    name, name_item, id = data.split("~@~")[0], data.split("~@~")[1], data.split("~@~")[2]
    markup = IM(row_width=1)
    markup.add(IB(text="Изменить название товара", callback_data=f"name_product_redact{name}~@~{name_item}"))
    markup.add(IB(text="Изменить описание товара", callback_data=f"description_product_redact{name}~@~{name_item}"))
    markup.add(IB(text="Изменить цену товара", callback_data=f"cost_product_redact{name}~@~{name_item}"))
    markup.add(IB(text="Изменить фотографии товара", callback_data=f"media_product_redact{name}~@~{name_item}"))
    markup.add(IB(text="< Назад", callback_data=f"move{name}~@~{id}"))
    await red_product.name_bot.set()
    await query.message.edit_text(f'редактирование товара {name_item}', reply_markup=markup)
    pass
#@todo last block


@dp.callback_query_handler(text_contains="name_product_redact", state=red_product.name_bot)
async def product_name(query: call, state: FSMContext):
    data = query.data[19:]
    name, name_item = data.split("~@~")[0], data.split("~@~")[1]
    await state.update_data(name_bot=name)
    await state.update_data(name_item=name_item)
    await red_product.next()
    await query.message.answer("Введите новое название продукта")
    pass


@dp.message_handler(state=red_product.name_item)
async def take_new_name_product(msg: Message, state: FSMContext):
    new_name = msg.text
    async with state.proxy() as data:
        name_bot = data["name_bot"]
        name_item = data["name_item"]
    update_sql("""update catalog set name=? where name=?""",[new_name, name_item], f"/root/bot/{name_bot}.sqlite3")
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)


@dp.callback_query_handler(text_contains="cost_product_redact", state=red_product.name_bot)
async def product_description(query: call, state: FSMContext):
    data = query.data[19:]
    name, name_item = data.split("~@~")[0], data.split("~@~")[1]
    await state.update_data(name_bot=name)
    await state.update_data(name_item=name_item)
    await red_product.next()
    await red_product.next()
    await red_product.next()
    await query.message.answer("Введите новую цену продукта")
    pass


@dp.message_handler(state=red_product.cost)
async def take_new_description_product(msg: Message, state: FSMContext):
    new_cost = msg.text
    async with state.proxy() as data:
        name_bot = data["name_bot"]
        name_item = data["name_item"]
    update_sql("""update catalog set cost=? where name=?""", [new_cost, name_item], f"/root/bot/{name_bot}.sqlite3")
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)


@dp.callback_query_handler(text_contains="description_product_redact", state=red_product.name_bot)
async def product_cost(query: call, state: FSMContext):
    data = query.data[26:]
    name, name_item = data.split("~@~")[0], data.split("~@~")[1]
    await state.update_data(name_bot=name)
    await state.update_data(name_item=name_item)
    await red_product.next()
    await red_product.next()
    await query.message.answer("Введите новое описание продукта")
    pass


@dp.message_handler(state=red_product.description)
async def take_new_cost_product(msg: Message, state: FSMContext):
    new_description = msg.text
    async with state.proxy() as data:
        name_bot = data["name_bot"]
        name_item = data["name_item"]
    update_sql("""update catalog set description=? where name=?""",[new_description, name_item], f"/root/bot/{name_bot}.sqlite3")
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)


@dp.callback_query_handler(text_contains="media_product_redact", state=red_product.name_bot)
async def product_media(query: call, state: FSMContext):
    data = query.data[20:]
    name, name_item = data.split("~@~")[0], data.split("~@~")[1]
    await state.update_data(name_bot=name)
    await state.update_data(name_item=name_item)
    await red_product.next()
    await red_product.next()
    await red_product.next()
    await red_product.next()
    media = take_sql("""select photo from catalog  where name=?""",[name_item],f"/root/bot/{name}.sqlite3")[0][0].split(",")
    media.pop()
    os.system(f'echo -e"\n{media}\n" | wall')
    if media[0] == "none":
        media = []
    markup = IM(row_width=1)
    await state.update_data(len_media=len(media))
    if len(media) < 10:
        markup.add(IB(text="Добавить фото", callback_data="update_media"))
    markup.add(IB(text="Обновить фото (старые удаляются)", callback_data="new_media"))
    await query.message.edit_text(f"Фотографии для {name_item}", reply_markup=markup)
    pass

@dp.callback_query_handler(text="new_media", state=red_product.media)
@dp.callback_query_handler(text="update_media", state=red_product.media)
async def take_new_media_product(query: call, state: FSMContext):
    os.system(f'echo -e"\nwork\n" | wall')
    async with state.proxy() as f:
        len_media = f["len_media"]
        markup = KM(resize_keyboard=True, row_width=1)
        markup.add(KB("< Отмена"))
        markup.add(KB("Завершить"))
    if query.data == "new_media":
        await red_product.next()
    await query.message.answer(f"Пришлите новые фотографии, свободно мест {10-len_media}", reply_markup=markup)

@dp.message_handler(content_types=ContentTypes.PHOTO, state=red_product.media)
async def update_media(msg: Message, state: FSMContext):
    photo = msg.photo[0]["file_id"]
    markup = KM(resize_keyboard=True, row_width=1)
    markup.add(KB("Завершить"))
    markup.add(KB("< Отмена"))
    async with state.proxy() as data:
        if "media" in data.keys():
            len_media = len(data["media"])
            old_len = data["len_media"]
            if len(data["media"]) < (10-old_len)-len_media:
                await state.update_data(data["media"].append(photo))
            else:
                await end_update_media(msg, state)
        else:
            await state.update_data([photo, ])
            await msg.answer("Фотографии зашружаются", reply_markup=markup)
    pass


@dp.message_handler(text="Завершить", state=red_product.media)
async def end_update_media(msg: Message, state: FSMContext):
    try:
        async with state.proxy() as f:
            name_bot = f["name_bot"]
            name_item = f["name_item"]
            media = f["media"]
        photos = take_sql("""select photo from catalog where name=?""",[name_item], f"/root/bot/{name_bot}.sqlite3")[0][0]
        new_media = ''.join((f"{photo}," for photo in media))
        if phtots == "none,":
            photos = new_media
        else:
            photos = photos.join(new_media)
        update_sql("""update catalog set photo=? where name=?""",[photos, name_item], f"/root/bot/{name_bot}.sqlite3")
        await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    finally:
        await main_menu(msg,state)


@dp.message_handler(text="Завершить", state=red_product.len_media)
async def save_new_media(msg: Message, state: FSMContext):
    async with state.proxy() as f:
        name_bot = f["name_bot"]
        name_item = f["name_item"]
        media = f["media"]
    new_media = ''.join((f"{photo}," for photo in media))
    update_sql("""update catalog set photo=? where name=?""",[new_media, name_item], f"/root/bot/{name_bot}.sqlite3")
    await msg.answer(config["text"]["done"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(msg, state)

@dp.message_handler(content_types=ContentTypes.PHOTO, state=red_product.len_media)
async def new_media(msg: Message, state:FSMContext):
    photo = msg.photo[0]["file_id"]
    markup = KM(resize_keyboard=True, row_width=1)
    async with state.proxy() as data:
        if "media" in data.keys():
            if len(data["media"]) < 10:
                data["media"].append(photo)
            else:
                await end_update_media(msg, state)
        else:
            data["media"] = [photo, ]
            await msg.edit_text("Фотографии зашружаются")


@dp.message_handler(commands="start")
async def start(msg: Message):
    registration(msg.from_user.id)
    markup = KM(resize_keyboard=True)
    markup.add(KB("создать свою лавку"))
    text = config["text"]["start"]
    await bot.send_message(msg.chat.id, text=text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


class bot_information(StatesGroup):
    token = State()
    type = State()
    wallet = State()
    minimal = State()
    accaunt = State()


@dp.callback_query_handler(text="create_new")
async def confirm_create_new(query: call):
    markup = KM(resize_keyboard=True)
    markup.add(KB("Создать свою лавку"))
    await query.message.answer("Хотите создать новую лавку?", reply_markup=markup)


@dp.message_handler(text="Создать свою лавку")
async def create(msg: Message):
    if check_valid(msg.from_user.id):
        text = config["text"]["text1"]
        await bot_information.token.set()

    else:
        text = config["text"]["full_pull"]
    await msg.answer(text)


@dp.message_handler(state=bot_information.token)
async def take_token(msg: Message, state: FSMContext):
    check = msg.text.split(":")
    if get_me(msg.text)["ok"]:
        async with state.proxy() as data:
            data['token'] = msg.text
        text = config["text"]["text2"]
        await bot_information.next()
        markup = KM(resize_keyboard=True)
        markup.add(KB("📌 Фиксированная цена"), KB("🧧 Донаты"))
    else:
        text = config["text"]["wrong"]
        markup = None
    await msg.answer(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=bot_information.type)
async def take_type(msg: Message, state: FSMContext):
    if msg.text in ["📌 Фиксированная цена", "🧧 Донаты"]:
        await bot_information.next()
        if "📌" in msg.text:
            await state.update_data(type="fixed")
        else:
            await state.update_data(type="donats")
        text = config["text"]["text3"]
    else:
        text = config["text"]["wrong_type"]
    await msg.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=bot_information.wallet)
async def take_wallet(msg: Message, state: FSMContext):
    if msg.text in Currency.keys() or msg.text in Currency.values():
        await bot_information.next()
        await state.update_data(wallet=msg.text)
        text = config["text"]["text4"]
        markup = KM(resize_keyboard=True)
        markup.add(KB("Без минимального заказа"))
    else:
        markup = None
        text = config["text"]["wrong_wallet"]
    await msg.answer(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=bot_information.minimal)
async def take_minimal(msg: Message, state: FSMContext):
    if msg.text.isdigit() or msg.text == "Без минимального заказа":
        await bot_information.next()
        await state.update_data(minimal=msg.text)
        markup = KM(resize_keyboard=True)
        markup.add(KB(f'@{msg.from_user.username}'))
        text = config["text"]["text5"]
    else:
        markup = None
        text = config["text"]["wrong_minimal"]
    await msg.answer(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=bot_information.accaunt)
async def take_accaunt(msg: Message, state: FSMContext):
    if msg.text.startswith('@'):
            async with state.proxy() as data:
                await msg.answer(str(data))
                data["accaunt"] = msg.text
            text = config['text']['create_lavka'].format(name_lavka=f"""@{get_me(data['token'])["result"]["username"]}""")
            Data = {
                data["token"] : {
                    "accaunt" : data["accaunt"],
                    "minimal" : data["minimal"],
                    "type" : data["type"],
                    "wallet" : data["wallet"],
                }
            }
            await msg.answer("wor1")
            json_data = take_sql("""select bot from user_list where id=?""",[msg.from_user.id], db=bd)[0][0]
            data = json.loads(json_data)
            for count in range(3):
               if not data["bot"][count]:
                   data["bot"][count] = list(Data.keys())[0]
                   name_bot = get_me(Data["bot"][count])["result"]["username"]
                   break
            data_json = json.dumps(data)
            update_sql("""update user_list set bot=? where id=?""",[data_json, msg.from_user.id], db="/root/bot/lavka_manager.sqlite3")
            config.set("currency_bot",name_bot, "test")
            with open("configurate.ini", "w", encoding="UTF-8") as f:
                config.write(f)
            await msg.answer(text)
            await state.finish()
            await create_bot(msg, Data)

            pass
    else:
        await msg.answer(config['text']['wrong_accaunt'])


@dp.callback_query_handler(text_contains="main_menu", state="*")
async def report(query: call, state: FSMContext):
    await query.message.delete()
    await main_menu(query, state, user_id=query.from_user.id)


if __name__ == "__main__":
    executor.start_polling(dp)
