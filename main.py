import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
import random
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from collections import Counter

class Roles:
    Mafia = "Мафиози"
    Doktor = "Доктор"
    Prostitute = "Красотка"
    Don = "Крёстный отец"
    Stiller = "Вор"
    Advocat = "Адвокат"
    Snitch = "Стукач"
    Villager = "Mирный житель."
    Detective = "Детектив"
    SaintFather = "Священник"
    Loer = "Судья"
    Paparaci = "Журналист"
    Sherif = "Шериф"
    Prizonist = "Тюремщик"
    Security = "Телохранитель"
    Somnambula = "Лунатик"
    Fan = "Поклонница"

class Types:
    Peasefull = "Pease"
    Mafiozy = "Mafia"

class Player:
    def __init__(self, name, role, id, type):
        self.name = name
        self.role = role
        self.id = id
        self._shooted = False  # Инициализируем атрибут _victim значением None
        self._block = False
        self.block_voise = False
        self._type = type
        self._cosmetic_role = role

    def setShoot(self, is_shooting, shooter):
        if not shooter.getBlock():
            self._shooted = is_shooting

    def setBlock(self, is_blocking, blocker):
        if not blocker.getBlock():
            self._block = is_blocking

    def setBlockVoise(self, is_blocking, blocker):
        if not blocker.getBlock():
            self.block_voise = is_blocking

    def setRole(self, role, shooter):
        if not shooter.getBlock():
            self.role = role

    def setCosmeticRole(self, role, shooter):
        if not shooter.getBlock():
            self._cosmetic_role = role

    def getShoot(self):
        return self._shooted

    def getType(self):
        return self._type

    def getBlock(self):
        return self._block

    def getBlockVoise(self):
        return self.block_voise

    def getName(self):
        return self.name

    def getRole(self):
        return self.role

    def getCosmeticRole(self):
        return self._cosmetic_role

    def main_function(self, victim):
        pass

class Doctor(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Doktor, id, Types.Peasefull)

    def main_function(self, victim):
        victim.setShoot(False, self)
        return f"Доктор хочет защитить {victim.getName()}"

class Security(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Security, id, Types.Peasefull)

    def main_function(self, victim):
        if victim.getShoot():
            victim.setShoot(False, self)
            self.setShoot(True, self)
        return f"Телохранитель хочет защитить {victim.getName()}"

class Somnambula(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Somnambula, id, Types.Peasefull)

    def main_function(self, victim):
        victim.setShoot(True, self)
        return f"Лунатик притворяется, что хочет застрелить {victim.getName()}"

class Prostitute(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Prostitute, id, Types.Peasefull)

    def main_function(self, victim):
        victim.setBlock(True, self)
        victim.setShoot(False, self)
        return f"Красотка хочет лишить способностей, а заодно и защитить {victim.getName()}"

class Fan(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Fan, id, Types.Peasefull)

    def main_function(self, victim):
        if victim.getCosmeticRole() == Roles.Detective or victim.getCosmeticRole() == Roles.SaintFather or victim.getCosmeticRole() == Roles.Loer or victim.getCosmeticRole() == Roles.Paparaci or victim.getCosmeticRole() == Roles.Prizonist or victim.getCosmeticRole() == Roles.Sherif:
            return f"Поклонница хочет проверить {victim.getName()}" \
                f"\n{victim.getName()} это {victim.getCosmeticRole()}"
        else:
            return f"Поклонница хочет проверить {victim.getName()}" \
                f"\n{victim.getName()} это не лидер"

class Sherif(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Sherif, id, Types.Peasefull)

    def main_function(self, victim):
        victim.setShoot(True, self)
        return f"Шериф хочет застрелить {victim.getName()}"

prizon = []
class Prizonist(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Prizonist, id, Types.Peasefull)

    def main_function(self, victim):
        global prizon
        if victim.getRole() == Roles.Mafia or victim.getRole() == Roles.Don or victim.getRole() == Roles.Stiller or victim.getRole() == Roles.Advocat or victim.getRole() == Roles.Snitch:
            victim.setBlock(True, self)
            victim.setBlockVoise(True, self)
            prizon.append(victim)
            return f"Тюремщик хочет проверить {victim.getName()}" \
                   f"\n{victim.getName()} это {victim.getCosmeticRole()}" \
                   f"\n{victim.getName()} попадает в тюрьму."
        else:
            return f"Тюремщик хочет проверить {victim.getName()}" \
                   f"\n{victim.getName()} это {victim.getCosmeticRole()}"

class Detective(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Detective, id, Types.Peasefull)
        self._victim = None

    def set_victim(self, victim):
        self._victim = victim
    def main_function(self, victim):
        if victim is None:
            return "Детектив не назначен"
        if victim:
            self._victim.setShoot(True, self)
            return f"Детектив хочет застрелить {self._victim.getName()}"
        else:
            return f"Детектив хочет проверить {self._victim.getName()}" \
                   f"\n{self._victim.getName()} это {self._victim.getCosmeticRole()}"

class SaintFather(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.SaintFather, id, Types.Peasefull)
        self._victim = None
    def set_victim(self, victim):
        self._victim = victim

    def main_function(self, victim):
        if victim is None:
            return "Священник не назначен"
        if victim:
            self._victim.setShoot(True, self)
            return f"Священник хочет застрелить {self._victim.getName()}"
        else:
            return f"Священник хочет проверить {self._victim.getName()}" \
                   f"\n{self._victim.getName()} это {self._victim.getCosmeticRole()}"

class Paparaci(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Paparaci, id, Types.Peasefull)
        self._victim = None
    def set_victim(self, victim):
        self._victim = victim

    def main_function(self, victim):
        if victim is None:
            return "Журналист не назначен"
        if victim.getType() == self._victim.getType():
            return f"{self._victim.getName()} и {victim.getName()} принадлежат к одной стороне."
        else:
            return f"{self._victim.getName()} и {victim.getName()} не принадлежат к одной стороне."

class Loer(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Loer, id, Types.Peasefull)

    def main_function(self, victim):
        return f"Судья хочет проверить {victim.getName()}" \
               f"\n{victim.getName()} это {victim.getCosmeticRole()}"

class Mafia(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Mafia, id, Types.Mafiozy)

    def main_function(self, victim):
        if victim.getRole() == Roles.Somnambula:
            return "Мафиози вычислили и застрелили лунатика. " \
                   "\nOни получают право ещё на один выстрел."
        victim.setShoot(True, self)
        return f"Мафия хочет застрелить {victim.getName()}"

class Villager(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Villager, id, Types.Peasefull)

    def main_function(self, victim):
        return "HA-HA-HA-HA"

class Don(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Don, id, Types.Mafiozy)

    def main_function(self, victim):
        victim.setBlockVoise(True, self)
        return f"Крёстный отец хочет лишить права голоса {victim.getName()}"

class Stiller(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Stiller, id, Types.Mafiozy)

    def main_function(self, victim):
        victim.setBlock(True, self)
        return f"Вор хочет лишить способностей {victim.getName()}"

class Advocat(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Advocat, id, Types.Mafiozy)

    def main_function(self, victim):
        return f"Адвокат хочет проверить {victim.getName()}" \
               f"\n{victim.getName()} это {victim.getCosmeticRole()}" \
               f"\nАдвокат не имеет права озвучивать ночью то, что узнал, и не может прямо сообщить своим подельникам, что он адвокат."

class Snitch(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Snitch, id, Types.Mafiozy)

    def main_function(self, victim):
        victim.setCosmeticRole(Roles.Mafia, self)
        return f"Стукач хочет оклеветать {victim.getName()}"

role_classes = {
        Roles.Villager: Villager,
        Roles.Mafia: Mafia,
        Roles.Don: Don,
        Roles.Doktor: Doctor,
        Roles.Prostitute: Prostitute,
        Roles.Sherif: Sherif,
        Roles.Detective: Detective,
        Roles.SaintFather: SaintFather,
        Roles.Loer: Loer,
        Roles.Prizonist: Prizonist,
        Roles.Security: Security,
        Roles.Somnambula: Somnambula,
        Roles.Fan: Fan,
        Roles.Stiller: Stiller,
        Roles.Advocat: Advocat,
        Roles.Snitch: Snitch,
        Roles.Paparaci: Paparaci
    }
class Room:
    def __init__(self, num_players, password):
        self.num_players = num_players
        self.password = password
        self.players = []
        self.our_roles = []

        self.num_villagers = 0
        self.num_special_villagers = 0
        self.num_leaders = 0
        self.num_mafias = 0
        self.num_special_mafias = 0

        self.create_roles(self.num_players)

    def add_new_role(self, role):
        if len(self.our_roles) < self.num_players:
            self.our_roles.append(role)
        else:
            print(f"No, {len(self.our_roles)}")

    # Define a dictionary to map role names to role classes

    def add_new_player(self, role, name, id):

        if len(self.players) >= self.num_players:
            return "Количество игроков в комнате превышено"

        # Check if the role is valid
        if role not in role_classes:
            return "Введена некорректная роль."

        # Create a player instance using the role class from the dictionary
        player_class = role_classes[role]
        player = player_class(name, id)

        self.players.append(player)
        return f"{player.getName()}, Вы {player.getRole()}"

    def create_roles(self, num):
        role_configurations = [
            # num, num_villagers, num_leaders, num_special_villagers, num_mafias, num_special_mafias
            (2, 0, 1, 0, 0, 1),
            (5, 2, 1, 1, 1, 0),
            (6, 3, 1, 0, 2, 0),
            (7, 4, 1, 0, 1, 1),
            (8, 3, 1, 1, 2, 1),
            (11, 6, 1, 2, 3, 1),
            (14, 6, 1, 2, 4, 1),
            (17, 9, 1, 2, 3, 2),
        ]

        for config in role_configurations:
            if num == config[0]:
                self.num_villagers = config[1]
                self.num_leaders = config[2]
                self.num_special_villagers = config[3]
                self.num_mafias = config[4]
                self.num_special_mafias = config[5]
                break
        else:
            return "Некорректное количество игроков."

        # Add roles based on the configuration
        for _ in range(self.num_villagers):
            self.add_new_role(Roles.Villager)
        for _ in range(self.num_mafias):
            self.add_new_role(Roles.Mafia)


bot = Bot(token="")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

leader_roles = {
    "Детектив": "Может либо застрелить одного игрока, либо узнать его роль.",
    "Священник": "Может либо застрелить одного игрока, либо узнать его роль. Этот игрок узнаёт личность священника.",
    "Судья": "Ночью может узнать роль одного игрока. Днём может спасти от суда Линча одного игрока.",
    "Журналист": "Может выбрать двух игроков, чтобы узнать, одинаковые у них стороны или разные.",
    "Тюремщик": "Может узнать роль одного игрока. Если этот игрок преступник, он сразу отправляется в тюрьму. После смерти тюремщика все заключённые выходят из тюрьмы.",
    "Шериф": "Может застрелить одного игрока.",
}

special_mafia_roles = {
    "Крёстный отец": "Может выбрать одного игрока. Этот игрок не может голосовать днём.",
    "Вор": "Может выбрать одного из игроков. Этот игрок не может пользоваться своими способностями этой ночью.",
    "Адвокат": "Может узнать роль одного игрока.  Он не имеет права озвучивать ночью то, что узнал, и не может прямо сообщить своим подельникам, что он адвокат.",
    "Стукач": "Может выбрать одного игрока. Если кто-нибудь узнаёт роль этого игрока, ведущий должен сообщить, что этот игрок мафиози.",
}

special_villager_roles = {
    "Доктор": "Перед стрельбой может выбрать другого игрока. Этот игрок не может быть убит этой ночью.",
    "Телохранитель": "Перед стрельбой может выбрать другого игрока. Погибает вместо него, если он должен быть убит этой ночью.",
    "Лунатик": "Притворяется одним из мафиози. Если убит мафией, мафия может застрелить ещё одного игрока.",
    "Красотка": "Перед остальными действиями может выбрать одного игрока. Этот игрок не может пользоваться своими способностями этой ночью, но также не может быть убит.",
    "Поклонница": "Может выбрать одного игрока. Если это лидер, узнаёт его роль.",
}

class CreateRoom(StatesGroup):
    WaitingForNumberOfPlayers = State()  # Ожидание количества игроков
    WaitingForPasswordToAdd = State()
    WaitingForChoosingLeader = State()
    WaitingForEnterLeader = State()
    WaitingForEnterSpecialVillager = State()
    WaitingForEnterSpecialMafia = State()
    WaitingForEnterVictim = State()
    WaitingForGolos = State()
    WaitingForLoginToAdd = State()
    StartAddingToRoom = State()
    StartNewNight = State()
    StartNewDay = State()
    StartVoting = State()
    WaitingForStartNewNight = State()
    WaitingForChoosingFuncktion = State()
    A = State()
    B = State()

room = None
creator_id = 0
can_voiting = []
voit = []

# Funkce pro vytvoření klávesnice s rolí
async def create_buttons(roles, prefix, message):
    role_options = list(roles.keys())
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(*role_options)
    await message.answer(f"{prefix}", reply_markup=keyboard)
    out = ""
    for role, description in roles.items():
        out += role + ": " + description + "\n"
    await message.answer(out)

# Funkce pro ukončení stavu a vytvoření hry
async def end_func(message, Room, state):
    await message.answer(f"Комната на {len(Room.our_roles)} игроков создана! Пароль {Room.password}")
    await message.answer("/create_room - создать комнату\n /add_to_room - присоединиться к комнате")
    global room
    room = Room
    await state.finish()

# Odpovídající message handler pro příkaz /start
@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    await message.answer("Привет! Я ваш mafia-бот.\n /create_room - создать комнату\n /add_to_room - присоединениться к комнате")

# Odpovídající message handler pro příkaz /create_room
@dp.message_handler(commands=['create_room'])
async def create_room(message: types.Message):
    global creator_id
    if creator_id == 0:
        creator_id = message.from_user.id
    else:
        await message.answer("Вы не являетесь создателем комнаты, обратитесь за помощью к ведущему.")
        return
    await message.answer("Введите количество игроков в комнате:")
    await CreateRoom.WaitingForNumberOfPlayers.set()

# Odpovídající message handler pro stav WaitingForNumberOfPlayers
@dp.message_handler(state=CreateRoom.WaitingForNumberOfPlayers)
async def get_number_of_players(message: types.Message, state: FSMContext):
    try:
        num_players = int(message.text)
        if num_players < 0:
            await message.answer("Количество игроков должно быть больше 4. Введите количество игроков еще раз:")
        else:
            await message.answer("Пожалуйста, придумайте пароль для присоединения:")
            await state.update_data(num_players=num_players)
            await CreateRoom.WaitingForChoosingLeader.set()
    except ValueError:
        await message.answer("Пожалуйста, введите число игроков в числовом формате.")

# Odpovídající message handler pro stav WaitingForChoosingLeader
@dp.message_handler(state=CreateRoom.WaitingForChoosingLeader)
async def choose_leader(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        num_players = data.get('num_players')
    enter_code = message.text
    room = Room(num_players, enter_code)
    await state.update_data(room=room)

    await create_buttons(leader_roles, "Выберите лидера:", message)
    await CreateRoom.WaitingForEnterLeader.set()

# Odpovídající message handler pro stav WaitingForEnterLeader
@dp.message_handler(state=CreateRoom.WaitingForEnterLeader)
async def get_leader(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        room = data.get('room')
    leader = message.text
    role_mapping = {
        "Детектив": Roles.Detective,
        "Священник": Roles.SaintFather,
        "Судья": Roles.Loer,
        "Журналист": Roles.Paparaci,
        "Тюремщик": Roles.Prizonist,
        "Шериф": Roles.Sherif
    }
    if leader in role_mapping:
        room.our_roles.append(leader)
        await state.update_data(room=room)
        await message.answer(f"лидер {leader} назначен")
        if room.num_special_mafias > 0:
            await create_buttons(special_mafia_roles, "Oсобые персонажи мафии:", message)
            await CreateRoom.WaitingForEnterSpecialMafia.set()
        elif room.num_special_villagers > 0:
            await create_buttons(special_villager_roles, "Oсобые мирные жители:", message)
            await CreateRoom.WaitingForEnterSpecialVillager.set()
        else:
            await end_func(message, room, state)
    else:
        await message.answer("Роли не существует. Пожалуйста, введите существующего лидера:")

@dp.message_handler(state=CreateRoom.WaitingForEnterSpecialMafia)
async def get_special_mafia(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        room = data.get('room')
    special_mafia = message.text
    role_mapping = {
        "Крёстный отец": Roles.Don,
        "Вор": Roles.Stiller,
        "Адвокат": Roles.Advocat,
        "Стукач": Roles.Snitch
    }
    if special_mafia in role_mapping:
        room.our_roles.append(special_mafia)
        await message.answer(f"{special_mafia} назначен")
        room.num_special_mafias -= 1
        await state.update_data(room=room)
        if room.num_special_mafias > 0:
            await message.answer("Пожалуйста, введите ещё одного особого персонажа мафии")
        elif room.num_special_villagers > 0:
            await create_buttons(special_villager_roles, "Oсобые мирные жители:", message)
            await CreateRoom.WaitingForEnterSpecialVillager.set()
        else:
            await end_func(message, room, state)
    else:
        await message.answer("Роли не существует. Пожалуйста, введите существующего особого персонажа мафии:")


@dp.message_handler(state=CreateRoom.WaitingForEnterSpecialVillager)
async def get_special_villager(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        room = data.get('room')
    special_villager = message.text
    role_mapping = {
        "Доктор": Roles.Doktor,
        "Телохранитель": Roles.Security,
        "Лунатик": Roles.Somnambula,
        "Красотка": Roles.Prostitute,
        "Поклонница": Roles.Fan
    }
    if special_villager in role_mapping:
        room.our_roles.append(special_villager)
        await message.answer(f"{special_villager} назначен")
        room.num_special_villagers -= 1
        await state.update_data(room=room)
        if room.num_special_villagers > 0:
            await message.answer("Пожалуйста, введите ещё одного особого персонажа")
        else:
            await end_func(message, room, state)
    else:
        await message.answer("Роли не существует. Пожалуйста, введите существующего особого персонажа:")

async def players_buttons(room, text):
    role_options = []
    for p in room.players:
        role_options.append(p.getName())

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(*role_options)

    for player in room.players:
        await bot.send_message(player.id, text, reply_markup=keyboard)

async def room_is_exist(room, message, state):
    if room is None:
        await message.answer("Комната не существует!")
        await state.finish()
        return
@dp.message_handler(commands=['add_to_room'])
async def add_to_room(message: types.Message, state: FSMContext):
    global room

    if room is None:
        await message.answer("Комната не существует!")
        await state.finish()
        return

    if len(room.our_roles) > 0:
        await message.answer("Пожалуйста, введите пароль для присоединения: ")
        await CreateRoom.WaitingForPasswordToAdd.set()
    else:
        await message.answer("А игра еще не началась!")
        await state.finish()
        return

@dp.message_handler(state=CreateRoom.WaitingForPasswordToAdd)
async def adder_func(message: types.Message, state: FSMContext):
    global room
    player_id = message.from_user.id
    password_to_enter = message.text
    if room is None:
        await message.answer("Комната не существует!")
        await state.finish()
        return
    if any(player.id == player_id for player in room.players):
        await bot.send_message(player_id, "ID игрока уже существует.")
        await state.finish()
        return
    if room.password == password_to_enter:
        await message.answer("Комната существует! Пожалуйста, введите ник: ")
        await CreateRoom.WaitingForLoginToAdd.set()
    else:
        await message.answer("Пожалуйста, введите корректный пароль для присоединения:")

@dp.message_handler(state=CreateRoom.WaitingForLoginToAdd)
async def login_func(message: types.Message, state: FSMContext):
    global room

    player_id = message.from_user.id
    login_to_enter = message.text

    random_role = random.choice(room.our_roles)
    room.our_roles.remove(random_role)
    response = room.add_new_player(random_role, login_to_enter, player_id)

    await bot.send_message(player_id, response + f"\nОсталось {len(room.our_roles)} мест.")
    await state.update_data(room=room)

    if len(room.our_roles) == 0:
        text = "А игра... уже началась! Ночью ведущий по очереди называет особых персонажей. " \
               "\n/do_your_bissnes - особыe персонажи ночью пользуются своими способностями " \
               "\n/end_night - Ночь заканчивается, и город сталкивается с ее последствиями. Наступает время суда Линча." \
               "\n/start_new_night - День линчевания подошла к концу, сейчас горожане услышат приговор суда, и счастливые пойдут спать."\
               "\n/voting - Ночь закончилась. Наступает время обсуждений и голосования."
        await players_buttons(room, text)

    await state.finish()
    return

@dp.message_handler(commands=['do_your_bissnes'])
async def do_bissnes(message: types.Message, state: FSMContext):
    global room
    player_id = message.from_user.id

    if room is None:
        await message.answer("Комната не существует!")
        await state.finish()
        return

    if any(player.id == player_id for player in room.players):
        await message.answer(f"Пожалуйста, введите имя:                                             👇")
        await CreateRoom.WaitingForEnterVictim.set()
    else:
        await message.answer("Извините, но вы не состоите в этой комнате.")
        await state.finish()
        return

@dp.message_handler(state=CreateRoom.WaitingForEnterVictim)
async def get_victim_name(message: types.Message, state: FSMContext):
    global room
    victim_name = message.text
    player_id = message.from_user.id

    victim = next((victim_player for victim_player in room.players if victim_player.getName() == victim_name), None)
    shoot_player = next((player for player in room.players if player.id == player_id and (player.getRole() == Roles.SaintFather or player.getRole() == Roles.Detective)), None)
    paparaci_player = next((player for player in room.players if player.id == player_id and player.getRole() == Roles.Paparaci), None)

    if shoot_player:
        shoot_player.set_victim(victim)

        role_options = ["Shoot", "Control"]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(*role_options)

        await message.answer(f"Пожалуйста, введите действие :                                             👇", reply_markup=keyboard)
        await CreateRoom.A.set()
    elif paparaci_player:
        paparaci_player.set_victim(victim)
        await message.answer(f"Пожалуйста, введите имя :                                             👇")
        await CreateRoom.B.set()
    elif victim:
        matching_player = next((player for player in room.players if player.id == player_id), None)
        message_text = matching_player.main_function(victim)
        if message_text:  # Check if the message text is not empty
            await bot.send_message(player_id, message_text)
        else:
            await message.answer("Неизвестное имя.")
        await state.finish()
        return
    else:
        await message.answer("Неизвестное имя. Введите имя еще раз: ")

@dp.message_handler(state=CreateRoom.B)
async def get_victim_do(message: types.Message, state: FSMContext):
    player_id = message.from_user.id
    global room
    victim = next((victim_player for victim_player in room.players if victim_player.getName() == message.text), None)
    matching_player = next((player for player in room.players if player.id == player_id and player.getRole() == Roles.Paparaci), None)
    message_text = matching_player.main_function(victim)
    if message_text:  # Check if the message text is not empty
        await bot.send_message(player_id, message_text)
    else:
        await message.answer("Неизвестное имя.")
    await state.finish()
    return

@dp.message_handler(state=CreateRoom.A)
async def get_victim_do(message: types.Message, state: FSMContext):
    player_id = message.from_user.id
    global room
    matching_player = next((player for player in room.players if player.id == player_id and (player.getRole() == Roles.SaintFather or player.getRole() == Roles.Detective)), None)
    if message.text == "Shoot":
        message_text = matching_player.main_function(True)
    else:
        message_text = matching_player.main_function(False)
        if matching_player.getRole() == Roles.SaintFather:
            await bot.send_message(matching_player._victim.id, f"Священник это {matching_player.getName()}")

    if message_text:  # Check if the message text is not empty
        await bot.send_message(player_id, message_text)
    else:
        await message.answer("Неизвестное имя.")
    await state.finish()
    return

async def recikle_players(room, can_voiting, add_text, state):
    num_mafias = 0;
    num_villagers = 0;
    out = ""
    for p in room.players:
        if p.getBlockVoise() or p.getShoot():
            if p.getBlockVoise():
                out += f"\n{p.getName()} не может голосовать днём"
            if p.getShoot():
                out += f"\n{p.getName()} убит"
                if p.id == creator_id:
                    await bot.send_message(p.id,
                                           f"Сегодня ты покидаешь наш город навсегда, {p.getName()}. Но ты остаешься ведущим игры, поэтому не забывай о своих обязанностях даже после смерти." \
                                           "\n/end_night - Ночь заканчивается, и город сталкивается с ее последствиями. Наступает время суда Линча." \
                                           "\n/start_new_night - День линчевания подошла к концу, сейчас горожане услышат приговор суда, и счастливые пойдут спать.")
                else:
                    await bot.send_message(p.id,
                                           f"Сегодня ты покидаешь наш город навсегда, {p.getName()}. Покойся с миром и прощай.")
                room.players.remove(p)
        else:
            can_voiting.append(p.id)

    for p in room.players:
        if p.getType() == Types.Peasefull:
            num_villagers += 1
        elif p.getType() == Types.Mafiozy:
            num_mafias += 1

    if num_mafias == 0:
        out += "\nМирные жители смогли изгнать мафию из города."
    elif num_mafias >= num_villagers:
        out += "\nСегодня мафия победила."
    else:
        out += add_text

    await players_buttons(room, out)

@dp.message_handler(commands=['end_night'])
async def show_rezults(message: types.Message, state: FSMContext):
    global can_voiting
    global room
    global creator_id
    if creator_id == message.from_user.id:
        await message.answer("С возвращением, ведущий.")
    else:
        await message.answer("Вы не являетесь создателем комнаты, обратитесь за помощью к ведущему.")
        return
    await recikle_players(room, can_voiting, f"\nНочь закончилась. Наступает время обсуждений и голосования.\n/voting", state)
    await state.finish()
    return

@dp.message_handler(commands=['voting'])
async def upgrade(message: types.Message, state: FSMContext):
    global can_voiting
    if len(can_voiting) <= 0:
        await message.answer("Боюсь, голосовать просто некому.")
        return
    await message.answer("Введите имя: ")
    await CreateRoom.WaitingForGolos.set()

@dp.message_handler(state=CreateRoom.WaitingForGolos)
async def get_victim_name(message: types.Message, state: FSMContext):
    global voit
    global can_voiting

    victim_name = message.text
    player_id = message.from_user.id

    for ID in can_voiting:
        if player_id == ID:
            voit.append(victim_name)
            can_voiting.remove(player_id)
            if len(can_voiting) <= 0:
                await message.answer("Голосование подошло к концу. Потребуется от ведущего завершить день и объявить результаты суда.")
            else:
                await message.answer("Ваш голос будет учтен на справедливом суде Линча.")
            await state.finish()
            return

    await message.answer("Вы не можете пока голосовать.")
    await state.finish()
    return

@dp.message_handler(commands=['start_new_night'])
async def upgrade(message: types.Message, state: FSMContext):
    global room
    global voit
    global can_voiting
    global creator_id
    global prizon
    if creator_id == message.from_user.id:
        await message.answer("С возвращением, ведущий.")
    else:
        await message.answer("Вы не являетесь создателем комнаты, обратитесь за помощью к ведущему.")
        await state.finish()
        return

    if room is None:
        # Обработка случая, если room равно None
        await message.answer("Ошибка: комната не инициализирована.")
        await state.finish()
        return
    shooter = Mafia("no_name", 1)
    for p in room.players:
        if p in prizon:
            pass
        else:
            p._cosmetic_role = p.getRole()
            p._block = False
            p.block_voise = False

    if len(voit) > 0:
        counter = Counter(voit)
        most_common_value = counter.most_common(1)[0][0]
        linch_player = next((player for player in room.players if player.getName() == most_common_value), None)
        linch_player._shooted = True
        text = " и начинается новая ночь."
        await recikle_players(room, can_voiting, text, state)


    can_voiting = []
    voit = []
    await state.finish()
    return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
