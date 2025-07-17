import pickle
import difflib             #for correct command
from colorama import Fore, Style, init  #for color text
import pandas as pd        #for make table
from tabulate import tabulate       #for center table
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
            return f"{Fore.RED}Contact not found.{Style.RESET_ALL}"
        except ValueError as e:
            return Fore.RED + str(e) + Style.RESET_ALL
        except IndexError:
            return f"{Fore.RED}Not enough parameters.{Style.RESET_ALL}"
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
def show_all(book):
    res = pd.DataFrame()
    for record in book.data.values():
        phones = "\n".join(p.value for p in record.phones)
        birthday = str(record.birthday) if record.birthday else "No birthday"
        email = str(record.email) if record.email else "No email"
        address = str(record.address) if record.address else "No address"
        
        res = res._append({
            "Name": record.name.value,
            "Phones": phones,
            "Birthday": birthday,
            "Email": email,
            "Address": address
        }, ignore_index=True)
    if not book.data:
        return "No contacts found."
    return (Fore.GREEN + tabulate(res, headers="keys", tablefmt="grid", showindex=False, colalign=("center", "center", "center", "center", "center")) + Style.RESET_ALL)
    #return '\n'.join(str(record) for record in book.data.values())

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
'''Search by Tag Notes'''
@input_error
def find_tag(args, notebook):
    if not args:
        raise ValueError("Please provide a tag to search.")

    keyword = args[0]
    results = notebook.find_by_tag(keyword)

    if not results:
        return f"No notes found with tag containing '{keyword}'."

    return '\n'.join([str(note) for note in results])
@input_error
def find_note(args, notebook):
    if not args:
        raise ValueError("Please provide a keyword to search in note text.")
    
    keyword = args[0]
    results = notebook.search_text(keyword)

    if not results:
        return f"No notes found containing '{keyword}'."

    return '\n'.join([str(note) for note in results])
@input_error
def edit_note_command(args, notebook):
    if len(args) < 2:
        raise ValueError("Usage: edit-note <note_id> <new_text>")
    
    note_id = args[0]
    new_text = ' '.join(args[1:])  # дозволяємо багатослівний текст

    if note_id in notebook.data:
        notebook.edit_note(note_id, new_text)
        return f"Note {note_id} updated."
    else:
        return "Note ID not found."
@input_error
def add_tag_command(args, notebook):
    if len(args) < 2:
        raise ValueError("Usage: add-tag <note_id> <tag>")

    note_id = args[0]
    tag = args[1]

    if note_id in notebook.data:
        notebook.data[note_id].add_tag(tag)
        return f"Tag '{tag}' added to note {note_id}."
    else:
        return "Note ID not found."
@input_error
def delete_tag_command(args, notebook):
    if len(args) < 2:
        raise ValueError("Usage: delete-tag <note_id> <tag>")

    note_id = args[0]
    tag = args[1]

    if note_id in notebook.data:
        note = notebook.data[note_id]
        if tag in note.tags:
            note.remove_tag(tag)
            return f"Tag '{tag}' removed from note {note_id}."
        else:
            return f"Tag '{tag}' not found in note {note_id}."
    else:
        return "Note ID not found."


#---------------#
'''Corrective Command'''

valide_comands =["close", "exit", "hello", "add", "change", "phone", "all", "add-birthday",
                    "show-birthday", "birthdays", "show", "remove-phone", "add-phone", "add-email",
                    "show-email", "add-address", "show-address", "add-note", "delete-note", "show-notes",
                    "find-tag", "find-note", "edit-note", "add-tag", "delete-tag"]

def corective_command(command, valide_comands, args):
    closest_matches = difflib.get_close_matches(command, valide_comands, n=2, cutoff=0.6)
    if closest_matches:
        return (f"{Fore.YELLOW}Did you mean: {', '.join(closest_matches)}?{Style.RESET_ALL}")
        # Match = ' '.join([closest_matches[0]] + args[:])
        # confirm = input(f"Did you mean {Match}? Y/N: ").strip().lower()
        # if confirm.lower() == 'y':
        #     global user_input
        #     user_input = Match 
        #     return user_input
        # else:
        #     return "Command not recognized. Please try again."
    return "Command not found"

#---------------#
'''Menu'''
def print_available_commands():
    print(Fore.YELLOW + """
    Available commands:
          
      hello                             - Greet the bot
      add <name> <phone>                - Add a new contact
      change <name> <new phone>         - Change existing contact's phone
      phone <name>                      - Show the phone number of a contact
      all                               - Show all contacts
      show                              - Show all commands
      add-birthday <name> <DD.MM.YYYY>  - Add BD to Contact
      show-birthday <name>              - Show BD of Contact
      show                              - Show all commands
      close / exit                      - Exit the bot
      add-phone <name> <phone>          - Add phone to existing contact
      remove-phone <name> <phone>       - Remove phone from contact
      add-email <name> <email>          - Add email to contact
      show-email <name>                 - Show email of contact
      add-address <name> <address>      - Add address to contact
      show-address <name>               - Show address of contact
      add-note <text> [tags...]         - Add a note with optional tags
      delete-note <note_id>             - Delete a note by its ID
      show-notes                        - Show all notes
      find-tag <tag>                    - Find notes by tag (partial match)
      find-note <text>                  - Find notes by text content
      edit-note <id> <new text>         - Edit text of an existing note
      add-tag <id> <tag>                - Add a tag to a note
      delete-tag <id> <tag>             - Remove a tag from a note
    """ + Style.RESET_ALL)
    

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
        # init(autoreset=True)
        global user_input
        user_input = input(f"Enter a command: ").strip()

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
            save_data(book, "addressbook.pkl")
            save_data(notebook, "notes.pkl" )
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
            print(show_all(book))
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
        elif command == "find-tag":
            print(find_tag(args, notebook))
        elif command == "find-note":
            print(find_note(args, notebook))
        elif command == "edit-note":
            print(edit_note_command(args, notebook))
        elif command == "add-tag":
            print(add_tag_command(args, notebook))
        elif command == "delete-tag":
            print(delete_tag_command(args, notebook))
        else:
            try:
                print(corective_command(command, valide_comands, args))
            except ValueError:
                print(f"{Fore.RED}Invalid command. Please select correct one of{Style.RESET_ALL}")
                print_available_commands()
   


if __name__ == "__main__":
    main()