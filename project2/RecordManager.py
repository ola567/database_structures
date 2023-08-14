from Record import Record


class RecordManager:
    def __init__(self, file_name, size_of_block, record_size):
        open(file_name, "w")
        self.file = open(file_name, "rb+")
        self.size_of_block = size_of_block
        self.record_size = record_size
        self.byte_buffer = bytearray()
        self.count_read_block = 0
        self.count_write_block = 0
        self.page_number_in_buffer = -1
        self.records_per_page = int(self.size_of_block / self.record_size)
        self.deleted_address = []
        self.next_insert_at = 0
        self.number_of_pages_in_file = -1
        self.if_page_was_modified = False

    def read_record(self, address):
        page_number = address // self.records_per_page
        offset = (address % self.records_per_page) * self.record_size
        if self.page_number_in_buffer != page_number:
            self.read_page(page_number)
        record_bytes = self.byte_buffer[offset:offset + self.record_size]
        rec = Record([])
        rec.from_bytes(record_bytes)
        return rec

    def read_page(self, page_number):
        if self.if_page_was_modified and page_number != self.page_number_in_buffer and self.page_number_in_buffer != -1:
            self.write_page()
        self.file.seek(page_number * self.size_of_block)
        self.byte_buffer = bytearray(self.file.read(self.size_of_block))
        self.page_number_in_buffer = page_number
        self.count_read_block += 1

    def write_page(self):
        self.file.seek(self.page_number_in_buffer * self.size_of_block)
        self.file.write(self.byte_buffer)
        self.count_write_block += 1

    def insert_record(self, record):
        insert_at = 0
        record_bytes = record.to_bytes()
        if len(self.deleted_address) > 0:
            insert_at = self.deleted_address[0]
            self.deleted_address.pop(0)
        else:
            insert_at = self.next_insert_at
            self.next_insert_at += 1
        page_number = insert_at // self.records_per_page
        offset = (insert_at % self.records_per_page) * self.record_size
        if page_number == self.page_number_in_buffer:
            pass
        elif page_number <= self.number_of_pages_in_file:
            self.read_page(page_number)
        else:
            self.byte_buffer = bytearray(self.size_of_block)
            self.page_number_in_buffer = page_number
            self.number_of_pages_in_file += 1

        for i in range(0, self.record_size):
            self.byte_buffer[i+offset] = record_bytes[i]

        self.if_page_was_modified = True
        return insert_at

    def delete_record(self, address):
        self.deleted_address.append(address)

    def update_record(self, address, record):
        record_bytes = record.to_bytes()
        page_number = address // self.records_per_page
        offset = (address % self.records_per_page) * self.record_size
        if self.page_number_in_buffer != page_number:
            self.read_page(page_number)
        for i in range(0, self.record_size):
            self.byte_buffer[i+offset] = record_bytes[i]

    def close_file(self):
        self.file.close()
