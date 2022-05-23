import os
import psycopg2
import time

host = os.environ.get('POSTGRES_HOST')
user = os.environ.get('POSTGRES_USER')
passw = os.environ.get('POSTGRES_PASSWORD')
db = os.environ.get('POSTGRES_DB')

test_size_kbytes = 1024 * 1024 * 1

# k = 4 * 8 = 32 bytes, v = 12 * 8 = 96 bytes, total = 128 bytes
step = int((test_size_kbytes * 1024) / 128)
print(f"STEP: {step}")

conn = psycopg2.connect(host=host, database=db, user=user, password=passw)
command = """
    CREATE TABLE kv (
        k bytea,
        v bytea
    )
    """
cur = conn.cursor()
cur.execute(command)
conn.commit()

# INITIALIZE KEYS AND VALUES
t = time.time()
for i in range(step):
    my_64bits = i.to_bytes(8, 'big')
    k = my_64bits + my_64bits + my_64bits + my_64bits
    v = my_64bits + my_64bits + my_64bits + my_64bits + \
        my_64bits + my_64bits + my_64bits + my_64bits + \
        my_64bits + my_64bits + my_64bits + my_64bits
    sql = """INSERT INTO kv(k, v) VALUES(%s, %s);"""
    cur.execute(sql, (k, v))
    if i % 8192 == 0:
        conn.commit()
        delta = time.time() - t
        print(f'INSERT OF {i} ({int((i*128)/1024/1024)}MB) TOOK {delta:.3f}s '
              f'({int(i/delta)} op/s)', flush=True)

# # RETRIEVE KEYS AND VALUES
# t = time.time()
# for k, orig_v in zip(ks, vs):
#     K = ''.join([bin(x)[2:].zfill(64) for x in k])
#     sql = """SELECT v from kv where k=%s;"""
#     cur.execute(sql, (K,))
#     V = cur.fetchone()[0]

#     v = [int(x, 2) for x in list(map(''.join, zip(*[iter(V)]*64)))]
#     try:
#         assert(v == orig_v)
#     except AssertionError:
#         print(f'v:{v} orig_V:{orig_v}')
#         raise

# delta = time.time() - t
# print(f'RETRIEVAL OF {len(ks)} TOOK {delta:.3f}s '
#     f'({int(step/delta)} op/s)', flush=True)

# # DELETE KEYS AND VALUES
# t = time.time()
# for k in ks:
#     K = ''.join([bin(x)[2:].zfill(64) for x in k])
#     sql = """delete from kv where k=%s;"""
#     cur.execute(sql, (K,))
# conn.commit()

# delta = time.time() - t
# print(f'REMOVAL OF {len(ks)} TOOK {delta:.3f}s '
#     f'({int(step/delta)} op/s)', flush=True)

# # END
# print(f':: END STEP {step}')
