import os
from random import randint
import plyvel
import time

db = plyvel.DB('/tmp/testdb/', create_if_missing=True)

# test_size_kbytes = 1024 * 1024 * 1
test_size_kbytes = 1024 * 1024 * 2

# k = 4 * 8 = 32 bytes, v = 12 * 8 = 96 bytes, total = 128 bytes
test_size = int((test_size_kbytes * 1024) / 128)
read_test_size = int(test_size / 100)

write_report_step = 40960  # each 5MB of data, 1MB = 8192 iterations
delete_report_step = 40960
read_report_step = 10

# INITIALIZE KEYS AND VALUES
print(f"WRITE | TEST_SIZE: {test_size} | REPORT_STEP: {write_report_step}")
start = time.time()
t = start
for i in range(test_size):
    my_64bits = i.to_bytes(8, 'big')
    k = my_64bits + my_64bits + my_64bits + my_64bits
    v = my_64bits + my_64bits + my_64bits + my_64bits + \
        my_64bits + my_64bits + my_64bits + my_64bits + \
        my_64bits + my_64bits + my_64bits + my_64bits
    sql = """INSERT INTO kv(k, v) VALUES(%s, %s);"""
    db.put(k, v)
    if i and i % write_report_step == 0:
        delta = time.time() - t
        total_time = time.time() - start
        print(
            f'Partial of {write_report_step} took {delta:.3f} '
            f'({int(write_report_step/delta)}op/s). '
            f'TOTAL: {i} ({int((i*128)/1024/1024)}MB), '
            f'Avg of {int(i/total_time)}op/s.',
            flush=True
        )
        t = time.time()

# RETRIEVE KEYS AND VALUES
print(f"READ | TEST SIZE: {read_test_size} | REPORT STEP: {read_report_step}")
start = time.time()
t = start
for i in range(read_test_size):
    my_64bits = randint(0, test_size).to_bytes(8, 'big')
    k = my_64bits + my_64bits + my_64bits + my_64bits
    expected_v = my_64bits + my_64bits + my_64bits + my_64bits + \
        my_64bits + my_64bits + my_64bits + my_64bits + \
        my_64bits + my_64bits + my_64bits + my_64bits

    v = db.get(k)
    assert(v == expected_v)

    if i and i % read_report_step == 0:
        delta = time.time() - t
        total_time = time.time() - start
        print(
            f'Partial of {read_report_step} took {delta:.3f} '
            f'({int(read_report_step/delta)}op/s). '
            f'TOTAL: {i} ({int((i*128)/1024/1024)}MB), '
            f'Avg of {int(i/total_time)}op/s.',
            flush=True
        )
        t = time.time()

# DELETE KEYS AND VALUES
print(f"DELETE | TEST_SIZE: {test_size} | REPORT_STEP: {delete_report_step}")
start = time.time()
t = start
for i in range(test_size):
    my_64bits = i.to_bytes(8, 'big')
    k = my_64bits + my_64bits + my_64bits + my_64bits
    db.delete(k)

    if i and i % delete_report_step == 0:
        delta = time.time() - t
        total_time = time.time() - start
        print(
            f'Partial of {delete_report_step} took {delta:.3f} '
            f'({int(delete_report_step/delta)}op/s). '
            f'TOTAL: {i} ({int((i*128)/1024/1024)}MB), '
            f'Avg of {int(i/total_time)}op/s.',
            flush=True
        )
        t = time.time()
