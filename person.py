"""Person base class module.

This module defines the :class:`Person` class, a base class representing
an individual in the school management system. It includes validation
of email addresses, safe initialization of attributes, and helper
methods for serialization and deserialization.

All docstrings follow the Sphinx/Napoleon style for compatibility with
autodoc and napoleon extensions.
"""

import re


class Person:
    """Base class representing a person in the school management system.

    Attributes
    ----------
    name : str
        Full name of the person.
    age : int
        Age of the person (must be >= 0).
    _email : str
        Email address of the person (validated during construction).
    """

    def __init__(self, name: str, age: int, email: str):
        """Initialize a Person object.

        :param name: Person's name.
        :type name: str
        :param age: Person's age (must be non-negative).
        :type age: int
        :param email: Person's email (must match a valid email format).
        :type email: str
        :raises ValueError: If ``age`` is negative or if ``email`` is invalid.
        """
        if age < 0:
            raise ValueError("Invalid age value")

        email_format = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_format, email):
            raise ValueError("Invalid email format")

        self.name = name
        self.age = age
        self._email = email

    def get_email(self) -> str:
        """Return the person's email address.

        :return: Email address of the person.
        :rtype: str
        """
        return self._email

    def introduce(self) -> None:
        """Print a short introduction message for the person.

        Example
        -------
        >>> p = Person("Ali", 20, "ali@example.com")
        >>> p.introduce()
        Hey, this is Ali, I am 20 years old.
        You can reach out to me on my email: ali@example.com.

        :return: ``None``
        :rtype: None
        """
        print(
            f"Hey, this is {self.name}, I am {self.age} years old. \n"
            f"You can reach out to me on my email: {self._email}."
        )

    def create_dict_from_obj(self) -> dict:
        """Convert this Person instance into a dictionary.

        :return: Dictionary with keys ``name``, ``age``, and ``email``.
        :rtype: dict[str, str | int]
        """
        return {"name": self.name, "age": self.age, "email": self._email}

    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Person":
        """Create a Person object from a dictionary.

        :param data: Dictionary with keys ``name``, ``age``, and ``email``.
        :type data: dict
        :return: A new Person instance created from the dictionary.
        :rtype: Person
        """
        return cls(data["name"], data["age"], data["email"])
