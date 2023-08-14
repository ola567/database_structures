import copy


class Record:
    max_length = 15
    array_of_number = []

    def __init__(self, list_of_numbers):
        self.array_of_number = copy.deepcopy(list_of_numbers)
        if len(self.array_of_number) < self.max_length:
            for i in range(0, self.max_length - len(self.array_of_number)):
                self.array_of_number.append(0)

    def from_bytes(self, bytes):
        self.array_of_number = []
        for i in range(0, len(bytes), 4):
            self.array_of_number.append(int.from_bytes(bytes[i:i+4], byteorder="little"))

    def to_bytes(self):
        bytes = bytearray()
        for i in range(0, len(self.array_of_number)):
            bytes.extend(self.array_of_number[i].to_bytes(4, byteorder="little"))
        return bytes