import os
import uuid
import redis
import time

redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_host = redis_host or "redis"
steps = [5000, 15000, 30000]
print(f':: REDIS_HOST: {redis_host}, STEPS: {steps}')

r = redis.Redis(host=redis_host)

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
        K = ''.join([bin(x)[2:].zfill(512) for x in k])  # bin repr 2048 chars
        V = ''.join([bin(y)[2:].zfill(512) for y in v])  # bin repr 6144 chars
        r.set(K, V)

    delta = time.time() - t
    print(f'INSERT OF {len(ks)} TOOK {delta:.3f}s '
        f'({int(step/delta)} op/s)', flush=True)

    # RETRIEVE KEYS AND VALUES
    t = time.time()
    for k, orig_v in zip(ks, vs):
        K = ''.join([bin(x)[2:].zfill(512) for x in k])
        V = r.get(K).decode()
        v = [int(x, 2) for x in list(map(''.join, zip(*[iter(V)]*512)))]
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
        K = ''.join([bin(x)[2:].zfill(512) for x in k])
        r.delete(K)

    delta = time.time() - t
    print(f'REMOVAL OF {len(ks)} TOOK {delta:.3f}s '
        f'({int(step/delta)} op/s)', flush=True)

    # END
    print(f':: END STEP {step}')