import copy
import random


class Record:
    max_length = 15
    array_of_number = []
    key = 0

    def __init__(self, list_of_numbers):
        self.array_of_number = copy.deepcopy(list_of_numbers)
        if len(self.array_of_number) < self.max_length:
            for i in range(0, self.max_length - len(self.array_of_number)):
                self.array_of_number.append(0)
        self.key = sum(self.array_of_number)

    def from_bytes(self, bytes):
        self.array_of_number = []
        for i in range(4, len(bytes), 4):
            self.array_of_number.append(int.from_bytes(bytes[i:i+4], byteorder="little"))

    def to_bytes(self):
        bytes = bytearray()
        for i in range(0, len(self.array_of_number)):
            bytes.extend(self.array_of_number[i].to_bytes(4, byteorder="little"))
        return bytes


class SeqFile:
    byte_buffor = bytearray()
    count_read_block = 0
    count_write_block = 0
    count_read_record = 0
    count_write_record = 0
    records_per_block = 0

    def __init__(self, file_name, size_of_block, record_size):
        self.file_name = file_name
        open(self.file_name, "w")
        self.file = open(self.file_name, "rb+")
        self.records_per_block = int(size_of_block / record_size)
        self.record_size = record_size
        self.size_of_block = size_of_block

    def read_record(self):
        index = self.count_read_record % self.records_per_block
        if index == 0:
            self.read_block()
        record_bytes = self.byte_buffor[index*self.record_size:(index+1)*self.record_size]
        rec = Record([])
        rec.from_bytes(record_bytes)
        self.count_read_record += 1
        return rec

    def write_record(self, record):
        index = self.count_write_record % self.records_per_block
        if index == 0 and self.count_write_record != 0:
            self.write_block()
            self.byte_buffor = bytearray()
        self.byte_buffor.extend(record.to_bytes())
        self.count_write_record += 1

    def read_block(self):
        self.byte_buffor = self.file.read(self.size_of_block)
        self.count_read_block += 1

    def write_block(self):
        number_of_records_on_block = self.count_write_record % self.records_per_block
        if number_of_records_on_block == 0:
            number_of_records_on_block = self.records_per_block
        number_of_zeros = self.size_of_block - number_of_records_on_block * self.record_size
        if number_of_zeros == self.size_of_block:
            return
        for i in range(0, number_of_zeros):
            self.byte_buffor.extend(int(0).to_bytes(1, byteorder="little"))
        self.file.write(self.byte_buffor)
        self.count_write_block += 1

    def end_writing(self):
        self.write_block()
        self.file.seek(0)
        self.count_write_record = 0
        self.count_read_block = 0

    def reset_to_write(self):
        self.file.seek(0)
        self.count_write_record = 0
        self.count_read_block = 0

    def close_file(self):
        self.file.close()


def generate_file(nr, t):
    for i in range(0, nr):
        numbers_in_record = random.randint(1, 15)
        array_of_number = []
        for i in range(0, numbers_in_record):
            array_of_number.append(random.randint(0, 10))
        for i in range(0, 15-numbers_in_record):
            array_of_number.append(0)
        print(array_of_number)
        t.write_record(Record(array_of_number))
    t.end_writing()


def transform_existing_file_to_bin(path, t):
    file_txt = open(path)
    for line in file_txt.readlines():
        line.replace("\n", "")
        numbers = line.split(" ")
        numbers = [int(number) for number in numbers]
        print(numbers)
        rec = Record(numbers)
        t.write_record(rec)
    t.end_writing()
    file_txt.close()


def user_input_to_bin(nr, t):
    for i in range(0, int(nr)):
        numbers_per_record = input("Enter number of numbers per record: \n")
        array_of_number = []
        for i in range(0, int(numbers_per_record)):
            number = input("Number: \n")
            array_of_number.append(int(number))
        t.write_record(Record(array_of_number))
    t.end_writing()


def natural_merge(t1, t2, t3):
    pass


if __name__ == "__main__":
    block_size = 200
    tape3 = SeqFile("t3.bin", block_size, 15 * 4)

    print("--------------MENU--------------")
    print("1. Generate file.")
    print("2. Use existing file.")
    print("3. Write records from keyboard.")
    user_choice = input("Choose option: \n")
    if int(user_choice) == 1:
        number_of_records = input("Enter number of records: \n")
        generate_file(int(number_of_records), tape3)
    elif int(user_choice) == 2:
        path = input("Enter full path to file: \n")
        transform_existing_file_to_bin(path, tape3)
    elif int(user_choice) == 3:
        user_number_of_records = input("Enter number of records, which you want enter: \n")
        user_input_to_bin(int(user_number_of_records), tape3)

    tape1 = SeqFile("t1.bin", block_size, 15*4)
    tape2 = SeqFile("t2.bin", block_size, 15*4)

    natural_merge(tape1, tape2, tape3)

    tape1.close_file()
    tape2.close_file()
    tape3.close_file()
