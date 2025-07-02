MASK = 0xffffffffffffffff

def reverse17(val):
    """
     Extract highest 17 bits (positions 63-47)
     Original: [63.............47][46.............30][29.............13][12...0]
     >>47:     0000000000000000000...[63.............47] (now in bits 16-0 position)
                                            ▲
                                          b63_47
    a_high = b63_47 
    """
    a_high = val >> 47  # No need to masked, cause the firest 47 bits are all 0
    
    """
     Extract mid high 17 bits (positions 46-30)
     Original: [63.............47][46.............30][29.............13][12...0]
     >>30:     0000000000000000000...[63.............47][46.............30] (now in bits 16-0 position)
                                                                ▲
                                                              b46_30
    a_mid_high = b46_30 ^ a_high
    """
    a_mid_high = ((val >> 30) & 0x1FFFF) ^ a_high  # Using mask to keep only right most 17 bits after shift
    
    """
     Extract mid low 17 bits (positions 29-13)
     Original: [63.............47][46.............30][29.............13][12...0]
     >>13:     0000000000000000000...[63.............47][46.............30][29.............13] (now in bits 16-0 position)
                                                                                    ▲
                                                                                  b29_13
    a_mid_low = b29_13 ^ a_mid_high
    """
    a_mid_low = ((val >> 13) & 0x1FFFF) ^ (a_mid_high)  # Using mask to keep only right most 17 bits after shift
    
    """
     Extract low 13 bits (positions 12-0)
     Original: [63.............47][46.............30][29.............13][12...0]
     &0x1FFF:     0000000000000000000...[12.......0] (get first 13 bits)
                                              ▲
                                            b12_0

    But after >> 17, the original [29...13] qill be shifted to [12...-4], the right most 4 bits are not involved in the xor operation => we need to remove them by (>> 4) 

    a_low = b12_0 ^ (a_mid_low >> 4)
                           ▲
                         a29_17
    """
    a_low = (val & 0x1FFF) ^ (a_mid_low >> 4)  # 13 bits need 17-4=13 shift
    
    # Concatinate all with OR operation
    return (
        (a_high << 47) |
        (a_mid_high << 30) |
        (a_mid_low << 13) |
        a_low
    ) & MASK

def xor17(val):
    """XOR with 17-bit right shift"""
    return (val ^ (val >> 17)) & MASK

def check():
    a = 0x123456789abcdef
    b = xor17(a)
    c = reverse17(b)
    print(hex(a), hex(b), hex(c))



if __name__ == "__main__":
    check()