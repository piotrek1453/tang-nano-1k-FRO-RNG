#!/usr/bin/env python3
import math
import sys

import numpy as np

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <path_to_binary_file>")
    sys.exit(1)

file_path = sys.argv[1]

# Load binary data
with open(file_path, "rb") as f:
    data = f.read()

# Convert bits to bytes
bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

# Bias
p1 = bits.mean()
bias = abs(p1 - 0.5)


# Autocorrelation lag 1..100
def autocorr(x, lag):
    if lag >= len(x):
        return 0
    return np.corrcoef(x[:-lag], x[lag:])[0, 1]


ac = [autocorr(bits, i) for i in range(1, 101)]

# Entropy
p0 = 1 - p1
H = -(p1 * math.log2(p1) + p0 * math.log2(p0))

print(f"File: {file_path}")
print("bias:", bias)
print("entropy:", H)
print("max autocorr:", max(map(abs, ac)))
