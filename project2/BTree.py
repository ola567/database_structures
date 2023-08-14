import copy
from enum import Enum
from RecordManager import RecordManager
from TreeNodeManager import TreeNodeManager
from TreeRecord import TreeRecord


class ReturnValue(Enum):
    OK = 0
    NOT_FOUND = 1
    ALREADY_EXIST = 2
    NOT_POSSIBLE = 3


class BTree:
    ORDER: int
    height: int
    root_address: int
    NIL = 2**32 - 1
    tree_node_manager: TreeNodeManager
    record_manger: RecordManager

    def __init__(self, order, file_name_index, file_name_record, size_of_block, record_size):
        self.ORDER = order
        self.height = 0
        self.root_address = self.NIL
        self.tree_node_manager = TreeNodeManager(file_name_index, size_of_block)
        self.record_manager = RecordManager(file_name_record, size_of_block, record_size)
        self.sequential_last_node = self.NIL
        self.sequential_index = 0

    # private methods
    def _search(self, key, address, prev_address) -> (ReturnValue, int, int):
        if address == self.NIL:
            return ReturnValue.NOT_FOUND, 0, prev_address
        node = self.tree_node_manager.get_tree_node(address)
        index = node.binary_search(key)
        tree_record = node.tree_records[index]
        if tree_record.key == key:
            return ReturnValue.OK, tree_record.address, address
        if tree_record.key < key:
            index += 1
        if key < node.tree_records[0].key:
            return self._search(key, node.children[0], address)
        if key > node.tree_records[node.number_of_records - 1].key:
            return self._search(key, node.children[node.number_of_records], address)
        return self._search(key, node.children[index], address)

    def _insert(self, tree_record, node_address, child):
        if self.height == 0:
            self.root_address = self.tree_node_manager.get_new_node()
            root_node = self.tree_node_manager.get_tree_node(self.root_address)
            root_node.parent_address = self.NIL
            root_node.number_of_records = 1
            root_node.children.append(self.NIL)
            root_node.children.append(self.NIL)
            root_node.tree_records.append(TreeRecord(tree_record.key, tree_record.address))
            self.height = 1
            self.tree_node_manager.set_tree_node(self.root_address, root_node)
            return
        node = self.tree_node_manager.get_tree_node(node_address)
        if node.number_of_records < 2 * self.ORDER:
            node.insert_pair(child, tree_record)
            self.tree_node_manager.set_tree_node(node_address, node)
            return
        if self.compensation_left_possible(node_address, tree_record, child):
            return
        if self.compensation_right_possible(node_address, tree_record, child):
            return
        self.split(node_address, tree_record, child)

    def split(self, node_address, tree_record, child):
        node = self.tree_node_manager.get_tree_node(node_address)
        new_node_address = self.tree_node_manager.get_new_node()
        new_node = self.tree_node_manager.get_tree_node(new_node_address)
        index = 0
        tree_records = copy.deepcopy(node.tree_records)
        while index < len(tree_records) and tree_records[index].key < tree_record.key:
            index += 1
        children = copy.deepcopy(node.children)
        tree_records.insert(index, tree_record)
        children.insert(index, child)
        middle_index = len(tree_records) // 2

        new_node.tree_records = []
        new_node.children = []

        for i in range(0, middle_index):
            new_node.tree_records.append(tree_records[i])
            new_node.children.append(children[i])
        new_node.children.append(children[middle_index])
        new_node.number_of_records = middle_index

        node.tree_records = []
        node.children = []

        for i in range(middle_index + 1, len(tree_records)):
            node.tree_records.append(tree_records[i])
            node.children.append(children[i])
        node.children.append(children[-1])
        node.number_of_records = len(node.tree_records)

        new_node.parent_address = node.parent_address
        for i in range(0, new_node.number_of_records + 1):
            if new_node.children[i] != self.NIL:
                child_node = self.tree_node_manager.get_tree_node(new_node.children[i])
                child_node.parent_address = new_node_address
                self.tree_node_manager.set_tree_node(new_node.children[i], child_node)

        if node_address != self.root_address:
            self.tree_node_manager.set_tree_node(new_node_address, new_node)
            self.tree_node_manager.set_tree_node(node_address, node)
            self._insert(tree_records[middle_index], node.parent_address, new_node_address)
            return

        self.root_address = self.tree_node_manager.get_new_node()
        new_root = self.tree_node_manager.get_tree_node(self.root_address)
        new_root.parent_address = self.NIL
        new_root.number_of_records = 1
        new_root.children = []
        new_root.tree_records = []
        new_root.children.append(new_node_address)
        new_root.tree_records.append(tree_records[middle_index])
        new_root.children.append(node_address)

        node.parent_address = self.root_address
        new_node.parent_address = self.root_address

        self.tree_node_manager.set_tree_node(self.root_address, new_root)
        self.tree_node_manager.set_tree_node(new_node_address, new_node)
        self.tree_node_manager.set_tree_node(node_address, node)

        self.height += 1

    def compensation_left_possible(self, node_address, tree_record, child):
        node = self.tree_node_manager.get_tree_node(node_address)
        parent_node = self.tree_node_manager.get_tree_node(node.parent_address)
        for i in range(0, len(parent_node.children)):
            if parent_node.children[i] == node_address:
                if i == 0:
                    return False
                left_sibling_address = parent_node.children[i-1]
                left_sibling = self.tree_node_manager.get_tree_node(left_sibling_address)
                if left_sibling.number_of_records < 2 * self.ORDER:
                    self.compensate(left_sibling, node, parent_node, tree_record, child, i - 1, left_sibling_address, node_address)
                    self.tree_node_manager.set_tree_node(node_address, node)
                    self.tree_node_manager.set_tree_node(node.parent_address, parent_node)
                    self.tree_node_manager.set_tree_node(left_sibling_address, left_sibling)
                    return True
                return False

    def compensation_right_possible(self, node_address, tree_record, child):
        node = self.tree_node_manager.get_tree_node(node_address)
        parent_node = self.tree_node_manager.get_tree_node(node.parent_address)
        for i in range(0, len(parent_node.children)):
            if parent_node.children[i] == node_address:
                if i == len(parent_node.children) - 1:
                    return False
                right_sibling_address = parent_node.children[i + 1]
                right_sibling = self.tree_node_manager.get_tree_node(right_sibling_address)
                if right_sibling.number_of_records < 2 * self.ORDER:
                    self.compensate(node, right_sibling, parent_node, tree_record, child, i, node_address, right_sibling_address)
                    self.tree_node_manager.set_tree_node(node_address, node)
                    self.tree_node_manager.set_tree_node(node.parent_address, parent_node)
                    self.tree_node_manager.set_tree_node(right_sibling_address, right_sibling)
                    return True
                return False

    def compensate(self, left_node, right_node, parent, tree_record, child, parent_index, left_node_address, right_node_address):
        tree_records = left_node.tree_records + [parent.tree_records[parent_index]] + right_node.tree_records
        children = left_node.children + right_node.children
        index = 0
        while index < len(tree_records) and tree_records[index].key < tree_record.key:
            index += 1
        tree_records.insert(index, tree_record)
        children.insert(index, child)
        middle_index = len(tree_records) // 2

        left_node.tree_records = []
        left_node.children = []

        for i in range(0, middle_index):
            left_node.tree_records.append(tree_records[i])
            left_node.children.append(children[i])
        left_node.children.append(children[middle_index])
        left_node.number_of_records = middle_index

        parent.tree_records[parent_index] = tree_records[middle_index]

        right_node.tree_records = []
        right_node.children = []

        for i in range(middle_index + 1, len(tree_records)):
            right_node.tree_records.append(tree_records[i])
            right_node.children.append(children[i])
        right_node.children.append(children[-1])
        right_node.number_of_records = len(right_node.tree_records)

        for i in range(0, left_node.number_of_records + 1):
            if left_node.children[i] != self.NIL:
                child_node = self.tree_node_manager.get_tree_node(left_node.children[i])
                child_node.parent_address = left_node_address
                self.tree_node_manager.set_tree_node(left_node.children[i], child_node)

        for i in range(0, right_node.number_of_records + 1):
            if right_node.children[i] != self.NIL:
                child_node = self.tree_node_manager.get_tree_node(right_node.children[i])
                child_node.parent_address = right_node_address
                self.tree_node_manager.set_tree_node(right_node.children[i], child_node)

    def _print_index(self, print_queue, node_new_line):
        if len(print_queue) == 0:
            print()
            return
        node_address = print_queue[0]
        node = self.tree_node_manager.get_tree_node(node_address)
        print_queue.pop(0)
        if node_new_line == node_address:
            if node_address != self.root_address:
                print()
            node_new_line = node.children[0]
        node.print(node_address)
        for i in range(0, node.number_of_records + 1):
            if node.children[i] != self.NIL:
                print_queue.append(node.children[i])
        self._print_index(print_queue, node_new_line)

    def get_next_record(self):
        if self.sequential_last_node == self.NIL:
            return None
        node = self.tree_node_manager.get_tree_node(self.sequential_last_node)

        tree_record = node.tree_records[self.sequential_index]
        self.sequential_index += 1
        child_address = node.children[self.sequential_index]
        if child_address != self.NIL:
            return_value, address, last_node = self._search(-2**32, child_address, self.NIL)
            self.sequential_index = 0
            self.sequential_last_node = last_node
        elif self.sequential_index == node.number_of_records:
            self.set_next_seq_read(node.parent_address, self.sequential_last_node)

        return tree_record

    def set_next_seq_read(self, parent_node_address, child_node_address):
        if parent_node_address == self.NIL:
            self.sequential_last_node = self.NIL
            return
        parent_node = self.tree_node_manager.get_tree_node(parent_node_address)
        child_index = 0
        while parent_node.children[child_index] != child_node_address:
            child_index += 1
        if child_index == parent_node.number_of_records:
            self.set_next_seq_read(parent_node.parent_address, parent_node_address)
        else:
            self.sequential_last_node = parent_node_address
            self.sequential_index = child_index

    # public methods
    def insert(self, key, record):
        return_value, address, last_node = self._search(key, self.root_address, self.NIL)
        if return_value == ReturnValue.OK:
            return ReturnValue.ALREADY_EXIST
        rec_address = self.record_manager.insert_record(record)
        self._insert(TreeRecord(key, rec_address), last_node, self.NIL)
        return ReturnValue.OK

    def search(self, key):
        return_value, address, last_node = self._search(key, self.root_address, self.NIL)
        if return_value == ReturnValue.OK:
            return self.record_manager.read_record(address)
        return None

    def print_index(self):
        if self.root_address == self.NIL:
            print("Index empty!")
            return
        self._print_index([self.root_address], self.root_address)

    def update(self, key, record):
        return_value, address, last_node = self._search(key, self.root_address, self.NIL)
        if return_value == ReturnValue.OK:
            self.record_manager.update_record(address, record)
            return ReturnValue.OK
        else:
            return ReturnValue.NOT_FOUND

    def print_file(self):
        return_value, address, last_node = self._search(-2**32, self.root_address, self.NIL)
        self.sequential_last_node = last_node
        self.sequential_index = 0
        tree_record = self.get_next_record()
        if tree_record is None:
            print("File empty!!!")
            return
        while tree_record is not None:
            record = self.record_manager.read_record(tree_record.address)
            print(tree_record.key)
            print(record.array_of_number)
            tree_record = self.get_next_record()
