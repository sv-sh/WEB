from fields_part import Name, Birthday, Phone, Email, Address, Note
from datetime import datetime
import re
from abc import abstractmethod, ABC

class ReccordAbstraction(ABC):
    @abstractmethod
    def __init__(self, name, phone, birthday, email, notes=None, address=None) -> None:
        self.name = Name(name)
        self.birthday = Birthday(birthday)
        self.phone = Phone(phone) if phone else None
        self.phones = [self.phone] if phone else []
        self.email = Email(email)
        self.address = Address(address)
        self.notes = [Note(notes)] if notes else []
    
    @abstractmethod
    def add_phone(self, phone_number):
        pass
    @abstractmethod
    def remove_phone(self, phone_number):
        pass
    @abstractmethod
    def edit_email(self, new_email):
        pass
    @abstractmethod
    def show_notes(self):
        pass
    @abstractmethod
    def find_note(self, keyword):
        pass
    @abstractmethod
    def delete_note(self, keyword):
        pass
    @abstractmethod
    def add_note(self, note):
        pass
    @abstractmethod
    def edit_note(self, keyword, note, tag=None):
        pass
    @abstractmethod
    def add_tag(self, keyword, tag):
        pass
    @abstractmethod
    def remove_tag(self, keyword, tag):
        pass
    @abstractmethod
    def sort_notes(self):
        pass
    @abstractmethod
    def days_to_birthday(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

class Record(ReccordAbstraction):
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