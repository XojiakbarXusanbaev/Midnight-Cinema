import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from transliterate import translit

BOT_TOKEN = ""
GROUP_ID = -1002364345269

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
current_movies = {}
movies_cache = {}

class MovieStates(StatesGroup):
    waiting_for_thumbnail = State()
    waiting_for_quality = State()

@dp.errors_handler()
async def error_handler(update, exception):
    print(f"ERROR: {exception}")
    if isinstance(exception, InvalidQueryID):
        print("Invalid Query ID received in inline handler.")
    elif isinstance(exception, BotBlocked):
        print("Bot was blocked by the user.")
    return True

@dp.message_handler(commands=['update_db'])
async def send_welcome(message: types.Message):
    text = load_movies()
    await message.answer(text)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        language_keyboard = InlineKeyboardMarkup(row_width=2)
        language_keyboard.add(
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_language_ru"),
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_language_uz")
        )

        await message.answer(
            "🌐 Пожалуйста, выберите ваш язык:",
            reply_markup=language_keyboard
        )
    else:
        language_code = result[0]
        keyboard = InlineKeyboardMarkup(row_width=2)
        if language_code == 'ru':
            keyboard.add(InlineKeyboardButton(text="🎄 Новогодние фильмы", callback_data="genre_newyear"))
            keyboard.add(
                InlineKeyboardButton(text="🎥 Топ просмотров", callback_data="top_movies_1"),
                InlineKeyboardButton(text="🔍 Поиск фильма", switch_inline_query_current_chat=""),
                InlineKeyboardButton(text="📚 Мультфильмы", callback_data="genre_cartoon_1"),
                InlineKeyboardButton(text="✨ Фантастика", callback_data="genre_sci_fi_1"),
                InlineKeyboardButton(text="🏎 Гонки", callback_data="genre_racing_1"),
                InlineKeyboardButton(text="❤️ Романтические", callback_data="genre_romantic_1"),
                InlineKeyboardButton(text="🗺️ Приключения", callback_data="genre_adventure_1"),
                InlineKeyboardButton(text="🔫 Боевик", callback_data="genre_action_1"),
                InlineKeyboardButton(text="😂 Комедия", callback_data="genre_comedy_1"),
                InlineKeyboardButton(text="👻 Ужастик", callback_data="genre_horror_1"),
                InlineKeyboardButton(text="🌐 Сменить язык", callback_data="change_language")
            )
            await message.answer(
                "🎬 <b>Добро пожаловать в Midnight Cinema!</b>\n\n"
                "⚠️ Поиск кино на латинском алфавите в БЕТА-тестировании\n"
                "😊 Выберите интересующий <b>раздел</b> или воспользуйтесь <b>поиском:</b>",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        elif language_code == 'uz':
            keyboard.add(InlineKeyboardButton(text="🎄 Yangi yil filmlar", callback_data="genre_newyear"))
            keyboard.add(
                InlineKeyboardButton(text="🎥 Ko'rishlar bo'yicha", callback_data="top_movies_1"),
                InlineKeyboardButton(text="🔍 Film qidirish", switch_inline_query_current_chat=""),
                InlineKeyboardButton(text="📚 Multfilmlar", callback_data="genre_cartoon_1"),
                InlineKeyboardButton(text="✨ Fantastika", callback_data="genre_sci_fi_1"),
                InlineKeyboardButton(text="🏎 Poygalar", callback_data="genre_racing_1"),
                InlineKeyboardButton(text="❤️ Romantik", callback_data="genre_romantic_1"),
                InlineKeyboardButton(text="🗺️ Sarguzashtlar", callback_data="genre_adventure_1"),
                InlineKeyboardButton(text="🔫 Jangari", callback_data="genre_action_1"),
                InlineKeyboardButton(text="😂 Komediya", callback_data="genre_comedy_1"),
                InlineKeyboardButton(text="👻 Qo'rqinchli", callback_data="genre_horror_1"),
                InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="change_language")
            )
            await message.answer(
                "🎬 <b>Midnight Cinema ga xush kelibsiz!</b>\n\n"
                "⚠️ Lotin alifbosida kino qidirish beta sinovida\n"
                "😊 Qiziqarli <b>bo'limni</b> tanlang yoki <b>qidiruvdan</b> foydalaning:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

@dp.callback_query_handler(lambda c: c.data.startswith('set_language_'))
async def set_language(callback_query: CallbackQuery):
    language_code = callback_query.data.split('_')[-1]
    user_id = callback_query.from_user.id

    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, language) VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET language=excluded.language
    """, (user_id, language_code))
    conn.commit()
    conn.close()

    if language_code == 'ru':
        await bot.send_message(callback_query.from_user.id, "Язык успешно установлен на русский!")
    elif language_code == 'uz':
        await bot.send_message(callback_query.from_user.id, "Til o'zbek tiliga o'rnatildi!")
    await bot.answer_callback_query(callback_query.id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    if language_code == 'ru':
        keyboard.add(InlineKeyboardButton(text="🎄 Новогодние фильмы", callback_data="genre_newyear"))
        keyboard.add(
            InlineKeyboardButton(text="🎥 Топ просмотров", callback_data="top_movies_1"),
            InlineKeyboardButton(text="🔍 Поиск фильма", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="📚 Мультфильмы", callback_data="genre_cartoon_1"),
            InlineKeyboardButton(text="✨ Фантастика", callback_data="genre_sci_fi_1"),
            InlineKeyboardButton(text="🏎 Гонки", callback_data="genre_racing_1"),
            InlineKeyboardButton(text="❤️ Романтические", callback_data="genre_romantic_1"),
            InlineKeyboardButton(text="🗺️ Приключения", callback_data="genre_adventure_1"),
            InlineKeyboardButton(text="🔫 Боевик", callback_data="genre_action_1"),
            InlineKeyboardButton(text="😂 Комедия", callback_data="genre_comedy_1"),
            InlineKeyboardButton(text="👻 Ужастик", callback_data="genre_horror_1")
        )
    elif language_code == 'uz':
        keyboard.add(InlineKeyboardButton(text="🎄 Yangi yil filmlar", callback_data="genre_newyear"))
        keyboard.add(
            InlineKeyboardButton(text="🎥 Ko'rishlar bo'yicha", callback_data="top_movies_1"),
            InlineKeyboardButton(text="🔍 Film qidirish", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="📚 Multfilmlar", callback_data="genre_cartoon_1"),
            InlineKeyboardButton(text="✨ Fantastika", callback_data="genre_sci_fi_1"),
            InlineKeyboardButton(text="🏎 Poygalar", callback_data="genre_racing_1"),
            InlineKeyboardButton(text="❤️ Romantik", callback_data="genre_romantic_1"),
            InlineKeyboardButton(text="🗺️ Sarguzashtlar", callback_data="genre_adventure_1"),
            InlineKeyboardButton(text="🔫 Jangari", callback_data="genre_action_1"),
            InlineKeyboardButton(text="😂 Komediya", callback_data="genre_comedy_1"),
            InlineKeyboardButton(text="👻 Qo'rqinchli", callback_data="genre_horror_1")
        )

    if language_code == 'ru':
        await bot.send_message(callback_query.from_user.id,
            "🎬 <b>Добро пожаловать в Midnight Cinema!</b>\n\n"
            "⚠️ Поиск кино на латинском алфавите в БЕТА-тестировании\n"
            "😊 Выберите интересующий <b>раздел</b> или воспользуйтесь <b>поиском:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    elif language_code == 'uz':
        await bot.send_message(callback_query.from_user.id,
            "🎬 <b>Midnight Cinema ga xush kelibsiz!</b>\n\n"
            "⚠️ Lotin alifbosida kino qidirish beta sinovida\n"
            "😊 Qiziqarli <b>bo'limni</b> tanlang yoki <b>qidiruvdan</b> foydalaning:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def handle_main_menu(callback_query: CallbackQuery):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    keyboard = InlineKeyboardMarkup(row_width=2)
    language_code = result[0]
    keyboard = InlineKeyboardMarkup(row_width=2)
    if language_code == 'ru':
        keyboard.add(InlineKeyboardButton(text="🎄 Новогодние фильмы", callback_data="genre_newyear"))
        keyboard.add(
            InlineKeyboardButton(text="🎥 Топ просмотров", callback_data="top_movies_1"),
            InlineKeyboardButton(text="🔍 Поиск фильма", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="📚 Мультфильмы", callback_data="genre_cartoon_1"),
            InlineKeyboardButton(text="✨ Фантастика", callback_data="genre_sci_fi_1"),
            InlineKeyboardButton(text="🏎 Гонки", callback_data="genre_racing_1"),
            InlineKeyboardButton(text="❤️ Романтические", callback_data="genre_romantic_1"),
            InlineKeyboardButton(text="🗺️ Приключения", callback_data="genre_adventure_1"),
            InlineKeyboardButton(text="🔫 Боевик", callback_data="genre_action_1"),
            InlineKeyboardButton(text="😂 Комедия", callback_data="genre_comedy_1"),
            InlineKeyboardButton(text="👻 Ужастик", callback_data="genre_horror_1"),
            InlineKeyboardButton(text="🌐 Сменить язык", callback_data="change_language")
        )
        await callback_query.message.answer(
            "🎬 <b>Добро пожаловать в Midnight Cinema!</b>\n\n"
            "⚠️ Поиск кино на латинском алфавите в БЕТА-тестировании\n"
            "😊 Выберите интересующий <b>раздел</b> или воспользуйтесь <b>поиском:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    elif language_code == 'uz':
        keyboard.add(InlineKeyboardButton(text="🎄 Yangi yil filmlar", callback_data="genre_newyear"))
        keyboard.add(
            InlineKeyboardButton(text="🎥 Ko'rishlar bo'yicha", callback_data="top_movies_1"),
            InlineKeyboardButton(text="🔍 Film qidirish", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="📚 Multfilmlar", callback_data="genre_cartoon_1"),
            InlineKeyboardButton(text="✨ Fantastika", callback_data="genre_sci_fi_1"),
            InlineKeyboardButton(text="🏎 Poygalar", callback_data="genre_racing_1"),
            InlineKeyboardButton(text="❤️ Romantik", callback_data="genre_romantic_1"),
            InlineKeyboardButton(text="🗺️ Sarguzashtlar", callback_data="genre_adventure_1"),
            InlineKeyboardButton(text="🔫 Jangari", callback_data="genre_action_1"),
            InlineKeyboardButton(text="😂 Komediya", callback_data="genre_comedy_1"),
            InlineKeyboardButton(text="👻 Qo'rqinchli", callback_data="genre_horror_1")
        )
        keyboard.add(InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="change_language"))
        await callback_query.message.answer(
                "🎬 <b>Midnight Cinema ga xush kelibsiz!</b>\n\n"
                "⚠️ Lotin alifbosida kino qidirish beta sinovida\n"
                "😊 Qiziqarli <b>bo'limni</b> tanlang yoki <b>qidiruvdan</b> foydalaning:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id = ?", (callback_query.from_user.id,))
    language_code = cursor.fetchone()[0]
    conn.close()

@dp.callback_query_handler(lambda c: c.data.startswith("movie_"))
async def handle_movie_selection(callback_query: CallbackQuery):
    movie_id = int(callback_query.data.split("_")[1])
    genre, page = None, None

    movie = get_movie_by_id(movie_id)
    if movie:
        movie_id, name, year, genres, is_premium, age, thumbnail, quality_1080p, quality_720p, quality_480p, views, description = movie

        qualities = []
        if quality_1080p: qualities.append("1080p")
        if quality_720p: qualities.append("720p")
        if quality_480p: qualities.append("480p")
        views = "{:,}".format(views).replace(",", ".")

        caption = (
            f"🎬 <b>{name}</b> ({year})\n\n"
            f"Описание: {description}\n\n"
            f"Возраст: <b>{age}</b>\n"
            f"Просмотры: <b>{views}</b>\n\n"
            f"Жанры: <b>{genres}</b>\n"
        )

        media = types.InputMediaPhoto(
            media=thumbnail,
            caption=caption,
            parse_mode="HTML"
        )

        await bot.edit_message_media(
            media=media,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=quality_keyboard(movie_id, qualities)  
        )
    else:
        await callback_query.message.edit_text("Фильм не найден.")

@dp.callback_query_handler(lambda c: c.data.startswith("quality_"))
async def handle_quality_selection(callback_query: CallbackQuery):
    _, quality, movie_id = callback_query.data.split("_")
    movie_id = int(movie_id)

    if not quality.endswith("p"):
        quality += "p"

    movie = get_movie_by_id(movie_id)

    if movie:
        movie_id, name, year, genres, is_premium, age, thumbnail, quality_1080p, quality_720p, quality_480p, views, discription = movie
        qualities = [quality_1080p,quality_720p,quality_480p]
        file_ids = [quality_1080p,quality_720p,quality_480p]

        if quality == "1080p": file_id = file_ids[0]
        if quality == "720p": file_id = file_ids[1]
        if quality == "480p": file_id = file_ids[2]

        await bot.send_video(
            chat_id=callback_query.from_user.id,
            video=file_id,
            caption=f"🎬 {name} {age} ({year})\nКачество: {quality}",
            protect_content=True
        )
        await bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id
        )
        await callback_query.answer("Видео отправлено!")
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE movies SET views = ? WHERE id = ?", (views + 1, movie_id))
        conn.commit()
        conn.close()
    else:
        await callback_query.message.edit_text("Фильм не найден.")

@dp.callback_query_handler(lambda c: c.data == "top_movies" or c.data.startswith("top_movies_"))
async def handle_top_movies(callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    page = int(data[-1]) if len(data) > 1 else 1  

    items_per_page = 5
    offset = (page - 1) * items_per_page

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, year, views FROM movies ORDER BY views DESC LIMIT ? OFFSET ?",
        (items_per_page, offset)
    )
    movies = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM movies")
    total_movies = cursor.fetchone()[0]
    conn.close()

    if not movies:
        await callback_query.message.edit_text("Нет фильмов в базе данных.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for movie_id, name, year, views in movies:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{name} ({year}) | 👁 {views}",
                callback_data=f"movie_{movie_id}"
            )
        )

    total_pages = (total_movies + items_per_page - 1) // items_per_page

    if page > 1 and page < total_pages:
        keyboard.row(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"top_movies_{page-1}"),
            InlineKeyboardButton("➡️ Вперед", callback_data=f"top_movies_{page+1}")
        )
    elif page > 1:  
        keyboard.add(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"top_movies_{page-1}")
        )
    elif page < total_pages:  
        keyboard.add(
            InlineKeyboardButton("➡️ Вперед", callback_data=f"top_movies_{page+1}")
        )

    keyboard.add(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )

    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id = ?", (callback_query.from_user.id,))
    language_code = cursor.fetchone()[0]
    conn.close()

    if language_code == 'ru':
        await callback_query.message.edit_text(
            f"🔥 <b>Топ фильмов по просмотрам</b>\n\n"
            f"Страница {page} из {total_pages}\n",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    elif language_code == 'uz':
        await callback_query.message.edit_text(
            f"🔥 <b>Ko'rishlar bo'yicha filmlar reytingi</b>\n\n"
            f"{page} -sahifa {total_pages} dan\n",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@dp.callback_query_handler(lambda c: c.data.startswith("genre_"))
async def handle_genre_selection(callback_query: CallbackQuery):
    data = callback_query.data
    parts = data.split("_")

    if len(parts) < 3:
        await callback_query.answer("Ошибка в данных кнопки.", show_alert=True)
        return

    genre = "_".join(parts[1:-1])
    page_str = parts[-1]

    try:
        page = int(page_str)
    except ValueError:
        await callback_query.answer(f"Некорректный номер страницы: {page_str}", show_alert=True)
        return

    items_per_page = 5
    offset = (page - 1) * items_per_page

    genres_mapping = {
        "newyear": "Новый_год",
        "cartoon": "Мультфильм",
        "sci_fi": "Фантастика",
        "racing": "Гонки",
        "romantic": "Романтика",
        "adventure": "Приключения",
        "action": "Боевик",
        "comedy": "Комедия",
        "horror": "Ужасы"
    }
    selected_genre = genres_mapping.get(genre, None)

    if not selected_genre:
        await callback_query.message.edit_text("Жанр не найден.")
        return

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, year FROM movies WHERE genres LIKE ? LIMIT ? OFFSET ?",
        (f"%{selected_genre}%", items_per_page, offset)
    )
    movies = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) FROM movies WHERE genres LIKE ?",
        (f"%{selected_genre}%",)
    )
    total_movies = cursor.fetchone()[0]
    conn.close()

    if not movies:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE id = ?", (callback_query.from_user.id,))
        language_code = cursor.fetchone()[0]
        conn.close()

        if language_code == 'ru':
            await callback_query.message.edit_text(f"Нет фильмов в жанре {selected_genre}.")
        elif language_code == 'uz':
            await callback_query.message.edit_text(f"{selected_genre} janrida filmlar yo'q.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for movie_id, title, year in movies:
        keyboard.add(InlineKeyboardButton(
            text=f"{title} ({year})",
            callback_data=f"movie_{movie_id}"
        ))

    total_pages = (total_movies + items_per_page - 1) // items_per_page

    if page > 1 and page < total_pages:
        keyboard.row(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"genre_{genre}_{page-1}"),
            InlineKeyboardButton("➡️ Вперед", callback_data=f"genre_{genre}_{page+1}")
        )
    elif page > 1:  
        keyboard.add(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"genre_{genre}_{page-1}")
        )
    elif page < total_pages:  
        keyboard.add(
            InlineKeyboardButton("➡️ Вперед", callback_data=f"genre_{genre}_{page+1}")
        )

    keyboard.add(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )

    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id = ?", (callback_query.from_user.id,))
    language_code = cursor.fetchone()[0]
    conn.close()

    if language_code == 'ru':
        await callback_query.message.edit_text(
            f"📚 <b>{selected_genre}</b>\n\n"
            f"Страница {page} из {total_pages}\n",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    elif language_code == 'uz':
        await callback_query.message.edit_text(
            f"📚 <b>{selected_genre}</b>\n\n"
            f"{page} -sahifa {total_pages} dan\n",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@dp.callback_query_handler(lambda c: c.data.startswith("quality"))
async def handle_quality_choice(callback_query: types.CallbackQuery):
    _, quality, file_id = callback_query.data.split(":")
    await bot.send_video(callback_query.message.chat.id, video=file_id,protect_content=True)
    await callback_query.answer(f"Вы выбрали качество {quality}.")

async def laymon(message=None, callback_query=None):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Недавно опубликованные", callback_data="recent_movies"))

    if message:
        await message.answer("Выберите действие:", reply_markup=keyboard)
    elif callback_query:
        await callback_query.message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message_handler()
async def send_movie(message: types.Message):
    await message.delete()
    if message.text.startswith("фильм:"):
            
        movie_title= message.text[6:]
        conn = sqlite3.connect("movies.db")
        query = "SELECT id FROM movies WHERE title = ?"
        cursor = conn.cursor()
        cursor.execute(query, (movie_title,))
        movie_id = list(cursor.fetchone())[0]

        movie = get_movie_by_id(movie_id)
        if movie:
            movie_id, name, year, genres, is_premium, age, thumbnail, quality_1080p, quality_720p, quality_480p, views, discription = movie

            qualities = []
            if quality_1080p: qualities.append("1080p")
            if quality_720p: qualities.append("720p")
            if quality_480p: qualities.append("480p")
            views = "{:,}".format(views).replace(",", ".")

            caption = (
                f"🎬 <b>{name}</b> ({year})\n\n"
                f"Описание: {discription}\n\n"
                f"Возраст: <b>{age}</b>\n"
                f"Просмотры: <b>{views}</b>\n\n"
                f"Жанры: <b>{genres}</b>\n"
            )

            await bot.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,  
                caption=caption,  
                reply_markup=quality_keyboard(movie_id,qualities, True),
                parse_mode="HTML"  
            )
        else:
            await bot.send_message(message.chat.id, "Фильм не найден.")

@dp.callback_query_handler(lambda c: c.data == "change_language")
async def change_language(callback_query: CallbackQuery):
    language_keyboard = InlineKeyboardMarkup(row_width=2)
    language_keyboard.add(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_language_ru"),
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_language_uz")
    )
    await bot.send_message(callback_query.from_user.id, "🌐 Пожалуйста, выберите ваш язык:", reply_markup=language_keyboard)
    await bot.answer_callback_query(callback_query.id)

if __name__ == "__main__":
    init_db()
    load_movies()
    logging.info("Бот запущен и готов к работе.")
    executor.start_polling(dp, skip_updates=True)