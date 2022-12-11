import copy
import os
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
        for i in range(0, len(bytes), 4):
            self.array_of_number.append(int.from_bytes(bytes[i:i+4], byteorder="little"))
        self.key = sum(self.array_of_number)

    def to_bytes(self):
        bytes = bytearray()
        for i in range(0, len(self.array_of_number)):
            bytes.extend(self.array_of_number[i].to_bytes(4, byteorder="little"))
        return bytes


class SeqFile:
    count_read_block = 0
    count_write_block = 0
    count_read_record = 0
    count_write_record = 0
    records_per_block = 0
    records_in_file = 0

    def __init__(self, file_name, size_of_block, record_size):
        self.file_name = file_name
        open(self.file_name, "w")
        self.file = open(self.file_name, "rb+")
        self.records_per_block = int(size_of_block / record_size)
        self.record_size = record_size
        self.size_of_block = size_of_block
        self.byte_buffor = bytearray()

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
        self.byte_buffor = bytearray()
        self.records_in_file = self.count_write_record
        self.count_write_record = 0
        self.count_read_record = 0

    def reset_to_write(self):
        self.file.seek(0)
        self.count_write_record = 0
        self.count_write_block = 0
        self.count_read_block = 0
        self.byte_buffor = bytearray()

    def reset_tape3(self):
        self.file.seek(0)
        self.byte_buffor = bytearray()
        self.count_read_record = 0
        self.count_read_record = 0

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
        t.write_record(Record(array_of_number))
    t.records_in_file = nr
    t.end_writing()


def transform_existing_file_to_bin(path, t):
    file_txt = open(path)
    n = 0
    for line in file_txt.readlines():
        n += 1
        line.replace("\n", "")
        numbers = line.split(" ")
        numbers = [int(number) for number in numbers]
        rec = Record(numbers)
        t.write_record(rec)
    t.records_in_file = n
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
    t.records_in_file = nr
    t.end_writing()


def distribute_files(t1, t2, t3):
    swap = False
    rec_first = t3.read_record()
    t1.write_record(rec_first)
    while t3.count_read_record < t3.records_in_file:
        rec_second = t3.read_record()
        if not swap:
            if rec_first.key <= rec_second.key:
                t1.write_record(rec_second)
            else:
                t2.write_record(rec_second)
                swap = True
        else:
            if rec_first.key <= rec_second.key:
                t2.write_record(rec_second)
            else:
                t1.write_record(rec_second)
                swap = False
        rec_first = rec_second
    t1.end_writing()
    t2.end_writing()
    return t1, t2


def natural_merge(t1, t2, t3):
    t3.reset_to_write()
    rec_t1 = t1.read_record()
    rec_t2 = t2.read_record()
    while t1.count_read_record <= t1.records_in_file and t2.count_read_record <= t2.records_in_file:
        if rec_t1.key <= rec_t2.key:
            t3.write_record(rec_t1)
            store_prev_key1 = rec_t1.key
            rec_t1 = t1.read_record()

            if t1.count_read_record <= t1.records_in_file and store_prev_key1 > rec_t1.key:
                t3.write_record(rec_t2)
                store_prev_key2 = rec_t2.key
                rec_t2 = t2.read_record()
                while t2.count_read_record <= t2.records_in_file and store_prev_key2 <= rec_t2.key:
                    t3.write_record(rec_t2)
                    store_prev_key2 = rec_t2.key
                    rec_t2 = t2.read_record()
        else:
            t3.write_record(rec_t2)
            store_prev_key2 = rec_t2.key
            rec_t2 = t2.read_record()
            if t2.count_read_record <= t2.records_in_file and store_prev_key2 > rec_t2.key:
                t3.write_record(rec_t1)
                store_prev_key1 = rec_t1.key
                rec_t1 = t1.read_record()
                while t1.count_read_record <= t1.records_in_file and store_prev_key1 <= rec_t1.key:
                    t3.write_record(rec_t1)
                    store_prev_key1 = rec_t1.key
                    rec_t1 = t1.read_record()

    if not t1.count_read_record <= t1.records_in_file:
        t3.write_record(rec_t2)
        while t2.count_read_record < t2.records_in_file:
            t3.write_record(t2.read_record())
    else:
        t3.write_record(rec_t1)
        while t1.count_read_record < t1.records_in_file:
            rec = t1.read_record()
            t3.write_record(rec)
    t1.reset_to_write()
    t2.reset_to_write()
    t3.end_writing()
    return t3


def print_t3(t3):
    for i in range(0, t3.records_in_file):
        record = t3.read_record()
        print(record.array_of_number, end = f" key: {record.key} \n")
    t3.reset_tape3()


def is_sorted(t3):
    rec_first = t3.read_record()
    i = 0
    while t3.count_read_record <= t3.records_in_file:
        rec_second = t3.read_record()
        if rec_first.key > rec_second.key:
            break
        i += 1
        rec_first = rec_second
    t3.reset_tape3()
    if i == t3.records_in_file - 1:
        return True
    else:
        return False


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

    print("--------------BEFORE SORTING--------------")
    print_t3(tape3)
    print()

    if_want_each_phase = input("Do you want to see file after each phase of sorting? (y/n)")
    phases = 0
    while not is_sorted(tape3):
        phases += 1
        tape1 = SeqFile("t1.bin", block_size, 15 * 4)
        tape2 = SeqFile("t2.bin", block_size, 15 * 4)
        tape1, tape2 = distribute_files(tape1, tape2, tape3)
        tape3 = natural_merge(tape1, tape2, tape3)
        tape1.close_file()
        tape2.close_file()
        os.remove(tape1.file_name)
        os.remove(tape2.file_name)
        if if_want_each_phase == 'y':
            print(f"--------------AFTER PHASE {phases}--------------")
            print_t3(tape3)
            print()
    print("--------------AFTER SORTING--------------")
    print_t3(tape3)
    print()
    print(f"Phases: {phases}")
    print(f"Read_block: {tape3.count_read_block}")
    print(f"Write_block: {tape3.count_write_block}")
    tape3.close_file()
    pass
