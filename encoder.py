from typing import BinaryIO, Deque, Dict
from collections import deque

from utils import fill_deque_from_byte, bits_to_bytes
from huffman_tree import HuffmanTree


INPUT_BUFFER_SIZE = 10240  # bytes
OUTPUT_BUFFER_FLUSH_SIZE = 81920  # bits (weak limitation)


class Encoder:
    def __init__(self, input_file: BinaryIO, output_file: BinaryIO):
        """
        Initializes the instance of encoder without reading or writing any data from/to files
        """
        self.input_file = input_file
        self.output_file = output_file
        self.coding_table = {}
        self.encoding_buffer = deque()

    def generate_codes(self) -> Dict[int, Deque[bool]]:
        """
        Reads the whole input file and generates coding_table by the Huffman tree

        :return: coding table where key is byte and value is deque of bits
        """
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
        """
        Writes the coding_table into the output file

        :return: offset of the byte after written table (in file) to start writing data from
        """
        self.output_file.seek(0)
        self.output_file.write(bytes(0 for _ in range(5)))
        table_length_counter = 0  # count of bits in table
        for coding_entry in self.coding_table:
            # writing each coding entry first to buffer and then to file
            fill_deque_from_byte(self.encoding_buffer, coding_entry)
            entry_bit_repr = self.coding_table[coding_entry]
            fill_deque_from_byte(self.encoding_buffer, len(entry_bit_repr))
            self.encoding_buffer.extend(entry_bit_repr)
            table_length_counter += 16 + len(entry_bit_repr)
            if len(self.encoding_buffer) >= OUTPUT_BUFFER_FLUSH_SIZE:
                # write all buffer's full bytes to the file if it is too large
                self.output_file.write(bits_to_bytes(self.encoding_buffer))
        self.output_file.write(bits_to_bytes(self.encoding_buffer, flush=True))  # flush everything left in buffer to the file
        self.output_file.flush()
        curr_pos = self.output_file.tell()
        self.output_file.seek(1)
        self.output_file.write(table_length_counter.to_bytes(4, 'little'))  # write the size of coding table to the output file
        self.output_file.seek(curr_pos)
        return curr_pos

    def _encode(self, data: bytes) -> None:
        """
        Encode given bytes to the buffer (flushing it in process if it's too large)

        :param data: bytes to encode
        """
        for byte in data:
            self.encoding_buffer.extend(self.coding_table[byte])
            if len(self.encoding_buffer) >= OUTPUT_BUFFER_FLUSH_SIZE:
                self.output_file.write(bits_to_bytes(self.encoding_buffer))

    def __call__(self) -> None:
        """
        Generates the coding table, writes it to file, encodes the file by it
        and writes number of trailing zeros to the output file
        """
        self.coding_table = self.generate_codes()
        data_start = self.write_header()
        self.output_file.seek(data_start)
        self.input_file.seek(0)
        self.encoding_buffer.clear()
        while len(bytes_to_encode := self.input_file.read(INPUT_BUFFER_SIZE)) != 0:
            self._encode(bytes_to_encode)  # encode the file, breaking it down into sections in the process
        trailing_zeros = self.flush()
        self.output_file.seek(0)
        self.output_file.write(trailing_zeros.to_bytes(1, 'little'))  # write number if trailing zeros to the start of file

    def flush(self) -> int:
        """
        Flush everything from the buffer to the file

        :return: additional zero bits in the end of file
        """
        result = (8 - (len(self.encoding_buffer) % 8)) % 8
        self.output_file.write(bits_to_bytes(self.encoding_buffer, flush=True))
        return result
