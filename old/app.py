#!/usr/local/bin/python
import merkle
import random
from time import time

level = 32
recalculate = True
mt = merkle.Tree(level=level, recalculate=recalculate)

test_size = 50000
valid_keys = {}
invalid_keys = {}
valid_values = {}

# TESTING INSERT OF KEY/VALUES
print(f"Generating test data (size={test_size})")
for i in range(test_size):
    k = random.randint(0, 2**256)
    ik = random.randint(0, 2**256)
    v = random.randint(0, 2**256)
    valid_keys[i] = k
    invalid_keys[i] = ik
    valid_values[i] = v

print(f"Storing...")
start = time()
for i in range(test_size):
    mt.store(valid_keys[i], valid_values[i])
delta = time() - start
print(f"Store done in {delta}")

# TESTING DUMP WHOLE TREE
print(f"Dumping...")
start = time()
mt.dump(silent=True)
delta = time() - start
print(f"Dump done in {delta}")

# TESTING GETTING INVALID KEYS
print(f"Getting invalid keys...")
start = time()
for i in range(test_size):
    x = mt.get(invalid_keys[i])
    assert(x == 0)
delta = time() - start
print(f"Get done in {delta}")

# TESTING GETTING VALID KEYS
print(f"Getting valid keys...")
start = time()
for i in range(test_size):
    x = mt.get(valid_keys[i])
    assert(x != 0)
delta = time() - start
print(f"Get done in {delta}")

print("Ready!", flush=True)
