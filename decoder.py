from typing import BinaryIO

BUFFER_SIZE = 1024


class Decoder:
    def __init__(self, input_file: BinaryIO, output_file: BinaryIO):
        pass

    def read_header(self):
        pass

    def decode(self, data: bytes):
        pass

    def flush(self):
        pass
