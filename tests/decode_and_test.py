#!/usr/bin/env python3
import os
import re
import subprocess
from glob import glob

# Folders
input_dir = "data/input"
ascii_dir = "data/output/ascii"
binary_dir = "data/output/binary"

os.makedirs(ascii_dir, exist_ok=True)
os.makedirs(binary_dir, exist_ok=True)

# Get all .txt files from output/ dir
input_files = glob(os.path.join(input_dir, "*.txt"))
print(
    f"\n{'#' * 20} Input files:  {'#' * 20}\n{', '.join(char for char in input_files)}\n"
)

for input_file in input_files:
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    ascii_file = os.path.join(ascii_dir, f"{base_name}.txt")
    binary_file = os.path.join(binary_dir, f"{base_name}.bin")

    byte = 0
    count = 0

    with (
        open(input_file) as f,
        open(ascii_file, "w") as out_ascii,
        open(binary_file, "wb") as out_bin,
    ):
        for line in f:
            m = re.search(r"Items:\s*([01])", line)
            if not m:
                continue
            bit = int(m.group(1))

            # ASCII output
            out_ascii.write(str(bit))

            # Binary output
            byte = (byte << 1) | bit
            count += 1
            if count == 8:
                out_bin.write(bytes([byte]))
                byte = 0
                count = 0

        # pad last byte if shorter than 8 bits
        if count > 0:
            byte <<= 8 - count
            out_bin.write(bytes([byte]))

    print(f"Processed {input_file}")
    print(f"  ASCII output: {ascii_file}")
    print(f"  Binary output: {binary_file}")

    # Run tests on binary output
    test_commands = [
        ["ent", binary_file],  # basic statistical parameters
        ["dieharder", "-a", "-f", binary_file],  # dieharder test suite
    ]

    for test in test_commands:
        print(
            f"\n{'#' * 20} RUNNING TEST {' '.join(str(char) for char in test)} {'#' * 20}\n"
        )
        process = subprocess.Popen(
            test, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in process.stdout:  # type: ignore
            print(line, end="")
        process.wait()
        print(
            f"\n{'#' * 20} FINISHED TEST {' '.join(str(char) for char in test)} {'#' * 20}\n"
        )
