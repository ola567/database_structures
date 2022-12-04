import copy
import random


class Record:
    length = 15
    array_of_number = []
    key = 0

    def __init__(self, list_of_numbers):
        self.array_of_number = copy.deepcopy(list_of_numbers)
        if len(self.array_of_number) < 15:
            for i in range(0, 15-len(self.array_of_number)):
                self.array_of_number.append(0)
        self.key = sum(self.array_of_number)


    def from_bytes(self, bytes):
        self.key = int.from_bytes(bytes[0:4], byteorder="little")
        self.array_of_number = []
        for i in range(4, len(bytes), 4):
            self.array_of_number.append(int.from_bytes(bytes[i:i+4], byteorder="little"))

    def to_bytes(self):
        bytes = bytearray()
        bytes.extend(self.key.to_bytes(4, byteorder="little"))
        for i in range(0, len(self.array_of_number)):
            bytes.extend(self.array_of_number[i].to_bytes(4, byteorder="little"))
        return bytes


class SeqFile:
    def read_record(self):
        pass
    def write_record(self):
        pass


def generate_file(nr):
    file = open("tasma3.bin", "wb")

    for i in range(0, nr):
        number_of_numbers_in_record = random.randint(1, 15)
        array_of_number = []
        for i in range(0, number_of_numbers_in_record):
            array_of_number.append(random.randint(0, 10))
        for i in range(0, 15-number_of_numbers_in_record):
            array_of_number.append(0)
        rec = Record(array_of_number)
        print(array_of_number)
        file.write(rec.to_bytes())
    file.close()


def transform_existing_file_to_bin(path):
    file_bin = open("tasma3.bin", "wb")
    file_txt = open(path)

    for line in file_txt.readlines():
        line.replace("\n", "")
        numbers = line.split(" ")
        numbers = [int(number) for number in numbers]
        print(numbers)
        rec = Record(numbers)
        file_bin.write(rec.to_bytes())

    file_bin.close()
    file_txt.close()


def user_input_to_bin(nr):
    file_bin = open("tasma3.bin", "wb")
    for i in range(0, int(nr)):
        numbers_per_record = input("Enter number of numbers per record: \n")
        array_of_number = []
        for i in range(0, int(numbers_per_record)):
            number = input("Number: \n")
            array_of_number.append(int(number))
        rec = Record(array_of_number)
        file_bin.write(rec.to_bytes())
    file_bin.close()


if __name__ == "__main__":
    print("--------------MENU--------------")
    print("1. Generate file.")
    print("2. Use existing file.")
    print("3. Write records from keyboard.")

    user_choice = input("Choose option: \n")
    if int(user_choice) == 1:
        number_of_records = input("Enter number of records: \n")
        generate_file(int(number_of_records))
    elif int(user_choice) == 2:
        path = input("Enter full path to file: \n")
        transform_existing_file_to_bin(path)
    elif int(user_choice) == 3:
        user_number_of_records = input("Enter number of records, which you want enter: \n")
        user_input_to_bin(int(user_number_of_records))

    print("done")
