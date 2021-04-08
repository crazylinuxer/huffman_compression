from typing import Dict, Deque, Any
from collections import deque
import heapq


class TreeHeapItem:
    def __init__(self, weight: int, value: Any):
        self.weight = weight
        self.value = value

    def __eq__(self, other: 'TreeHeapItem'):
        return self.weight == other.weight

    def __gt__(self, other: 'TreeHeapItem'):
        return self.weight > other.weight


class HuffmanNode:
    def __init__(self, value, parent, left, right):
        self.value = value
        self.parent = parent
        self.left = left
        self.right = right


class HuffmanTree:
    def __init__(self, freq_table: Dict[int: int]):
        self.leaves = [TreeHeapItem(weight, value) for value, weight in freq_table]
        heapq.heapify(self.leaves)
        self._build()

    def _build(self) -> None:
        pass

    def generate_codes_table(self) -> Dict[int: Deque[bool]]:
        pass
