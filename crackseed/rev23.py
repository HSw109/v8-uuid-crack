MASK = 0xffffffffffffffff

def reverse23(val):
    """
     Extract low 23 bits (positions 22-0)
     Original: [63.............23][22...........0]
     &0x7FFFFF:     0000000000000000000...[22.......0] (get first 23 bits)
                                              ▲
                                            b22_0
    a_low = b22_0 
    """
    a_low = val & 0x7FFFFF  
    
    """
     Extract mid 23 bits (positions 45-23)
     Original: [63.............46][45.............23][22...........0]
     >>23:     0000000000000000000...[63.............46][45.............23] (now in bits 22-0 position)
                                                                ▲
                                                              b45_23
    a_mid = b45_23 ^ a_low
    """
    a_mid = ((val >> 23) & 0x7FFFFF) ^ a_low  # Using mask to keep only right most 17 bits after shift
    
    """
     Extract high 18 bits (positions 63-46)
     Original: [63.............46][45...........0]
     >>46:     0000000000000000000...[63.............46] (now in bits 17-0 position)
                                              ▲
                                            b63_46
    a_high = b63_46 ^ a_mid
    """
    a_high = ((val >> 46) & 0x3FFFF) ^ a_mid  # No need to use mask, cause the redundant right most bits aren't affect the result of XOR
    
    
    # Concatinate all with OR operation
    return (
        (a_high << 46) |
        (a_mid << 23) |
        a_low
    ) & MASK

def xor23(val):
    """XOR with 23-bit right shift"""
    return (val ^ (val << 23)) & MASK

def check():
    a = 0x123456789abcdef
    b = xor23(a)
    c = reverse23(b)
    print(hex(a), hex(b), hex(c))

if __name__ == "__main__":
    check()


