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

class CreateRoom(StatesGroup):
    WaitingForNumberOfPlayers = State()  # Ожидание количества игроков
    WaitingForPlayerNames = State()  # Ожидание имен игроков
    WaitingForEnterPassword = State()  # Ожидание пароля
    WaitingForPasswordToAdd = State()
    WaitingForChoosingLeader = State()
    WaitingForChoosingSpecialVillager = State()
    WaitingForChoosingSpecialMafia = State()
    WaitingForEnterLeader = State()
    WaitingForEnterSpecialVillager = State()
    WaitingForEnterSpecialMafia = State()
    WaitingForEnterVictim = State()
    WaitingForRoleSelection = State()
    WaitingForEndRoomCreation = State()
    WaitingForGolos = State()

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

class Player:
    def __init__(self, name, role, id):
        self.name = name
        self.role = role
        self.id = id
        self._shooted = False  # Инициализируем атрибут _victim значением None
        self._block = False
        self.block_voise = False

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

    def getShoot(self):
        return self._shooted

    def getBlock(self):
        return self._block

    def getBlockVoise(self):
        return self.block_voise

    def getName(self):
        return self.name

    def getRole(self):
        return self.role

    def main_function(self, victim):
        pass

class Doctor(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Doktor, id)

    def main_function(self, victim):
        victim.setShoot(False, self)
        return f"Доктор хочет защитить {victim.getName()}"

class Security(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Security, id)

    def main_function(self, victim):
        if victim.getShoot():
            victim.setShoot(False, self)
            self.setShoot(True, self)
        return f"Телохранитель хочет защитить {victim.getName()}"

class Somnambula(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Somnambula, id)

    def main_function(self, victim):
        victim.setShoot(True, self)
        return f"Лунатик притворяется, что хочет застрелить {victim.getName()}"

class Prostitute(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Prostitute, id)

    def main_function(self, victim):
        victim.setBlock(True, self)
        victim.setShoot(False, self)
        return f"Красотка хочет лишить способностей, а заодно и защитить {victim.getName()}"

class Fan(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Fan, id)

    def main_function(self, victim):
        if victim.getRole() == Roles.Detective or victim.getRole() == Roles.SaintFather or victim.getRole() == Roles.Loer or victim.getRole() == Roles.Paparaci or victim.getRole() == Roles.Prizonist or victim.getRole() == Roles.Sherif:
            return f"Поклонница хочет проверить {victim.getName()}" \
                f"\n{victim.getName()} это {victim.getRole()}"
        else:
            return f"Поклонница хочет проверить {victim.getName()}" \
                f"\n{victim.getName()} это не лидер"

class Sherif(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Sherif, id)

    def main_function(self, victim):
        victim.setShoot(True, self)
        return f"Шериф хочет застрелить {victim.getName()}"

class Prizonist(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Prizonist, id)

    def main_function(self, victim):
        if victim.getRole() == Roles.Mafia or victim.getRole() == Roles.Don or victim.getRole() == Roles.Stiller or victim.getRole() == Roles.Advocat or victim.getRole() == Roles.Snitch:
            victim.setBlock(True, self)
            victim.setBlockVose(True, self)
            return f"Тюремщик хочет проверить {victim.getName()}" \
                   f"\n{victim.getName()} это {victim.getRole()}" \
                   f"\n{victim.getName()} попадает в тюрьму."
        else:
            return f"Тюремщик хочет проверить {victim.getName()}" \
                   f"\n{victim.getName()} это {victim.getRole()}"

class Detective(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Detective, id)

    def main_function(self, victim):
        if victim[1]:
            victim[0].setShoot(True, self)
            return f"Детектив хочет застрелить {victim[0].getName()}"
        else:
            return f"Детектив хочет проверить {victim[0].getName()}" \
                   f"\n{victim[0].getName()} это {victim[0].getRole()}"

class SaintFather(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.SaintFather, id)

    def main_function(self, victim):
        if victim[1]:
            victim[0].setShoot(True, self)
            return f"Священник хочет застрелить {victim[0].getName()}"
        else:
            # await bot.send_message(victim[0].id, f"Священник это {self.getName()}")
            return f"Священник хочет проверить {victim[0].getName()}" \
                   f"\n{victim[0].getName()} это {victim[0].getRole()}"

class Loer(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Loer, id)

    def main_function(self, victim):
        return f"Судья хочет проверить {victim[0].getName()}" \
               f"\n{victim[0].getName()} это {victim[0].getRole()}"

class Mafia(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Mafia, id)

    def main_function(self, victim):
        if victim.getRole() == Roles.Somnambula:
            return "Мафиози вычислили и застрелили лунатика. " \
                   "\nOни получают право ещё на один выстрел."
        victim.setShoot(True, self)
        return f"Мафия хочет застрелить {victim.getName()}"

class Villager(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Villager, id)

    def main_function(self, victim):
        return "HA-HA-HA-HA"

class Don(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Don, id)

    def main_function(self, victim):
        victim.setBlockVoise(True, self)
        return f"Крёстный отец хочет лишить права голоса {victim.getName()}"

class Stiller(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Stiller, id)

    def main_function(self, victim):
        victim.setRole(Roles.Mafia, self)
        return f"Стукач хочет оклеветать {victim.getName()}"

class Advocat(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Advocat, id)

    def main_function(self, victim):
        return f"Адвокат хочет проверить {victim.getName()}" \
               f"\n{victim.getName()} это {victim.getRole()}" \
               f"\nАдвокат не имеет права озвучивать ночью то, что узнал, и не может прямо сообщить своим подельникам, что он адвокат."

class Snitch(Player):
    def __init__(self, name, id):
        super().__init__(name, Roles.Snitch, id)

    def main_function(self, victim):
        victim.setBlock(True, self)
        return f"Вор хочет лишить способностей {victim.getName()}"

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
            return True
        else:
            print(f"No, {self.our_roles.count()}")
            return False

    def add_new_player(self, role, name, id):
        if len(self.players) >= self.num_players:
            return "Количество игроков в комнате превышено"
        player = None
        if role == Roles.Villager:
            player = Villager(name, id)
        elif role == Roles.Mafia:
            player = Mafia(name, id)
        elif role == Roles.Don:
            player = Don(name, id)
        elif role == Roles.Doktor:
            player = Doctor(name, id)
        elif role == Roles.Prostitute:
            player = Prostitute(name, id)
        elif role == Roles.Sherif:
            player = Sherif(name, id)
        elif role == Roles.Detective:
            player = Detective(name, id)
        elif role == Roles.SaintFather:
            player = SaintFather(name, id)
        elif role == Roles.Loer:
            player = Loer(name, id)
        elif role == Roles.Prizonist:
            player = Prizonist(name, id)
        elif role == Roles.Security:
            player = Security(name, id)
        elif role == Roles.Somnambula:
            player = Somnambula(name, id)
        elif role == Roles.Fan:
            player = Fan(name, id)
        elif role == Roles.Stiller:
            player = Stiller(name, id)
        elif role == Roles.Advocat:
            player = Advocat(name, id)
        elif role == Roles.Snitch:
            player = Snitch(name, id)

        self.players.append(player)
        return f"{player.getName()}, Вы {player.getRole()}"

    def create_roles(self, num):
        if num == 2:
            self.num_villagers = 0
            self.num_leaders = 1
            self.num_special_villagers = 0
            self.num_mafias = 0
            self.num_special_mafias = 1
        elif num == 5:
            self.num_villagers = 2
            self.num_leaders = 1
            self.num_special_villagers = 1
            self.num_mafias = 1
        elif num == 6:
            self.num_villagers = 3
            self.num_leaders = 1
            self.num_mafias = 2
        elif num == 7:
            self.num_villagers = 4
            self.num_leaders = 1
            self.num_mafias = 1
            self.num_special_mafias = 1
        elif 8 <= num < 11:
            self.num_villagers = num - 5
            self.num_special_villagers = 1
            self.num_leaders = 1
            self.num_mafias = 2
            self.num_special_mafias = 1
        elif 11 <= num < 14:
            self.num_villagers = num - 7
            self.num_special_villagers = 2
            self.num_leaders = 1
            self.num_mafias = 3
            self.num_special_mafias = 1
        elif num == 14:
            self.num_villagers = 6
            self.num_special_villagers = 2
            self.num_leaders = 1
            self.num_mafias = 4
            self.num_special_mafias = 1
        elif 15 <= num < 17:
            self.num_villagers = num - 8
            self.num_special_villagers = 2
            self.num_leaders = 1
            self.num_mafias = 3
            self.num_special_mafias = 2
        for _ in range(self.num_villagers):
            self.add_new_role(Roles.Villager)
        for _ in range(self.num_mafias):
            self.add_new_role(Roles.Mafia)


bot = Bot(token="6525366774:AAE1wYeQf03USfM2ilT-1h6aIKwrk8q5jjE")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

global num_players
num_players = 0

global room
room = None

global creator_id
creator_id = ""
@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    global creator_id
    await message.answer("Привет! Я ваш mafia-бот.\n /create_room - создать комнату\n /add_to_room - присоединениться к комнате")
    creator_id = message.from_user.id

@dp.message_handler(commands=['create_room'])
async def create_room(message: types.Message):
    role_options = []

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(*role_options)
    await message.answer("Введите количество игроков в комнате:", reply_markup=keyboard)
    await CreateRoom.WaitingForNumberOfPlayers.set()

@dp.message_handler(state=CreateRoom.WaitingForNumberOfPlayers)
async def get_number_of_players(message: types.Message, state: FSMContext):
    global num_players
    try:
        num_players = int(message.text)
        if num_players < 0:
            await message.answer("Количество игроков должно быть больше 4. Введите количество игроков еще раз:")
        else:
            await message.answer("Пожалуйста, придумайте пароль для присоединения:")
            await CreateRoom.WaitingForChoosingLeader.set()
    except ValueError:
        await message.answer("Пожалуйста, введите число игроков в числовом формате.")


@dp.message_handler(state=CreateRoom.WaitingForChoosingLeader)
async def choose_leader(message: types.Message, state: FSMContext):
    enter_code = message.text
    global room
    room = Room(num_players, enter_code)
    if room is None:
        await message.answer("Комната не существует!")
        await state.finish()
        return
    role_options = [
            "Детектив", "Священник", "Судья",
            "Журналист", "Тюремщик", "Шериф"
        ]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(*role_options)

    await message.answer("В игре может быть только один лидер: "
                             "\n     Детектив - Может либо застрелить одного игрока, либо узнать его роль."
                             "\n     📿Священник - Может либо застрелить одного игрока, либо узнать его роль. Этот игрок узнаёт личность священника."
                             "\n     ⚖️Судья - Ночью может узнать роль одного игрока. Днём может спасти от суда Линча одного игрока."
                             "\n     📼Журналист - Может выбрать двух игроков, чтобы узнать, одинаковые у них стороны или разные."
                             "\n     Тюремщик - Может узнать роль одного игрока. Если этот игрок преступник, он сразу отправляется в тюрьму. После смерти тюремщика все заключённые выходят из тюрьмы."
                             "\n     Шериф - Может застрелить одного игрока."
                             "\nПожалуйста, введите лидера:                                             👇", reply_markup=keyboard)

    await CreateRoom.WaitingForEnterLeader.set()


@dp.message_handler(state=CreateRoom.WaitingForEnterLeader)
async def get_leader(message: types.Message, state: FSMContext):
    global room
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
        room.add_new_role(leader)
        await message.answer(f"лидер {leader} назначен")
        if room.num_special_mafias > 0:
            role_options = [
                "Крёстный отец", "Вор", "Адвокат",
                "Стукач"
            ]

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            keyboard.add(*role_options)
            await message.answer(f"Oсобые персонажи мафии: "
                    "\n    💰Крёстный отец - Может выбрать одного игрока. Этот игрок не может голосовать днём."
                    "\n    🔐Вор - Может выбрать одного из игроков. Этот игрок не может пользоваться своими способностями этой ночью."
                    "\n    💼Адвокат - Может узнать роль одного игрока.  Он не имеет права озвучивать ночью то, что узнал, и не может прямо сообщить своим подельникам, что он адвокат."
                    "\n    🐀Стукач - Может выбрать одного игрока. Если кто-нибудь узнаёт роль этого игрока, ведущий должен сообщить, что этот игрок мафиози."
                    f"\n Пожалуйста, введите особого персонажа мафии:                                             👇", reply_markup=keyboard)
            await CreateRoom.WaitingForEnterSpecialMafia.set()
        elif room.num_special_villagers > 0:
            role_options = [
                "Доктор", "Телохранитель", "Лунатик",
                "Красотка", "Поклонница"
            ]

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            keyboard.add(*role_options)
            await message.answer(f"Oсобые мирные жители: "
                    "\n    💉Доктор - Перед стрельбой может выбрать другого игрока. Этот игрок не может быть убит этой ночью."
                    "\n    🛡️Телохранитель - Перед стрельбой может выбрать другого игрока. Погибает вместо него, если он должен быть убит этой ночью."
                    "\n    💤Лунатик - Притворяется одним из мафиози. Если убит мафией, мафия может застрелить ещё одного игрока."
                    "\n    👗Красотка -  Перед остальными действиями может выбрать одного игрока. Этот игрок не может пользоваться своими способностями этой ночью, но также не может быть убит."
                    "\n    💋Поклонница - Может выбрать одного игрока. Если это лидер, узнаёт его роль."
                    f"\nПожалуйста, введите особого персонажа мафии:                                             👇", reply_markup=keyboard)
            await CreateRoom.WaitingForEnterSpecialVillager.set()
        else:
            await message.answer(f"Комната на {len(room.our_roles)} игроков создана! Пароль {room.password}")
            await message.answer("/create_room - создать комнату\n /add_to_room - присоединиться к комнате")
            await state.finish()  # Завершение состояния
            return
    else:
        await message.answer("Роли не существует. Пожалуйста, введите существующего лидера:")

@dp.message_handler(state=CreateRoom.WaitingForEnterSpecialMafia)
async def get_special_mafia(message: types.Message, state: FSMContext):
    global room
    special_mafia = message.text
    role_mapping = {
        "Крёстный отец": Roles.Don,
        "Вор": Roles.Stiller,
        "Адвокат": Roles.Advocat,
        "Стукач": Roles.Snitch
    }
    if special_mafia in role_mapping:
        room.add_new_role(special_mafia)
        await message.answer(f"{special_mafia} назначен")
        room.num_special_mafias -= 1
        if room.num_special_mafias > 0:
            await message.answer("Пожалуйста, введите ещё одного особого персонажа мафии")
        elif room.num_special_villagers > 0:
            role_options = [
                "Доктор", "Телохранитель", "Лунатик",
                "Красотка", "Поклонница"
            ]

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            keyboard.add(*role_options)
            await message.answer(f"Oсобые мирные жители: "
                    "\n    💉Доктор - Перед стрельбой может выбрать другого игрока. Этот игрок не может быть убит этой ночью."
                    "\n    🛡️Телохранитель - Перед стрельбой может выбрать другого игрока. Погибает вместо него, если он должен быть убит этой ночью."
                    "\n    💤Лунатик - Притворяется одним из мафиози. Если убит мафией, мафия может застрелить ещё одного игрока."
                    "\n    👗Красотка -  Перед остальными действиями может выбрать одного игрока. Этот игрок не может пользоваться своими способностями этой ночью, но также не может быть убит."
                    "\n    💋Поклонница - Может выбрать одного игрока. Если это лидер, узнаёт его роль."
                    f"\nПожалуйста, введите особого персонажа мафии:                                             👇", reply_markup=keyboard)
            await CreateRoom.WaitingForEnterSpecialVillager.set()
        else:
            await message.answer(f"Комната на {len(room.our_roles)} игроков создана! Пароль {room.password}")
            await message.answer("/create_room - создать комнату\n /add_to_room - присоединиться к комнате")
            await state.finish()  # Завершение состояния
            return
    else:
        await message.answer("Роли не существует. Пожалуйста, введите существующего особого персонажа мафии:")


@dp.message_handler(state=CreateRoom.WaitingForEnterSpecialVillager)
async def get_special_villager(message: types.Message, state: FSMContext):
    global room
    special_villager = message.text
    role_mapping = {
        "Доктор": Roles.Doktor,
        "Телохранитель": Roles.Security,
        "Лунатик": Roles.Somnambula,
        "Красотка": Roles.Prostitute,
        "Поклонница": Roles.Fan
    }
    if special_villager in role_mapping:
        room.add_new_role(special_villager)
        await message.answer(f"{special_villager} назначен")
        room.num_special_villagers -= 1
        if room.num_special_villagers > 0:
            await message.answer("Пожалуйста, введите ещё одного особого персонажа")
        else:
            await message.answer(f"Комната на {len(room.our_roles)} игроков создана! Пароль {room.password}")
            await message.answer("/create_room - создать комнату\n /add_to_room - присоединиться к комнате")
            await state.finish()  # Завершение состояния
            return
    else:
        await message.answer("Роли не существует. Пожалуйста, введите существующего особого персонажа:")

@dp.message_handler(state=CreateRoom.WaitingForEndRoomCreation)
async def end_creation(message: types.Message, state: FSMContext):
    await message.answer(f"Комната на {len(room.our_roles)} игроков создана! Пароль {room.password}")
    await message.answer("/create_room - создать комнату\n /add_to_room - присоединиться к комнате")
    await state.finish()  # Завершение состояния
    return

@dp.message_handler(commands=['add_to_room'])
async def add_to_room(message: types.Message, state: FSMContext):
    global room
    player_id = message.from_user.id
    if len(room.our_roles) > 0:
        await message.answer("Пожалуйста, введите пароль для присоединения и свой ник: (password login)")
        await CreateRoom.WaitingForPasswordToAdd.set()
    else:
        await bot.send_message(player_id, "А игра еще не началась!")
        await state.finish()
        return

@dp.message_handler(state=CreateRoom.WaitingForPasswordToAdd)
async def adder_func(message: types.Message, state: FSMContext):
    player_id = message.from_user.id
    passwor_to_enter = message.text.split(' ')
    global room
    if room is None:
        await message.answer("Комната не существует!")
        await state.finish()
        return
    if room.password == passwor_to_enter[0]:
        await message.answer("Комната существует! Роли будут разосланы в ближайшее время.")

        for player in room.players:
            if player_id == player.id:
                await bot.send_message(player_id, "ID игрока уже существует.")
                await state.finish()
                return

        if len(room.our_roles) > 0:
            random_role = random.choice(room.our_roles)
            room.our_roles.remove(random_role)
            response = room.add_new_player(random_role, passwor_to_enter[1], player_id)
            if response:  # Проверяем, что response не None
                await bot.send_message(player_id, response + f"\nОсталось {len(room.our_roles)} мест.")
            else:
                await bot.send_message(player_id, "Введена некорректная роль.")

            if len(room.our_roles) == 0:
                role_options = []

                for p in room.players:
                    role_options.append(p.getName())

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                keyboard.add(*role_options)

                for player in room.players:
                    await bot.send_message(player.id,
                                           "А игра... уже началась! Ночью ведущий по очереди называет особых персонажей. "
                                           "\n/do_your_bissnes - особыe персонажи ночью пользуются своими способностями"
                                           "\n/end_night - наступает новое дневное обсуждение"
                                           "\n/start_new_night"
                                           "\n/golosovanije"
                                          f"\nВ игре действуют имена: {role_options}", reply_markup=keyboard)
        await state.finish()
        return
    else:
        await message.answer("Пожалуйста, введите пароль для присоединения. Введите свой ник:")

@dp.message_handler(commands=['do_your_bissnes'])
async def do_bissnes(message: types.Message, state: FSMContext):
    player_id = message.from_user.id
    for player in room.players:
        if player.id == player_id:
            if player.getShoot():
                await message.answer("You are dead, camone!")
                await state.finish()
                return
    out = ""
    for player in room.players:
        out += f"\n- {player.getName()}"

    await message.answer(f"В игре действуют имена: {out}\nПожалуйста, введите имя: ")
    await CreateRoom.WaitingForEnterVictim.set()

@dp.message_handler(state=CreateRoom.WaitingForEnterVictim)
async def get_victim_name(message: types.Message, state: FSMContext):
    global room
    victim_name = message.text
    victim = None
    player_id = message.from_user.id
    for victim_player in room.players:
        if victim_player.getName() == victim_name:
            victim = victim_player
            continue
    for player in room.players:
        if player.id == player_id:
            message_text = player.main_function(victim)
            if message_text:  # Check if the message text is not empty
                await bot.send_message(player_id, message_text)
            else:
                await bot.send_message(player_id, "Message text is empty")
            await state.finish()
            return
    await bot.send_message(player_id, "Unknow name")
    await state.finish()
    return

@dp.message_handler(commands=['end_night'])
async def show_rezults(message: types.Message, state: FSMContext):
    global room
    out = ""
    role_options = []

    for p in room.players:
        role_options.append(p.getName())
        if p.getShoot():
            out += f"\n{p.getName()} убит"
            room.players.remove(p)
        if p.getBlockVoise():
            out += f"\n{p.getName()} не может голосовать днём"

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(*role_options)
    for p in room.players:
        bot.send_message(p.id, "End night", reply_markup=keyboard)

    for player in room.players:
        if not player.getBlockVoise():
            await bot.send_message(player.id, f"{out}\n Nachinajem golosovanije /golosovanije", reply_markup=keyboard)
    await state.finish()
    return

@dp.message_handler(commands=['start_new_night'])
async def upgrade(message: types.Message, state: FSMContext):
    global room
    role_options = []

    for p in room.players:
        role_options.append(p.getName())

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(*role_options)
    for p in room.players:
        p._block = False
        p.block_voise = False

    for player in room.players:
        if not player.getShoot():
            await bot.send_message(player.id, "Start new night", reply_markup=keyboard)
    await state.finish()
    return

@dp.message_handler(commands=['golosovanije'])
async def upgrade(message: types.Message, state: FSMContext):

    await message.answer("Vvedite name: ")
    await CreateRoom.WaitingForGolos.set()
global golosoval
golosoval = []

global golos
golos = []
from collections import Counter
@dp.message_handler(state=CreateRoom.WaitingForGolos)
async def get_victim_name(message: types.Message, state: FSMContext):
    global golos
    global golosoval
    global room
    golos.append(message.text)
    golosoval.append(message.from_user.id)

    counter = Counter(golos)
    most_common_value = counter.most_common(1)[0][0]
    for player in room.players:
        await bot.send_message(player.id, f"\n{most_common_value} убит")

    await state.finish()
    return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
