from random import choice, randint
from string import ascii_letters, digits
import csv
import io


def random_string(start: int = 9, end: int = 15) -> str:
    return ''.join(choice(ascii_letters + digits) for _ in range(randint(start, end)))


def random_list_of_strings(start: int = 9, end: int = 15) -> list[str]:
    return [random_string() for _ in range(randint(start, end))]


def random_buffered_csv(start: int = 9, end: int = 15):
    csvdata = random_list_of_strings()
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(csvdata)
    return output
