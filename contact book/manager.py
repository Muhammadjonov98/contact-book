# =============================================================================
# manager.py — Менеджер контактов: управление бизнес-логикой приложения
# =============================================================================

# Импортируем List для типизации, Optional для необязательных значений
from typing import List, Optional

# Импортируем модели контактов
from models import Contact, PersonalContact, BusinessContact

# Импортируем класс хранилища для работы с файлами
from storage import FileStorage


# =============================================================================
# Класс ContactManager — координирует операции над контактами
# Изолирует бизнес-логику от пользовательского интерфейса
# =============================================================================
class ContactManager:
    """
    Менеджер контактов — единственная точка доступа к данным для UI.
    Управляет списком контактов и взаимодействует с хранилищем.
    """

    def __init__(self, storage: FileStorage):
        """
        Инициализация менеджера.
        :param storage: объект хранилища для чтения/записи файла
        """
        # Сохраняем ссылку на объект хранилища (внедрение зависимости)
        self.storage = storage

        # Загружаем контакты из файла при старте приложения
        self._contacts: List[Contact] = self.storage.load()

    def get_all(self) -> List[Contact]:
        """
        Возвращает полный список всех контактов.
        :return: список всех контактов
        """
        # Возвращаем копию списка, чтобы предотвратить прямое изменение
        return list(self._contacts)

    def search(self, query: str) -> List[Contact]:
        """
        Ищет контакты по запросу (имя, фамилия, телефон, email).
        :param query: строка поиска
        :return: список контактов, соответствующих запросу
        """
        # Если запрос пустой — возвращаем все контакты
        if not query.strip():
            return self.get_all()

        # Фильтруем контакты через полиморфный метод matches_search
        return [c for c in self._contacts if c.matches_search(query)]

    def add(self, contact: Contact) -> bool:
        """
        Добавляет новый контакт в список и сохраняет в файл.
        :param contact: объект нового контакта
        :return: True при успехе
        """
        # Добавляем контакт в список в памяти
        self._contacts.append(contact)

        # Сохраняем обновлённый список в файл через хранилище
        return self.storage.save(self._contacts)

    def update(self, contact_id: str, updated_contact: Contact) -> bool:
        """
        Обновляет существующий контакт по его ID.
        :param contact_id: уникальный идентификатор контакта
        :param updated_contact: объект с новыми данными
        :return: True при успехе, False если контакт не найден
        """
        # Ищем индекс контакта с нужным ID в списке
        for i, contact in enumerate(self._contacts):
            if contact.id == contact_id:
                # Заменяем старый контакт на обновлённый
                self._contacts[i] = updated_contact
                # Сохраняем изменения в файл
                return self.storage.save(self._contacts)

        # Контакт с таким ID не найден
        return False

    def delete(self, contact_id: str) -> bool:
        """
        Удаляет контакт из списка по его ID.
        :param contact_id: уникальный идентификатор контакта
        :return: True при успехе, False если контакт не найден
        """
        # Запоминаем исходный размер списка для проверки удаления
        original_count = len(self._contacts)

        # Оставляем только контакты с другим ID (удаляем нужный)
        self._contacts = [c for c in self._contacts if c.id != contact_id]

        # Проверяем, был ли удалён хотя бы один контакт
        if len(self._contacts) < original_count:
            # Сохраняем обновлённый список в файл
            return self.storage.save(self._contacts)

        # Контакт с таким ID не найден
        return False

    def get_by_id(self, contact_id: str) -> Optional[Contact]:
        """
        Находит и возвращает контакт по его уникальному ID.
        :param contact_id: уникальный идентификатор контакта
        :return: объект контакта или None, если не найден
        """
        # Ищем контакт с нужным ID
        for contact in self._contacts:
            if contact.id == contact_id:
                # Контакт найден — возвращаем его
                return contact

        # Контакт не найден — возвращаем None
        return None

    def get_count(self) -> int:
        """
        Возвращает общее количество контактов в книге.
        :return: количество контактов
        """
        # Возвращаем длину списка контактов
        return len(self._contacts)
