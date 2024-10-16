# ************************************************************* #
#  A program for determining an efficient route and             #
#  delivery distribution for the Daily Local Deliveries (DLD)   #
#  of Western Governors University Parcel Services (WGUPS).     #
#                                                               #
#  First name: CAMARA                                           #
#  Last name:  MAMI                                             #
#  Student ID:
# ************************************************************* #

import sys
from simulator import Simulator
from models.truck import Truck


def menu():
    print('''
    What would you like to do?
        1. View a package by ID and Time.
        2. View all packages by time (block).
        3. View all packages by time (inline).
        4. View trucks' total mileage.
        5. Exit.
    ''')


def input_id_no(packages) -> int:
    """
    Prompts user for input and returns it as integer if its a valid integer.
    """
    while True:
        user_input = input('Enter package ID number: ')
        if user_input.isdigit():
            num = int(user_input)
            if num in packages:
                return num, False

            print(f'Package #"{num}" does not exist')
        else:
            user_input = input("Enter 1 to continue, 0 to exit")
            if user_input == '0':
                return 0, True


def input_time() -> int:
    """ Promps user for input, parses the time and returns it as total minutes """
    done = False
    total_minutes = -1
    while not done:
        try:
            user_input = input('Enter time (HH:MM): ')
            hrs, mins = map(int, user_input.split(':'))

            if hrs < 0 or hrs > 23 or mins < 0 or mins > 59:
                option = input('  invalid time: enter 0 to cancel re-entry, any to continue: ')
                done = option == '0'
            else:
                total_minutes = mins + (hrs * 60)
                done = True
        except Exception:
            option = input(' invalid time: enter 0 to cancel re-entry, any to continue: ')
            done = option == '0'

    return total_minutes


def print_package(time, package) -> None:
    """ Displays information of the given package.  """
    print()
    print(package.to_block_str(time))
    print()


def print_one_package(packages, time):
    """ Prints information of one package using the given time and package ID"""
    id_no, done = input_id_no(packages)
    if done: return
    print_package(time, packages.get(id_no))


def print_all_packages_block(packages, time):
    """ Prints information of all packages at the specified time in blocks """

    for (_, package) in packages:
        print_package(time, package)


def print_all_packages_inline(packages, time):
    """ Prints information of all packages at the specified time inline """

    package_list = [package for (_, package) in packages]
    package_list.sort(key=lambda p: p.get_id_no())
    for package in package_list:
        print(package.brief(time))


def print_trucks_mileage(trucks):
    """ Prints the truck's mileage information """

    print("Trucks mileage (in miles):")

    for truck in trucks:
        print(f'  Truck #{truck.get_id()}: {round(truck.get_mileage(), 1)}')


def main():
    """
    Run the simulation and displays the resulting information requested by the user.
    """

    print('Western Governors University Parcel Services (WGUPS))\n'
          '  Delivery distribution and routing informer\n'
          '----------------------------------------------------')

    # Run the simulation
    simulator = Simulator()
    simulator.run(2)

    # Retrieve information about the packages.
    packages = simulator.get_packages()

    # Retrieve mileage information of the trucks.
    trucks = simulator.get_trucks()

    done = False
    while not done:
        menu()
        option = input("Enter: ")

        if option in ['1', '2', '3']:
            time = input_time()

            if time < 0:
                continue

            if option == '1':
                print_one_package(packages, time)
            elif option == '2':
                print_all_packages_block(packages, time)
            elif option == '3':
                print_all_packages_inline(packages, time)
        elif option == '4':
            print_trucks_mileage(trucks)
        elif option == '5':
            done = True
        else:
            print("Error: unknown option")


if __name__ == '__main__':
    main()
