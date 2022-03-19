import config
import json
import time
from datetime import datetime
from vkbottle.bot import Bot, Message

bot = Bot(token=config.TOKEN)

def get_info():
    with open("info.json", 'r') as read_file:
        data = json.load(read_file)

    return data

def write_info(data: dict):
    with open("info.json", "w") as write_file:
        json.dump(data, write_file)

async def user_info(member: int, nc: str = None):
    user = (await bot.api.users.get(user_ids=[member], name_case=nc))[0]
    return user

def get_time(tm:int, arg: str):
    if arg in ['с', 'сек']:
        return time.time() + tm

    elif arg in ['м', 'мин']:
        return time.time() + tm*60

    elif arg in ['ч', 'час']:
        return  time.time() + tm*3600

    elif arg in ['д',]:
        return  time.time() + tm*86400

    else:
        return None

@bot.on.chat_message(text=['!мут <tm> <arg>', '!мут <tm>', '!мут'])
async def mute(message: Message, tm: int = None, arg: str = None):

    admins = get_info()['admins']
    if message.from_id not in admins:
        return

    if message.reply_message:
        member = message.reply_message.from_id

    elif message.fwd_messages != []:
        member = message.fwd_messages[0].from_id

    else:
        return "Перешлите сообщение пользователя"

    if member in admins:
        return "Вы не можете наказать модератора"

    if member in get_info()['mutes']:
        return "Пользователь уже заглушен"

    try:
        old, tm = tm, int(tm)
    except ValueError:
        return "Введите время в виде числа"

    tm = get_time(tm, arg)
    if not tm:
        return " Укажите верный аргумент типа времени <с/м/ч>"

    data = get_info()
    data['mutes'].append({f"{member}": tm})
    write_info(data)

    dtime = datetime.fromtimestamp(tm)
    user = await user_info(member)
    await message.answer(f"[id{user.id}|{user.first_name} {user.last_name}] получил мут на {old} {arg}\nДата окончания: {dtime.strftime('%d')} {config.MONTHES[int(dtime.strftime('%m'))]} {dtime.strftime('%Y')} год", disable_mentions=1)

@bot.on.chat_message(text='!размут')
async def mute(message: Message):
    admins = get_info()['admins']
    if message.from_id not in admins:
        return

    if message.reply_message:
        member = message.reply_message.from_id

    elif message.fwd_messages != []:
        member = message.fwd_messages[0].from_id

    else:
        return "Перешлите сообщение пользователя"

    data = get_info()
    num = None
    for n, i in enumerate(data['mutes'], 0):
        try:
            i.pop(f"{member}")
            num = n
            break
        except KeyError:
            continue

    if num is None:
        return "Пользовтель не заглушен"

    data['mutes'].pop(num)
    write_info(data)

    admin = await user_info(message.from_id)
    user = await user_info(member, "gen")
    await message.answer(f"[id{admin.id}|{admin.first_name}] снял мут с [id{user.id}|{user.first_name} {user.last_name}]", disable_mentions=1)

@bot.on.chat_message(text='!модер')
async def mute(message: Message):
    admins = get_info()['admins']
    if message.from_id not in admins:
        return

    if message.reply_message:
        member = message.reply_message.from_id

    elif message.fwd_messages != []:
        member = message.fwd_messages[0].from_id

    else:
        return "Перешлите сообщение пользователя"

    if member not in get_info()['admins']:
        data = get_info()
        data['admins'].append(member)
        write_info(data)

        user = await user_info(member)
        await message.answer(f"[id{user.id}|{user.first_name} {user.last_name}] назначен Модератором", disable_mentions=1)

    else:
        data = get_info()
        data['admins'].remove(member)
        write_info(data)

        user = await user_info(member)
        await message.answer(f"[id{user.id}|{user.first_name} {user.last_name}] разжалован с Модератора", disable_mentions=1)

@bot.on.chat_message()
async def messange(messange: Message):
    data = get_info()['mutes']
    for i in data:
        for key, value in i.items():
            if value ['peer_id'] == messange.peer_id:
                if int(key) == messange.from_id:
                    group = (await bot.api.groups.get_by_id())[0]
                await bot.api.delete(peer_id=messange.peer_id, messange_id=[messange.conversation_message_id], group_id=group.id)


async def chek_mutes():
    import asyncio
    while True:
        await asyncio.sleep(2)
        data = get_info()
        for n, i in enumerate(data['mutes'], 0):
            for key, value in i .items():
                if value <= time.time():
                    data['mutes'].pop(n)
                    write_info(data)
                    user = await user_info(key)
                    await bot.api.messages.send(chat_id=3, message=f"[id{user.id}|{user.first_name} {user.last_name}] размучен в беседе", disable_mentions=1, random_id=0)

bot.loop.create_task(chek_mutes())
bot.run_forever()