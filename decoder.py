from typing import BinaryIO, Hashable, Iterable, Dict
from collections import deque
from os import stat

from utils import fill_deque_from_byte, bits_to_bytes


INPUT_BUFFER_SIZE = 10240


class BitSequence(Hashable):
    def __init__(self, bits: Iterable[bool], use_given_deque: bool = False):
        if isinstance(bits, deque) and use_given_deque:
            self.data = bits
        else:
            self.data = deque(bits)

    def __hash__(self) -> int:
        result = 0
        for bit in self.data:
            result <<= 1
            result |= bit
        return result

    def __eq__(self, other):
        if isinstance(other, BitSequence):
            other = other.data
        if len(self.data) != len(other):
            return False
        return all(self.data[i] == other[i] for i in range(len(self.data)))


class Decoder:
    def __init__(self, input_file: BinaryIO, output_file: BinaryIO):
        self.input_file = input_file
        self.output_file = output_file
        self.coding_table: Dict[BitSequence, int] = {}
        self.decoding_buffer = deque()
        self.trailing_zeros = 0
        self.input_file_size = stat(self.input_file.name).st_size

    def read_header(self) -> int:
        self.input_file.seek(0)
        self.trailing_zeros = self.input_file.read(1)[0]
        table_size = int.from_bytes(self.input_file.read(4), byteorder='little')
        table_bytes = (table_size // 8) + (table_size % 8 > 0)
        for byte in self.input_file.read(table_bytes):
            fill_deque_from_byte(self.decoding_buffer, byte)
        for _ in range(table_size % 8):
            self.decoding_buffer.pop()
        while len(self.decoding_buffer) > 16:
            byte, cipher_len = (int.from_bytes(bits_to_bytes(deque(
                self.decoding_buffer.popleft() for _ in range(8)
            )), byteorder='little') for _ in range(2))
            self.coding_table[BitSequence(self.decoding_buffer.popleft() for _ in range(cipher_len))] = byte
        self.decoding_buffer.clear()
        return table_bytes

    def _decode(self, data: bytes, skip_last_bits: int = 0):
        for byte in data:
            fill_deque_from_byte(self.decoding_buffer, byte)
        for _ in range(min(len(self.decoding_buffer), skip_last_bits)):
            self.decoding_buffer.pop()
        cipher_storage = deque()
        output_buffer = []
        stop = False
        while True:
            while BitSequence(cipher_storage, use_given_deque=True) not in self.coding_table:
                if not self.decoding_buffer:
                    self.decoding_buffer.extend(cipher_storage)
                    stop = True
                    break
                cipher_storage.append(self.decoding_buffer.popleft())
                if len(cipher_storage) > 256:
                    raise RuntimeError("Invalid code size")
            if stop:
                break
            output_buffer.append(self.coding_table[BitSequence(cipher_storage, use_given_deque=True)])
        self.output_file.write(bytes(output_buffer))

    def input_is_eof(self, table_size: int) -> bool:
        return (5 + table_size + self.input_file.tell()) >= self.input_file_size

    def __call__(self):
        table_size = self.read_header()
        while not self.input_is_eof(table_size):
            buffer = self.input_file.read(INPUT_BUFFER_SIZE)
            is_eof = self.input_is_eof(table_size)
            self._decode(buffer, self.trailing_zeros if is_eof else 0)
            if is_eof:
                return
