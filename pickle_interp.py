import pickle
from scipy.interpolate import interp1d

adjustment_factors = {
  45: 4.286,
  30: 3.158,
  25: 2.727,
  20: 2.297,
  15: 1.846,
  10: 1.459,
  8: 1.337,
  6: 1.228,
  4: 1.135,
  2: 1.055,
  0: 1.0,
  -2: 0.96,
  -4: 0.918,
  -6: 0.891,
  -8: 0.876,
  -10: 0.876,
  -15: 0.941,
  -20: 1.081,
  -25: 1.273,
  -30: 1.495,
  -45: 2.096
}
interp_fn = interp1d(list(adjustment_factors.keys()), list(adjustment_factors.values()))

f = open('gap_interp', 'ab')
pickle.dump(interp_fn, f)
f.close()

with open('gap_interp', 'rb') as f:
  fnc = pickle.load(f)

print(fnc)
print(fnc(10))