import re
from enum import Enum, auto
from common import timeFromMinutes, standardize_address, EOD

class PackageStatus(Enum):
    AT_THE_HUB = auto()
    EN_ROUTE = auto()
    DELIVERED = auto()

class Package:

    def __init__(self, id_no, address, city, state, zip, deadline, mass, notes):
        self._id_no = int(id_no)
        self.address = address
        self.city = city
        self.state = state
        self._zip = zip
        self.mass = int(mass)
        self._status = PackageStatus.AT_THE_HUB
        self._wrong_address = False
        self._required_truck = None
        self._loaded_at = None
        self._delivered_by = None
        self._delivered_at = None
        self._available_at = 0.0
        self._delivery_number = 0
        self._associated_packages = set()
        self.associated = set()
        self.deadline = self.minutesFromString(deadline)
        self.address_zip = standardize_address(f'{self.address} ({self._zip})')
        self._retrieve_note(notes)

    
    def get_delivered_at(self):
        return self._delivered_at
    
    def get_associated_packages(self):
        return self._associated_packages


    def is_urgent(self, time: float) -> bool:
        return self.at_the_hub() and self.deadline < EOD and self._available_at <= time

    def is_available(self, truck, exclude: set = set()) -> bool:
        """
        Determines if this package (and recursively its associated ones) is
        available for delivery by the current truck
        """
        if self._wrong_address:
            return False

        if self._available_at > truck.get_time():
            return False

        if not self.at_the_hub():
            return False

        if self._required_truck is not None and self._required_truck != truck.get_id():
            return False

        deps_available = True
        exclude.add(self)
        for deps in [d for d in self.associated if not d in exclude]:
            deps_available = deps.is_available(truck, exclude)

        return deps_available

    def _retrieve_note(self, notes: str) -> None:
        """
        """
        if len(notes) == 0:
            pass
        elif match := re.search(r'\d?\d:\d\d [ap]m', notes):
            self._available_at = self.minutesFromString(match.group(0))
        elif match := re.search(r'truck (\d)', notes):
            self._required_truck = int(match.group(1))
        elif 'delivered with' in notes:
            self._associated_packages = set[int](
                map(int, re.findall(r'\d+', notes)))
        else:
            self.address_zip = ''
            self._available_at = self.minutesFromString('10:20 am')
            self._wrong_address = True

    def set_enroute(self, truck) -> None:
        if self._status == PackageStatus.EN_ROUTE:
            raise Exception
        
        if (self._required_truck or truck.get_id()) != truck.get_id():
            raise Exception
        
        self._delivered_by = truck.get_id()
        self._loaded_at = truck.get_time()
        self._status = PackageStatus.EN_ROUTE

    def complete_delivery(self, truck) -> None:
        if self._status == PackageStatus.DELIVERED:
            raise Exception
        self._status = PackageStatus.DELIVERED
        self._delivered_at = truck.get_time()
        self._delivery_number = truck.get_delivered()

    def isdelivered(self) -> bool:
        return self._status == PackageStatus.DELIVERED

    def at_the_hub(self) -> bool:
        return self._status == PackageStatus.AT_THE_HUB

    def correct_address_available(self, time: float):
        return self._wrong_address and self._available_at <= time

    def update_address(self):
        self._wrong_address = False
        self.address_zip = '410 S State St (84111)'
        self.address = '410 S State St'
        self._zip = '84111'

    def get_status(self, time) -> str:
        if self._available_at > time:
            return f'Delayed, package available at {timeFromMinutes(self._available_at)}'

        loaded_at = self._loaded_at
        if time < loaded_at:
            return f'At the hub, expected load time {timeFromMinutes(loaded_at)}'

        _delivered_at = self._delivered_at
        delivered_by = self._delivered_by
        if time < _delivered_at:
            return f'On truck {delivered_by}, loaded at {timeFromMinutes(loaded_at)}, expected delivery time {timeFromMinutes(_delivered_at)} '

        return f'Delivered at {timeFromMinutes(_delivered_at)} by truck {delivered_by}'

    def human_deadline(self) -> str:
        """
        Formats the deadline in a human-friendly format
        """
        if self.deadline == EOD:
            return 'EOD'

        return timeFromMinutes(self.deadline)

    def brief(self, time: int) -> str:
        brief = [f'id: {self._id_no}', f'address: {self.address_zip}']

        if (self._delivered_at or float('inf')) <= time:
            brief.append(PackageStatus.DELIVERED.name)
        elif (self._loaded_at or float('inf')) <= time:
            brief.append(PackageStatus.EN_ROUTE.name)
        else:
            brief.append(PackageStatus.AT_THE_HUB.name)

        brief.append(f'deadline: {self.human_deadline()}')

        if (self._loaded_at or float('inf')) <= time:
            brief.append(
                f'loaded at: {timeFromMinutes(self._loaded_at)}')
            brief.append(
                f'onto truck {self._delivered_by} in delivery number {self._delivery_number}')

        if (self._delivered_at or float('inf')) <= time:
            brief.append(
                f'delivered at: {timeFromMinutes(self._delivered_at)}')
            on_time = self._delivered_at < self.deadline 
            
            brief.append(f'delivered on time: {str(on_time)}')

        return str.join(',\t', brief)

    def __hash__(self) -> int:
        return hash(self._id_no)

    def get_id_no(self):
        return self._id_no

    def get_address(self):
        return self.address_zip


    def __str__(self) -> str:
        deadline = timeFromMinutes(self.deadline)
        
        brief = [f'id: {self._id_no}', f'address: {self.address_zip}',
                f'status: {self._status}', f'deadline: {deadline}']
        
        if self._delivered_at is not None:
            brief.append(
                f'delivered at: {timeFromMinutes(self._delivered_at)}')
            on_time = self._delivered_at < self.deadline

            brief.append(f'delivered on time: {on_time}')

        return str.join(', ', brief)
    
    def to_block_str(self, time: int) -> str:
        pkg_str = f'Package ID: #{self.get_id_no()}\n';
        pkg_str += f' delivery status:   {self.get_status(time)}\n';
        pkg_str += f' delivery deadline: {self.human_deadline()}\n';
        pkg_str += f' delivery weight:   {self.mass}\n';
        pkg_str += f' delivery address:  {self.address}\n';
        pkg_str += f' delivery city:     {self.city}\n';
        pkg_str += f' delivery state:    {self.state}\n';
        pkg_str += f' delivery zip:      {self._zip}\n';
        return pkg_str

    @staticmethod
    def minutesFromString(time_str) -> int:
        if time_str == 'EOD':
            return EOD
        
        match = re.search(r'(\d?\d):(\d\d) ([ap]m)', time_str, re.I)
        
        hrs, mins, ampm = match.groups()
        
        offset = 12 if ampm.lower() == 'pm' else 0

        return int(mins) + ((int(hrs) + offset) * 60)
