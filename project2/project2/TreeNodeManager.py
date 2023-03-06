from TreeNode import TreeNode


class TreeNodeManager:
    def __init__(self, file_name, size_of_block):
        open(file_name, "w")
        self.file = open(file_name, "rb+")
        self.size_of_block = size_of_block
        self.byte_buffer = bytearray()
        self.page_number_in_buffer = -1
        self.count_write_block = 0
        self.count_read_block = 0
        self.next_page_get = 0
        self.deleted_tree_nodes = []
        self.if_page_was_modified = False

    def get_tree_node(self, address):
        if self.page_number_in_buffer != address:
            if self.if_page_was_modified:
                self.file.seek(self.page_number_in_buffer * self.size_of_block)
                self.file.write(self.byte_buffer)
                self.count_write_block += 1
            self.file.seek(address * self.size_of_block)
            self.byte_buffer = bytearray(self.file.read(self.size_of_block))
            self.page_number_in_buffer = address
            self.count_read_block += 1
            self.if_page_was_modified = False
        tree_node = TreeNode()
        tree_node.from_bytes(self.byte_buffer)
        return tree_node

    def set_tree_node(self, address, tree_node):
        if address != self.page_number_in_buffer and self.page_number_in_buffer != -1:
            self.file.seek(self.page_number_in_buffer * self.size_of_block)
            self.file.write(self.byte_buffer)
            self.count_write_block += 1
        self.byte_buffer = bytearray(tree_node.to_bytes(self.size_of_block))
        self.page_number_in_buffer = address
        self.if_page_was_modified = True

    def get_new_node(self):
        new_node = 0
        if len(self.deleted_tree_nodes) > 0:
            new_node = self.deleted_tree_nodes[0]
            self.deleted_tree_nodes.pop(0)
        else:
            new_node = self.next_page_get
            self.next_page_get += 1
        self.file.seek(new_node * self.size_of_block)
        self.file.write(bytearray(self.size_of_block))
        return new_node

    def delete_tree_node(self, address):
        self.deleted_tree_nodes.append(address)

    def close_file(self):
        self.file.close()
