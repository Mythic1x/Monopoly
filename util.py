from typing import Self


class LLNode[T]:
    value: T
    next: Self | None
    def __init__(self, value: T, next: Self | None = None):
        self.value = value
        self.next = None

class LinkedList[T]:
    head: LLNode[T] | None
    tail: LLNode[T] | None
    len: int
    def __init__(self):
        self.head = None
        self.tail = None
        self.len = 0

    def append(self, item: T):
        self.len += 1
        if self.head is None:
            self.head = LLNode(item)
            self.tail = self.head
        elif self.tail:
            self.tail.next = LLNode(item)
            self.tail = self.tail.next
        else:
            #this should never happen
            self.tail = LLNode(item)
