class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self._cache = {}
        self._head = None
        self._tail = None


    def update(self, key, value=None):
        if key not in self._cache and value is None:
            return

        node = self._cache.get(key, Node(key, value))
        if value is not None:
            node.value = value

        if node is self._tail:
            return

        if node.prev is not None:
            node.prev.next = node.next

        if node.next is not None:
            node.next.prev = node.prev

        node.next = None
        self._tail = node
        if len(self._cache) == self.capacity:
            self._cache.pop(self._head.key)

        self._cache[key] = node
        self._head = self._head.next


    def put(self, key, value):
        self.update(key, value)


    def get(self, key):




