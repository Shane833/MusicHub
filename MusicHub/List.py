# Represents a node of the list

# CHANGE : Need to overload the __len__ function to obtain the length of the list

class Node:
    # Constructor
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
        
    # Hash Function
    def __hash__(self):
        return hash(self.key)
    # Comparision Function
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.key == other.key
        return False

# Represents the list
class List:
    # Constructor
    def __init__(self):
        self.head = None
        
    # Overriding the __len__ function to enable obtaining the length using len()
    def __len__(self):
        # Variable to hold the length of the list
        length = 0
        # First case : When its empty
        if self.isEmpty() is True:
            return length
        # Second case we'll traverse through the list
        current = self.head
        while current:
            current = current.next
            length += 1
        
        return length 
    
    # Checking if list is empty
    def isEmpty(self):
        # If head is None then its empty
        if self.head is None:
            return True
        # else
        return False
        
    # Append function
    def append(self, key, value):
        new_node = Node(key, value)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
            new_node.prev = current

    # Prepend Function
    def prepend(self, key, value):
        new_node = Node(key, value)
        if self.head is None:
            self.head = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
    
    # Search Function
    def search(self, key):
        current = self.head
        while current:
            if current.key == key:
                return current
            current = current.next
        return None
    
    # Remove Function
    def remove(self, key):
        current = self.head
        while current:
            if current.key == key:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                return True  # Node removed
            current = current.next
        return False  # Node not found

    # Display Function
    def display(self):
        current = self.head
        while current:
            print(f"({current.key}, {current.value})", end=" <-> ")
            current = current.next
        print("None")
    
    # Function to retrieve a list of keys
    def getKeys(self):
        keys = [] # empty list
        current = self.head
        while current:
            keys.append(current.key)
            current = current.next
        return keys
    
    # Function to clear the list 
    def clear(self):
        self.head = None
    
class CircularList:
    # Constructor
    def __init__(self):
        self.head = None
        self.current = self.head
    
    # Function to append data
    def append(self, key, value):
        new_node = Node(key, value)
        if self.head is None:
            self.head = new_node
            self.head.next = self.head
            self.head.prev = self.head
        else:
            last_node = self.head.prev
            last_node.next = new_node
            new_node.prev = last_node
            new_node.next = self.head
            self.head.prev = new_node
        
    # function to retreive the next data item
    def getNext(self):
        current = self.current.next
        self.current = self.current.next
        return current
