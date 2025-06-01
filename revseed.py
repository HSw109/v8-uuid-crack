from xs128 import solve_state
from rev23 import reverse23
from rev17 import reverse17

nums = [0.2074571142070556, 0.7094906253548635, 0.2090917477572467, 0.8971264835207703]

MASK = 0xffffffffffffffff

def murmurhash3(h):
    h ^= h >> 33
    h = (h * 0xFF51AFD7ED558CCD) & MASK
    h ^= h >> 33
    h = (h * 0xC4CEB9FE1A85EC53) & MASK
    h ^= h >> 33
    return h

def murmurhash3_inverse(h):
    h ^= h >> 33
    h = (h * 0x9CB4B2F8129337DB) & MASK
    h ^= h >> 33
    h = (h * 0x4F74430C22A54005) & MASK
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


