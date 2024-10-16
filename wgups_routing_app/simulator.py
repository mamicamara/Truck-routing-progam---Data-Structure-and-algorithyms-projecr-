import csv

from graph import Graph
from models.truck import Truck
from models.location import Location
from models.package import Package
from hashtable import HashTable


class Simulator:

    def __init__(self):
        self._trucks = None
        self._packages = None
        self._packages_with_wrong_address = None
        self._graph = None

    def get_remaining(self):
        """ Return the number of undelivered packages """
        total = 0
        for p in self._packages:
            if not p[1].isdelivered():
                total += 1
        return total

    def run(self, num_trucks) -> None:
        """
        Determines how to deliver packages efficiently.

        Either space or time complexity for this algorithm is O(m^2) + O(n),
        where m and n represent number of delivery locations and number of packages
        respectively.
        """

        destinations = self._load_packages()
        self._load_distances()
        self._trucks = [Truck() for i in range(num_trucks)]

        urgent_packages = True

        while urgent_packages:
            self._deliver_urgent_packages(destinations)

            urgent_packages = any([not truck.isempty() for truck in self._trucks])
            if urgent_packages:
                self._transport_packages()

        num_remaining_packages = self.get_remaining()

        while num_remaining_packages != 0:
            num_remaining_packages -= self._transport_packages()

    def _load_distances(self) -> None:
        """
        Loads the hubs' name+address, address+zip, and distances from the data/wgups_distance_table.csv
        csv file into a list of Location objects. The address plus zip code in the second
        column of the file is used as the identifier for every location and will be used for
        retrieving a Location object in the graph.

        Either space or time complexity is O(n^2) as it is for a nested loop.
        """

        self._graph = Graph()
        with open('data/wgups_distance_table.csv') as dists_file:
            locations = []
            reader = csv.reader(dists_file, delimiter=',', quotechar='"')
            for name_address, address_zip, *distances in reader:
                location = Location(address_zip, name_address)
                locations.append(location)
                self._graph.add_vertex(location)
                for (idx, distance) in enumerate(distances):
                    self._graph.add_edge(location, locations[idx], float(distance))

    def _load_packages(self) -> HashTable:
        """
        Loads information about the packages from 'data/wgups_packages.csv' as Package
        objects into a list and into a hashtable. The hashtable groups packages according
        to their destination addresses.

        Either space or time complexity is O(n)
        """
        self._packages = HashTable()
        destinations = HashTable()
        associated_packages = HashTable()

        with open('data/wgups_packages.csv') as pkgs_file:
            reader = csv.reader(pkgs_file, delimiter=',')

            for line in reader:
                package = Package(*line)

                self._packages.put(package.get_id_no(), package)

                dest_packages = destinations.get(package.get_address())

                if (dest_packages) is None:
                    dest_packages = []
                    destinations.put(package.get_address(), dest_packages)

                dest_packages.append(package)

                for associated in package.get_associated_packages():
                    assoc_set = associated_packages.get(associated)
                    if assoc_set is None:
                        assoc_set = set()
                        associated_packages.put(associated, assoc_set)
                    assoc_set.add(package)

                for pkg in associated_packages.get(package.get_id_no()) or []:
                    pkg.associated.add(package)
                    package.associated.add(pkg)

        return destinations

    def _package_nearest_to_location(self, packages, location) -> Package:
        """
        Returns the package that is nearest to the given location.

        Time complexity is O(n) while space complexity is O(1).
        """
        min_distance = float('inf')

        nearest_package = None
        for package in packages:
            distance = self._graph.get_distance(package.get_address(), location)
            if distance < min_distance:
                min_distance = distance
                nearest_package = package

        return nearest_package

    def _deliver_urgent_packages(self, destinations):
        """
        Delivers urgent packages to their given destinations. Either time or space complexity is O(n)
        """
        urgent_packages = set()

        for p in self._packages:
            if any([p[1].is_urgent(t.get_time()) and p[1].is_available(t) for t in self._trucks]):
                urgent_packages.add(p[1])

        # Sort the list of trucks according to their mileage so that
        # the trucks with the least mileage are loaded first.

        self._trucks.sort(key=lambda truck: truck.get_mileage())

        for truck in self._trucks:

            # Load packages into the truck until it's full or there are no more packages.
            while not truck.isfull() and len(urgent_packages) != 0:

                nearest_package = self._package_nearest_to_location(urgent_packages, truck.location())

                # Determine all packages associated to the nearest package.
                associated_pkgs = nearest_package.associated
                for assoc_pkg in associated_pkgs:
                    associated_pkgs = associated_pkgs.union(assoc_pkg.associated)
                associated_pkgs.add(nearest_package)

                # Load truck only if it has enough space for a package (including its associated packages).
                if truck.available_space() >= len(associated_pkgs):
                    while len(associated_pkgs) != 0:

                        # Note the main package that is nearest to the associated packages.
                        pkg = self._package_nearest_to_location(associated_pkgs, truck.location())
                        associated_pkgs.discard(pkg)

                        # ignore those that have been processed.
                        if not pkg.at_the_hub():
                            continue

                        # Load the package into the truck and erase it from the urgent list.
                        urgent_packages.discard(pkg)
                        truck.load(pkg)

                        # Load other packages destined to same location as the one loaded earlier.
                        for p in (destinations.get(pkg.get_address()) or []):
                            if not truck.isfull() and p.is_available(truck):
                                urgent_packages.discard(p)
                                truck.load(p)

    def _transport_packages(self) -> int:
        """
        Takes the packages to their destination. Either the time complexity or space complexity is O(n)
        """
        remaining_packages = []
        for p in self._packages:
            if p[1].at_the_hub():
                remaining_packages.append(p[1])

        # If possible, share the packages among the trucks so that
        # the trucks use the least mileage possible.

        total = float('inf')
        while total > 2:
            total = 0
            for truck in self._trucks:
                if truck.isfull():
                    continue
                shortest = float('inf')
                nearest_package = None
                for p in remaining_packages:
                    if p.is_available(truck):
                        total += 1
                        distance = self._graph.get_distance(
                            truck.location(), p.get_address())
                        if distance < shortest:
                            shortest = distance
                            nearest_package = p

                if nearest_package is not None:
                    truck.load(nearest_package)

        # First update invalid addresses when the correct one is availed, and then
        # loops through all trucks in the trucks list to deliver packages.

        if self._packages_with_wrong_address is None:
            self._packages_with_wrong_address = []
            for p in self._packages:
                if p[1]._wrong_address:
                    self._packages_with_wrong_address.append(p[1])

        packages_sent = 0

        for truck in self._trucks:
            packages_sent += len(truck.get_packages())
            truck.deliver(self._graph)

            if len(self._packages_with_wrong_address) != 0:
                for p in self._packages_with_wrong_address:
                    if p.correct_address_available(truck.get_time()):
                        p.update_address()
                        self._packages_with_wrong_address.remove(p)

        return packages_sent

    def get_trucks(self) -> [Truck]:
        """ Returns the trucks - a Hashtable """
        return self._trucks

    def get_packages(self) -> HashTable:
        """ Returns the packages - a Hashtable """
        return self._packages
