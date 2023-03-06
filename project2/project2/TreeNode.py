from TreeRecord import TreeRecord


class TreeNode:
    parent_address: int
    number_of_records: int
    tree_records: list[TreeRecord]
    children: list[int]

    def __init__(self):
        self.tree_records = []
        self.children = []
        self.parent_address = 0
        self.number_of_records = 0

    def from_bytes(self, bytes):
        self.parent_address = int.from_bytes(bytes[0:4], byteorder="little")
        self.number_of_records = int.from_bytes(bytes[4:8], byteorder="little")
        for i in range(8, self.number_of_records*12, 12):
            self.children.append(int.from_bytes(bytes[i:i+4], byteorder="little"))
            tree_record = TreeRecord(0, 0)
            tree_record.from_bytes(bytes[i + 4:i + 12])
            self.tree_records.append(tree_record)
        if self.number_of_records != 0:
            self.children.append(int.from_bytes(bytes[8+self.number_of_records*12:8+self.number_of_records*12+4], byteorder="little"))

    def to_bytes(self, size_of_block):
        bytes = bytearray()
        bytes.extend(self.parent_address.to_bytes(4, byteorder="little"))
        bytes.extend(self.number_of_records.to_bytes(4, byteorder="little"))
        for i in range(0, self.number_of_records):
            bytes.extend(self.children[i].to_bytes(4, byteorder="little"))
            bytes.extend(self.tree_records[i].to_bytes())
        bytes.extend(self.children[self.number_of_records].to_bytes(4, byteorder="little"))
        bytes.extend([0 for i in range(len(bytes), size_of_block)])
        return bytes

    def insert_pair(self, child, tree_record):
        index = self.binary_search(tree_record.key)
        rec_at_index = self.tree_records[index]
        if tree_record.key < self.tree_records[0].key:
            self.tree_records.insert(0, tree_record)
            self.children.insert(0, child)
            self.number_of_records += 1
            return
        if tree_record.key > self.tree_records[self.number_of_records - 1].key:
            self.tree_records.append(tree_record)
            self.children.insert(self.number_of_records, child)
            self.number_of_records += 1
            return
        if rec_at_index.key < tree_record.key:
            index += 1
        self.tree_records.insert(index, tree_record)
        self.children.insert(index, child)
        self.number_of_records += 1

    def binary_search(self, key):
        l = 0
        r = self.number_of_records - 1
        index = (l + r) // 2
        while l < r:
            k = self.tree_records[index].key
            if k == key:
                return index
            if key > k:
                l = index + 1
            else:
                r = index - 1
            index = (l + r) // 2
        return index

    def print(self, node_addr):
        string = ""
        string += "<" + str(node_addr) + ">"
        if self.parent_address == 4294967295:
            string += "[NIL]"
        else:
            string += "[" + str(self.parent_address) + "]"
        for i in range(0, self.number_of_records):
            if self.children[i] == 4294967295:
                string += " NIL "
            else:
                string += " " + str(self.children[i]) + " "
            string += "(" + str(self.tree_records[i].key) + "," + str(self.tree_records[i].address) + ")"
        if self.children[self.number_of_records] == 4294967295:
            string += " NIL "
        else:
            string += " " + str(self.children[self.number_of_records]) + " "
        print(string, end="")
