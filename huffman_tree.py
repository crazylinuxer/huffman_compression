from typing import Dict, Deque, List, Optional
from collections import deque
import heapq


class HuffmanNode:
    def __init__(
            self, value: Optional[int], weight: int, parent: 'HuffmanNode' = None,
            left: 'HuffmanNode' = None, right: 'HuffmanNode' = None
    ):
        self.value = value
        self.weight = weight
        self.parent = parent
        self.left = left
        self.right = right

    def __hash__(self):
        return sum(id(i) for i in (self.left, self.right, self.parent)) + hash(self.value) + hash(self.weight)

    def __eq__(self, other: 'HuffmanNode'):
        return id(self.left) == id(other.left) and\
               id(self.right) == id(other.right) and\
               id(self.parent) == id(other.parent) and\
               self.value == other.value and\
               self.weight == other.weight


class HuffmanTree:
    class BuildHeapItem:
        def __init__(self, node: HuffmanNode):
            self.node = node

        def __eq__(self, other: 'HuffmanTree.BuildHeapItem'):
            return self.node.weight == other.node.weight

        def __gt__(self, other: 'HuffmanTree.BuildHeapItem'):
            return self.node.weight > other.node.weight

    def __init__(self, freq_table: Dict[int, int]):
        self.leaves = [HuffmanNode(value, freq_table[value]) for value in freq_table]
        build_heap = [self.BuildHeapItem(node) for node in self.leaves]
        heapq.heapify(build_heap)
        self.root = self._build(build_heap)

    @staticmethod
    def _build(heap: List['HuffmanTree.BuildHeapItem']) -> HuffmanNode:
        while len(heap) >= 2:
            light_node1, light_node2 = heapq.heappop(heap).node, heapq.heappop(heap).node
            new_item = HuffmanTree.BuildHeapItem(HuffmanNode(
                None, light_node1.weight + light_node2.weight, left=light_node2, right=light_node1
            ))
            light_node1.parent = light_node2.parent = new_item.node
            heapq.heappush(heap, new_item)
        return heap[0].node

    def generate_codes(self) -> Dict[int, Deque[bool]]:
        result = {}
        for leaf in self.leaves:
            leaf_path = deque()
            tmp_node_ptr = leaf
            while tmp_node_ptr and tmp_node_ptr.parent:
                leaf_path.appendleft(tmp_node_ptr.parent.right == tmp_node_ptr)
                tmp_node_ptr = tmp_node_ptr.parent
            result[leaf.value] = leaf_path
        return result
