import re

EOD = 60 * 24

def timeFromMinutes(total_minutes) -> str:
    """
    Converts given minutes to HH:MM format
    """
    return "{hrs:02}:{mins:02}".format(hrs=int(total_minutes / 60), mins=int(total_minutes) % 60 )

def standardize_address(addr) -> str:
    """
    Removes line breaks and replaces the words east, north, south and west with
    their corresponding initials (first letter in capital case).
    """
    initial_or_space = lambda match: ' ' if match.group(0)[0] == '\n' else match.group(0)[0].upper()

    return re.sub(r'(\n|east|north|south|west)', initial_or_space, addr.strip(), flags=re.I)
