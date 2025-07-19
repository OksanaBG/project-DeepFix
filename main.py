import pickle
import difflib             #for correct command
from colorama import Fore, Style, init  #for color text
import pandas as pd        #for make table
from tabulate import tabulate       #for center table
import re
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
            raise ValueError(f"{Fore.RED}Invalid date format.{Style.RESET_ALL}Use{Fore.YELLOW} <DD.MM.YYYY>{Style.RESET_ALL}")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

#--------------#   
'''Клас для зберігання номера телефону з покращеною валідацією'''
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError(f"{Fore.RED}Phone number must be 10 digits.{Style.RESET_ALL}")
        super().__init__(value)
#--------------#    
'''Клас Email з валідацією рядка - умова у рядку є @ та .''' 
class Email(Field):
    def __init__(self, value):
        if "@" not in value or "." not in value:
            raise ValueError(f"{Fore.RED}Invalid email address.{Style.RESET_ALL}")
        super().__init__(value)
#------ADDRESS CLASS------#
'''Клас Address для зберігання адреси контакту'''
class Address(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError(f"{Fore.RED}Address cannot be empty.{Style.RESET_ALL}")
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
            raise ValueError(f"{Fore.RED}Phone number not found.{Style.RESET_ALL}")

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
    
    def get_birthdays_in_days(self, days):
        '''Отримати список днів народження через задану кількість днів'''
        birthdays_in_period = []
        today = datetime.today().date()
        target_date = today + timedelta(days=days)

        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value.replace(year=today.year)
                if bday < today:
                    bday = bday.replace(year=today.year + 1)

                if today <= bday <= target_date:
                    # Розрахунок дати привітання з урахуванням вихідних
                    congratulation_date = bday
                    if bday.weekday() == 5:  # Saturday
                        congratulation_date += timedelta(days=2)
                    elif bday.weekday() == 6:  # Sunday
                        congratulation_date += timedelta(days=1)

                    # Розрахунок кількості днів до дня народження
                    days_until = (bday - today).days
                    
                    birthdays_in_period.append({
                        "name": record.name.value,
                        "birthday": bday.strftime("%d.%m.%Y"),
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                        "days_until": days_until
                    })

        # Сортуємо за кількістю днів до дня народження
        birthdays_in_period.sort(key=lambda x: x['days_until'])
        return birthdays_in_period
    
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
    #----17/05/2025---sort method for notes
    def get_sorted_notes(self, sort_type="date", reverse=False):
        if sort_type == "date":
            key_func = lambda item: item[1].created
        elif sort_type == "tag-count":
            key_func = lambda item: len(item[1].tags)
        elif sort_type == "tag-name":
            key_func = lambda item: item[1].tags[0].lower() if item[1].tags else ''
        else:
            raise ValueError("Unsupported sort type.")

        return sorted(self.data.items(), key=key_func, reverse=reverse)
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
    message = f"{Fore.BLUE}Contact updated.{Style.RESET_ALL}"
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"{Fore.YELLOW}Contact added.{Style.RESET_ALL}"
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
        return f"{Fore.BLUE}Phone updated.{Style.RESET_ALL}"
    else:
        raise KeyError
    
#---------------#
'''Show Phone - Serch contact by Name/Phone'''
@input_error
def show_phone(args, book):
    if not args:
        raise ValueError("Please provide a search keyword (name or phone).")
    
    keyword = args[0].lower()  
    # рядок результату
    results = [] 

    for record in book.data.values():
        # шукаємо у іменах
        name_match = keyword in record.name.value.lower()
        # шукаємо в номерах через генеративний вираз
        phone_match = any(keyword in phone.value for phone in record.phones)
        #формуємо результат
        if name_match or phone_match:
            # номера через ;
            phones = "; ".join(p.value for p in record.phones)
            results.append(f"{record.name.value}: {phones}")

    if not results:
        return "No matching contacts found."
    # кожне входження з нового рядкаф
    return '\n'.join(results)

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
        return f"{Fore.RED}No contacts found.{Style.RESET_ALL}"
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
        return f"{Fore.YELLOW}Birthday added.{Style.RESET_ALL}"
    else:
        raise KeyError

#---------------#
'''Show BD of Contact'''
@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {Fore.YELLOW, record.birthday, Style.RESET_ALL}"
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

#---------------#
'''Birthdays in specified days'''
@input_error
def birthdays_in_days(args, book):
    if not args:
        raise ValueError("Please provide the number of days.")
    
    try:
        days = int(args[0])
        if days < 0:
            raise ValueError("Number of days cannot be negative.")
    except ValueError:
        raise ValueError("Please provide a valid number of days.")
    
    bdays = book.get_birthdays_in_days(days)
    if not bdays:
        return f"No birthdays in the next {days} days."
    
    result = [f"Birthdays in the next {days} days:"]
    for b in bdays:
        if b['days_until'] == 0:
            result.append(f"{b['name']} - TODAY ({b['birthday']})")
        elif b['days_until'] == 1:
            result.append(f"{b['name']} - TOMORROW ({b['birthday']})")
        else:
            result.append(f"{b['name']} - in {b['days_until']} days ({b['birthday']})")
    
    return '\n'.join(result)

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
        return f"{Fore.BLUE, name} has no email set.{Style.RESET_ALL}"
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
        return f"{Fore.YELLOW}Phone added.{Style.RESET_ALL}"
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
        return f"{Fore.YELLOW}Address added.{Style.RESET_ALL}"
    else:
        raise KeyError
'''Show Address'''
@input_error
def show_address(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.address:
        return f"{name}'s address is {Fore.YELLOW, record.address, Style.RESET_ALL}"
    elif record:
        return f"{Fore.BLUE, name} has no address set.{Style.RESET_ALL}"
    else:
        raise KeyError
    
#------Notes-----------------------------------------#
'''Add Notes'''
@input_error
def add_note(args, notebook):
    print("Please enter your note text:")
    text = input(">>> ").strip()

    if not text:
        raise ValueError("Note text cannot be empty.")

    print("Please enter your tags for this note (separated by ';' or press Enter to skip):")
    raw_tags = input(">>> ").strip()

    # Розділяємо по крапці з комою
    tags = [tag.strip() for tag in raw_tags.split(";") if tag.strip()] if raw_tags else []

    note = Note(text, tags)
    notebook.add_note(note)
    return "Note added."

'''Delete Notes'''
@input_error
def delete_note(args, notebook):
    note_id = args[0]
    if note_id in notebook.data:
        notebook.delete_note(note_id)
        return f"Note {Fore.YELLOW, note_id, Style.RESET_ALL} deleted."
    else:
        return f"{Fore.RED}Note ID not found.{Style.RESET_ALL}"
'''Show Notes'''
@input_error
def show_notes(notebook):
    if not notebook.data:
        return f"{Fore.RED}No notes found.{Style.RESET_ALL}"

    result = []
    for note_id, note in notebook.get_all_notes():
        result.append(f"{note_id}: {note}")
    return '\n'.join(result)
'''Search by Tag Notes'''
@input_error
def find_tag(args, notebook):
    if not args:
        raise ValueError(f"{Fore.RED}Please provide a tag to search.{Style.RESET_ALL}")

    keyword = args[0]
    results = notebook.find_by_tag(keyword)

    if not results:
        return f"{Fore.RED}No notes found with tag containing '{Fore.YELLOW, keyword, Fore.RED}'.{Style.RESET_ALL}"

    return '\n'.join([str(note) for note in results])
'''Serch Notes'''
@input_error
def find_note(args, notebook):
    if not args:
        raise ValueError(f"{Fore.RED}Please provide a keyword to search in note text.{Style.RESET_ALL}")
    
    keyword = args[0]
    results = notebook.search_text(keyword)

    if not results:
        return f"{Fore.RED}No notes found containing '{Fore.RED, keyword, Fore.RED}'.{Style.RESET_ALL}"

    return '\n'.join([str(note) for note in results])
'''Edit Notes'''
@input_error
def edit_note_command(args, notebook):
    if len(args) < 2:
        raise ValueError(f"Usage: {Fore.YELLOW}edit-note <note_id> <new_text>{Style.RESET_ALL}")
    
    note_id = args[0]
    new_text = ' '.join(args[1:])  # дозволяємо багатослівний текст

    if note_id in notebook.data:
        notebook.edit_note(note_id, new_text)
        return f"Note {Fore.YELLOW, note_id, Style.RESET_ALL} updated."
    else:
        return f"{Fore.RED}Note ID not found.{Style.RESET_ALL}"
    
@input_error
def add_tag_command(args, notebook):
    if len(args) < 2:
        raise ValueError(f"Usage: {Fore.YELLOW}add-tag <note_id> <tag>{Style.RESET_ALL}")

    note_id = args[0]
    tag = args[1]

    if note_id in notebook.data:
        notebook.data[note_id].add_tag(tag)
        return f"Tag '{Fore.YELLOW, tag, Style.RESET_ALL}' added to note {Fore.YELLOW, note_id, Style.RESET_ALL}."
    else:
        return f"{Fore.RED}Note ID not found.{Style.RESET_ALL}"
    
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
            return f"Tag '{Fore.YELLOW, tag, Style.RESET_ALL}' removed from note {Fore.YELLOW, note_id, Style.RESET_ALL}."
        else:
            return f"{Fore.RED}Tag '{Fore.YELLOW, tag, Fore.RED}' not found in note {Fore.YELLOW, note_id, Fore.RED}.{Style.RESET_ALL}"
    else:
        return f"{Fore.RED}Note ID not found.{Style.RESET_ALL}"
    
'''Sort Notes by parametrs:
    sort-notes                       # за датою створення (від старих до нових)
    sort-notes date desc             # за датою у зворотному порядку
    sort-notes tag-count             # за кількістю тегів
    sort-notes tag-count desc        # за кількістю тегів у зворотному порядку
    sort-notes tag-name              # за алфавітом першого тегу
'''
@input_error
def sort_notes(args, notebook):
    sort_type = args[0].lower() if args else "date"
    reverse = "desc" in args

    sorted_notes = notebook.get_sorted_notes(sort_type=sort_type, reverse=reverse)

    if not sorted_notes:
        return f"{Fore.RED}No notes found.{Style.RESET_ALL}"

    return '\n'.join([f"{note_id}: {note}" for note_id, note in sorted_notes])

#---------------#
'''Corrective Command'''

valide_comands = [
    "close", "exit", "hello", "add", "change", "phone", "all", "add-birthday",
    "show-birthday", "birthdays", "show", "remove-phone", "add-phone",
    "add-email", "show-email", "add-address", "show-address", "add-note",
    "delete-note", "show-notes", "find-tag", "find-note", "edit-note",
    "add-tag", "delete-tag"]

@input_error
def corective_command(command, valide_comands, args):
    closest_matches = difflib.get_close_matches(command, valide_comands, n=2, cutoff=0.6)
    if closest_matches:
        Match = ' '.join([closest_matches[0]] + args[:])
        confirm = input(f"{Fore.YELLOW}Did you mean {Match} ? Y/N:{Style.RESET_ALL} ").strip().lower()
        return Match if confirm.lower() == 'y' else None
    return

#---------------#
'''Menu'''
def print_available_commands():
    print(Fore.YELLOW + """
    Control commands:    
         hello                             - Greet the bot
         close / exit                      - Exit the bot
         show                              - Show all commands
          
    Available commands for Addressbook:
      add <name> <phone>                - Add a new contact
      all                               - Show all contacts
      change <name> <new phone>         - Change existing contact's phone
      search                            - Show the phone number of a contact      
      add-birthday <name> <DD.MM.YYYY>  - Add BD to Contact
      show-birthday <name>              - Show BD of Contact 
      birthdays                         - Show upcoming birthdays (next 7 days)
      birthdays-in <days>               - Show birthdays in next X days             
      add-phone <name> <phone>          - Add phone to existing contact
      remove-phone <name> <phone>       - Remove phone from contact
      add-email <name> <email>          - Add email to contact
      show-email <name>                 - Show email of contact
      add-address <name> <address>      - Add address to contact
      show-address <name>               - Show address of contact
    
    Available commands for Notebook:    
      add-note <text> [tags...]         - Add a note with optional tags
      delete-note <note_id>             - Delete a note by its ID
      show-notes                        - Show all notes
      find-tag <tag>                    - Find notes by tag (partial match)
      find-note <text>                  - Find notes by text content
      edit-note <id> <new text>         - Edit text of an existing note
      add-tag <id> <tag>                - Add a tag to a note
      delete-tag <id> <tag>             - Remove a tag from a note
      sort-notes [date|tag-count|tag-name] [desc] - Sort notes by selected method
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
        print(f"{Fore.RED}No file found:{Style.RESET_ALL} {filename}. {Fore.YELLOW}Creating new empty object...{Style.RESET_ALL}")
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
    autopaste = None

    while True:
        # user_input = input("Enter a command: ")
        # command, args = parse_input(user_input)
        # init(autoreset=True)
        #---------------#
        '''Command Valodator'''
        if autopaste:
            try:
                command, args = parse_input(autopaste)
                autopaste = None
            except ValueError:
                print_available_commands()
                autopaste = None
                continue
        else:
            user_input = input(f"Enter a command: ").strip()
            try:
                command, args = parse_input(user_input)
            except ValueError:
                print_available_commands()
                continue
            
        ''''''

        match command:
            case "close" | "exit":
                '''Save AddressBook before exit'''
                save_data(book, "addressbook.pkl")
                save_data(notebook, "notes.pkl")
                print("Good bye!")
                break

            case "hello":
                print("How can I help you?")

            case "add":
                print(add_contact(args, book))

            case "change":
                print(change_contact(args, book))

            case "search":
                print(show_phone(args, book))

            case "all":
                print(show_all(book))

            case "add-birthday":
                print(add_birthday(args, book))

            case "show-birthday":
                print(show_birthday(args, book))

            case "birthdays":
                print(birthdays(args, book))

            case "birthdays-in":
                print(birthdays_in_days(args, book))

            case "show":
                print_available_commands()

            case "remove-phone":
                print(remove_phone(args, book))

            case "add-phone":
                print(add_phone(args, book))

            case "add-email":
                print(add_email(args, book))

            case "show-email":
                print(show_email(args, book))

            case "add-address":
                print(add_address(args, book))

            case "show-address":
                print(show_address(args, book))

            # ----- Notes -----
            case "add-note":
                print(add_note(args, notebook))

            case "delete-note":
                print(delete_note(args, notebook))

            case "show-notes":
                print(show_notes(notebook))

            case "find-tag":
                print(find_tag(args, notebook))

            case "find-note":
                print(find_note(args, notebook))

            case "edit-note":
                print(edit_note_command(args, notebook))

            case "add-tag":
                print(add_tag_command(args, notebook))

            case "delete-tag":
                print(delete_tag_command(args, notebook))

            case _:
                print(f"{Fore.RED}command not found.{Style.RESET_ALL}")
                autopaste = corective_command(command, valide_comands, args)


if __name__ == "__main__":
    main()
