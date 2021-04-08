from typing import BinaryIO
import sys
import os


def try_open_output_file(input_file_stat) -> BinaryIO:
    try:
        output_file = open(sys.argv[2])
        output_stat = os.fstat(output_file.fileno())
        if input_file_stat.st_ino == output_stat.st_ino and input_file_stat.st_dev == output_stat.st_dev:
            print(f"Error: '{sys.argv[1]}' and '{sys.argv[2]}' are the same file")
            exit(1)
        output_file.close()
    except FileNotFoundError:
        pass
    return open(sys.argv[2], 'wb')


def main() -> None:
    usage_msg = "Usage:\n    python main.py --compress /path/to/file /path/to/output/file.hc\n"\
        "Or\n    python main.py --decompress /path/to/file.hc /path/to/output/file\n"\
        "(default behavior is compressing)"
    if len(sys.argv) not in (3, 4):
        print(
            usage_msg,
            file=sys.stdout if '-h' in sys.argv or '--help' in sys.argv else sys.stderr
        )
        exit(1)
    compress = True
    if sys.argv[1].startswith("--"):
        if sys.argv[1] == "--decompress":
            compress = False
        elif sys.argv[1] == "--compress":
            compress = True
        else:
            print(usage_msg)
            exit(1)
        del sys.argv[1]
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    if not os.path.isfile(input_file_name):
        print(f"Can not find '{input_file_name}' file", file=sys.stderr)
        exit(1)
    input_file = None
    input_stat = None
    try:
        input_file = open(input_file_name, 'rb')
        input_stat = os.fstat(input_file.fileno())
    except PermissionError:
        print(f"Can not open '{input_file_name}' (permission denied)", file=sys.stderr)
        exit(1)
    output_file = None
    if os.path.isfile(output_file_name):
        print(f"Output file '{output_file_name}' already exists. Would you like to rewrite it? [Y/n] ", end='')
        if input() in ('', 'Y', 'y'):
            try:
                output_file = try_open_output_file(input_stat)
            except PermissionError:
                print(f"Can not open '{output_file_name}' (permission denied)", file=sys.stderr)
                exit(1)
        else:
            print("Aborted")
            exit()
    else:
        try:
            os.makedirs(os.path.dirname(output_file_name) or '.', exist_ok=True)
            output_file = try_open_output_file(input_stat)
        except (FileNotFoundError, PermissionError):
            print(f"Can not open file '{output_file_name}' for writing")
            exit(1)
        except IsADirectoryError:
            print(f"'{output_file_name}' is a directory")
            exit(1)
    #complete_firmware_file(output_file, input_file, input_stat.st_size)
    print("Done!")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("Exit")
