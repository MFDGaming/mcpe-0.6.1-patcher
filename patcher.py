# Copyright Alexander Argentakis
# Repo: https://github.com/MFDGaming/mcpe-0.6.1-patcher
# This file is licensed under the MIT license

import struct
import sys


MAGIC = b"\xff\x50\x54\x50"
OP_CODES = b"\xaa\xdd\xee"
MINECRAFT_VERSION = 209

def log(text) -> None:
    print("[PATCHER] > " + text)

class Header:
    def __init__(self):
        self.minecraft_version = 0
        self.patch_count = 0
        self.indices = b""

class Patcher:
    def __init__(self, patch_path):
        self.patch_path = patch_path
        self.header = Header()
        self.patch_array = b""
        self.count = 0
        self.name = ""

    def get_minecraft_version(self):
        return self.patch_array[4]

    def get_patch_count(self):
        return self.patch_array[5]

    def get_indices(self):
        indices = b""
        for i in range(6, self.header.patch_count * 4 + 6):
            indices += self.patch_array[i:i+1]
        return indices

    def load_patch(self):
        file = open(self.patch_path, "rb")
        self.patch_array = file.read()
        file.close()
        self.header.minecraft_version = self.get_minecraft_version()
        self.header.patch_count = self.get_patch_count()
        self.header.indices = self.get_indices()
        self.count = 0

    def get_index(self, count):
        offset = count * 4
        return struct.unpack(">I", self.header.indices[offset:offset+4])[0]

    def get_current_index(self):
        return self.get_index(self.count)

    def get_next_address(self):
        index = self.get_current_index()
        return struct.unpack(">I", self.patch_array[index:index+4])[0]

    def get_data_length(self):
        start = self.get_current_index() + 4
        end = len(self.patch_array) if self.count == (self.header.patch_count - 1) else self.get_index(self.count + 1)
        return end - start

    def get_next_data(self):
        data = b""
        index = self.get_current_index()
        for i in range(self.get_data_length()):
            offset = i + (index + 4)
            data += self.patch_array[offset:offset+1]
        return data

    def apply_patch(self, library_path):
        file = open(library_path, "rb");
        data = list(file.read())
        file.close()
        while self.count < self.header.patch_count:
            offset = self.get_next_address()
            code = self.get_next_data()
            print(offset)
            data[offset:offset+len(code)] = list(code)
            self.count += 1
        patched_file = open(library_path, "wb")
        patched_file.write(bytes(data))
        patched_file.close()

def main() -> None:
    if len(sys.argv) > 2:
        log("Patching please wait...")
        patcher = Patcher(sys.argv[2])
        patcher.load_patch()
        patcher.apply_patch(sys.argv[1])
        log("Patched.")
    else:
        print(sys.argv[0] + " 'library_path'" + " 'patch_path'")

if __name__ == "__main__":
    main()
