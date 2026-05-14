# =============================================================================
# app.py — Главное окно приложения «Контактная книга» (Tkinter UI)
# =============================================================================

# Импортируем tkinter — стандартная библиотека Python для GUI
import tkinter as tk
from tkinter import ttk, messagebox

# Импортируем наши модули
from models import Contact, PersonalContact, BusinessContact
from manager import ContactManager
from storage import FileStorage

# Импортируем диалог добавления/редактирования контакта
from dialog import ContactDialog


# =============================================================================
# Константы цветовой схемы приложения
# =============================================================================
COLOR_BG = "#F0F4F8"          # Цвет фона главного окна
COLOR_SIDEBAR = "#2D3748"     # Цвет боковой панели (тёмно-синяя)
COLOR_ACCENT = "#4299E1"      # Акцентный цвет (синий)
COLOR_ACCENT_HOVER = "#3182CE" # Цвет кнопки при наведении
COLOR_WHITE = "#FFFFFF"        # Белый цвет
COLOR_TEXT = "#2D3748"         # Основной цвет текста
COLOR_MUTED = "#718096"        # Приглушённый цвет текста
COLOR_PERSONAL = "#48BB78"     # Зелёный для личных контактов
COLOR_BUSINESS = "#4299E1"     # Синий для рабочих контактов
COLOR_DANGER = "#FC8181"       # Красный для удаления


# =============================================================================
# Класс ContactApp — главное окно приложения
# =============================================================================
class ContactApp:
    """
    Главный класс приложения — управляет главным окном и компонентами UI.
    Связывает менеджер контактов с графическим интерфейсом.
    """

    def __init__(self, root: tk.Tk):
        """
        Инициализация главного окна приложения.
        :param root: корневой виджет Tkinter
        """
        # Сохраняем ссылку на корневое окно Tkinter
        self.root = root

        # Настраиваем заголовок главного окна
        self.root.title("📒 Контактная книга")

        # Устанавливаем размер и позицию окна по центру экрана
        self.root.geometry("900x600")
        self.root.minsize(700, 450)
        self.root.configure(bg=COLOR_BG)

        # Создаём хранилище и менеджер контактов
        storage = FileStorage("contacts.json")
        self.manager = ContactManager(storage)

        # Переменная для хранения ID выбранного контакта
        self.selected_contact_id: str = ""

        # Строим пользовательский интерфейс
        self._build_ui()

        # Загружаем и отображаем список контактов
        self._refresh_list()

    def _build_ui(self):
        """Создаёт все виджеты главного окна."""
        # ── Верхняя панель инструментов ──────────────────────────────────────
        toolbar = tk.Frame(self.root, bg=COLOR_SIDEBAR, height=55)
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)

        # Заголовок приложения в панели инструментов
        tk.Label(
            toolbar, text="📒  Контактная книга",
            bg=COLOR_SIDEBAR, fg=COLOR_WHITE,
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=20, pady=12)

        # Кнопка «Добавить контакт»
        self.btn_add = tk.Button(
            toolbar, text="＋  Добавить",
            bg=COLOR_ACCENT, fg=COLOR_WHITE,
            font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=14, pady=6,
            command=self._on_add
        )
        self.btn_add.pack(side="right", padx=16, pady=10)

        # ── Строка поиска ─────────────────────────────────────────────────────
        search_frame = tk.Frame(self.root, bg=COLOR_BG, pady=10)
        search_frame.pack(fill="x", padx=16)

        # Иконка поиска
        tk.Label(search_frame, text="🔍", bg=COLOR_BG, font=("Arial", 12)).pack(side="left")

        # Переменная для хранения текста поиска
        self.search_var = tk.StringVar()
        # Привязываем обновление списка при изменении текста в поле поиска
        self.search_var.trace("w", lambda *_: self._refresh_list())

        # Поле ввода для поиска контактов
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=("Arial", 11), relief="flat",
            bg=COLOR_WHITE, fg=COLOR_TEXT,
            insertbackground=COLOR_TEXT
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=8, ipady=6)

        # Метка для отображения количества контактов
        self.count_label = tk.Label(
            search_frame, text="", bg=COLOR_BG,
            fg=COLOR_MUTED, font=("Arial", 9)
        )
        self.count_label.pack(side="right", padx=4)

        # ── Основное содержимое: список + детали ─────────────────────────────
        content = tk.Frame(self.root, bg=COLOR_BG)
        content.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Левая панель: список контактов с прокруткой
        list_frame = tk.Frame(content, bg=COLOR_WHITE, relief="flat", bd=0)
        list_frame.pack(side="left", fill="both", expand=True)

        # Создаём виджет Treeview для отображения списка контактов
        cols = ("name", "type", "phone")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")

        # Настраиваем заголовки столбцов таблицы
        self.tree.heading("name", text="ФИО")
        self.tree.heading("type", text="Тип")
        self.tree.heading("phone", text="Телефон / Информация")

        # Задаём ширину столбцов
        self.tree.column("name", width=200, minwidth=150)
        self.tree.column("type", width=85, minwidth=70)
        self.tree.column("phone", width=200, minwidth=150)

        # Настраиваем цвета тегов для разных типов контактов
        self.tree.tag_configure("personal", foreground=COLOR_PERSONAL)
        self.tree.tag_configure("business", foreground=COLOR_BUSINESS)

        # Стиль для Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), rowheight=32, background=COLOR_WHITE)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])

        # Полоса прокрутки для списка контактов
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Размещаем таблицу и полосу прокрутки
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем обработчик выбора строки в таблице
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Правая панель: детали выбранного контакта
        self.detail_frame = tk.Frame(content, bg=COLOR_WHITE, width=240, relief="flat")
        self.detail_frame.pack(side="right", fill="y", padx=(12, 0))
        self.detail_frame.pack_propagate(False)

        # Показываем заглушку «выберите контакт»
        self._show_placeholder()

        # ── Нижняя панель статуса ─────────────────────────────────────────────
        status_bar = tk.Frame(self.root, bg=COLOR_SIDEBAR, height=24)
        status_bar.pack(fill="x", side="bottom")

        # Метка статуса в нижней панели
        self.status_label = tk.Label(
            status_bar, text="Готово",
            bg=COLOR_SIDEBAR, fg=COLOR_MUTED,
            font=("Arial", 8)
        )
        self.status_label.pack(side="left", padx=12)

    def _show_placeholder(self):
        """Отображает сообщение-заглушку в панели деталей."""
        # Очищаем панель деталей перед отображением заглушки
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # Отображаем иконку и подсказку для пользователя
        tk.Label(
            self.detail_frame, text="👤",
            bg=COLOR_WHITE, font=("Arial", 40)
        ).pack(pady=(60, 10))

        tk.Label(
            self.detail_frame,
            text="Выберите контакт\nиз списка",
            bg=COLOR_WHITE, fg=COLOR_MUTED,
            font=("Arial", 11), justify="center"
        ).pack()

    def _show_contact_detail(self, contact: Contact):
        """
        Отображает подробную информацию о выбранном контакте.
        :param contact: объект контакта для отображения
        """
        # Очищаем панель деталей перед отображением новых данных
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # Определяем цвет значка в зависимости от типа контакта
        icon_color = COLOR_PERSONAL if isinstance(contact, PersonalContact) else COLOR_BUSINESS
        icon_text = "👤" if isinstance(contact, PersonalContact) else "💼"

        # Верхняя часть с иконкой и полным именем
        header = tk.Frame(self.detail_frame, bg=COLOR_WHITE, pady=16)
        header.pack(fill="x")

        # Иконка и тип контакта
        tk.Label(header, text=icon_text, bg=COLOR_WHITE, font=("Arial", 32)).pack()
        tk.Label(
            header, text=contact.get_type_label(),
            bg=COLOR_WHITE, fg=icon_color,
            font=("Arial", 9, "bold")
        ).pack()
        tk.Label(
            header, text=contact.get_full_name(),
            bg=COLOR_WHITE, fg=COLOR_TEXT,
            font=("Arial", 13, "bold"), wraplength=200
        ).pack(pady=(4, 0))

        # Разделительная линия
        tk.Frame(self.detail_frame, bg="#E2E8F0", height=1).pack(fill="x", padx=16, pady=8)

        # Контейнер для полей информации
        info_frame = tk.Frame(self.detail_frame, bg=COLOR_WHITE, padx=16)
        info_frame.pack(fill="x")

        # Вспомогательная функция для добавления строки информации
        def add_info_row(label: str, value: str):
            if not value:
                return
            row = tk.Frame(info_frame, bg=COLOR_WHITE, pady=3)
            row.pack(fill="x")
            tk.Label(row, text=label, bg=COLOR_WHITE, fg=COLOR_MUTED,
                     font=("Arial", 8), anchor="w").pack(fill="x")
            tk.Label(row, text=value, bg=COLOR_WHITE, fg=COLOR_TEXT,
                     font=("Arial", 10), anchor="w", wraplength=190).pack(fill="x")

        # Отображаем общие поля контакта
        add_info_row("📱 Телефон", contact.phone)
        add_info_row("✉️  Email", contact.email)

        # Отображаем поля, специфичные для типа контакта
        if isinstance(contact, PersonalContact):
            add_info_row("🎂 День рождения", contact.birthday)
            add_info_row("🏠 Адрес", contact.address)
        elif isinstance(contact, BusinessContact):
            add_info_row("🏢 Компания", contact.company)
            add_info_row("👔 Должность", contact.position)

        # Дата создания контакта
        add_info_row("📅 Добавлен", contact.created_at)

        # Разделительная линия перед кнопками действий
        tk.Frame(self.detail_frame, bg="#E2E8F0", height=1).pack(fill="x", padx=16, pady=8)

        # Кнопки действий: редактировать и удалить
        btn_frame = tk.Frame(self.detail_frame, bg=COLOR_WHITE, padx=16)
        btn_frame.pack(fill="x")

        # Кнопка «Редактировать» контакт
        tk.Button(
            btn_frame, text="✏️  Редактировать",
            bg=COLOR_ACCENT, fg=COLOR_WHITE,
            font=("Arial", 9, "bold"),
            relief="flat", cursor="hand2", pady=6,
            command=lambda: self._on_edit(contact)
        ).pack(fill="x", pady=(0, 6))

        # Кнопка «Удалить» контакт
        tk.Button(
            btn_frame, text="🗑️  Удалить",
            bg=COLOR_DANGER, fg=COLOR_WHITE,
            font=("Arial", 9, "bold"),
            relief="flat", cursor="hand2", pady=6,
            command=lambda: self._on_delete(contact)
        ).pack(fill="x")

    def _refresh_list(self):
        """
        Обновляет список контактов в таблице.
        Применяет поисковый фильтр если он задан.
        """
        # Получаем текущий поисковый запрос из поля ввода
        query = self.search_var.get()

        # Получаем отфильтрованный список контактов от менеджера
        contacts = self.manager.search(query)

        # Очищаем таблицу перед заполнением новыми данными
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем таблицу данными контактов
        for contact in contacts:
            # Определяем тег для цветовой маркировки строки
            tag = "personal" if isinstance(contact, PersonalContact) else "business"

            # Добавляем строку в таблицу с данными контакта
            self.tree.insert(
                "", "end",
                iid=contact.id,
                values=(contact.get_full_name(), contact.get_type_label(), contact.get_display_info()),
                tags=(tag,)
            )

        # Обновляем счётчик контактов
        total = self.manager.get_count()
        shown = len(contacts)
        if query:
            self.count_label.config(text=f"Найдено: {shown} из {total}")
        else:
            self.count_label.config(text=f"Всего: {total}")

    def _on_select(self, event):
        """
        Обработчик выбора строки в таблице контактов.
        Отображает детали выбранного контакта.
        """
        # Получаем выбранные строки таблицы
        selection = self.tree.selection()
        if not selection:
            # Ничего не выбрано — показываем заглушку
            self._show_placeholder()
            return

        # Берём ID первого выбранного элемента
        contact_id = selection[0]
        self.selected_contact_id = contact_id

        # Находим контакт по ID через менеджер
        contact = self.manager.get_by_id(contact_id)
        if contact:
            # Отображаем детали выбранного контакта
            self._show_contact_detail(contact)

    def _on_add(self):
        """Обработчик кнопки «Добавить контакт»."""
        # Открываем диалог добавления нового контакта
        dialog = ContactDialog(self.root, title="Новый контакт")
        self.root.wait_window(dialog.top)

        # Если пользователь подтвердил создание контакта
        if dialog.result:
            # Добавляем новый контакт через менеджер
            self.manager.add(dialog.result)
            # Обновляем список контактов в таблице
            self._refresh_list()
            # Обновляем статусную строку
            self.status_label.config(text=f"Контакт «{dialog.result.get_full_name()}» добавлен")

    def _on_edit(self, contact: Contact):
        """
        Обработчик кнопки «Редактировать контакт».
        :param contact: объект контакта для редактирования
        """
        # Открываем диалог редактирования с передачей существующего контакта
        dialog = ContactDialog(self.root, title="Редактировать контакт", contact=contact)
        self.root.wait_window(dialog.top)

        # Если пользователь сохранил изменения
        if dialog.result:
            # Обновляем контакт через менеджер
            self.manager.update(contact.id, dialog.result)
            # Обновляем список контактов в таблице
            self._refresh_list()
            # Отображаем детали обновлённого контакта
            self._show_contact_detail(dialog.result)
            # Обновляем статусную строку
            self.status_label.config(text=f"Контакт «{dialog.result.get_full_name()}» обновлён")

    def _on_delete(self, contact: Contact):
        """
        Обработчик кнопки «Удалить контакт».
        :param contact: объект контакта для удаления
        """
        # Запрашиваем подтверждение удаления у пользователя
        confirmed = messagebox.askyesno(
            "Подтверждение",
            f"Вы уверены, что хотите удалить контакт\n«{contact.get_full_name()}»?",
            parent=self.root
        )

        # Выполняем удаление только при подтверждении
        if confirmed:
            # Удаляем контакт через менеджер
            self.manager.delete(contact.id)
            # Показываем заглушку в панели деталей
            self._show_placeholder()
            # Обновляем список контактов в таблице
            self._refresh_list()
            # Обновляем статусную строку
            self.status_label.config(text=f"Контакт «{contact.get_full_name()}» удалён")


# =============================================================================
# Точка входа в приложение
# =============================================================================
if __name__ == "__main__":
    # Создаём корневое окно Tkinter
    root = tk.Tk()

    # Создаём экземпляр главного приложения
    app = ContactApp(root)

    # Запускаем главный цикл обработки событий Tkinter
    root.mainloop()
