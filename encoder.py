from typing import BinaryIO

from huffman_tree import HuffmanTree


BUFFER_SIZE = 1024


class Encoder:
    def __init__(self, input_file: BinaryIO, output_file: BinaryIO):
        pass

    def build_tree(self):
        pass

    def write_header(self):
        pass

    def encode(self, data: bytes):
        pass

    def flush(self):
        pass
