from record_part import Record
from fields_part import Name, Birthday, Phone, Email, Address, Note
from _collections_abc import Iterator
from collections import UserDict
import pickle


# Class store all contacts and main logic contacts processing
class AddressBook(UserDict):
    # ID = 1
    def add_record(self, record: Record):  # add record in dictionary
        key = record.name.value
        # key = self.ID
        # self.ID += 1
        self.data[key] = record
        # print(f"{key}.{self.data[key]}")
        return f"Contact {record.name.value} added"
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

if __name__ == '__main__':    
    record = Record("Jon Dou", "0971231232", "1990-09-09", "qwqwq@gmail.com", "wdqdqddqdw", "Ukraine, CH")
    print(record)
    adressbook = AddressBook()
    print(adressbook.add_record(record))