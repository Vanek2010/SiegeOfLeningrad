import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(script_dir, "images")

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    exit("Error: No token provided")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class StoryState(StatesGroup):
    reading_story = State()
    current_part = State()

stories = {
    "long_story": {
        "parts": [
            {
                "text": """Блокада Ленинграда — военная блокада немецкими, финскими и испанскими войсками во
время Великой Отечественной войны Ленинграда (ныне Санкт-Петербург). Длилась с 8
сентября 1941 по 27 января 1944 (блокадное кольцо было прорвано 18 января 1943 года) — 872
дня.""",
                "image": os.path.join(image_dir, "image.jpg")
            },
            {
                "text": """В течение сентября, октября и ноября на город было совершено около 100 налетов и сброшено
64930 зажигательных и 3055 фугасных бомб. Всего же за время блокады на Ленинград было
сброшено 102520 зажигательных и 4653 фугасные бомбы. К моменту снятия блокады в городе
не осталось ни одного полностью уцелевшего квартала. Несмотря на принятые меры,
пострадали многие памятники архитектуры. Были повреждены Адмиралтейство, Инженерный
замок и др. (В одни только Нарвские ворота попало около 2 000 осколков). Значительные
разрушения претерпело здание Кировского театра оперы и балета (Мариинского)""",
                "image": os.path.join(image_dir, "image2.jpg")
            },
            {
                "text": """К середине сентября 1941 запасов муки и зерна оставалось на 35 дней, крупы и макарон - на 30,
мяса - на 33, жиров - на 45, сахара и кондитерских изделий - на 60 дней. В течении сентября -
ноября нормы выдачи хлеба населению снижались в пять раз. Резко сократилась и суточная
норма питания в войсках. Ввиду блокады города с 20 ноября размер продовольственного
пайка составлял: Рабочим — 250 граммов хлеба в сутки , Служащим, иждивенцам и детям до 12
лет — по 125 граммов.
Личному составу военизированной охраны, пожарных команд, истребительных отрядов,
ремесленных училищ и школ ФЗО, находившемуся на котловом довольствии — 300 граммов
Войскам первой линии — 500 граммов
При этом до 50 % хлеба составляли примеси, и он был почти несъедобным. Все остальные
продукты почти перестали выдаваться.""",
                "image": os.path.join(image_dir, "image3.jpg")
            },
            {
                "text": """Число жертв голода стремительно росло − каждый день умирали более 4000 человек Столько
людей умирало в городе в мирное время в течение 40 дней. Были дни, когда умирало 6−7
тысяч человек. Мужчины умирали гораздо быстрее, чем женщины (на каждые 100 смертей
приходилось примерно 63 мужчины и 37 женщин). К концу войны женщины составляли
основную часть городского населения.""",
                "image": os.path.join(image_dir, "image4.jpg")
            },
            {
                "text": """Из меню столовой лета 1942 года: 
Щи из подорожника
Пюре из крапивы и щавеля
Котлеты из свекольной ботвы
Шницель из лебеды
Оладьи из казеина
Суп из дрожжей
Соевое молоко""",
                "image": os.path.join(image_dir, "image5.jpg")
            },
            {
                "text": """Из «Блокадной книги» А.Адамовича и Д.Гранина.
«Восьмилетней Жанне блокада вспоминается как страшный холод. Все время холод, под
одеялом, в шубе и все равно холод. Еще огромная корзина, обитая кусками ватного одеяла, в
которой мать носила обед. Хлеб, кусочками по 200 граммов прятали в чемодан, а чемодан
клали в чулан, чтобы не съесть этот хлеб сразу. Как-то не существовало ни утра, ни вечера.
Ничего. Казалось, что темень сплошная стоит все время, я научилась различать циферблат
часов. И до сих пор, к стыду своему, вспоминаю, что помню только час, когда мама должна
была покормить меня. Иногда я знала, что утро, иногда не знала, потому что практически мы не
спали. Говорят - хлеб спит в человеке. А поскольку хлеба не было, нам не спалось».""",
                "image": os.path.join(image_dir, "image6.jpg")
            }
        ]
    }
}


def create_story_keyboard(has_next: bool) -> types.InlineKeyboardMarkup:
    buttons = []
    if has_next:
        buttons.append(types.InlineKeyboardButton(text="Вперед →", callback_data="next_part"))

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard


@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):

    story_key = "long_story"
    story = stories.get(story_key)

    if not story:
        await message.answer("История не найдена.")
        return

    await state.set_state(StoryState.reading_story)
    await state.update_data(story_key=story_key, current_part=0)
    await send_story_part(message, state)


async def send_story_part(message: types.Message, state: FSMContext):
    data = await state.get_data()
    story_key = data.get("story_key")
    current_part = data.get("current_part", 0)

    story = stories[story_key]
    parts = story["parts"]

    if current_part >= len(parts):
        await message.answer("")
        await state.clear()
        return

    part = parts[current_part]
    part_text = part["text"]
    part_image = part.get("image")

    has_next = current_part < len(parts) - 1

    keyboard = create_story_keyboard(has_next)

    if part_image:
        try:
            photo = FSInputFile(part_image)
            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=part_text, reply_markup=keyboard)
        except FileNotFoundError:
            logging.error(f"File not found: {part_image}")
            await bot.send_message(chat_id=message.chat.id, text=part_text,
                                   reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=message.chat.id, text=part_text,
                               reply_markup=keyboard)


@dp.callback_query(F.data == "next_part")
async def next_part_callback(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_part = data.get("current_part", 0)
    await state.update_data(current_part=current_part + 1)
    await send_story_part(query.message, state)
    await query.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

