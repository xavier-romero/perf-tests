import os
from random import randint
import psycopg2
import time

host = os.environ.get('POSTGRES_HOST')
user = os.environ.get('POSTGRES_USER')
passw = os.environ.get('POSTGRES_PASSWORD')
db = os.environ.get('POSTGRES_DB')

# test_size_kbytes = 1024 * 1024 * 1
test_size_kbytes = 1024 * 1024 * 1

# k = 4 * 8 = 32 bytes, v = 12 * 8 = 96 bytes, total = 128 bytes
test_size = int((test_size_kbytes * 1024) / 128)
read_test_size = int(test_size / 10)

write_report_step = 40960  # each 5MB of data, 1MB = 8192 iterations
delete_report_step = 40960
read_report_step = 20480

conn = psycopg2.connect(host=host, database=db, user=user, password=passw)
command = """
    CREATE TABLE kv (
        k VARCHAR(256) PRIMARY KEY,
        v VARCHAR(768)
    )
    """
cur = conn.cursor()
# cur.execute(command)
# conn.commit()

# INITIALIZE KEYS AND VALUES
# print(f"WRITE | TEST_SIZE: {test_size} | REPORT_STEP: {write_report_step}")
# start = time.time()
# t = start
# for i in range(test_size):
#     i_bin = bin(i)[2:].zfill(64)
#     k = ''.join(i_bin for _ in range(4))
#     v = ''.join(i_bin for _ in range(12))
#     sql = """INSERT INTO kv(k, v) VALUES(%s, %s);"""
#     cur.execute(sql, (k, v))
#     if i and i % write_report_step == 0:
#         conn.commit()
#         delta = time.time() - t
#         total_time = time.time() - start
#         print(
#             f'Partial of {write_report_step} took {delta:.3f} '
#             f'({int(write_report_step/delta)}op/s). '
#             f'TOTAL: {i} ({int((i*128)/1024/1024)}MB), '
#             f'Avg of {int(i/total_time)}op/s.',
#             flush=True
#         )
#         t = time.time()
# conn.commit()

# RETRIEVE KEYS AND VALUES
print(f"READ | TEST SIZE: {read_test_size} | REPORT STEP: {read_report_step}")
start = time.time()
t = start
for i in range(read_test_size):
    i_bin = bin(randint(0, test_size))[2:].zfill(64)
    k = ''.join(i_bin for _ in range(4))
    expected_v = ''.join(i_bin for _ in range(12))

    sql = """SELECT v from kv where k=%s;"""
    cur.execute(sql, (k,))
    v = cur.fetchone()[0]
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
    i_bin = bin(i)[2:].zfill(64)
    k = ''.join(i_bin for _ in range(4))
    sql = """delete from kv where k=%s;"""
    cur.execute(sql, (k,))

    if i and i % delete_report_step == 0:
        conn.commit()
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
conn.commit()
