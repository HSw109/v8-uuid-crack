from xs128 import solve_state
from rev23 import reverse23
from rev17 import reverse17

nums = [0.2074571142070556, 0.7094906253548635, 0.2090917477572467, 0.8971264835207703]

MASK = 0xffffffffffffffff

"""
// https://github.com/v8/v8/blob/dd5370d3d251320f6a5bed609ff8e1b71c767d97/src/base/utils/random-number-generator.cc#L228

uint64_t RandomNumberGenerator::MurmurHash3(uint64_t h) {
    h ^= h >> 33;
    h *= uint64_t{0xFF51AFD7ED558CCD};
    h ^= h >> 33;
    h *= uint64_t{0xC4CEB9FE1A85EC53};
    h ^= h >> 33;
    return h;
}

"""

def murmurhash3(h):
    h ^= h >> 33
    h = (h * 0xFF51AFD7ED558CCD) & MASK  
    h ^= h >> 33
    h = (h * 0xC4CEB9FE1A85EC53) & MASK
    h ^= h >> 33
    return h

"""
MASK 0xffffffffffffffff (2^64 - 1) is treated as mod 2^64, cause:

a & (b-1) = a % b (b is a power of 2)

So calculate the modular inverse of 0xFF51AFD7ED558CCD and 0xC4CEB9FE1A85EC53 modulo 2^64
"""
INV_C1 = pow(0xFF51AFD7ED558CCD, -1, 1<<64)
INV_C2 = pow(0xC4CEB9FE1A85EC53, -1, 1<<64)

def murmurhash3_inverse(h):
    h ^= h >> 33
    h = (h * INV_C2) & MASK
    h ^= h >> 33
    h = (h * INV_C1) & MASK
    h ^= h >> 33
    return h

def xorshift128(state0, state1):
    s1 = state0 & MASK
    s0 = state1 & MASK

    s1 ^= (s1 << 23) & MASK
    s1 ^= (s1 >> 17) & MASK
    s1 ^= s0 & MASK
    s1 ^= (s0 >> 26) & MASK
    

    state0 = state1 & MASK
    state1 = s1 & MASK
    return state0,state1


def reverse_xorshift(s0,s1):
    prev_s0 = s1 ^ (s0 >> 26)
    prev_s0 = prev_s0 ^ s0
    prev_s0 = reverse17(prev_s0)
    prev_s0 = reverse23(prev_s0)
    return prev_s0

s0, s1 = solve_state(nums[::-1])
steps = 0

while murmurhash3_inverse(s0) != murmurhash3_inverse(s1)^MASK:
    steps += 1
    s0, s1 = reverse_xorshift(s0, s1), s0

seed = murmurhash3_inverse(s0)
assert seed == murmurhash3_inverse(s1)^MASK
print(f"recovered seed {seed} after {steps} steps")
print("Wanna predict the next (nexts) number? 1 for yes, 0 for no")
predict = input()

ns0, ns1 = murmurhash3(seed), murmurhash3(seed^MASK)

if predict == "1":
    all_predicted = []
    print("How many? Should be a multiple of 64 for in order prediction")
    cnt = int(input())
    left = cnt % 64
    num_cache_fills = cnt // 64

    for _ in range(num_cache_fills):
        for _ in range(64):
            ns0, ns1 = xorshift128(ns0, ns1)
            predicted = (ns0 >> 11) / (1 << 53) # toDouble()
            all_predicted.append(predicted)

    for _ in range(left):
        ns0, ns1 = xorshift128(ns0, ns1)
        predicted = (ns0 >> 11) / (1 << 53) # toDouble()
        all_predicted.append(predicted)

    chunks = [all_predicted[i : i + 64] for i in range(0, len(all_predicted), 64)]
    for chunk in chunks:
        print(chunk[::-1])


