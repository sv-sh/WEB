
from cleaner import clean
from address_book_part import AddressBook
import os
import re
import time
from rich import print
from rich.console import Console
from rich.theme import Theme
from rich.progress import track
from abc import abstractmethod, ABC

custom_theme = Theme(
    {"success": "bold green", "error": "bold red", "warning": "bold yellow", "menu": "yellow", "row":"bright_blue", "note":"bold magenta"})
console = Console(theme=custom_theme)

# Error handler
def error_handler(func):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # Save to file even in case of an exception
            # address_book.save_to_file(filename)
            print(f'Error: {e}')
    return inner

#/////////////////////////User Interface abstraction/////////////////////////////
class UserInterfaceAbstraction(ABC):
    @abstractmethod
    def show_main_menu(self):
        pass
    @abstractmethod
    def show_edit_menu(self):
        pass
    @abstractmethod
    def show_note_menu(self):
        pass
    @abstractmethod
    def run(self):
        pass

class BotUserInterface(UserInterfaceAbstraction):
    def __init__(self, address_book) -> None:
        self.address_book = address_book
    
    def show_main_menu(self):
        console.print(f'{"-" * 50}Main menu of contacts:{"-" * 53}', style = "row")
        console.print("| 1. Add | 2.All contacts | 3.Edit | 4.Delete | 5.Find | 6.Birthday soon! | 7.Note menu | 8.Sort directory | 9. Save & Exit |", style = "menu")
        console.print(f'{"-" * 125}', style = "row")
    
    def show_edit_menu(self):
        console.print(f'{"-" * 30}Contact edit menu:{"-" * 33}', style = "row")
        console.print("| 1.Edit whole contact | 2.Edit email | 3.Add phone | 4.Delete phone | 5.Return |", style = "success")
        console.print(f'{"-" * 81}', style = "row")
        
    def show_note_menu(self):
        console.print(f'{"-" * 50}Note edit menu:{"-" * 61}', style = "row")
        console.print("| 1.Add note | 2.Show notes | 3.Delete note | 4.Find note | 5.Edit note | 6.Add tag  | 7.Remove tag | 8.Sort note | 9.Return |", style="note")
        console.print(f'{"-" * 126}', style = "row")
    @error_handler
    def run(self):
        while True:
            self.show_main_menu()
            choice = input("Choose an option: ")
            if choice == '1': # add contact 
                self.address_book.add_record(self.address_book.get_contact())
                console.print('Contact added successfully', style="success")

            elif choice == '2':  # display all contacts
                for page in self.address_book:
                    for record in page:
                        console.print(record, style ="success")
# //////////////////////////CONTACT EDIT MENU///////////////////////           
            elif choice == '3': 
                while True:
                    self.show_edit_menu()
                    choice = input("Choose an option: ")
                    if choice == '1':  # Edit whole contact
                        contact = input("Input whose contact to edit: ")
                        record =  self.address_book.data.get(contact)
                        if record:
                            del self.address_book.data[contact]
                            new_reccord = self.address_book.get_contact()
                            self.address_book.add_record(new_reccord)
                            console.print('Contact modified and saved', style="success")

                    elif choice == '2':  # Edit email
                        contact = input("Input whose email to change: ")
                        record = self.address_book.get(contact)
                        if record:
                            new_email = input("Input new email: ")
                            record.edit_email(new_email)
                            console.print('Email modified and saved', style="success")
                            
                    elif choice == '3':  # Add phone 
                        contact = input("Input whose phone add: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            print(record.phones)                        
                            new_phone = input("Input new phone: ")
                            record.add_phone(new_phone)
                            console.print('Phone saved', style="success")
                    
                    elif choice == '4':  # Delete phone
                        contact = input("Input whose phone delete: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            print(record.phones)
                            new_phone = input("Input phone to delete: ")
                            record.remove_phone(new_phone)
                            console.print('Phone was removed', style="success")                    

                    elif choice == '5':  # Exit from edit menu and back to contact menu
                        self.address_book.save_to_file(filename)
                        break                
                    else:
                        console.print("Invalid choice. Please try again.", style="error")
#/////////////////////////////////////////////////////////////////////// 
            elif choice == '4':  # Delete contact
                contact_name = input("Enter contact name to delete: ")
                del self.address_book.data[contact_name]
                console.print('Contact was removed', style="success")
            
            elif choice == '5':  # Find contact
                query = input("Enter contact name, tag, or phone to find: ")
                results = self.address_book.search(query)  
                if results:
                    for result in results:
                        console.print(result, style="success")
                else:
                    console.print("Contact not found.", style="error")

            elif choice == '6':  # display_contacts_n_day_to birthday
                n = int(input("Input quantity days to birthday: "))
                for page in self.address_book:
                    for record in page:
                        m = record.days_to_birthday()
                        if m <= n:
                            console.print(f"To {record.name.value}s birthday {m} days", style='success')
# /////////////////////// NOTES MENU /////////////////////////                            
            elif choice == '7':
                while True:
                    self.show_note_menu()
                    choice = input("Choose an option: ")
                    if choice == '1':  # Add note
                        contact = input("Input contact name: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            note = input("Input note: ")
                            tag = input("Input tag: ")
                            record.add_note(note, tag)
                            console.print('Note was added', style="success")  

                    elif choice == '2':  # Show all notes
                        contact = input("Input contact name: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            console.print(record.show_notes(), style="success")
                    
                    elif choice == '3':  # Delete notes
                        contact = input("Input contact name: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            keyword = input("Input keyword or tag of note for deletion: ")
                            console.print(record.delete_note(keyword), style="success")

                    elif choice == '4':  # Find note
                        contact = input("Input contact name: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            keyword = input("Input keyword or tag for search: ")
                            result = record.find_note(keyword)
                            console.print(result, style="success")                                        

                    elif choice == '5':  # Edit note
                        contact = input("Input contact name: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            keyword = input("Input keyword or tag of note to edit: ")
                            note = input("Input new note: ")
                            tag = input("Input new tag: ")
                            console.print(record.edit_note(keyword, note, tag), style="success") 
                    
                    elif choice == '6':  # Add tag
                        contact = input("Input contact name: ")
                        keyword = input("Input keyword or tag of note to edit: ")
                        tag = input("Input tag to add: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            console.print(record.add_tag(keyword, tag), style="success")
                    
                    elif choice == '7':  # Remove tag
                        contact = input("Input contact name: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            keyword = input("Input keyword or tag of note to remove tag: ")
                            tag = input("Input tag to remove: ")
                            console.print(record.remove_tag(keyword, tag), style="success")
                    
                    elif choice == '8':  # Sort notes via tag keyword
                        contact = input("Input contact name: ")
                        record = self.address_book.data.get(contact)
                        if record:
                            sorted_notes = record.sort_notes()
                            for note in sorted_notes:
                                    console.print(note.value, style="success")

                    elif choice == '9':  # Exit from note menu and back to contact menu
                        self.address_book.save_to_file(filename)
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
                self.address_book.save_to_file(filename)
                console.print(f'Contactbook saved, have a nice day! :D', style="success")
                break                           


if __name__=="__main__":
    address_book = AddressBook()  # create object
    filename = 'contacts.pkl'
    try:
        if os.path.getsize(filename) > 0:  # check if file of data not empty
            address_book.restore_from_file(filename)
    except Exception:
        f'First run, will be create file'

    for i in track(range(3), description="Loading data..."):
        print(f"loading {i}")
        time.sleep(0.5)
ui= BotUserInterface(address_book)
ui.run()





