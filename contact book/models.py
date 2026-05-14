# =============================================================================
# models.py — Модели данных: базовый класс Contact и его подклассы
# =============================================================================

# Импортируем dataclasses для удобного создания классов данных
from dataclasses import dataclass, field
# Импортируем datetime для работы с датами
from datetime import datetime
# Импортируем Optional для указания необязательных полей
from typing import Optional


# =============================================================================
# Базовый класс Contact — инкапсулирует общие данные любого контакта
# =============================================================================
@dataclass
class Contact:
    """Базовый класс для представления контакта в телефонной книге."""

    # Уникальный идентификатор контакта (генерируется автоматически)
    id: str = field(default_factory=lambda: str(int(datetime.now().timestamp() * 1000)))

    # Имя контакта (обязательное поле)
    first_name: str = ""

    # Фамилия контакта (обязательное поле)
    last_name: str = ""

    # Номер телефона контакта
    phone: str = ""

    # Адрес электронной почты контакта
    email: str = ""

    # Дата создания записи (заполняется автоматически)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y %H:%M"))

    def get_full_name(self) -> str:
        """Возвращает полное имя контакта (имя + фамилия)."""
        # Объединяем имя и фамилию через пробел
        return f"{self.first_name} {self.last_name}".strip()

    def get_type_label(self) -> str:
        """
        Возвращает метку типа контакта.
        Полиморфный метод — переопределяется в подклассах.
        """
        # Базовый тип — просто «Контакт»
        return "Контакт"

    def get_display_info(self) -> str:
        """
        Возвращает краткую информацию для отображения в списке.
        Полиморфный метод — переопределяется в подклассах.
        """
        # Показываем телефон в базовой реализации
        return self.phone

    def matches_search(self, query: str) -> bool:
        """
        Проверяет, соответствует ли контакт поисковому запросу.
        Ищет вхождение строки в имени, фамилии, телефоне и email.
        """
        # Переводим запрос в нижний регистр для регистронезависимого поиска
        q = query.lower()

        # Проверяем каждое поле на вхождение поискового запроса
        return (
            q in self.first_name.lower()
            or q in self.last_name.lower()
            or q in self.phone
            or q in self.email.lower()
        )

    def to_dict(self) -> dict:
        """
        Преобразует объект контакта в словарь для сохранения в JSON.
        Используется для сериализации данных.
        """
        # Собираем все поля в словарь
        return {
            "id": self.id,
            "type": self.__class__.__name__,  # Сохраняем тип класса
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        """
        Создаёт объект контакта из словаря (десериализация из JSON).
        Фабричный метод для восстановления объектов из файла.
        """
        # Создаём объект и заполняем поля из словаря
        obj = cls(
            id=data.get("id", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            created_at=data.get("created_at", ""),
        )
        return obj


# =============================================================================
# Класс PersonalContact — контакт из личных знакомых (наследует Contact)
# =============================================================================
@dataclass
class PersonalContact(Contact):
    """Личный контакт — друг, родственник или знакомый."""

    # День рождения контакта (необязательное поле)
    birthday: str = ""

    # Адрес проживания (необязательное поле)
    address: str = ""

    def get_type_label(self) -> str:
        """Возвращает метку типа: Личный."""
        # Переопределяем метод базового класса для личного контакта
        return "Личный"

    def get_display_info(self) -> str:
        """Возвращает краткую информацию: телефон и день рождения при наличии."""
        # Формируем строку отображения с учётом необязательных полей
        info = self.phone
        if self.birthday:
            info += f" | ДР: {self.birthday}"
        return info

    def to_dict(self) -> dict:
        """Сериализует личный контакт в словарь, добавляя поля подкласса."""
        # Получаем базовый словарь от родительского класса
        data = super().to_dict()
        # Добавляем специфичные для личного контакта поля
        data["birthday"] = self.birthday
        data["address"] = self.address
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "PersonalContact":
        """Создаёт PersonalContact из словаря."""
        # Создаём базовый объект через родительский метод
        obj = super().from_dict(data)
        # Заполняем поля, специфичные для PersonalContact
        obj.birthday = data.get("birthday", "")
        obj.address = data.get("address", "")
        return obj


# =============================================================================
# Класс BusinessContact — рабочий контакт (наследует Contact)
# =============================================================================
@dataclass
class BusinessContact(Contact):
    """Рабочий контакт — коллега, партнёр или клиент."""

    # Название компании или организации
    company: str = ""

    # Должность контакта в компании
    position: str = ""

    def get_type_label(self) -> str:
        """Возвращает метку типа: Рабочий."""
        # Переопределяем метод базового класса для рабочего контакта
        return "Рабочий"

    def get_display_info(self) -> str:
        """Возвращает краткую информацию: телефон и компания при наличии."""
        # Формируем строку с телефоном и названием компании
        info = self.phone
        if self.company:
            info += f" | {self.company}"
        return info

    def to_dict(self) -> dict:
        """Сериализует рабочий контакт в словарь, добавляя поля подкласса."""
        # Получаем базовый словарь от родительского класса
        data = super().to_dict()
        # Добавляем специфичные для рабочего контакта поля
        data["company"] = self.company
        data["position"] = self.position
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "BusinessContact":
        """Создаёт BusinessContact из словаря."""
        # Создаём базовый объект через родительский метод
        obj = super().from_dict(data)
        # Заполняем поля, специфичные для BusinessContact
        obj.company = data.get("company", "")
        obj.position = data.get("position", "")
        return obj
