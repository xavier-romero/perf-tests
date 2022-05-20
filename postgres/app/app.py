import os
import uuid
import psycopg2
import time

host = os.environ.get('POSTGRES_HOST')
user = os.environ.get('POSTGRES_USER')
passw = os.environ.get('POSTGRES_PASSWORD')
db = os.environ.get('POSTGRES_DB')

steps = [5000, 15000, 30000]
conn = psycopg2.connect(host=host, database=db, user=user, password=passw)
command = """
    CREATE TABLE kv (
        k VARCHAR(256) PRIMARY KEY,
        v VARCHAR(768) NOT NULL
    )
    """
cur = conn.cursor()
cur.execute(command)
conn.commit()


for step in steps:
    print(f':: STEP {step}')
    ks = []
    vs = []

    # INITIALIZE KEYS AND VALUES
    t = time.time()
    for _ in range(step):
        k = []
        v = []

        # K = 4 numbers 64 bytes each
        for _ in range(4):
            k.append(uuid.uuid4().int & (1 << 64)-1)

        # V = 12 numbers 64 bytes each
        for _ in range(12):
            v.append(uuid.uuid4().int & (1 << 64)-1)

        ks.append(k)
        vs.append(v)

    delta = time.time() - t
    print(f'GENERATION OF {len(ks)} TOOK {delta:.3f}s '
          f'({int(step/delta)} op/s)', flush=True)

    # STORE KEYS AND VALUES
    t = time.time()
    for k, v in zip(ks, vs):
        K = ''.join([bin(x)[2:].zfill(64) for x in k])
        V = ''.join([bin(y)[2:].zfill(64) for y in v])
        sql = """INSERT INTO kv(k, v) VALUES(%s, %s);"""
        cur.execute(sql, (K, V))
    conn.commit()

    delta = time.time() - t
    print(f'INSERT OF {len(ks)} TOOK {delta:.3f}s '
          f'({int(step/delta)} op/s)', flush=True)

    # RETRIEVE KEYS AND VALUES
    t = time.time()
    for k, orig_v in zip(ks, vs):
        K = ''.join([bin(x)[2:].zfill(64) for x in k])
        sql = """SELECT v from kv where k=%s;"""
        cur.execute(sql, (K,))
        V = cur.fetchone()[0]

        v = [int(x, 2) for x in list(map(''.join, zip(*[iter(V)]*64)))]
        try:
            assert(v == orig_v)
        except AssertionError:
            print(f'v:{v} orig_V:{orig_v}')
            raise

    delta = time.time() - t
    print(f'RETRIEVAL OF {len(ks)} TOOK {delta:.3f}s '
        f'({int(step/delta)} op/s)', flush=True)

    # DELETE KEYS AND VALUES
    t = time.time()
    for k in ks:
        K = ''.join([bin(x)[2:].zfill(64) for x in k])
        sql = """delete from kv where k=%s;"""
        cur.execute(sql, (K,))
    conn.commit()

    delta = time.time() - t
    print(f'REMOVAL OF {len(ks)} TOOK {delta:.3f}s '
        f'({int(step/delta)} op/s)', flush=True)

    # END
    print(f':: END STEP {step}')
