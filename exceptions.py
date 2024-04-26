"""A module to define Custom Exceptions."""


class LATimesException(Exception):
    """Super Class for LA Times related Exceptions."""

    def __init__(self, message="An exception occurred in LATimes related process"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class NoResultsException(LATimesException):
    """Exception for No Results in Search Process."""

    def __init__(self, phrase):
        self.phrase = phrase
        self.message = f"No results found for the search phrase: '{self.phrase}'"
        super().__init__(self.message)