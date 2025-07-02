MASK = 0xFFFFFFFFFFFFFFFF

HEX  = "0123456789abcdef"
def generate_uuid(numbers_iter):
    uuid = ""
    for i in range(32):
        if i == 12:
            uuid += "4";  
            continue          # UUID-v4 nibble
        char = int(next(numbers_iter) * 16)
        if i == 16:                                      # variant nibble
            char = (char & 0x3) | 0x8
        uuid += HEX[char]
        if i in (7, 11, 15, 19):
            uuid += "-"
    return uuid


def murmurhash3(h):
    h ^= h >> 33
    h  = (h * 0xFF51AFD7ED558CCD) & MASK
    h ^= h >> 33
    h  = (h * 0xC4CEB9FE1A85EC53) & MASK
    h ^= h >> 33
    return h


def xorshift128(state0, state1):
    s1 = state0 & MASK
    s0 = state1 & MASK
    s1 ^= (s1 << 23) & MASK
    s1 ^= (s1 >> 17) & MASK
    s1 ^= s0
    s1 ^= (s0 >> 26)
    return s0, s1 & MASK            # new (state0, state1)


def state_to_double(state):
    return ((state >> 11) & ((1 << 53) - 1)) / (1 << 53)


def iter_math_random(seed):
    s0, s1 = murmurhash3(seed), murmurhash3(seed ^ MASK)
    while True:
        block = []
        for _ in range(64):               # V8 fills 64-entry cache
            s0, s1 = xorshift128(s0, s1)  # one RNG step
            block.append(state_to_double(s0))
        yield from block[::-1]            # served LIFO


def iter_random_seeds(root_seed):
    s0 = murmurhash3(root_seed)
    s1 = murmurhash3(s0 ^ MASK)

    out = []
    for _ in range(128):                  # 8 bytes per context seed
        byte = ((s0 + s1) & MASK) >> 56
        out.append(byte)
        s0, s1 = xorshift128(s0, s1)
        if len(out) >= 8:
            yield int.from_bytes(out[-8:], "little")


def main():
    root = 3636436853127911437
    for ctx_seed in iter_random_seeds(root):
        uuid = generate_uuid(iter_math_random(ctx_seed))
        print(uuid)


if __name__ == "__main__":
    main()
