from common import timeFromMinutes

class Truck:
    _max_capacity = 16
    _speed = 18
    _count = 0

    def __init__(self):
        self._id = self._increment_count()
        self._packages = []
        self._mileage = 0.0
        self._packages = []
        self._delivered = 0

    def get_id(self):
        return self._id

    def get_mileage(self):
        return self._mileage

    def get_delivered(self):
        return self._delivered
    
    def get_packages(self):
        return self._packages

    def get_time(self) -> float:
        return (8 * 60) + (self._mileage / self._speed * 60)

    def available_space(self) -> int:
        return self._max_capacity - len(self._packages)
    
    def deliver(self, graph) -> None:
        """
        Takes all packages in this truck to their destinations.
        """
        self._delivered += 1
        prev = ''
        curr = 'HUB'
        for pkg in self._packages:
            prev = curr 
            curr  = pkg.get_address()
            self._mileage += graph.get_distance(prev, curr )
            pkg.complete_delivery(self)

            info = f'truck {self._id}'
            info += f' delivered {pkg.get_id_no()},'
            info += f' time: {timeFromMinutes(pkg.get_delivered_at())}'
            info += f' address: {pkg.get_address()}'
            info += f' mileage: {round(self._mileage, 1)} miles'

        self._packages.clear()
        self._mileage += graph.get_distance(curr , 'HUB')      

    def isempty(self) -> bool:
        return len(self._packages) == 0
    
    def isfull(self) -> bool:
        return len(self._packages) == 16

    def load(self, package) -> None:
        if self.isfull():
            raise Exception

        package.set_enroute(self)
        self._packages.append(package)

    def location(self) -> str:
        return 'HUB' if self.isempty() else self._packages[-1].get_address()

    @staticmethod
    def _increment_count() -> int:
        Truck._count += 1
        return Truck._count