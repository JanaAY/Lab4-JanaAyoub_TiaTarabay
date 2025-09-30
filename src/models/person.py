from __future__ import annotations

import re


class Person:
    """
    Base domain entity representing a person.

    Stores a name, a non-negative integer age, and an email address
    (kept in the protected attribute ``_email``).

    :ivar name: Full name
    :vartype name: str
    :ivar age: Non-negative age in years
    :vartype age: int
    :ivar _email: Contact email address (protected attribute)
    :vartype _email: str
    """

    def __init__(self, name: str, age: int, email: str) -> None:
        """
        Construct a :class:`Person`.

        Note: Validation helpers (:meth:`_is_valid_email`, :meth:`_is_valid_age`)
        exist but are not enforced here; callers should validate before constructing
        or use higher-level factories.

        :param name: Full name
        :type name: str
        :param age: Non-negative age in years
        :type age: int
        :param email: Contact email address
        :type email: str
        """
        self.name = name
        self.age = age
        self._email = email

    def introduce(self) -> None:
        """
        Print a short self-introduction to stdout.

        :return: None
        :rtype: None
        """
        print(f"Hi, I'm {self.name}, I'm {self.age}. Reach me at {self._email}.")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        Check whether an email string loosely matches ``local@domain.tld``.

        This is a lightweight regex and not a full RFC-5322 validator.

        :param email: Email to validate
        :type email: str
        :return: ``True`` if email matches the simple pattern, else ``False``
        :rtype: bool
        """
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    @staticmethod
    def _is_valid_age(age: int) -> bool:
        """
        Check whether an age is a non-negative integer.

        :param age: Age in years
        :type age: int
        :return: ``True`` if valid, else ``False``
        :rtype: bool
        """
        return isinstance(age, int) and age >= 0

    def to_dict(self) -> dict:
        """
        Serialize the person to a JSON-ready dictionary.

        The mapping includes ``name``, ``age``, ``email`` (from ``_email``),
        and a ``type`` tag with the concrete class name.

        :return: JSON-ready mapping for this person
        :rtype: dict
        """
        return {
            "name": self.name,
            "age": self.age,
            "email": self._email,
            "type": self.__class__.__name__,
        }
