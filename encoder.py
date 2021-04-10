from typing import BinaryIO, Deque, Dict
from collections import deque

from utils import fill_deque_from_byte, bits_to_bytes
from huffman_tree import HuffmanTree


INPUT_BUFFER_SIZE = 10240  # bytes
OUTPUT_BUFFER_FLUSH_SIZE = 81920  # bits (weak limitation)


class Encoder:
    def __init__(self, input_file: BinaryIO, output_file: BinaryIO):
        self.input_file = input_file
        self.output_file = output_file
        self.coding_table = {}
        self.encoding_buffer = deque()

    def generate_codes(self) -> Dict[int, Deque[bool]]:
        self.input_file.seek(0)
        freq_table = {}
        while True:
            input_buffer = self.input_file.read(INPUT_BUFFER_SIZE)
            if not input_buffer:
                break
            for byte in input_buffer:
                if byte in freq_table:
                    freq_table[byte] += 1
                else:
                    freq_table[byte] = 1
        tree = HuffmanTree(freq_table)
        return tree.generate_codes()

    def write_header(self) -> int:
        self.output_file.seek(0)
        self.output_file.write(bytes(0 for _ in range(5)))
        output_buffer = deque()
        table_length_counter = 0  # bits
        for coding_entry in self.coding_table:
            fill_deque_from_byte(output_buffer, coding_entry)
            entry_bit_repr = self.coding_table[coding_entry]
            fill_deque_from_byte(output_buffer, len(entry_bit_repr))
            output_buffer.extend(entry_bit_repr)
            table_length_counter += 16 + len(entry_bit_repr)
            if len(output_buffer) >= OUTPUT_BUFFER_FLUSH_SIZE:
                self.output_file.write(bits_to_bytes(output_buffer))
        self.output_file.write(bits_to_bytes(output_buffer, flush=True))
        self.output_file.flush()
        curr_pos = self.output_file.tell()
        self.output_file.seek(1)
        self.output_file.write(table_length_counter.to_bytes(4, 'little'))
        self.output_file.seek(curr_pos)
        return curr_pos

    def _encode(self, data: bytes) -> None:
        for byte in data:
            self.encoding_buffer.extend(self.coding_table[byte])
            if len(self.encoding_buffer) >= OUTPUT_BUFFER_FLUSH_SIZE:
                self.output_file.write(bits_to_bytes(self.encoding_buffer))

    def __call__(self):
        self.coding_table = self.generate_codes()
        data_start = self.write_header()
        self.output_file.seek(data_start)
        self.input_file.seek(0)
        self.encoding_buffer.clear()
        while len(bytes_to_encode := self.input_file.read(INPUT_BUFFER_SIZE)) != 0:
            self._encode(bytes_to_encode)
        trailing_zeros = self.flush()
        self.output_file.seek(0)
        self.output_file.write(trailing_zeros.to_bytes(1, 'little'))

    def flush(self) -> int:
        """
        :return: additional zero bits in the end of file
        """
        result = len(self.encoding_buffer) % 8
        self.output_file.write(bits_to_bytes(self.encoding_buffer, flush=True))
        return result
