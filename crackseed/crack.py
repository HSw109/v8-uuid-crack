from rev23 import reverse23
from rev17 import reverse17
from sage.all import Matrix, vector, GF
from tqdm import tqdm
import itertools

MASK = 0xffffffffffffffff
INV_C1 = pow(0xFF51AFD7ED558CCD, -1, 1<<64)
INV_C2 = pow(0xC4CEB9FE1A85EC53, -1, 1<<64)


nums1 = [0.7096373763592614,0.9583317271535403,0.7239243954769161,0.9841879270784006]
nums2 = [0.44993663097264447,0.9544710086714234,0.020065368306808273,0.773864771893042]

def murmurhash3(h):
    h ^= h >> 33
    h = (h * 0xFF51AFD7ED558CCD) & MASK  
    h ^= h >> 33
    h = (h * 0xC4CEB9FE1A85EC53) & MASK
    h ^= h >> 33
    return h

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

def get_mathrand_seed(nums):
    from xs128 import solve_state
    s0, s1 = solve_state(nums[::-1])
    steps = 0
    while murmurhash3_inverse(s0) != murmurhash3_inverse(s1)^MASK:
        steps += 1
        s0, s1 = reverse_xorshift(s0, s1), s0
    seed = murmurhash3_inverse(s0)
    assert seed == murmurhash3_inverse(s1)^MASK
    return seed

seed1 = get_mathrand_seed(nums1)
seed2 = get_mathrand_seed(nums2)

print(f"seed1: {seed1}")
print(f"seed2: {seed2}")

###############################################

def init_state():
    mtx = [[0]*i + [1] + [0]*(127-i) for i in range(128)]
    return mtx[:64], mtx[64:]

def shl_sym(mtx, n):
    return mtx[n:] + [[0]*128]*n

def shr_sym(mtx, n):
    return [[0]*128]*n + mtx[:-n]

def xor_sym(a, b):
    return [[aaa^bbb for aaa, bbb in zip(aa, bb)] for aa, bb in zip(a, b)]

def xs128p_sym(old_s0, old_s1):
    s1, s0 = old_s0, old_s1
    s1 = xor_sym(s1, shl_sym(s1, 23))
    s1 = xor_sym(s1, shr_sym(s1, 17))
    s1 = xor_sym(s1, s0)
    s1 = xor_sym(s1, shr_sym(s0, 26))
    return s1

def bits_to_int(bits: list[bool]) -> int:
    return int("".join(map(str, map(int, bits))), 2)

def int_to_bits(n, length):
    return [((n >> (length - i - 1)) & 1) for i in range(length)]

def validate_solution_v8(s0, s1, count=128):
    for _ in range(count):
        if murmurhash3(s0^MASK) == s1:
            return murmurhash3_inverse(s0)
        s0, s1 = reverse_xorshift(s0, s1), s0

# set up matrix representing 8 top bits of 16 consecutive states
A = []
s0, s1 = init_state()
for _ in range(16):
    A += s0[:8]
    A += s1[:8]
    s0, s1 = s1, xs128p_sym(s0, s1)
A = Matrix(GF(2), A)

def get_root_init_bits(consecutive_seeds):
    return list(b"".join(seed.to_bytes(8, "little") for seed in consecutive_seeds))

outputs = get_root_init_bits([seed1, seed2])
print(outputs)

# 256 values of s0 guesses + 16 carry bits
attempts = itertools.product(*([range(256)] + [(0, 1)]*16))
for values in tqdm(list(attempts)):
    s0_guess = values[0]
    carry_bits = values[1:]
    
    s0_val = s0_guess

    b = []
    for o, c in zip(outputs, carry_bits):
        s1_val = (o - s0_val - c) % 256
        b += int_to_bits(s0_val, 8)
        b += int_to_bits(s1_val, 8)
        s0_val = s1_val # new s0 is old s1
    b = vector(GF(2), b)
    
    try:
        sol = A.solve_right(b)
        sol = bits_to_int(sol)
        s0, s1 = sol >> 64, sol & MASK
        seed = validate_solution_v8(s0, s1)
        if(seed):
            print(f"found isolated root seed: {seed}")
    except ValueError:
        # no solution
        pass



