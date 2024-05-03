from _collections_abc import Iterator
from datetime import datetime
from collections import UserDict
import pickle
import os
import re
import time
import shutil
from pathlib import Path
from rich import print
from rich.console import Console
from rich.theme import Theme
from rich.progress import track

custom_theme = Theme(
    {"success": "bold green", "error": "bold red", "warning": "bold yellow", "menu": "yellow", "row":"bright_blue", "note":"bold magenta"})
console = Console(theme=custom_theme)

# Parrent class for all fields
class Field:
    def __init__(self, value=None):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

# Class for contact name, allow letters and space characters
class Name(Field):
    @Field.value.setter
    def value(self, value: str):
        if not re.findall(r'[^a-zA-Z\s]', value):
            self._Field__value = value
        else:
            raise ValueError('Name should include only letter characters')

# Class for contact birthday date  allow "YYYY-MM-DD" format
class Birthday(Field):
    @Field.value.setter
    def value(self, value=None):
        if value:
            try:
                self._Field__value = datetime.strptime(value, '%Y-%m-%d').date()
            except Exception:
                raise ValueError("Date should be in the format YYYY-MM-DD")

# Class for contact phone with checking according UA providers
class Phone(Field):
    @Field.value.setter
    def value(self, value):
        phone_pattern_ua = re.compile(r"^0[3456789]\d{8}$")
        if phone_pattern_ua.match(value):
            self._Field__value = value
        else:
            raise ValueError('Phone is not valid')

# Class for contact email, allow format for more common email addresses
class Email(Field):
    @Field.value.setter
    def value(self, value):
        email_pattern = re.compile(
            "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if email_pattern.match(value):
            self._Field__value = value
        else:
            raise ValueError("Email is not valid")

# Class for contact address, allow any string
class Address(Field):
    @Field.value.setter
    def value(self, value):
        self._Field__value = value

# Class for contact notes, any string
class Note(Field):
    @Field.value.setter
    def value(self, value):
        self._Field__value = value

# Class for contacts main information
class Record:
    def __init__(self, name, phone, birthday, email, notes=None, address=None) -> None:
        self.name = Name(name)
        self.birthday = Birthday(birthday)
        self.phone = Phone(phone) if phone else None
        self.phones = [self.phone] if phone else []
        self.email = Email(email)
        self.address = Address(address)
        self.notes = [Note(notes)] if notes else []

# Methods for phone processing
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        if phone not in self.phones:
            self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone = Phone(phone_number)
        for i in self.phones:
            if phone.value == i.value:
                self.phones.remove(i)
                return "phone is removed"

# Methods for email changing
    def edit_email(self, new_email):
        new_email = Email(new_email)
        self.email = new_email
        return f"email:{self.email.value}"

# Methods for notes and tags processing
    def show_notes(self):
        return f'{"; ".join(note.value for note in self.notes) if self.notes else "No notes"}'

    def find_note(self, keyword):
        matching_notes = [note.value for note in self.notes if keyword.lower() in note.value.lower()]
        return matching_notes[0] if matching_notes else "Note not found."
    
    def delete_note(self, keyword):
        for note in self.notes:
            if keyword.lower() in note.value:
                self.notes.remove(note)
                return f"Note was removed"

    def add_note(self, note, tag=None):
        new_note = Note(f"{note} #{tag}" if tag else f'{note}')
        self.notes.append(new_note)
        return f'notes: {"; ".join(note.value for note in self.notes) if self.notes else "N/A"}'

    def edit_note(self, keyword, note, tag=None):
        new_note_obj = Note(f"{note} #{tag}" if tag else f'{note}')
        for i, note in enumerate(self.notes):
            if keyword.lower() in note.value:
                self.notes.pop(i)
                self.notes.insert(i, new_note_obj)
                return f"Note was edited"
        return "Note not found."

    def add_tag(self, keyword, tag):
        for note in self.notes:
            if keyword.lower() in note.value:
                existing_tags = re.findall(r'#(\w+)', note.value)
                existing_tags.append(tag)
                tags = "#".join(existing_tags)
                note.value = f"{note.value.split('#')[0]}#{tags}"
                return f"Tag was added"
        return f"Tag not found"
    
    def remove_tag(self, keyword, tag):
        for note in self.notes:
            if keyword.lower() in note.value:
                existing_tags = re.findall(r'#(\w+)', note.value)
                if tag in existing_tags:
                    existing_tags.remove(tag)
                    tags = "#".join(existing_tags)
                    note.value = f"{note.value.split('#')[0]}#{tags}"
                    return f"Tag was removed from the note"
        return f"Tag not found"
    
    def sort_notes(self):
        sorted_notes = sorted(self.notes, key=lambda note: re.findall(r'#(\w+)', note.value))
        self.notes = sorted_notes
        return sorted_notes
    
# Methods defines days to birthdays of the contact
    def days_to_birthday(self):
        if self.birthday:
            date_now = datetime.now().date()
            user_next_birthday = datetime(
                date_now.year, self.birthday.value.month, self.birthday.value.day).date()
            user_next_year = user_next_birthday.replace(year=date_now.year + 1)
            delta = user_next_birthday - \
                date_now if user_next_birthday >= date_now else user_next_year - date_now
            return delta.days

    def __str__(self) -> str:
        return (
            f"Contact: {self.name.value if self.name else 'N/A'} || "
            f"Phone: {'; '.join(i.value for i in self.phones) if self.phones else 'N/A'} || "
            f"Birthday: {self.birthday.value if self.birthday else 'N/A'} || "
            f"Email: {self.email.value if self.email else 'N/A'} || "
            f"Address: {self.address.value if self.address and self.address.value else 'N/A'} || "
            f"Notes: {'; '.join(note.value for note in self.notes) if self.notes else 'N/A'} || ")

# Class store all contacts and main logic contacts processing
class AddressBook(UserDict):
    def add_record(self, record: Record):  # add record in dictionary
        key = record.name.value
        self.data[key] = record

    def find(self, name):   # get record in dictionary
        return self.data.get(name)

    def delete(self, name):  # delete contact in dictionary
        if name in self.data:
            del self.data[name]
            return f'Record {name} deleted'
        else:
            raise KeyError(f"Contact '{name}' not found.")

    def save_to_file(self, filename):     # serialization data to file
        with open(filename, 'wb') as file_write:
            pickle.dump(self.data, file_write)
            return f'exit'

    def restore_from_file(self, filename):  # deserialization data from file
        with open(filename, 'rb') as file_read:
            self.data = pickle.load(file_read)

    def search(self, query):
        query = query.lower()
        results = []
        for record in self.data.values():
            if (query in record.name.value.lower() or
                any(query in phone.value for phone in record.phones) or
                any(query in note.value.lower() for note in record.notes)):
                results.append(record)
        return results
    
# Methods for user interaction, to retrieve contact record
    def validate_input(self, prompt, validation_func):
        while True:
            user_input = input(prompt)
            try:
                validation_func(user_input)
                return user_input
            except ValueError as e:
                print(f"Error: {e}")

    def get_contact(self):
        name = self.validate_input("Enter name: ", lambda x: Name(x))
        address = self.validate_input("Enter Address: ", lambda x: Address(x))
        phone = self.validate_input("Enter UA mobile phone(10 numbers, start from 0): ", lambda x: Phone(x))
        email = self.validate_input("Enter email: ", lambda x: Email(x))
        birthday = self.validate_input("Enter birthday (YYYY-MM-DD): ", lambda x: Birthday(x))
        note = self.validate_input("Enter note: ", lambda x: Note(x))
        tag = self.validate_input("Input tag message: ", lambda x: Note(x))
        message = f"{note} #{tag}" if tag else f"{note}"
        return Record(name, phone, birthday, email, message, address)

# Method for page view of the contact list
    def __iter__(self) -> Iterator:
        # Iterable class
        return AddressBookIterator(self.data.values(), page_size=2)
# Methods readeble view
    def __repr__(self):
        return f"AddressBook({self.data})"

# Class iterator
class AddressBookIterator:
    def __init__(self, records_list, page_size):
        self.records = list(records_list)
        self.page_size = page_size
        self.counter = 0  # quantity on page
        # use for showing part of the reccords that size < page_size
        self.page = len(self.records) // self.page_size

    def __next__(self):
        if self.counter >= len(self.records):
            raise StopIteration
        else:
            if self.page > 0:
                # slice reccords on the page
                result = list(
                    self.records[self.counter:self.counter + self.page_size])
                self.page -= 1
                self.counter += self.page_size
            else:
                # the rest of the records on the page
                result = list(self.records[self.counter:])
                self.counter = len(self.records)
        return result

# Error handler
def error_handler(func):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # Save to file even in case of an exception
            address_book.save_to_file(filename)
            print(f'Error: {e}')
    return inner
#////////////////start_clean_function////////////////
@error_handler
def clean(folder:Path):
    #normalize
    CYRILLIC_SYMBOLS = 'абвгдеєжзіийклмнопрстуфхцчшщьюяєїґ'
    TRANSLATION = ("a", "b", "v", "h", "d", "e", "ie", "j", "z", "i", "y", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                "f", "kh", "ts", "ch", "sh", "shch", "", "iy", "ia", "e", "yi", "h")
    ACCORD = dict()
    for cyril, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        ACCORD[ord(cyril)] = latin
        ACCORD[ord(cyril.upper())] = latin.capitalize()

    def normalize(name: str) -> str:
        translate_name = re.sub(r'[^\w.]', '_', name.translate(ACCORD))
        return translate_name
    #parser
    JPEG_IMG = []
    JPG_IMG = []
    PNG_IMG = []
    SVG_IMG = []
    #'MP3', 'OGG', 'WAV', 'AMR'
    MP3_AUDIO = []
    OGG_AUDIO = []
    WAV_AUDIO = []
    AMR_AUDIO = []
    #'AVI', 'MP4', 'MOV', 'MKV'
    MP4_VIDEO = []
    AVI_VIDEO = []
    MOV_VIDEO = []
    MKV_VIDEO = []
    #'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX, PY
    DOC_DOC = []
    DOCX_DOC = []
    TXT_DOC = []
    PDF_DOC = []
    XLSX_DOC = []
    PPTX_DOC = []
    PY_DOC = []
    #'ZIP', 'GZ', 'TAR'
    ZIP_ARCH = []
    GZ_ARCH = []
    TAR_ARCH = []
    NOT_DEFINED = []

    REGISTER_EXTENSION = {
        'JPEG': JPEG_IMG,
        'JPG': JPG_IMG,
        'PNG': PNG_IMG,
        'SVG': SVG_IMG,
        'OGG': OGG_AUDIO,
        'WAV': WAV_AUDIO,
        'AMR': AMR_AUDIO,            
        'MP3': MP3_AUDIO,
        'MP4': MP4_VIDEO,
        'AVI': AVI_VIDEO,
        'MOV': MOV_VIDEO,
        'MKV': MKV_VIDEO,
        'DOC': DOC_DOC,
        'DOCX': DOCX_DOC,
        'TXT': TXT_DOC,
        'PDF': PDF_DOC,
        'XLSX': XLSX_DOC,
        'PPTX': PPTX_DOC,
        'PY': PY_DOC,
        'ZIP': ZIP_ARCH,
        'GZ': GZ_ARCH,
        'TAR': TAR_ARCH
    }

    FOLDERS = []
    EXTENSIONS = set()
    UNKNOWN = set()

    def get_extension(name: str) -> str:
        return Path(name).suffix[1:].upper()  
    #folder
    def scan(folder: Path):
        for item in folder.iterdir():
            if item.is_dir(): 
                if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'not_defined'):
                    FOLDERS.append(item)
                    scan(item)
                continue
            extension = get_extension(item.name)  # gex file extention
            full_name = folder / item.name  # full path to file
            if not extension:
                NOT_DEFINED.append(full_name)
            else:
                try:
                    REGISTER_EXTENSION[extension].append(full_name)
                    EXTENSIONS.add(extension)
                except KeyError:
                    UNKNOWN.add(extension) 
                    NOT_DEFINED.append(full_name)

    def handle_media(file_name: Path, target_folder: Path):
        target_folder.mkdir(exist_ok=True, parents=True)
        file_name.replace(target_folder / normalize(file_name.name))

    def handle_archive(file_name: Path, target_folder: Path):
        target_folder.mkdir(exist_ok=True, parents=True)
        folder_for_file = target_folder / normalize(file_name.name.replace(file_name.suffix, ''))
        folder_for_file.mkdir(exist_ok=True, parents=True)
        try:
            shutil.unpack_archive(str(file_name.absolute()), str(folder_for_file.absolute()))
        except shutil.ReadError:
            folder_for_file.rmdir()
            return file_name.unlink()

    def main_cleaner(folder: Path):
        scan(folder)
        for file in JPEG_IMG:
            handle_media(file, folder / 'images' / 'JPEG')
        for file in JPG_IMG:
            handle_media(file, folder / 'images' / 'JPG')
        for file in PNG_IMG:
            handle_media(file, folder / 'images' / 'PNG')
        for file in SVG_IMG:
            handle_media(file, folder / 'images' / 'SVG')

        for file in MP3_AUDIO:
            handle_media(file, folder / 'audio' / 'MP3')
        for file in OGG_AUDIO:
            handle_media(file, folder / 'audio' / 'OGG')
        for file in WAV_AUDIO:
            handle_media(file, folder / 'audio' / 'WAV')  
        for file in AMR_AUDIO:
            handle_media(file, folder / 'audio' / 'AMR')  

        for file in AVI_VIDEO:
            handle_media(file, folder / 'video' / 'AVI')
        for file in MP4_VIDEO:
            handle_media(file, folder / 'video' / 'MP4')
        for file in MOV_VIDEO:
            handle_media(file, folder / 'video' / 'MOV')                                    
        for file in MKV_VIDEO:
            handle_media(file, folder / 'video' / 'MKV')

        for file in DOC_DOC:
            handle_media(file, folder / 'documents' / 'DOC')
        for file in DOCX_DOC:
            handle_media(file, folder / 'documents' / 'DOCX')        
        for file in TXT_DOC:
            handle_media(file, folder / 'documents' / 'TXT')        
        for file in PDF_DOC:
            handle_media(file, folder / 'documents' / 'PDF')        
        for file in XLSX_DOC:
            handle_media(file, folder / 'documents' / 'XLSX') 
        for file in PPTX_DOC:
            handle_media(file, folder / 'documents' / 'PPTX')               
        for file in PY_DOC:
            handle_media(file, folder / 'documents' / 'PY')        

        for file in NOT_DEFINED:
            handle_media(file, folder / 'not_defined')

        for file in ZIP_ARCH:
            handle_archive(file, folder / 'archives' / 'ZIP')
        for file in GZ_ARCH:
            handle_archive(file, folder / 'archives' / 'GZ') 
        for file in TAR_ARCH:
            handle_archive(file, folder / 'archives' / 'TAR')               

        for folder in FOLDERS[::-1]: #delete empty folders
            try:
                folder.rmdir()
            except OSError:
                print(f'Error during remove folder {folder}')
        return REGISTER_EXTENSION, UNKNOWN
       
    if folder:
        folder_path = Path(folder)
        exstention, unknown = main_cleaner(folder_path)
        return  {key: value for key, value in exstention.items() if value}, unknown 
#/////////////End_clean_function/////////////
@error_handler
def main():
    address_book = AddressBook()  # create object
    filename = 'contacts.pkl'
    try:
        if os.path.getsize(filename) > 0:  # check if file of data not empty
            address_book.restore_from_file(filename)
    except Exception:
        f'First run, will be create file'

    for i in track(range(5), description="Loading data..."):
        print(f"loading {i}")
        time.sleep(0.5)
    while True:
        console.print(f'{"-" * 50}Main menu of contacts:{"-" * 53}', style = "row")
        console.print("| 1. Add | 2.All contacts | 3.Edit | 4.Delete | 5.Find | 6.Birthday soon! | 7.Note menu | 8.Sort directory | 9. Save & Exit |", style = "menu")
        console.print(f'{"-" * 125}', style = "row")
        choice = input("Choose an option: ")

        if choice == '1': # add contact 
            address_book.add_record(address_book.get_contact())
            console.print('Contact added successfully', style="success")

        elif choice == '2':  # display all contacts
            for page in address_book:
                for record in page:
                    console.print(record, style ="success")
# //////////////////////////CONTACT EDIT MENU/////////////////////// 
        elif choice == '3': 
            while True:
                console.print(f'{"-" * 30}Contact edit menu:{"-" * 33}', style = "row")
                console.print("| 1.Edit whole contact | 2.Edit email | 3.Add phone | 4.Delete phone | 5.Return |", style = "success")
                console.print(f'{"-" * 81}', style = "row")
                choice = input("Choose an option: ")
               
                if choice == '1':  # Edit whole contact
                    contact = input("Input whose contact to edit: ")
                    record =  address_book.data.get(contact)
                    if record:
                         del address_book.data[contact]
                         new_reccord = address_book.get_contact()
                         address_book.add_record(new_reccord)
                         console.print('Contact modified and saved', style="success")

                elif choice == '2':  # Edit email
                    contact = input("Input whose email to change: ")
                    record = address_book.get(contact)
                    if record:
                        new_email = input("Input new email: ")
                        record.edit_email(new_email)
                        console.print('Email modified and saved', style="success")
                        
                elif choice == '3':  # Add phone 
                    contact = input("Input whose phone add: ")
                    record = address_book.data.get(contact)
                    if record:
                        print(record.phones)                        
                        new_phone = input("Input new phone: ")
                        record.add_phone(new_phone)
                        console.print('Phone saved', style="success")
                
                elif choice == '4':  # Delete phone
                    contact = input("Input whose phone delete: ")
                    record = address_book.data.get(contact)
                    if record:
                        print(record.phones)
                        new_phone = input("Input phone to delete: ")
                        record.remove_phone(new_phone)
                        console.print('Phone was removed', style="success")                    

                elif choice == '5':  # Exit from edit menu and back to contact menu
                    break                
                else:
                    console.print("Invalid choice. Please try again.", style="error")
#///////////////////////////////////////////////////////////////////////
        elif choice == '4':  # Delete contact
            contact_name = input("Enter contact name to delete: ")
            del address_book.data[contact_name]
            console.print('Contact was removed', style="success")  
           
        elif choice == '5':  # Find contact
            query = input("Enter contact name, tag, or phone to find: ")
            results = address_book.search(query)  
            if results:
                for result in results:
                    console.print(result, style="success")
            else:
                console.print("Contact not found.", style="error")

        elif choice == '6':  # display_contacts_n_day_to birthday
            n = int(input("Input quantity days to birthday: "))
            for page in address_book:
                for record in page:
                    m = record.days_to_birthday()
                    if m <= n:
                        console.print(f"To {record.name.value}s birthday {m} days", style='success')
# /////////////////////// NOTES MENU /////////////////////////
        elif choice == '7':
            while True:
                console.print(f'{"-" * 50}Note edit menu:{"-" * 61}', style = "row")
                console.print("| 1.Add note | 2.Show notes | 3.Delete note | 4.Find note | 5.Edit note | 6.Add tag  | 7.Remove tag | 8.Sort note | 9.Return |", style="note")
                console.print(f'{"-" * 126}', style = "row")
                choice = input("Choose an option: ")

                if choice == '1':  # Add note
                    contact = input("Input contact name: ")
                    record = address_book.data.get(contact)
                    if record:
                        note = input("Input note: ")
                        tag = input("Input tag: ")
                        record.add_note(note, tag)
                        console.print('Note was added', style="success")  

                elif choice == '2':  # Show all notes
                    contact = input("Input contact name: ")
                    record = address_book.data.get(contact)
                    if record:
                        console.print(record.show_notes(), style="success")
                   
                elif choice == '3':  # Delete notes
                    contact = input("Input contact name: ")
                    record = address_book.data.get(contact)
                    if record:
                        keyword = input("Input keyword or tag of note for deletion: ")
                        console.print(record.delete_note(keyword), style="success")

                elif choice == '4':  # Find note
                    contact = input("Input contact name: ")
                    record = address_book.data.get(contact)
                    if record:
                        keyword = input("Input keyword or tag for search: ")
                        result = record.find_note(keyword)
                        console.print(result, style="success")                                        

                elif choice == '5':  # Edit note
                    contact = input("Input contact name: ")
                    record = address_book.data.get(contact)
                    if record:
                        keyword = input("Input keyword or tag of note to edit: ")
                        note = input("Input new note: ")
                        tag = input("Input new tag: ")
                        console.print(record.edit_note(keyword, note, tag), style="success") 
                
                elif choice == '6':  # Add tag
                    contact = input("Input contact name: ")
                    keyword = input("Input keyword or tag of note to edit: ")
                    tag = input("Input tag to add: ")
                    record = address_book.data.get(contact)
                    if record:
                        console.print(record.add_tag(keyword, tag), style="success")
                
                elif choice == '7':  # Remove tag
                    contact = input("Input contact name: ")
                    record = address_book.data.get(contact)
                    if record:
                        keyword = input("Input keyword or tag of note to remove tag: ")
                        tag = input("Input tag to remove: ")
                        console.print(record.remove_tag(keyword, tag), style="success")
                
                elif choice == '8':  # Sort notes via tag keyword
                    contact = input("Input contact name: ")
                    record = address_book.data.get(contact)
                    if record:
                        sorted_notes = record.sort_notes()
                        for note in sorted_notes:
                                console.print(note.value, style="success")

                elif choice == '9':  # Exit from note menu and back to contact menu
                    break
                else:
                    console.print("Invalid choice. Please try again.", style="error")
# /////////////////////////// END NOTES MENU//////////////////////////////
        elif choice == '8':  # sort folder  
            folder = input("Enter folder path to sort: ")
            ext_find, unknown = clean(folder)
            exten_list = ', '.join(ext_find.keys())

            console.print(f"Directory was sorted, extensions: {exten_list}, files:", style="note")
            for item in ext_find.items():
                file_name_match = re.search(r'[^\/]+$', str(item))
                file_name = file_name_match.group() if file_name_match else None
                console.print(re.sub(r'\'\)\]\)', '', file_name), style="success")
            console.print(f'{unknown}', style="note")
        
        elif choice == '9':
            address_book.save_to_file(filename)
            console.print(f'Contactbook saved, have a nice day! :D', style="success")
            break

if __name__ == '__main__': 
    main()
    