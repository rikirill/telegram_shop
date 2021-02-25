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
import sqlite3
import json
import configparser
import asyncio
import logging


file_name = f'{__file__.split("/")[-1][:-3]}'
config = configparser.ConfigParser()
config.read(f'/root/bot/{file_name}.ini')
logging.basicConfig(filename=f"/root/bot/{file_name}.log", level=logging.DEBUG, format="%(levelname)s - %(asctime)s: \n%(message)s\n---------------")
storage = MemoryStorage()
comands = config['bot']['comands'].split(",")
bot = Bot(config['manage']['token'])
markuplib = eval(config['bot']['markuplib'])
dp = Dispatcher(bot, storage=storage)
bd = f"/root/bot/{file_name}.sqlite3"


def take_text(arg):
    return config['text'][arg]


def take_sql(what_do, what_use):
    con = sqlite3.connect(bd)
    cursor = con.cursor()
    sql = cursor.execute(what_do, [what_use]).fetchall()
    con.close()
    return sql


def update_sql(what_do, what_use):
    con = sqlite3.connect(bd)
    cursor = con.cursor()
    cursor.execute(what_do, what_use)
    con.commit()
    con.close()


def addbutton(comand, one_time=None):
    items = markuplib[comand]
    markup = KM(row_width=1, resize_keyboard=True, one_time_keyboard=one_time)
    markup.add(*(KB(text) for text in items))
    return markup

    pass


def addinlinebutton(items, callback, callback_back="move", back=None):
    """
    :param callback_back:
    :param callback:
    :param items: предметы для добавления в кнопки
    :param back: кнопка назад (опциональная)
    :return: inline_buttons
    """
    markup = IM(row_width=2)
    if items:
        markup.add(*(IB(text=item, callback_data=callback + item) for item in items))
    if back:
        markup.row(IB(text=config["text"]["back"], callback_data=callback_back + back))
    return markup


def take_catalog(where=None):
    with open(f'/root/bot/{file_name}.json', "r",encoding="UTF-8") as f:
        catalog = json.load(f)
        f.close()
    return catalog[where]["movein"], catalog[where]["back"], catalog[where]["description"]


class step(StatesGroup):
    name = State()
    geoposition = State()
    contacts = State()


@dp.callback_query_handler(text_contains="confirm")
async def confirming(query: call):
    full_name = query.from_user.full_name
    markup = KM(resize_keyboard=True)
    markup.add(KB(full_name))
    markup.add(KB("< Назад"))
    await step.name.set()
    await query.message.answer(config["text"]["confirm1"], reply_markup=markup)
    pass


@dp.message_handler(text="< Назад", state="*")
async def report(msg: Message, state: FSMContext):
    await state.finish()
    await shoping(msg)
    pass


@dp.message_handler(state=step.name)
async def name_confirming(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    markup = KM(row_width=1, resize_keyboard=True)
    location = KB("📍 Текущий адрес", request_location=True)
    backing = KB("< Назад")
    markup.add(location, backing)
    await step.next()
    await msg.answer(config["text"]["geoposition"], reply_markup=markup)
    pass


@dp.message_handler(content_types=ContentTypes.LOCATION | ContentTypes.TEXT, state=step.geoposition)
async def geoposition_confirming(msg: Message, state: FSMContext):
    await step.next()
    if msg.location:
        await state.update_data(geoposition={"latitude": msg.location.latitude, "longitude": msg.location.longitude})
    else:
        await state.update_data(geoposition=msg.text)
    markup = KM(row_width=1, resize_keyboard=True)
    markup.add(KB("📱 Мой телефон", request_contact=True))
    markup.add(KB("< Назад"))
    await msg.answer(config["text"]["contact"], reply_markup=markup)
    pass


@dp.message_handler(content_types=ContentTypes.CONTACT | ContentTypes.TEXT, state=step.contacts)
async def confirmed(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.contact:
            data["contacts"] = msg.contact.phone_number
        else:
            data["contacts"] = msg.text
    json_data = take_sql("""select current_order  from user where id =?""", msg.from_user.id)
    Data = json.loads(json_data[0][0])
    order = ''
    summa = 0
    for item in Data.keys():
        count = Data[item]["count"]
        cost = Data[item]["cost"]
        cost = float(cost) * count
        if ".0" == str(cost)[-2:]:
            cost = int(cost)
        order += f"{item} x {count} — {cost} {config['manage']['currency']}\n"
        summa += cost
    if isinstance(data["geoposition"], dict):
        locate = "📍 Текущий адрес"
    else:
        locate = data["geoposition"]
    text = config["text"]["confirmed"].format(location=locate, name=data["name"], contact=data["contacts"], order=order,
                                              sum=summa, main=config["manage"]["main"])
    await msg.answer(text)
    await report(msg, state)
    if isinstance(data["geoposition"], dict):
        locate = "В предыдущем сообщении"
        await bot.send_location(int(config["manage"]["manager_id"]), latitude=data["geoposition"]["latitude"], longitude=data["geoposition"]["longitude"])
    else:
        locate = data["geoposition"]
    text = config["text"]["for_main"].format(location=locate, name=data["name"], contact=data["contacts"],
                                             username=f'@{msg.from_user.username}', order=order, sum=summa)
    await bot.send_message(int(config["manage"]["manager_id"]), text)
    update_sql("""update user set last_order=?,current_order = ? where id=?""", [json_data[0][0], '{}', msg.from_user.id])


@dp.callback_query_handler(text_contains="del_for_order")
async def del_for_order(query: call):
    name = query.data[13:]
    json_data = take_sql("""select current_order  from user where id =?""", query.from_user.id)
    data = json.loads(json_data[0][0])
    data.pop(name)
    json_data = json.dumps(data)
    update_sql("""update user set current_order=? where id =?""", [json_data, query.from_user.id])
    await query.message.delete()
    pass


@dp.callback_query_handler(text_contains="for_order")
async def add_and_orb_for_order(query: call):
    name = query.data[13:]
    markup = IM(row_width=3)
    markup.add(IB("❌", callback_data=f"del_for_order{name}"), IB("-", callback_data=f"rob_for_order{name}"),
               IB("+", callback_data=f"add_for_order{name}"))
    json_data = take_sql("""select current_order  from user where id =?""", query.from_user.id)
    data = json.loads(json_data[0][0])
    if "add" in query.data:
        count = data[name]["count"] + 1
    else:
        count = data[name]["count"]
        if count != 1:
            count = count - 1
        else:
            return None
    data[name]["count"] = count
    cost = data[name]["cost"]
    cost = float(cost) * count
    if ".0" == str(cost)[-2:]:
        cost = int(cost)
    await query.message.edit_text(f"{name} x {count} — {cost} {config['manage']['currency']}", reply_markup=markup)
    json_data = json.dumps(data)
    update_sql("""update user set current_order=? where id =?""", [json_data, query.from_user.id])
    pass


@dp.callback_query_handler(text_contains="move")
async def move_in_catalog(query: call):
    name = query.data[4:]
    items, back, description = take_catalog(name)
    Callback = "move"
    if items == "item":
        sql = take_sql("""select name from catalog where id=? """, name)
        items = []
        for item in sql:
            items.append(item[0])
        Callback = "item"
    markup = addinlinebutton(items, back=back, callback=Callback, callback_back="move")
    await query.message.edit_text(f'{name}\n{description}', reply_markup=markup)
    pass


@dp.callback_query_handler(text_contains="item")
async def take_item(query: call):
    name = query.data[4:]
    sql = take_sql("""select * from catalog where name=?""", name)
    description = sql[0][1]
    photos = sql[0][2]
    photos = photos.split(',')
    cost = sql[0][3]
    id = sql[0][4]
    text = f"""{name}\n\n{description}\n\n{cost}{config['manage']['currency']}"""
    markup = IM(row_width=1)
    markup.add(IB('отложить в корзину', callback_data=f"add_in_order{name}"))
    markup.add(IB("< назад", callback_data=f"move{id}"))
    await query.message.edit_text(text, reply_markup=markup)
    await asyncio.sleep(0.4)
    try:
        media = MediaGroup()
        photos.pop()
        media.attach_photo(*(photo for photo in photos))
        media.attach_photo()
        await bot.send_media_group(query.from_user.id, media=media)

    except:
        pass
    pass


@dp.callback_query_handler(text_contains="add_in_order")
async def add_in_order(query: call):
    name = query.data[12:]
    sql = take_sql("""select * from catalog where name=?""", name)
    cost = sql[0][3]
    id = sql[0][4]
    markup = IM(row_width=1)
    markup.row(IB(text='✅  ещё отложить', callback_data=f"add_in_order{name}"))
    markup.add(IB("< назад", callback_data=f"move{id}"))
    try:
        await query.message.edit_reply_markup(markup)
    except:
        pass
    json_data = take_sql("""select current_order  from user where id =?""", query.from_user.id)
    data = json.loads(json_data[0][0])
    if name in data.keys():
        data[name]["count"] = data[name]["count"] + 1
    else:
        order = {
            name: {
                "cost": cost,
                "count": 1
            }
        }
        data.update(order)
    data = json.dumps(data)
    update_sql("""update user set current_order=? where id=?""", [data, query.from_user.id])
    pass


@dp.callback_query_handler(text_contains="removing")
async def remove(query: call):
    data = take_sql("""select last_order  from user where id =?""", query.from_user.id)
    update_sql("""update user set current_order=? where id=?""", [data[0][0], query.from_user.id])
    await bascet(query.message)

@dp.message_handler(text=[comands[1]])
async def terms(msg: Message):
    await msg.answer(config["text"]["terms"])


@dp.message_handler(text=[comands[2]])
async def support(msg: Message):
    await msg.answer(take_text("sup").format(config['manage']['main']))


@dp.message_handler(text=config["text"]["catalog"])
async def catalog(msg: Message):
    items, back, description = take_catalog("catalog")
    if items[0]:
        markup = addinlinebutton(items, callback="move")
    else:
        markup = None
    await msg.answer(f'Каталог\n{description}', reply_markup=markup)


@dp.message_handler(text=config["text"]["bascet"])
async def bascet(msg: Message):
    jsonData = take_sql("select current_order from user where id=?", msg.chat.id)
    data = json.loads(jsonData[0][0])
    if jsonData[0][0] != '{}':
        markup = addbutton(comand="confirm")
        await msg.answer(config["text"]["current_order"], reply_markup=markup)
        for name in data.keys():
            count = data[name]["count"]
            cost = data[name]["cost"]
            cost = float(cost) * count
            if ".0" == str(cost)[-2:]:
                cost = int(cost)
            markup = IM(row_width=3)
            delete = IB("❌", callback_data=f"del_for_order{name}")
            rob = IB("-", callback_data=f"rob_for_order{name}")
            add = IB("+", callback_data=f"add_for_order{name}")
            markup.row(delete, rob, add)
            text = f"{name} x {count} — {cost} {config['manage']['currency']}"
            await msg.answer(text, reply_markup=markup)
    else:
        await msg.answer(config["text"]["empty_bascet"])
    pass


@dp.message_handler(text=config["text"]["confirm_order"])
async def confirm_order(msg: Message):
    json_data = take_sql("""select current_order  from user where id =?""", msg.from_user.id)
    if json_data[0][0] != "{}":
        markup = IM(row_width=1)
        markup.add(IB("Оформить", callback_data=f"confirm{msg.from_user.id}"))
        data = json.loads(json_data[0][0])
        text = f"В заказе:\n"
        sum = 0
        for name in data.keys():
            count = data[name]["count"]
            cost = data[name]["cost"]
            cost = float(cost) * count
            if ".0" == str(cost)[-2:]:
                cost = int(cost)
            text = text + f"{name} x {count} — {cost} {config['manage']['currency']}\n"
            sum += cost
        first_text = f"Заказ на {sum} {config['manage']['currency']}\nПроверьте заказ.\nС условиями оплаты и доставки можно ознакомиться на /terms."
        await msg.answer(first_text)
        await msg.answer(text, reply_markup=markup)
    else:
        markup = addbutton("shop")
        await msg.answer(config["text"]["empty_bascet"], reply_markup=markup)


@dp.message_handler(text=config["text"]["last"])
async def last_order(msg: Message):
    json_data = take_sql("""select last_order  from user where id =?""", msg.from_user.id)
    if "{}" != json_data[0][0]:
        data = json.loads(json_data[0][0])
        order = 'В заказе:\n'
        for item in data.keys():
            count = data[item]["count"]
            cost = data[item]["cost"]
            cost = float(cost) * count
            if ".0" == str(cost)[-2:]:
                cost = int(cost)
            order += f"{item} x {count} — {cost} {config['manage']['currency']}\n"
        order += "\nМожно сразу наполнить им корзину 🛍"
        markup = IM()
        markup.add(IB("Наполнить", callback_data=f"removing{msg.from_user.id}"))
        await msg.answer(order, reply_markup=markup)
    else:
        await msg.answer("Вы ещё не совершали заказов")


@dp.message_handler(text=[comands[0], "< Назад"])
async def shoping(msg: Message):
    markup = addbutton("shop")
    await msg.answer(config["text"]["shop"], reply_markup=markup)

@dp.message_handler()
async def help(msg: Message):
    try:
        update_sql("""insert into user values (?,?,?)""", [msg.from_user.id, f'@{msg.from_user.username}','{}','{}','None', "{}"])
    except:
        pass
    await msg.answer(config["text"]["help"])


if __name__ == "__main__":
    executor.start_polling(dp)
