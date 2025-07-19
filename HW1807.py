import re
import pickle

class Contact:
    def __init__(self, name, phone=None, email=None):
        self.name = name
        self.phone = phone if self.validate_phone(phone) else None
        self.email = email if self.validate_email(email) else None

    def validate_phone(self, phone):
        pattern = r'^\+380\d{9}$'
        return bool(re.match(pattern, phone))

    def validate_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def __str__(self):
        return f"Ім’я: {self.name}, Телефон: {self.phone or 'не вказано'}, Email: {self.email or 'не вказано'}"


class AddressBook:
    def __init__(self):
        self.contacts = {}

    def add_contact(self, contact):
        if contact.name in self.contacts:
            return "Контакт вже існує."
        self.contacts[contact.name] = contact
        return "Контакт додано."

    def find(self, name):
        return self.contacts.get(name)

    def delete(self, name):
        if name in self.contacts:
            del self.contacts[name]
            return "Контакт видалено."
        return "Контакт не знайдено."

    def edit(self, name, phone=None, email=None):
        contact = self.contacts.get(name)
        if contact:
            if phone:
                contact.phone = phone if contact.validate_phone(phone) else contact.phone
            if email:
                contact.email = email if contact.validate_email(email) else contact.email
            return "Контакт оновлено."
        return "Контакт не знайдено."

    def show_all(self):
        if not self.contacts:
            return "Книга контактів порожня."
        return "\n".join(str(contact) for contact in self.contacts.values())

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def find_contact_by_full_name(address_book, name):
    contact = address_book.find(name)
    return str(contact) if contact else f"Контакт '{name}' не знайдено."


def main():
    book = load_data()
    print("📘 Вітаю у персональному помічнику!")

    while True:
        command = input("\nВведіть команду (add/find/edit/delete/show/exit): ").strip().lower()

        if command == "add":
            name = input("Ім’я: ")
            phone = input("Телефон (+380xxxxxxxxx): ")
            email = input("Email: ")
            contact = Contact(name, phone, email)
            print(book.add_contact(contact))

        elif command == "find":
            name = input("Введіть повне ім’я для пошуку: ")
            print(find_contact_by_full_name(book, name))

        elif command == "edit":
            name = input("Ім’я контакту для редагування: ")
            phone = input("Новий телефон (або натисніть Enter): ")
            email = input("Новий email (або натисніть Enter): ")
            print(book.edit(name, phone or None, email or None))

        elif command == "delete":
            name = input("Ім’я контакту для видалення: ")
            print(book.delete(name))

        elif command == "show":
            print(book.show_all())

        elif command == "exit":
            save_data(book)
            print("Дані збережено. До побачення!")
            break

        else:
            print("Невідома команда. Спробуйте ще раз.")


if __name__ == "__main__":
    main()