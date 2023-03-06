class TreeRecord:
    key: int
    address: int

    def __init__(self, key, address):
        self.key = key
        self.address = address

    def to_bytes(self):
        bytes = bytearray()
        bytes.extend(self.key.to_bytes(4, byteorder="little"))
        bytes.extend(self.address.to_bytes(4, byteorder="little"))
        return bytes

    def from_bytes(self, bytes):
        self.key = int.from_bytes(bytes[0:4], byteorder="little")
        self.address = int.from_bytes(bytes[4:8], byteorder="little")