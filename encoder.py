from typing import BinaryIO

from huffman_tree import HuffmanTree


INPUT_BUFFER_SIZE = 1024
OUTPUT_BUFFER_SIZE = 1024


class Encoder:
    def __init__(self, input_file: BinaryIO, output_file: BinaryIO):
        self.input_file = input_file
        self.output_file = output_file

    def generate_header(self):
        pass

    def write_header(self):
        pass

    def _encode(self, data: bytes) -> None:
        pass

    def __call__(self):
        pass

    def flush(self):
        pass
