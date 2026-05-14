# =============================================================================
# storage.py — Изолированный модуль работы с файлами (сохранение и загрузка)
# =============================================================================

# Импортируем json для работы с форматом JSON
import json

# Импортируем os для проверки существования файла
import os

# Импортируем List для типизации списков
from typing import List

# Импортируем модели контактов из нашего модуля
from models import Contact, PersonalContact, BusinessContact


# =============================================================================
# Класс FileStorage — отвечает исключительно за чтение и запись файла данных
# =============================================================================
class FileStorage:
    """
    Изолированный класс для работы с файловой системой.
    Принцип единственной ответственности: только чтение и запись JSON.
    """

    def __init__(self, filepath: str = "contacts.json"):
        """
        Инициализация хранилища.
        :param filepath: путь к файлу JSON для хранения данных
        """
        # Сохраняем путь к файлу базы данных
        self.filepath = filepath

    def save(self, contacts: List[Contact]) -> bool:
        """
        Сохраняет список контактов в JSON-файл.
        :param contacts: список объектов контактов
        :return: True при успехе, False при ошибке
        """
        try:
            # Преобразуем каждый объект контакта в словарь
            data = [contact.to_dict() for contact in contacts]

            # Открываем файл для записи с кодировкой UTF-8
            with open(self.filepath, "w", encoding="utf-8") as f:
                # Записываем данные в JSON с красивым форматированием
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Возвращаем True при успешном сохранении
            return True

        except (IOError, OSError) as e:
            # Выводим сообщение об ошибке записи файла
            print(f"Ошибка сохранения файла: {e}")
            return False

    def load(self) -> List[Contact]:
        """
        Загружает контакты из JSON-файла.
        :return: список объектов контактов (пустой, если файла нет)
        """
        # Проверяем, существует ли файл данных
        if not os.path.exists(self.filepath):
            # Файл не найден — возвращаем пустой список
            return []

        try:
            # Открываем файл для чтения с кодировкой UTF-8
            with open(self.filepath, "r", encoding="utf-8") as f:
                # Читаем и разбираем JSON-данные из файла
                data = json.load(f)

            # Преобразуем каждый словарь обратно в объект нужного класса
            contacts = []
            for item in data:
                # Определяем тип контакта по сохранённому полю "type"
                contact_type = item.get("type", "Contact")

                # Создаём объект нужного подкласса в зависимости от типа
                if contact_type == "PersonalContact":
                    contact = PersonalContact.from_dict(item)
                elif contact_type == "BusinessContact":
                    contact = BusinessContact.from_dict(item)
                else:
                    # Неизвестный тип — создаём базовый контакт
                    contact = Contact.from_dict(item)

                # Добавляем восстановленный контакт в список
                contacts.append(contact)

            # Возвращаем загруженный список контактов
            return contacts

        except (json.JSONDecodeError, KeyError) as e:
            # Выводим сообщение об ошибке чтения или разбора файла
            print(f"Ошибка загрузки файла: {e}")
            return []
