from common import standardize_address

class Location:
    """ A class to represent a delivery location """
    def __init__(self, address_zip,  name_address) -> None:
        """ Creates an instance of this location with given parameters """
        self.address_zip = standardize_address(address_zip)
        self.name = name_address

    def __eq__(self, other) -> bool:
        """ Overrides the equals function so as to check equlity based
        on the hash of this Location. """
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        """ Overrides the hash method so as to calculate the hash value
         based on this Location's address+zip. Used internally by the __eq__
         method."""
        return hash(self.address_zip)

    def __repr__(self) -> str:
        """ Overrides this base repr method so as to return this Location's
         address+zip as its string representation """
        return self.address_zip


    def __str__(self) -> str:
        """ Overrides this base str method so as to return this Location's
         address+zip as its string representation """
        return self.address_zip
    
    def get_address(self) -> str:
        """ Returns the address of this locations represented as address+zip """
        return self.address_zip

