
from datetime import datetime
from abc import abstractmethod, ABC
import re

# Abstraction for user classes
class UserClassAbstraction(ABC):
    @abstractmethod
    def __init__(self, value=None):
        self.value = value
    @abstractmethod
    def value(self):
        pass
    @abstractmethod
    def value(self, value):
        pass
    @abstractmethod
    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


# Parrent class for all fields
class Field(UserClassAbstraction):
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




