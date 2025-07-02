import z3

"""
Feed >= 4 numbers to achieve the most-correct result.
"""
input = [0.40964814799790417, 0.18708215427060482, 0.8575164809521881, 0.8325001157289675, 0.6619077510736652]

"""
Why LIFO:

1. https://github.com/v8/v8/blob/dd5370d3d251320f6a5bed609ff8e1b71c767d97/src/numbers/math-random.cc#L68

   Tagged<Smi> new_index = Smi::FromInt(kCacheSize);  // kCacheSize = 64
   native_context->set_math_random_index(new_index);

2. https://github.com/v8/v8/blob/dd5370d3d251320f6a5bed609ff8e1b71c767d97/src/builtins/math.tq#L517

   let smiIndex: Smi = *NativeContextSlot(ContextSlot::MATH_RANDOM_INDEX_INDEX);
   if (smiIndex == 0) {
      // refill math random.
      smiIndex = RefillMathRandom(context);
   }
   const newSmiIndex: Smi = smiIndex - 1;       // Decrement the index (kCacheSize = 64) 
   *NativeContextSlot(ContextSlot::MATH_RANDOM_INDEX_INDEX) = newSmiIndex;
"""

input = input[::-1]

solver = z3.Solver()

state0, state1 = z3.BitVecs("state0 state1", 64)

"""
Symbolic execution of xorshift128+

// https://github.com/v8/v8/blob/dd5370d3d251320f6a5bed609ff8e1b71c767d97/src/base/utils/random-number-generator.h#L121

   static inline void XorShift128(uint64_t* state0, uint64_t* state1) {
      uint64_t s1 = *state0;
      uint64_t s0 = *state1;
      *state0 = s0;
      s1 ^= s1 << 23;
      s1 ^= s1 >> 17;
      s1 ^= s0;
      s1 ^= s0 >> 26;
      *state1 = s1;
   }

"""
def sym_xs128(solver, s0, s1, generated):
   # XorShift128+ forward step
   new_s0 = s1
   new_s1 = s0 
   new_s1 ^= (new_s1 << 23)
   new_s1 ^= z3.LShR(new_s1, 17)
   new_s1 ^= new_s0
   new_s1 ^= z3.LShR(new_s0, 26)

   """
According to the new version of toDouble(), now we don't need to understand the mantissa things to predict.
Testing in JavaScript V8 13.7.152.10

// https://github.com/v8/v8/blob/dd5370d3d251320f6a5bed609ff8e1b71c767d97/src/base/utils/random-number-generator.h#L111
   static inline double ToDouble(uint64_t state0) {
      // Get a random [0,2**53) integer value (up to MAX_SAFE_INTEGER) by dropping
      // 11 bits of the state.
      double random_0_to_2_53 = static_cast<double>(state0 >> 11);
      // Map this to [0,1) by division with 2**53.
      constexpr double k2_53{static_cast<uint64_t>(1) << 53};
      return random_0_to_2_53 / k2_53;
   }   
   """
   observed = int(round(generated * (1 << 53)))
   solver.add(z3.LShR(new_s0, 11) == observed)

   return new_s0, new_s1

def solve_state(input):
   solver.reset()
   sym_s0, sym_s1 = state0, state1
   for val in input:
      sym_s0, sym_s1 = sym_xs128(solver, sym_s0, sym_s1, val)

   if solver.check() == z3.sat:
      model = solver.model()
      print("state0 =", model[state0].as_long())
      print("state1 =", model[state1].as_long())
      return model[state0].as_long(), model[state1].as_long()
   
   else:
      print("No solution found")
      return None, None 

if __name__ == "__main__":
    #state0 = 9905731058272958205
    #state1 = 12210042884460550825
    #next number: 0.5369907566718337
    solve_state(input)



    