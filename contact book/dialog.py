# =============================================================================
# dialog.py — Диалоговое окно добавления и редактирования контакта
# =============================================================================

# Импортируем tkinter для создания диалогового окна
import tkinter as tk
from tkinter import ttk

# Импортируем модели контактов из нашего модуля
from models import Contact, PersonalContact, BusinessContact
from typing import Optional


# =============================================================================
# Класс ContactDialog — всплывающее окно формы контакта
# =============================================================================
class ContactDialog:
    """
    Диалоговое окно для создания нового или редактирования существующего контакта.
    Возвращает заполненный объект контакта через атрибут result.
    """

    def __init__(self, parent: tk.Widget, title: str, contact: Optional[Contact] = None):
        """
        Инициализация диалогового окна.
        :param parent: родительский виджет
        :param title: заголовок диалогового окна
        :param contact: существующий контакт для редактирования (None для нового)
        """
        # Сохраняем ссылку на редактируемый контакт (None = создание нового)
        self.existing_contact = contact

        # Результат диалога — заполненный объект контакта (None если отменено)
        self.result: Optional[Contact] = None

        # Создаём дочернее окно Toplevel поверх родительского
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("440x520")
        self.top.resizable(False, False)
        self.top.configure(bg="#F7FAFC")

        # Делаем окно модальным (блокирует взаимодействие с родителем)
        self.top.grab_set()
        self.top.focus_set()

        # Центрируем диалоговое окно относительно родительского
        self.top.transient(parent)

        # Строим виджеты диалогового окна
        self._build_form()

        # Если передан существующий контакт — заполняем форму его данными
        if contact:
            self._populate_form(contact)

    def _build_form(self):
        """Создаёт все виджеты формы диалогового окна."""
        # Заголовок формы
        tk.Label(
            self.top, text="Данные контакта",
            bg="#F7FAFC", fg="#2D3748",
            font=("Arial", 13, "bold")
        ).pack(pady=(18, 4))

        # Разделительная линия под заголовком
        tk.Frame(self.top, bg="#E2E8F0", height=1).pack(fill="x", padx=20, pady=(0, 12))

        # Фрейм с прокруткой для полей формы
        form_frame = tk.Frame(self.top, bg="#F7FAFC", padx=24)
        form_frame.pack(fill="both", expand=True)

        # ── Выбор типа контакта ──────────────────────────────────────────────
        tk.Label(form_frame, text="Тип контакта", bg="#F7FAFC",
                 fg="#718096", font=("Arial", 9)).pack(anchor="w")

        # Переменная для хранения выбранного типа контакта
        self.type_var = tk.StringVar(value="personal")

        # Фрейм с переключателями типа контакта
        type_frame = tk.Frame(form_frame, bg="#F7FAFC")
        type_frame.pack(fill="x", pady=(2, 10))

        # Переключатель «Личный контакт»
        tk.Radiobutton(
            type_frame, text="👤 Личный", variable=self.type_var,
            value="personal", bg="#F7FAFC", fg="#2D3748",
            font=("Arial", 10), activebackground="#F7FAFC",
            command=self._on_type_change
        ).pack(side="left", padx=(0, 16))

        # Переключатель «Рабочий контакт»
        tk.Radiobutton(
            type_frame, text="💼 Рабочий", variable=self.type_var,
            value="business", bg="#F7FAFC", fg="#2D3748",
            font=("Arial", 10), activebackground="#F7FAFC",
            command=self._on_type_change
        ).pack(side="left")

        # ── Общие поля (имя, фамилия, телефон, email) ───────────────────────
        # Создаём текстовые поля с подписями
        self.entries = {}
        base_fields = [
            ("first_name", "Имя *"),
            ("last_name", "Фамилия *"),
            ("phone", "Телефон"),
            ("email", "Email"),
        ]
        for key, label in base_fields:
            self._add_field(form_frame, key, label)

        # ── Поля для личного контакта ────────────────────────────────────────
        self.personal_frame = tk.Frame(form_frame, bg="#F7FAFC")
        self.personal_frame.pack(fill="x")
        self._add_field(self.personal_frame, "birthday", "День рождения (ДД.ММ.ГГГГ)")
        self._add_field(self.personal_frame, "address", "Адрес")

        # ── Поля для рабочего контакта ───────────────────────────────────────
        self.business_frame = tk.Frame(form_frame, bg="#F7FAFC")
        self.business_frame.pack(fill="x")
        self._add_field(self.business_frame, "company", "Компания")
        self._add_field(self.business_frame, "position", "Должность")

        # Сразу скрываем блок рабочих полей (показываем личные по умолчанию)
        self.business_frame.pack_forget()

        # ── Кнопки подтверждения и отмены ───────────────────────────────────
        btn_frame = tk.Frame(self.top, bg="#F7FAFC", padx=24, pady=14)
        btn_frame.pack(fill="x", side="bottom")

        # Кнопка «Сохранить» — подтверждает создание/редактирование
        tk.Button(
            btn_frame, text="💾  Сохранить",
            bg="#4299E1", fg="white",
            font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", pady=8,
            command=self._on_save
        ).pack(side="right", padx=(8, 0), ipadx=16)

        # Кнопка «Отмена» — закрывает диалог без сохранения
        tk.Button(
            btn_frame, text="Отмена",
            bg="#E2E8F0", fg="#4A5568",
            font=("Arial", 10),
            relief="flat", cursor="hand2", pady=8,
            command=self.top.destroy
        ).pack(side="right", ipadx=12)

    def _add_field(self, parent: tk.Widget, key: str, label: str):
        """
        Добавляет поле ввода с подписью в указанный контейнер.
        :param parent: родительский виджет для размещения поля
        :param key: ключ для словаря entries (идентификатор поля)
        :param label: текст подписи над полем ввода
        """
        # Создаём контейнер для поля с отступами
        row = tk.Frame(parent, bg="#F7FAFC", pady=2)
        row.pack(fill="x")

        # Подпись поля ввода
        tk.Label(
            row, text=label, bg="#F7FAFC",
            fg="#718096", font=("Arial", 9)
        ).pack(anchor="w")

        # Поле ввода текста
        entry = tk.Entry(
            row, font=("Arial", 10),
            bg="white", fg="#2D3748",
            relief="flat", bd=1,
            insertbackground="#2D3748"
        )
        entry.pack(fill="x", ipady=5)

        # Добавляем рамку под полем ввода для визуального выделения
        tk.Frame(row, bg="#CBD5E0", height=1).pack(fill="x")

        # Сохраняем ссылку на поле в словаре по ключу
        self.entries[key] = entry

    def _on_type_change(self):
        """Обработчик смены типа контакта — показывает нужные поля."""
        # Определяем выбранный тип контакта
        contact_type = self.type_var.get()

        if contact_type == "personal":
            # Показываем поля для личного контакта
            self.business_frame.pack_forget()
            self.personal_frame.pack(fill="x")
        else:
            # Показываем поля для рабочего контакта
            self.personal_frame.pack_forget()
            self.business_frame.pack(fill="x")

    def _populate_form(self, contact: Contact):
        """
        Заполняет поля формы данными существующего контакта.
        :param contact: контакт, данные которого нужно отобразить
        """
        # Определяем тип контакта и устанавливаем переключатель
        if isinstance(contact, BusinessContact):
            self.type_var.set("business")
            self._on_type_change()
        else:
            self.type_var.set("personal")

        # Заполняем общие поля данными контакта
        fields = ["first_name", "last_name", "phone", "email"]
        for field in fields:
            if field in self.entries:
                # Получаем значение атрибута объекта контакта
                value = getattr(contact, field, "")
                # Очищаем поле и вставляем новое значение
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, value)

        # Заполняем специфичные поля в зависимости от типа контакта
        if isinstance(contact, PersonalContact):
            extra_fields = ["birthday", "address"]
        elif isinstance(contact, BusinessContact):
            extra_fields = ["company", "position"]
        else:
            extra_fields = []

        # Заполняем дополнительные поля
        for field in extra_fields:
            if field in self.entries:
                value = getattr(contact, field, "")
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, value)

    def _on_save(self):
        """
        Обработчик кнопки «Сохранить» — валидирует форму и создаёт объект контакта.
        """
        # Считываем значения из полей ввода формы
        first_name = self.entries["first_name"].get().strip()
        last_name = self.entries["last_name"].get().strip()
        phone = self.entries["phone"].get().strip()
        email = self.entries["email"].get().strip()

        # Проверяем обязательное поле «Имя»
        if not first_name:
            # Выделяем красным поле с ошибкой и выходим без сохранения
            self.entries["first_name"].configure(bg="#FED7D7")
            self.entries["first_name"].focus_set()
            return

        # Сбрасываем подсветку ошибки если поле заполнено
        self.entries["first_name"].configure(bg="white")

        # Определяем выбранный тип контакта
        contact_type = self.type_var.get()

        if contact_type == "personal":
            # Создаём объект личного контакта с введёнными данными
            contact = PersonalContact(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                birthday=self.entries.get("birthday", tk.Entry()).get().strip(),
                address=self.entries.get("address", tk.Entry()).get().strip(),
            )
        else:
            # Создаём объект рабочего контакта с введёнными данными
            contact = BusinessContact(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                company=self.entries.get("company", tk.Entry()).get().strip(),
                position=self.entries.get("position", tk.Entry()).get().strip(),
            )

        # При редактировании сохраняем исходный ID и дату создания
        if self.existing_contact:
            contact.id = self.existing_contact.id
            contact.created_at = self.existing_contact.created_at

        # Сохраняем результат и закрываем диалоговое окно
        self.result = contact
        self.top.destroy()
