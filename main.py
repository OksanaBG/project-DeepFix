import pickle
from collections import UserDict
from datetime import datetime, timedelta
 #--------------#   
'''Базовий клас для полів запису'''
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
 #--------------#   
'''Клас для зберігання імені контакту. Обов'язкове поле.'''
class Name(Field):
    pass
 #--------------#   
'''Birthday з можливістю додавання поля для дня народження до контакту'''
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")
 #--------------#   
'''Клас для зберігання номера телефону. Має валідацію формату (10 цифр).'''
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)
#--------------#    
'''Клас Email з валідацією рядка - умова у рядку є @ та .''' 
class Email(Field):
    def __init__(self, value):
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email address.")
        super().__init__(value)
#------ADDRESS CLASS------#
'''Клас Address для зберігання адреси контакту'''
class Address(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Address cannot be empty.")
        super().__init__(value.strip())
#--------------#          
'''Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів.'''
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if phone:
            self.phones.remove(phone)
            self.phones.append(Phone(new_number))
        else:
            raise ValueError("Phone number not found.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)
    #-------add email--------#
    def add_email(self, email_str):
        self.email = Email(email_str)
    #-------add address--------#
    def add_address(self, address_str):
        self.address = Address(address_str)
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        bday_str = f", birthday: {self.birthday}" if self.birthday else ""
        email_str = f", email: {self.email}" if self.email else ""
        address_str = f", address: {self.address}" if self.address else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{bday_str}{email_str}{address_str}"
 #--------------#   
'''Клас для зберігання та управління записами'''
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()
        this_week = today + timedelta(days=7)

        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value.replace(year=today.year)
                if bday < today:
                    bday = bday.replace(year=today.year + 1)

                if today <= bday <= this_week:
                    congratulation_date = bday
                    if bday.weekday() == 5:  # Saturday
                        congratulation_date += timedelta(days=2)
                    elif bday.weekday() == 6:  # Sunday
                        congratulation_date += timedelta(days=1)

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%Y.%m.%d")
                    })

        return upcoming_birthdays
#--15/07/2025----------------------------------------------#
'''Клас Note- нотаток із текстом і тегом. Тегі можуть бути пусті'''
class Note:
    def __init__(self, text, tags=None):
        self.text = text
        self.tags = tags if tags else []
        self.created = datetime.now()
    '''edit note'''        
    def edit(self, new_text):
        self.text = new_text

    '''add tag to note'''
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
    
    '''delete tag'''
    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
    
    def __str__(self):
        tag_str = f" [tags: {', '.join(self.tags)}]" if self.tags else ""
        return f"{self.text}{tag_str} (Created: {self.created.strftime('%Y-%m-%d %H:%M')})"
    
'''Клас Notebook- для зберігання та управління нотатками'''
class Notebook(UserDict):
    '''add note  with uniq_id as %Y%m%d%H%M%S (date and time creating)'''
    def add_note(self, note):
        self.data[note.created.strftime("%Y%m%d%H%M%S")] = note

    def delete_note(self, note_id):
        if note_id in self.data:
            del self.data[note_id]
    '''search tag as any - not district'''
    def find_by_tag(self, keyword):
        return [note for note in self.data.values()
            if any(keyword.lower() in tag.lower() for tag in note.tags)]

    def search_text(self, keyword):
        return [note for note in self.data.values() if keyword.lower() in note.text.lower()]

    def edit_note(self, note_id, new_text):
        if note_id in self.data:
            self.data[note_id].edit(new_text)

    def get_all_notes(self):
        return list(self.data.items())
# ---------------------------------------------------------#        
'''Errors decorator'''   
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough parameters."
       # except EmptyLine:
    return wrapper
#---------------#
'''Add Contact'''
@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message
#---------------#
'''Change Contact'''
@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone updated."
    else:
        raise KeyError
    
#---------------#
'''Show Phone'''
@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {'; '.join(p.value for p in record.phones)}"
    else:
        raise KeyError

#---------------#
'''Show all contacts'''
@input_error
def show_all(args, book):
    if not book.data:
        return "No contacts found."
    return '\n'.join(str(record) for record in book.data.values())

#---------------#
'''Add BD to Contact'''
@input_error
def add_birthday(args, book):
    name, date = args
    record = book.find(name)
    if record:
        record.add_birthday(date)
        return "Birthday added."
    else:
        raise KeyError

#---------------#
'''Show BD of Contact'''
@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday}"
    elif record:
        return f"{name} has no birthday set."
    else:
        raise KeyError

#---------------#
'''Upcoming BDs'''
@input_error
def birthdays(args, book):
    bdays = book.get_upcoming_birthdays()
    if not bdays:
        return "No upcoming birthdays."
    return '\n'.join([f"{b['name']} - {b['congratulation_date']}" for b in bdays])
#------15/07/2025---------#
'''Add Email'''
@input_error
def add_email(args, book):
    name, email = args
    record = book.find(name)
    if record:
        record.add_email(email)
        return "Email added."
    else:
        raise KeyError
'''Show Email'''
@input_error
def show_email(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.email:
        return f"{name}'s email is {record.email}"
    elif record:
        return f"{name} has no email set."
    else:
        raise KeyError
'''Remove PhoneNumber'''
@input_error
def remove_phone(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.remove_phone(phone)
        return "Phone removed."
    else:
        raise KeyError
'''Add PhoneNumber'''
@input_error
def add_phone(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Phone added."
    else:
        raise KeyError
#------ADDRESS FUNCTIONS------#
'''Add Address'''
@input_error
def add_address(args, book):
    name = args[0]
    address = ' '.join(args[1:])  # Об'єднуємо всі аргументи після імені в адресу
    record = book.find(name)
    if record:
        record.add_address(address)
        return "Address added."
    else:
        raise KeyError
'''Show Address'''
@input_error
def show_address(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.address:
        return f"{name}'s address is {record.address}"
    elif record:
        return f"{name} has no address set."
    else:
        raise KeyError
#------Notes-----------------------------------------#
'''Add Notes'''
@input_error
def add_note(args, notebook):
    if not args:
        raise ValueError("Please provide a note text.")
    
    text = args[0]
    tags = args[1:]  # необов’язкові теги

    note = Note(text, tags)
    notebook.add_note(note)
    return "Note added."
'''Delete Notes'''
@input_error
def delete_note(args, notebook):
    note_id = args[0]
    if note_id in notebook.data:
        notebook.delete_note(note_id)
        return f"Note {note_id} deleted."
    else:
        return "Note ID not found."
'''Show Notes'''
@input_error
def show_notes(args, notebook):
    if not notebook.data:
        return "No notes found."
    
    result = []
    for note_id, note in notebook.get_all_notes():
        result.append(f"{note_id}: {note}")
    return '\n'.join(result)
#---------------#
'''Menu'''
def print_available_commands():
    print("Available commands:")
    print("  hello                        - Greet the bot")
    print("  add <name> <phone>           - Add a new contact")
    print("  change <name> <new phone>    - Change existing contact's phone")
    print("  phone <name>                 - Show the phone number of a contact")
    print("  all                          - Show all contacts")
    print("  show                         - Show all commands")
    ''''''
    print("  add-birthday <name> <DD.MM.YYYY>         - Add BD to Contact")
    print("  show-birthday <name>         - Show BD of Contact")
    print("  show                         - Show all commands")
    print("  close / exit                 - Exit the bot") 
    ''''''
    print("  add-phone <name> <phone>     - Add phone to existing contact")
    print("  remove-phone <name> <phone>  - Remove phone from contact")
    print("  add-email <name> <email>     - Add email to contact")
    print("  show-email <name>            - Show email of contact")
    print("  add-address <name> <address> - Add address to contact")
    print("  show-address <name>          - Show address of contact")
    '''Notes'''
    print("  add-note <text> [tags...]     - Add a note with optional tags")
    print("  delete-note <note_id>         - Delete a note by its ID")
    print("  show-notes                    - Show all notes")
    

#---------------#
'''Parser'''
def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.lower(), args

#---------------#
'''Серіалізація з pickle'''
def save_data(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)
#def save_data(book, filename="addressbook.pkl"):
#    with open(filename, "wb") as f:
#        pickle.dump(book, f)

#---------------#
'''Десеріалізація з pickle'''
def load_data(filename, default_factory):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"No file found: {filename}. Creating new empty object...")
        return default_factory()
#def load_data(filename="addressbook.pkl"):
#    try:
#        with open(filename, "rb") as f:
#            return pickle.load(f)
#    except FileNotFoundError:
#        print("Starting new address book...") 
#        return AddressBook()
#---------------#
#---------------#
'''Main'''
def main():
    ###book = AddressBook()
    '''Load AddressBook'''
     # book = load_data()
    book = load_data("addressbook.pkl", AddressBook)
    notebook = load_data("notes.pkl", Notebook)
    print("Welcome to the assistant bot!")
    print_available_commands()

    while True:
        # user_input = input("Enter a command: ")
        # command, args = parse_input(user_input)
        user_input = input("Enter a command: ").strip()
        #---------------#
        '''Command Valodator'''
        if not user_input:
            print_available_commands()
            continue
        try:
            command, args = parse_input(user_input)
        except ValueError:
            print_available_commands()
            continue
        ''''''
        if command in ["close", "exit"]:
            '''Save AddressBook before exit '''
            save_data(book) 
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "show":
            print_available_commands()
        elif command == "remove-phone":
            print(remove_phone(args, book))
        elif command == "add-phone":
            print(add_phone(args, book))
        elif command == "add-email":
            print(add_email(args, book))
        elif command == "add-email":
            print(add_email(args, book))
        elif command == "show-email":
            print(show_email(args, book))
        elif command == "add-address":
            print(add_address(args, book))
        elif command == "show-address":
            print(show_address(args, book))
       #-----Notes---------
        elif command == "add-note":
            print(add_note(args, notebook))
        elif command == "delete-note":
            print(delete_note(args, notebook))
        elif command == "show-notes":
            print(show_notes(args, notebook))
        else:
            print("Invalid command. Please select correct one of ")
            print_available_commands()
   


if __name__ == "__main__":
    main()