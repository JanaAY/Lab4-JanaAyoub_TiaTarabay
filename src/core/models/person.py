# models/person.py
from __future__ import annotations

import re


class Person:
    """
    Unified Person base class (Tk + PyQt compatible).

    - Stores name, age, and email (kept in protected attribute `_email`).
    - Validates on construction (age >= 0, simple email regex).
    - Provides both dict APIs:
        * Tk style:    to_dict()      -> includes "type"
        * PyQt style:  create_dict_from_obj()
      And matching constructors:
        * from_dict() and create_obj_from_dict()
    - Keeps `introduce()` and `get_email()` for compatibility.
    - Also exposes a read-only `email` property (backed by `_email`).
    """

    # -------------------- construction & validation --------------------
    def __init__(self, name: str, age: int, email: str) -> None:
        """
        Initialize a Person.

        :param name: Full name.
        :param age: Non-negative age in years.
        :param email: Email address (simple validation).
        :raises ValueError: If age is negative or email is invalid.
        """
        if not self._is_valid_age(age):
            raise ValueError("Invalid age value")

        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")

        self.name = name
        self.age = int(age)
        self._email = email

    # -------------------- helpers / compatibility ---------------------
    @property
    def email(self) -> str:
        """Read-only public view of the email (backed by `_email`)."""
        return self._email

    def get_email(self) -> str:
        """PyQt-style accessor retained for compatibility."""
        return self._email

    def introduce(self) -> None:
        """Print a short self-introduction (PyQt-style text retained)."""
        print(
            f"Hey, this is {self.name}, I am {self.age} years old. \n"
            f"You can reach out to me on my email: {self._email}."
        )

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        Lightweight check for 'local@domain.tld' pattern (not full RFC).
        """
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    @staticmethod
    def _is_valid_age(age: int) -> bool:
        """Age must be a non-negative integer."""
        try:
            return int(age) >= 0
        except Exception:
            return False

    # -------------------- serialization (both styles) ------------------
    def to_dict(self) -> dict:
        """
        Tk-style export. Includes a 'type' tag.

        Returns:
            {
              "name": str, "age": int, "email": str, "type": "<ClassName>"
            }
        """
        return {
            "name": self.name,
            "age": self.age,
            "email": self._email,
            "type": self.__class__.__name__,
        }

    # PyQt-compatible alias (without the "type" field)
    def create_dict_from_obj(self) -> dict:
        """
        PyQt-style export (just name/age/email).
        """
        return {"name": self.name, "age": self.age, "email": self._email}

    @classmethod
    def from_dict(cls, data: dict) -> "Person":
        """
        Tk-style constructor from dict (ignores 'type' if present).
        Expects: name, age, email.
        """
        return cls(data["name"], int(data["age"]), data["email"])

    # PyQt-compatible alias
    @classmethod
    def create_obj_from_dict(cls, data: dict) -> "Person":
        """PyQt-style constructor from dict (alias to from_dict)."""
        return cls.from_dict(data)
