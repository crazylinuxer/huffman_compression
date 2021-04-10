from typing import BinaryIO

from collections import deque


INPUT_BUFFER_SIZE = 10240


class Decoder:
    def __init__(self, input_file: BinaryIO, output_file: BinaryIO):
        self.input_file = input_file
        self.output_file = output_file
        self.coding_table = {}
        self.decoding_buffer = deque()
        self.trailing_zeros = 0

    def read_header(self) -> int:
        pass

    def _decode(self, data: bytes):
        pass

    def __call__(self):
        pass

    def flush(self):
        pass
