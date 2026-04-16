import os
import random
import sqlite3
from tkinter import *
from datetime import datetime
from tkinter import messagebox, ttk


# Класс-контейнер для всех констант приложения
class Constants:

    # ----- ИМЕНА ФАЙЛОВ -----
    DEFAULT_FILE_NAME = "data.txt"
    DB_NAME = "data.db"
    ICON_NAME = "icon.png"

    # ----- ДИАПАЗОНЫ ЗНАЧЕНИЙ КОНФИГА -----
    SESSION_WORDS_MIN = 5
    SESSION_WORDS_MAX = 50
    CARD_WORDS_MIN = 2
    CARD_WORDS_MAX = 6
    WORD_LEARNED_LIMIT_MIN = 5
    WORD_LEARNED_LIMIT_MAX = 50
    DELAY_MIN = 0
    DELAY_MAX = 5

    # ----- ЗАГОЛОВКИ МЕНЮ -----
    MENU_TITLE = """
╔════════════════════════════════════════════════╗
║                                                ║
║                  Furry Words                   ║
║              Изучение английского              ║
║                                                ║
╚════════════════════════════════════════════════╝
""".strip()
    SESSION_TITLE = """
╔════════════════════════════════════════════════╗
║                                                ║
║                  Изучение слов                 ║
║                                                ║
╚════════════════════════════════════════════════╝
""".strip()
    RESULTS_TITLE = """
╔════════════════════════════════════════════════╗
║                                                ║
║                   Результаты                   ║
║                                                ║
╚════════════════════════════════════════════════╝
""".strip()
    SETTINGS_TITLE = """
╔════════════════════════════════════════════════╗
║                                                ║
║                    Настройки                   ║
║                                                ║
╚════════════════════════════════════════════════╝
""".strip()
    STATS_TITLE = """
╔════════════════════════════════════════════════╗
║                                                ║
║                   Статистика                   ║
║                                                ║
╚════════════════════════════════════════════════╝
""".strip()
    DB_EDITOR_TITLE = """
╔════════════════════════════════════════════════╗
║                                                ║
║              Редактор базы данных              ║
║                                                ║
╚════════════════════════════════════════════════╝
""".strip()
    IMPORT_TITLE = """
╔════════════════════════════════════════════════╗
║                                                ║
║                  Импорт данных                 ║
║                                                ║
╚════════════════════════════════════════════════╝
""".strip()

    # ----- СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЮ -----
    CONFIG_SAVED = "Конфиг успешно сохранён"
    WORD_ADDED = "Новое слово успешно добавлено в БД"
    WORD_EXISTS = "Некорректные данные или слово уже существует в БД"
    EMPTY_DB = "Недостаточно данных в БД..."
    EMPTY_FILE = "Файл пустой"
    NO_FILE_EXISTS = "Файл не найден"
    FILE_EXISTS = "Файл %s уже существует. Перезаписать данные в него?"
    NO_UNLEARNED = "Недостаточно неизученных слов. Добавьте новые, увеличьте предел изучения слова или сбросьте статистику."
    EXIT_YESNO = "Вы уверены, что хотите выйти?"
    WORD_DELETE_YESNO = "Вы уверены, что хотите удалить выделенные слова?"
    STATS_RESET_YESNO = "Вы уверены, что хотите сбросить статистику?"
    DB_RESET_YESNO = "Вы уверены, что хотите сбросить БД до начальных настроек?"
    DB_RESET_CONFIRM_YESNO = "Вы точно уверены?"
    NO_EXPORT_DATA = "Нет данных для экспорта"
    WELCOME = "Обнаружен файл %s. Заполнить базу данных данными из файла?"
    EXPORTED = "Экспортировано %s слов"

    # ----- НАЗВАНИЯ ТАБЛИЦ -----
    WORDS_ENG = "words_eng"
    WORDS_RUS = "words_rus"
    STATISTICS = "statistics"
    CONSTANTS = "constants"
    CONFIG = "config"

    # ----- КОНСТАНТЫ для таблицы constants -----
    SESSION_COUNT_CONST = "sessions_count"

    # ----- СТИЛИ ВИДЖЕТОВ -----
    TITLE_STYLE = "Title.TLabel"
    WORD_STYLE = "Word.TLabel"
    CORRECT_BTN_STYLE = "Correct.TButton"
    WRONG_BTN_STYLE = "Wrong.TButton"

    # ----- ШРИФТЫ -----
    DEFAULT_FONT = "Arial"
    TITLE_FONT = "Courier New"

    # ----- ШИРИНА КНОПОК -----
    MENU_BUTTON_WIDTH = 25
    SESSION_BUTTON_WIDTH = 30
    SESSION_RESULTS_BUTTON_WIDTH = 25
    STATS_BUTTON_WIDTH = 25
    SETTINGS_BUTTON_WIDTH = 25
    DB_EDITOR_BUTTON_WIDTH = 25
    IMPORT_EXPORT_BUTTON_WIDTH = 25
    TRANSLATION_BUTTON_WIDTH = 30

    # ----- ФИЛЬТРЫ ВЫБОРКИ СЛОВ -----
    LEARNED_ONLY = "learned_only"
    UNLEARNED_ONLY = "unlearned_only"
    WORDS_ONLY = "words_only"
    TRANSLATIONS_ONLY = "translations_only"

    # ----- SQL-СКРИПТЫ -----
    INIT_SCRIPT = """
CREATE TABLE IF NOT EXISTS words_eng (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_eng TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS words_rus (
    word_id INTEGER,
    word_rus TEXT NOT NULL,
    UNIQUE(word_id, word_rus)
);

CREATE TABLE IF NOT EXISTS statistics (
    word_id INTEGER REFERENCES words_eng(word_id) PRIMARY KEY,
    count_of_learned INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    unsuccessful_attempts INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS constants (
    sessions_count INTEGER
);

CREATE TABLE IF NOT EXISTS config (
    session_words INT,
    card_words INT,
    word_learned_limit INT,
    delay INT
);
"""

# Класс для работы с базой данных SQLite
class Database(Constants):

    # Конструктор: подключается к БД и инициализирует данные
    def __init__(self, file_name):
        self.name = file_name
        self.conn, self.cur = self.init_tables()
        self.init_data()

    # Создаёт таблицы в БД, если их нет
    def init_tables(self):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.executescript(self.INIT_SCRIPT)
        conn.commit()
        return conn, cur

    # Заполняет таблицы начальными данными (константы и настройки)
    def init_data(self):
        if self.is_empty(table=self.CONSTANTS):
            self.cur.execute("INSERT INTO constants VALUES (0);")
        if self.is_empty(table=self.CONFIG):
            self.cur.execute("INSERT INTO config VALUES (10, 4, 20, 1);")
        self.conn.commit()

    # Добавляет новое слово в БД или заменяет переводы существующего
    def add_word(self, word_eng, words_rus, is_replace=False):
        word_eng = word_eng.lower()
        words = self.get_words(word_filter=self.WORDS_ONLY)

        if word_eng in words and not is_replace:
            return False
        
        if word_eng in words and is_replace:
            self.cur.execute("SELECT word_id FROM words_eng WHERE word_eng = ?", (word_eng,))
            word_id = self.cur.fetchone()[0]
            self.cur.execute("DELETE FROM words_rus WHERE word_id = ?", (word_id,))

        if word_eng not in words:
            self.cur.execute("INSERT INTO words_eng(word_eng) VALUES (?)", (word_eng,))

        self.cur.execute("""
            INSERT OR IGNORE INTO statistics (word_id)
            SELECT word_id FROM words_eng WHERE word_eng = ?
        """, (word_eng,))

        self.cur.executemany("""
            INSERT OR IGNORE INTO words_rus(word_id, word_rus) VALUES
            ((SELECT word_id FROM words_eng WHERE word_eng = ?), ?)
        """, [(word_eng, word) for word in words_rus])
        
        self.conn.commit()
        return True

    # Удаляет слово из БД по его ID
    def delete_word(self, word_id):
        self.cur.execute("DELETE FROM words_eng WHERE word_id = ?", (word_id,))
        self.conn.commit()

    # Возвращает настройки приложения из таблицы config
    def get_config(self):
        self.cur.execute("SELECT * FROM config")
        session_words, card_words, word_learned_limit, delay = self.cur.fetchone()
        return session_words, card_words, word_learned_limit, delay

    # Возвращает статистику: кол-во слов, сессий, успехов и т.д.
    def get_stats(self, learned_words_limit):
        self.cur.execute("SELECT COUNT(*) FROM words_eng;")
        words_count = self.cur.fetchone()[0]

        self.cur.execute("SELECT sessions_count FROM constants")
        sessions_count = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM statistics WHERE count_of_learned > 0")
        opened_words = self.cur.fetchone()[0]

        limit = learned_words_limit["value"]
        self.cur.execute("SELECT COUNT(*) FROM statistics WHERE count_of_learned > ?", (limit,))
        full_learned_words = self.cur.fetchone()[0]

        self.cur.execute("SELECT SUM(successful_attempts), SUM(unsuccessful_attempts) FROM statistics")
        successful_attempts, unsuccessful_attempts = self.cur.fetchone()
        if successful_attempts is None:
            successful_attempts = 0
        if unsuccessful_attempts is None:
            unsuccessful_attempts = 0

        try:
            success_ratio = round(successful_attempts / unsuccessful_attempts, 2)
        except ZeroDivisionError:
            success_ratio = successful_attempts
        
        return words_count, sessions_count, opened_words, full_learned_words, successful_attempts, unsuccessful_attempts, success_ratio

    # Возвращает список слов. word_filter: words_only, learned_only, unlearned_only, translations_only
    def get_words(self, word_filter=None):
        _, _, word_learned_limit, _ = self.get_config()

        if word_filter == self.LEARNED_ONLY:
            query = """
SELECT word_id, word_eng
FROM words_eng
JOIN statistics USING(word_id)
WHERE count_of_learned > ?
ORDER BY word_eng
"""
            params = (word_learned_limit,)
            
        elif word_filter == self.UNLEARNED_ONLY:
            query = """
SELECT word_id, word_eng
FROM words_eng
JOIN statistics USING(word_id)
WHERE count_of_learned < ?
ORDER BY word_eng
"""
            params = (word_learned_limit,)
        else:
            query = "SELECT word_id, word_eng FROM words_eng ORDER BY word_eng"
            params = ()
        
        self.cur.execute(query, params)
        result = self.cur.fetchall()

        if word_filter == self.WORDS_ONLY:
            result = [word[1] for word in result]
            return result

        words = []
        for row in result:
            word_id, word_eng = row
            self.cur.execute("SELECT word_rus FROM words_rus WHERE word_id = ? ORDER BY word_rus", (word_id,))
            words_rus = [word[0] for word in self.cur.fetchall()]
            words.append((word_id, word_eng, words_rus))

        if word_filter == self.TRANSLATIONS_ONLY:
            translations = []
            for t in words:
                translations.extend(t[2])
            
            return translations

        return words

    # Обновляет настройки в таблице config
    def update_config(self, config):
        self.cur.execute("DELETE FROM config")
        self.cur.execute("INSERT INTO config VALUES (?, ?, ?, ?)", config)
        self.conn.commit()

    # Обновляет константы (например, счётчик сессий)
    def update_consts(self, const):
        if const == "sessions_count":
            self.cur.execute("UPDATE constants SET sessions_count = sessions_count + 1")
            self.conn.commit()

    # Обновляет статистику для слова: увеличивает счётчик правильных/неправильных ответов
    def update_statistics(self, word_id, success):
        self.cur.execute("""
UPDATE statistics 
SET count_of_learned = count_of_learned + 1
WHERE word_id = ?
""", (word_id,))

        if success:
            self.cur.execute("""
UPDATE statistics 
SET successful_attempts = successful_attempts + 1
WHERE word_id = ?
""", (word_id,))
        else:
            self.cur.execute("""
UPDATE statistics 
SET unsuccessful_attempts = unsuccessful_attempts + 1
WHERE word_id = ?
""", (word_id,))
        self.conn.commit()

    # Сбрасывает всю статистику изучения
    def reset_stats(self):
        self.cur.executescript("""
DELETE FROM statistics;
INSERT INTO statistics (word_id)
SELECT word_id FROM words_eng;
UPDATE constants SET sessions_count = 0;
""")
        self.conn.commit()

    # Полностью очищает БД и восстанавливает начальные данные
    def reset_db(self):
        self.cur.executescript("""
DELETE FROM constants;
DELETE FROM config;
DELETE FROM statistics;
DELETE FROM words_rus;
DELETE FROM words_eng;
""")
        self.conn.commit()
        self.init_data()

    # Проверяет, пуста ли указанная таблица
    def is_empty(self, table):
        self.cur.execute(f"SELECT COUNT(*) FROM {table}")
        return self.cur.fetchone()[0] == 0

    # Генерирует список слов для текущей сессии изучения
    def generate_current_words(self):
        session_words, _, word_learned_limit, _ = self.get_config()
        self.cur.execute("""
SELECT word_id, word_eng
FROM words_eng
JOIN statistics USING(word_id)
WHERE count_of_learned < ?
ORDER BY RANDOM()
LIMIT ?
""", (word_learned_limit, session_words,))

        result = self.cur.fetchall()

        if len(result) < session_words:
            return None

        words = []
        for word_id, word_eng in result:
            self.cur.execute("SELECT word_rus FROM words_rus WHERE word_id = ? ORDER BY word_rus", (word_id,))
            words_rus = [word[0] for word in self.cur.fetchall()]
            words.append([word_id, word_eng, words_rus])

        return words


# Главный класс приложения, управляющий интерфейсом и логикой
class VocabularyApp(Constants):

    # Конструктор: создаёт объект БД, настраивает окно и стили, показывает главное меню
    def __init__(self):
        self.db = Database(file_name=self.DB_NAME)
        self.setup_config()
        self.setup_window()
        self.setup_styles()
        self.show_main_menu()
        self.show_welcome_message()

    # Запускает главный цикл приложения
    def run(self):
        self.window.mainloop()

    # Закрывает приложение после подтверждения пользователя
    def finish(self):
        if messagebox.askyesno(message=self.EXIT_YESNO):
            self.db.conn.close()
            self.window.destroy()

    # Загружает настройки из БД и инициализирует переменные приложения
    def setup_config(self):
        session_words, card_words, word_learned_limit, delay = self.db.get_config()
        self.session_words = {"min": self.SESSION_WORDS_MIN, "max": self.SESSION_WORDS_MAX, "value": session_words}
        self.card_words = {"min": self.CARD_WORDS_MIN, "max": self.CARD_WORDS_MAX, "value": card_words}
        self.word_learned_limit = {"min": self.WORD_LEARNED_LIMIT_MIN, "max": self.WORD_LEARNED_LIMIT_MAX, "value": word_learned_limit}
        self.delay =  {"min": self.DELAY_MIN, "max": self.DELAY_MAX, "value": delay}
        return session_words, card_words, word_learned_limit, delay

    # Настраивает главное окно: размер, заголовок, иконку, поведение при закрытии
    def setup_window(self):
        self.window = Tk()
        self.window.title("FURRY WORDS")
        self.window.protocol("WM_DELETE_WINDOW", self.finish)
        file = self.ICON_NAME
        if os.path.exists(file):
            icon = PhotoImage(file=file)
            self.window.iconphoto(True, icon)
        if os.name == "nt": self.window.state("zoomed")
        else:
            width = self.window.winfo_screenwidth()
            height = self.window.winfo_screenheight()
            self.window.geometry(f"{width}x{height}+0+0")
            
            try: self.window.state("zoomed")
            except: pass

    # Настраивает стили виджетов в зависимости от разрешения экрана
    def setup_styles(self):
        screen_width = self.window.winfo_screenwidth()
    
        if screen_width < 1366:
            title_size = 24
            word_size = 22
            text_size = 18
            button_size = 16
        elif screen_width < 1920:
            title_size = 28
            word_size = 26
            text_size = 20
            button_size = 18
        else:
            title_size = 32
            word_size = 30
            text_size = 22
            button_size = 20

        ttk.Style().theme_use("alt")
        ttk.Style().configure(self.CORRECT_BTN_STYLE, foreground="white", background="green")
        ttk.Style().configure(self.WRONG_BTN_STYLE, foreground="white", background="red")

        ttk.Style().map(self.CORRECT_BTN_STYLE, background=[("active", "green")])
        ttk.Style().map(self.WRONG_BTN_STYLE, background=[("active", "red")])

        ttk.Style().configure(self.TITLE_STYLE, font=("Courier New", title_size))
        ttk.Style().configure(self.WORD_STYLE, font=("Arial", word_size))
        ttk.Style().configure("TLabel", font=("Arial", text_size))
        ttk.Style().configure("TRadiobutton", font=("Arial", button_size))
        ttk.Style().configure("TCheckbutton", font=("Arial", button_size))
        ttk.Style().configure("TButton", font=("Arial", button_size))

    def show_welcome_message(self):
        if len(self.db.get_words()) == 0 and os.path.exists(self.DEFAULT_FILE_NAME):
            if messagebox.askyesno(message=self.WELCOME % self.DEFAULT_FILE_NAME):
                self.show_import_export_menu(auto_import=True)
                self.show_main_menu()

    # Отображает главное меню с кнопками: Изучение слов, Статистика, Настройки, Выход
    def show_main_menu(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        menu_frame = ttk.Frame()
        menu_frame.pack(expand=True, fill=BOTH)

        title_frame = ttk.Frame(menu_frame)
        title_frame.pack(expand=True, fill=BOTH)

        buttons_frame = ttk.Frame(menu_frame)
        buttons_frame.pack(expand=True, fill=BOTH)

        ttk.Label(title_frame, text=self.MENU_TITLE, style=self.TITLE_STYLE, justify=CENTER).pack()
        ttk.Button(buttons_frame, text="ИЗУЧЕНИЕ СЛОВ", width=self.MENU_BUTTON_WIDTH, padding=[0, 10], command=self.show_session_menu).pack(anchor=CENTER, pady=20)
        ttk.Button(buttons_frame, text="СТАТИСТИКА", width=self.MENU_BUTTON_WIDTH, padding=[0, 10], command=self.show_stats).pack(anchor=CENTER, pady=20)
        ttk.Button(buttons_frame, text="НАСТРОЙКИ", width=self.MENU_BUTTON_WIDTH, padding=[0, 10], command=self.show_settings).pack(anchor=CENTER, pady=20)
        ttk.Button(buttons_frame, text="ВЫХОД", width=self.MENU_BUTTON_WIDTH, padding=[0, 10], command=self.finish).pack(anchor=CENTER, pady=20)

    # Отображает меню сессии изучения слов
    def show_session_menu(self):
        if self.db.is_empty(table=self.WORDS_ENG) or len(self.db.get_words()) < self.session_words["min"]:
            self.show_empty_db_message()
            return

        for widget in self.window.winfo_children():
            widget.destroy()
        
        session_frame = ttk.Frame()
        session_frame.pack(expand=True, fill=BOTH)

        title_frame = ttk.Frame(session_frame)
        title_frame.pack(expand=True, fill=BOTH)

        self.center_frame = ttk.Frame(session_frame)
        self.center_frame.pack(expand=True)

        self.word_frame = ttk.Frame(self.center_frame, relief=SOLID, borderwidth=1)
        self.word_frame.pack(expand=True, fill=BOTH, pady=10)

        self.buttons_frame = ttk.Frame(self.center_frame)
        self.buttons_frame.pack(expand=True, fill=BOTH, pady=10)

        self.progress_frame = ttk.Frame(self.center_frame)
        self.progress_frame.pack(expand=True, fill=BOTH, pady=10)

        ttk.Label(title_frame, text=self.SESSION_TITLE, style=self.TITLE_STYLE, justify=CENTER).pack()
        ttk.Button(session_frame, text="В главное меню", width=self.SESSION_BUTTON_WIDTH, command=self.show_main_menu).pack(pady=20)
        
        self.start_session()

    # Отображает окно статистики
    def show_stats(self):
        def reset_stats():
            if messagebox.askyesno(message=self.STATS_RESET_YESNO):
                self.db.reset_stats()
                self.show_stats()

        for widget in self.window.winfo_children():
            widget.destroy()
        
        words_count, sessions_count, opened_words, full_learned_words, successful_attempts, unsuccessful_attempts, succes_ratio = self.db.get_stats(learned_words_limit=self.word_learned_limit)

        try:
            opened_words_percent = round(opened_words / words_count * 100, 2)
        except ZeroDivisionError:
            opened_words_percent = 0

        try:
            full_learned_words_percent = round(full_learned_words / words_count * 100, 2)
        except ZeroDivisionError:
            full_learned_words_percent = 0

        stats_frame = ttk.Frame()
        stats_frame.pack(expand=True, fill=BOTH)

        title_frame = ttk.Frame(stats_frame)
        title_frame.pack(expand=True, fill=BOTH)

        center_frame = ttk.Frame(stats_frame)
        center_frame.pack(expand=True)

        buttons_frame = ttk.Frame(stats_frame)
        buttons_frame.pack(expand=True)

        ttk.Label(title_frame, text=self.STATS_TITLE, style=self.TITLE_STYLE, justify=CENTER).pack()
        ttk.Label(center_frame, padding=[5, 0], text=f"""
Всего слов в БД:

Сессий завершено:

Открыто слов:

Полностью изучено:

Правильных:

Коэффициент успеха:
""".strip()).pack(side=LEFT)
        ttk.Label(center_frame, justify=RIGHT, text=f"""
{words_count}

{sessions_count}

{opened_words} ({opened_words_percent}%)

{full_learned_words} ({full_learned_words_percent}%)

✓ {successful_attempts}  ✕ {unsuccessful_attempts}

{succes_ratio}
""".strip()).pack(side=LEFT)

        ttk.Button(buttons_frame, text="Сбросить статистику", width=self.STATS_BUTTON_WIDTH, command=reset_stats).pack(pady=5)
        ttk.Button(buttons_frame, text="В главное меню", width=self.STATS_BUTTON_WIDTH, command=self.show_main_menu).pack(pady=5)

    # Отображает окно настроек: слайдеры для изменения параметров
    def show_settings(self):
        def save_config():
            session_words = session_words_var.get()
            card_words = card_words_var.get()
            word_learned_limit = word_learned_limit_var.get()
            delay = delay_var.get()

            self.session_words["value"] = session_words
            self.card_words["value"] = card_words
            self.word_learned_limit["value"] = word_learned_limit
            self.delay["value"] = delay

            config = (session_words, card_words, word_learned_limit, delay)
            self.db.update_config(config=config)

            messagebox.showinfo(message=self.CONFIG_SAVED)

        def create_slider_frame(master, label_text, from_, to, variable):
            frame = ttk.Frame(master)
            frame.pack(expand=True, fill=BOTH, pady=10)
            ttk.Label(frame, text=label_text).pack(anchor=W)
            Scale(frame, from_=from_, to=to, variable=variable, orient=HORIZONTAL).pack(fill=X, pady=5)

        for widget in self.window.winfo_children():
            widget.destroy()

        session_words_var = IntVar(value=self.session_words["value"])
        card_words_var = IntVar(value=self.card_words["value"])
        word_learned_limit_var = IntVar(value=self.word_learned_limit["value"])
        delay_var = IntVar(value=self.delay["value"])

        settings_frame = ttk.Frame()
        settings_frame.pack(expand=True, fill=BOTH)

        title_frame = ttk.Frame(settings_frame)
        title_frame.pack(expand=True, fill=BOTH)

        center_frame = ttk.Frame(settings_frame, relief=SOLID, borderwidth=1)
        center_frame.pack(expand=True)

        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(expand=True, pady=20)

        params = [
            ("Количество слов в игре:", self.session_words["min"], self.session_words["max"], session_words_var),
            ("Вариантов перевода:", self.card_words["min"], self.card_words["max"], card_words_var),
            ("Предел изучения слова \n(слова с пределом выше \nсчитаются изученными):", self.word_learned_limit["min"], self.word_learned_limit["max"], word_learned_limit_var),
            ("Задержка между словами (сек):", self.delay["min"], self.delay["max"], delay_var)
        ]
        for param in params:
            label_text, from_, to, variable = param
            create_slider_frame(center_frame, label_text, from_, to, variable)

        ttk.Label(title_frame, text=self.SETTINGS_TITLE, style=self.TITLE_STYLE, justify=CENTER).pack()
        ttk.Button(buttons_frame, text="Сохранить изменения", width=self.SETTINGS_BUTTON_WIDTH, command=save_config).pack(pady=5)
        ttk.Button(buttons_frame, text="Редактор базы данных", width=self.SETTINGS_BUTTON_WIDTH, command=self.show_database_editor).pack(pady=5)
        ttk.Button(buttons_frame, text="В главное меню", width=self.SETTINGS_BUTTON_WIDTH, command=self.show_main_menu).pack(pady=5)

    # Отображает редактор БД: добавление/удаление слов, поиск
    def show_database_editor(self):
        def add_word():
            try:
                word_eng = word_eng_entry.get().strip()
                words_rus = words_rus_entry.get().strip()

                if not word_eng or not words_rus:
                    raise ValueError

                words_rus = [word.strip() for word in words_rus.split(',')]

                result = self.db.add_word(word_eng=word_eng, words_rus=words_rus)
                if result:
                    self.show_database_editor()
                    messagebox.showinfo(message=self.WORD_ADDED)
                else:
                    raise ValueError
            except (ValueError, TypeError):
                messagebox.showerror(message=self.WORD_EXISTS)

        def delete_word():
            if not listbox.curselection():
                return
            if words_var.get():
                if words_var.get()[0] == "None":
                    return
            selection_ids = listbox.curselection()
            word_ids = [words_list[selection_id][0] for selection_id in selection_ids]

            if messagebox.askyesno(message=self.WORD_DELETE_YESNO):
                for word_id in word_ids:
                    self.db.delete_word(word_id=word_id)
                
                self.show_database_editor()

        def filter_listbox(event):
            search_text = search_entry.get().lower()
            filtered = [word for word in formatted_words_list if search_text in word.lower()]
            words_var.set(filtered if filtered else "None")

        def reset_db():
            if messagebox.askyesno(message=self.DB_RESET_YESNO):
                if messagebox.askyesno(icon="warning", message=self.DB_RESET_CONFIRM_YESNO):
                    self.db.reset_db()
                    self.show_database_editor()

        for widget in self.window.winfo_children():
            widget.destroy()
        
        words_list = self.db.get_words()
        formatted_words_list = []

        for word_id, word_eng, words_rus in words_list:
            formatted_words_list.append(f"{word_eng} ({', '.join(words_rus)})")
        
        words_var = Variable(value=None if self.db.is_empty(table=self.WORDS_ENG) else formatted_words_list)

        db_editor_frame = ttk.Frame()
        db_editor_frame.pack(expand=True, fill=BOTH)

        title_frame = ttk.Frame(db_editor_frame)
        title_frame.pack(expand=True, fill=BOTH)

        add_word_frame = ttk.Frame(db_editor_frame, relief=SOLID, borderwidth=1)
        add_word_frame.pack(expand=True)

        delete_word_frame = ttk.Frame(db_editor_frame, relief=SOLID, borderwidth=1)
        delete_word_frame.pack(expand=True)

        search_frame = ttk.Frame(delete_word_frame)
        search_frame.pack(fill=X, padx=5, pady=5)

        list_container = ttk.Frame(delete_word_frame)
        list_container.pack(expand=True, fill=BOTH, padx=5)

        buttons_frame = ttk.Frame(db_editor_frame)
        buttons_frame.pack(expand=True)

        ttk.Label(title_frame, text=self.DB_EDITOR_TITLE, style=self.TITLE_STYLE, justify=CENTER).pack()
        ttk.Label(add_word_frame, text="Слово:").grid(column=0, row=1, sticky=W)
        ttk.Label(add_word_frame, text="Переводы:").grid(column=0, row=2, sticky=W)
        word_eng_entry = ttk.Entry(add_word_frame, width=40)
        word_eng_entry.grid(column=1, row=1)
        words_rus_entry = ttk.Entry(add_word_frame, width=40)
        words_rus_entry.grid(column=1, row=2)
        ttk.Label(add_word_frame, text="(через запятую)").grid(column=1, row=3)
        ttk.Button(add_word_frame, text="Добавить", command=add_word).grid(column=0, row=4, columnspan=2, pady=10, padx=10, sticky=NSEW)

        ttk.Label(search_frame, text="Поиск:").pack(side=LEFT)
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=LEFT, expand=True, fill=X, padx=5)
        search_entry.bind("<KeyRelease>", filter_listbox)
        listbox = Listbox(list_container, listvariable=words_var, width=70, height=15, activestyle=DOTBOX, selectmode=EXTENDED)
        listbox.pack(fill=BOTH, side=LEFT)
        scrollbar = ttk.Scrollbar(list_container, orient=VERTICAL, command=listbox.yview)
        scrollbar.pack(fill=Y, side=LEFT)
        listbox["yscrollcommand"] = scrollbar.set
        ttk.Button(delete_word_frame, text="Удалить", width=self.DB_EDITOR_BUTTON_WIDTH, command=delete_word).pack(fill=X, pady=10, padx=10)

        ttk.Button(buttons_frame, text="Импорт / экспорт", width=self.DB_EDITOR_BUTTON_WIDTH, command=self.show_import_export_menu).pack(pady=5)
        ttk.Button(buttons_frame, text="Очистить БД", width=self.DB_EDITOR_BUTTON_WIDTH, command=reset_db).pack(pady=5)
        ttk.Button(buttons_frame, text="В настройки", width=self.DB_EDITOR_BUTTON_WIDTH, command=self.show_settings).pack(pady=5)

    # Отображает меню импорта/экспорта данных
    def show_import_export_menu(self, auto_import=False):
        if auto_import:
            self.window.after(100, lambda: import_data(file_name=self.DEFAULT_FILE_NAME, separator=",", is_replace=False, is_check_len=False))

        def import_data(file_name=None, separator=None, is_replace=None, is_check_len=None):
            file_name = file_var.get()
            separator = separator_var.get()
            is_replace = replace_var.get()
            is_check_len = check_len_var.get()
            
            if not os.path.exists(file_name):
                messagebox.showerror(message=self.NO_FILE_EXISTS)
                return

            import_window = Toplevel(self.window)
            import_window.title("Импорт")
            import_window.geometry("400x150")
            import_window.resizable(False, False)
            import_window.transient(self.window)
            import_window.grab_set()
            import_window.focus_force()

            import_window.protocol("WM_DELETE_WINDOW", lambda: None)

            progress_var = StringVar(value="Подготовка к импорту...")
            ttk.Label(import_window, textvariable=progress_var).pack(pady=20)
            
            progress_bar = ttk.Progressbar(import_window, length=350, mode="determinate")
            progress_bar.pack(pady=20)

            import_window.update()

            with open(file_name, "r", encoding="utf-8") as file:
                rows = file.readlines()
                rows = [row.strip().split(separator) for row in rows if row.strip()]
                words_count = len(rows)
            
            if words_count < 1:
                messagebox.showwarning(message=self.EMPTY_FILE)
                import_window.destroy()
                return
            
            added_count = 0
            replaced_count = 0
            error_count = 0

            for i, row in enumerate(rows, 1):
                progress_var.set(f"Импорт: {i}/{words_count} слов")
                progress_bar["value"] = (i / words_count) * 100
                import_window.update()
                import_window.update_idletasks()
                
                if len(row) < 2:
                    error_count += 1
                    continue
                
                word_eng = row[0].strip()
                words_rus = [word.strip() for word in row[1:] if word.strip()]
                
                if not word_eng or not words_rus:
                    error_count += 1
                    continue

                if is_check_len:
                    if len(word_eng) < 3:
                        error_count += 1
                        continue
                
                added = self.db.add_word(word_eng=word_eng, words_rus=words_rus, is_replace=is_replace)
                if added and not is_replace:
                    added_count += 1
                elif added and is_replace:
                    replaced_count += 1
                else:
                    error_count += 1

            import_window.destroy()
            
            messagebox.showinfo(
                message=f"Добавлено: {added_count}\n"
                        f"Заменено: {replaced_count}\n"
                        f"Пропущено: {error_count}\n"
                        f"Всего: {words_count}"
            )
        
        def export_data():
            file_name = file_var.get()
            separator = separator_var.get()
            word_filter = filter_var.get()
            is_timestamp = timestamp_var.get()
            data = self.db.get_words(word_filter=word_filter)

            if not data:
                messagebox.showwarning(message=self.NO_EXPORT_DATA)
                return
    
            data = [f"{separator}".join([word_eng] + words_rus) + "\n" for _, word_eng, words_rus in data]
            
            if is_timestamp:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                name, ext = os.path.splitext(file_name)
                file_name = f"{timestamp}_{name}{ext}"

            if os.path.exists(file_name):
                if not messagebox.askyesno(message=self.FILE_EXISTS % file_name):
                    return

            with open(file_name, "w", encoding="utf-8") as file:
                file.writelines(data)

            messagebox.showinfo(message=self.EXPORTED % len(data))

        for widget in self.window.winfo_children():
            widget.destroy()

        import_export_frame = ttk.Frame()
        import_export_frame.pack(expand=True, fill=BOTH)

        title_frame = ttk.Frame(import_export_frame)
        title_frame.pack(expand=True)

        center_frame = ttk.Frame(import_export_frame)
        center_frame.pack(expand=True, fill=Y)

        file_frame = ttk.Frame(center_frame, relief=SOLID, borderwidth=1, padding=[5, 5])
        file_frame.pack(expand=True, fill=X, padx=5, pady=10)

        separator_frame = ttk.Frame(center_frame, relief=SOLID, borderwidth=1)
        separator_frame.pack(expand=True, fill=BOTH, padx=5, pady=10)

        separator_inner_frame = ttk.Frame(separator_frame)
        separator_inner_frame.pack(expand=True)

        import_frame = ttk.Frame(center_frame, relief=SOLID, borderwidth=1)
        import_frame.pack(expand=True, fill=BOTH, side=LEFT, padx=5, pady=10)

        export_frame = ttk.Frame(center_frame, relief=SOLID, borderwidth=1)
        export_frame.pack(expand=True, fill=BOTH, side=RIGHT, padx=5, pady=10)

        buttons_frame = ttk.Frame(import_export_frame)
        buttons_frame.pack(expand=True)

        file_var = StringVar()
        separator_var = StringVar(value=",")
        filter_var = StringVar(value="all")
        timestamp_var = BooleanVar(value=False)
        replace_var = BooleanVar(value=False)
        check_len_var = BooleanVar(value=False)
        
        ttk.Label(title_frame, text=self.IMPORT_TITLE, style=self.TITLE_STYLE, justify=CENTER).pack()
        ttk.Label(file_frame, text="Название файла:").pack(anchor=N)
        entry = ttk.Entry(file_frame, textvariable=file_var, width=40)
        entry.pack(anchor=N)
        entry.insert(0, self.DEFAULT_FILE_NAME)

        ttk.Label(separator_inner_frame, text="Разделитель:").pack(anchor=W)
        default_sep_radio = ttk.Radiobutton(separator_inner_frame, text="Запятая", variable=separator_var, value=",")
        default_sep_radio.pack(anchor=W)
        default_sep_radio.configure(state=ACTIVE)
        ttk.Radiobutton(separator_inner_frame, text="Точка с запятой", variable=separator_var, value=";").pack(anchor=W)
        ttk.Radiobutton(separator_inner_frame, text="Табуляция", variable=separator_var, value="    ").pack(anchor=W)

        ttk.Label(import_frame, text="Настройки импорта:").pack(anchor=W)
        ttk.Checkbutton(import_frame, text="Заменять существующие слова", variable=replace_var).pack(anchor=W)
        ttk.Checkbutton(import_frame, text="Проверять минимальную длину (3 буквы)", variable=check_len_var).pack(anchor=W)
        ttk.Label(import_frame, text="(файл должен находиться в папке программы)").pack(anchor=W)
        ttk.Label(import_frame, text="(слово,перевод1,перевод2... (например: cat,кот,кошка)").pack(anchor=W)
        ttk.Button(import_frame, text="Импорт из файла", width=20, command=import_data).pack(side=BOTTOM, pady=5)

        ttk.Label(export_frame, text="Настройки экспорта:").pack(anchor=W)
        ttk.Radiobutton(export_frame, text="Только изученные слова", variable=filter_var, value=self.LEARNED_ONLY).pack(anchor=W)
        ttk.Radiobutton(export_frame, text="Только неизученные слова", variable=filter_var, value=self.UNLEARNED_ONLY).pack(anchor=W)
        default_filter_radio = ttk.Radiobutton(export_frame, text="Все слова", variable=filter_var, value="all")
        default_filter_radio.pack(anchor=W)
        default_filter_radio.configure(state=ACTIVE)
        ttk.Checkbutton(export_frame, text="Добавлять временную метку в название файла", variable=timestamp_var).pack(anchor=W)
        ttk.Button(export_frame, text="Экспорт в файл", width=20, command=export_data).pack(side=BOTTOM, pady=5)

        ttk.Button(buttons_frame, text="В редактор базы данных", width=self.IMPORT_EXPORT_BUTTON_WIDTH, command=self.show_database_editor).pack(anchor=CENTER, pady=5)

    # Показывает предупреждение о том, что БД пуста
    def show_empty_db_message(self):
        messagebox.showwarning(message=self.EMPTY_DB)

    # Отображает результаты завершённой сессии: кол-во правильных ответов, процент
    def show_session_results(self):
        for widget in self.window.winfo_children():
            widget.destroy()
        
        self.db.update_consts(const=self.SESSION_COUNT_CONST)

        percent = round(self.correct_answers / self.total_words * 100, 2)

        session_frame = ttk.Frame()
        session_frame.pack(expand=True, fill=BOTH)

        title_frame = ttk.Frame(session_frame)
        title_frame.pack(expand=True, fill=BOTH)

        results_frame = ttk.Frame(session_frame)
        results_frame.pack(expand=True)

        buttons_frame = ttk.Frame(session_frame)
        buttons_frame.pack(expand=True)

        ttk.Label(title_frame, text=self.RESULTS_TITLE, style=self.TITLE_STYLE, justify=CENTER).pack()
        ttk.Label(results_frame, text="РЕЗУЛЬТАТЫ СЕССИИ").pack(pady=20)
        ttk.Label(results_frame, text=f"Правильных ответов: {self.correct_answers} из {self.total_words}").pack(pady=10)
        ttk.Label(results_frame, text=f"Процент правильных: {percent}%").pack(pady=10)
        ttk.Button(buttons_frame, text="Новая сессия", width=self.SESSION_RESULTS_BUTTON_WIDTH, command=self.show_session_menu).pack(pady=10)
        ttk.Button(buttons_frame, text="В главное меню", width=self.SESSION_RESULTS_BUTTON_WIDTH, command=self.show_main_menu).pack(pady=10)

    # Инициализирует новую сессию: обнуляет счётчики, загружает слова
    def start_session(self):
        self.correct_answers = 0
        self.wrong_answers = 0
        self.current_words = self.db.generate_current_words()

        if not self.current_words:
            self.show_main_menu()
            messagebox.showwarning(message=self.NO_UNLEARNED)
            return

        self.total_words = len(self.current_words)
        self.current_word = self.get_next_word()
        self.update_session_menu()

    # Обновляет интерфейс во время сессии: прогресс, слово, варианты ответов
    def update_session_menu(self):
        if not self.current_word or self.is_session_over():
            self.show_session_results()
            return

        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        current_count = self.total_words - len(self.current_words)

        progress_text = f"Прогресс: {current_count}/{self.total_words} \nПравильных: ✓ {self.correct_answers}    ✕ {self.wrong_answers}"
        ttk.Label(self.progress_frame, text=progress_text).pack()

        for widget in self.word_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.word_frame, text=self.current_word["word"], style=self.WORD_STYLE, padding=[10, 10]).pack(anchor=CENTER)

        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        for option in self.current_word["options"]:
            btn = ttk.Button(self.buttons_frame, text=option, width=self.TRANSLATION_BUTTON_WIDTH, command=lambda opt=option: self.on_answer(opt))
            btn.pack(pady=5)

            self.buttons.append(btn)

    # Формирует следующее слово для изучения с вариантами ответов
    def get_next_word(self):
        if not self.current_words:
            self.current_word = None
            return None
        
        self.current_word = self.current_words.pop()
        word_id, word_eng, correct_translations = self.current_word
        
        all_translations = self.db.get_words(word_filter=self.TRANSLATIONS_ONLY)
        all_translations = list(set(all_translations))
        incorrect_translations = [t for t in all_translations if t not in correct_translations]
        correct_answer = random.choice(correct_translations)
        needed = self.card_words["value"] - 1
        
        incorrect_answers = []
        for _ in range(needed):
            incorrect_answers.append(random.choice(incorrect_translations))
        
        options = incorrect_answers + [correct_answer]
        random.shuffle(options)
        
        self.current_word = {
            "word_id": word_id,
            "word": word_eng,
            "correct_answer": correct_answer,
            "options": options
        }
        
        return self.current_word

    # Обрабатывает ответ пользователя: проверяет, красит кнопки, запускает задержку
    def on_answer(self, user_answer):
        is_correct, _ = self.check_answer(user_answer)

        for btn in self.buttons:
            btn.config(state=DISABLED)

        for btn in self.buttons:
            if btn["text"] == self.current_word["correct_answer"]:
                btn.configure(style=self.CORRECT_BTN_STYLE)
        
        if not is_correct:
            for btn in self.buttons:
                if btn["text"] == user_answer:
                    btn.configure(style=self.WRONG_BTN_STYLE)

        self.window.update()
        self.window.update_idletasks()
        delay = self.delay["value"] * 1000
        self.window.after(delay, self.load_next_word)

    # Проверяет правильность ответа и обновляет статистику
    def check_answer(self, user_answer):
        is_correct = (user_answer == self.current_word["correct_answer"])
        
        if is_correct:
            self.db.update_statistics(self.current_word["word_id"], True)
            self.correct_answers += 1
        else:
            self.db.update_statistics(self.current_word["word_id"], False)
            self.wrong_answers += 1

        return is_correct, self.current_word["correct_answer"]

    # Загружает следующее слово после задержки
    def load_next_word(self):
        self.current_word = self.get_next_word()
        self.update_session_menu()

    # Проверяет, закончилась ли сессия
    def is_session_over(self):
        return self.current_word is None and len(self.current_words) == 0


# Точка входа: создание и запуск приложения
if __name__ == "__main__":
    VocabularyApp().run()
