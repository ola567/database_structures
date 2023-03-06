import os.path
from BTree import BTree, ReturnValue
from Record import Record

folder = "asd"
size_of_block = 4096
record_size = 15 * 4
order = 2


def print_disk_operations():
    print(f"numb_of_operations: {btree.record_manager.count_read_block + btree.tree_node_manager.count_read_block + btree.record_manager.count_write_block + btree.tree_node_manager.count_write_block}")
    # print(f"pages: {btree.tree_node_manager.next_page_get}")


def process_test_file(p):
    file = open(p)
    lines = file.readlines()

    i = 0
    while i < len(lines):
        if lines[i] == '1\n':
            key = lines[i + 1]
            key = int(key[:-1])
            record = Record([0])
            if btree.insert(key, record) == ReturnValue.OK:
                print("Successful insert.")
            else:
                print("Not successful insert.")
            i += 2
            print_disk_operations()
        elif lines[i] == '2\n':
            key = lines[i + 1]
            key = int(key[:-1])
            res = btree.search(key)
            if res is None:
                print("Doesn't exist.")
            else:
                print(res.array_of_number)
            i += 2
            print_disk_operations()
        elif lines[i] == '3\n':
            u_k = int(lines[i + 1])
            lines[i + 2].replace("\n", "")
            n = lines[i + 2].split(" ")
            n = [int(number) for number in n]
            r = Record(n)
            res = btree.update(u_k, r)
            i += 3
            if res == ReturnValue.OK:
                print("Successful update.")
            else:
                print("No record with given key.")
            print_disk_operations()
        elif lines[i] == '4\n':
            btree.print_index()
            i += 1
            print_disk_operations()
        elif lines[i] == '5\n':
            btree.print_file()
            i += 1
            print_disk_operations()


if __name__ == '__main__':
    btree = BTree(order, os.path.join(folder, "nodes.bin"), os.path.join(folder, "records.bin"), size_of_block, record_size)

    while True:
        print("----------MENU----------")
        print("1. Insert.")
        print("2. Search.")
        print("3. Update")
        print("4. Print tree.")
        print("5. Print file.")
        print("6. Read test file.")
        print("7. Exit")
        print("------------------------")

        user_input = input("Enter option number: \n")
        if user_input == '1':
            user_key = input("Key: \n")
            rec = Record([0])
            if btree.insert(int(user_key), rec) == ReturnValue.OK:
                print("Successful insert.")
            else:
                print("Not successful insert.")
            print_disk_operations()
        elif user_input == '2':
            user_key = input("Key: \n")
            result = btree.search(int(user_key))
            if result is None:
                print("Doesn't exist.")
            else:
                print(result.array_of_number)
            print_disk_operations()
        elif user_input == '3':
            user_key = int(input("Key: \n"))
            numbers = int(input("Number of numbers: \n"))
            ar = []
            for i in range(0, numbers):
                numb = input("Number: \n")
                ar.append(int(numb))
            for i in range(numbers, record_size):
                ar.append(0)
            record = Record(ar)
            result = btree.update(user_key, record)
            if result == ReturnValue.OK:
                print("Successful update.")
            else:
                print("No record with given key.")
            print_disk_operations()
        elif user_input == '4':
            btree.print_index()
            print_disk_operations()
        elif user_input == '5':
            btree.print_file()
            print_disk_operations()
        elif user_input == '6':
            user_file = input("Path: \n")
            process_test_file(user_file)
        elif user_input == '7':
            break
        else:
            print("Wrong option.")
