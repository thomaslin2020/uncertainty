import math

pi = math.pi
e = math.e
R = 8.31


class Constants:
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def __add__(self, other):
        return Constants(self.value + other.value, 0)

    def __str__(self):
        return str(self.value)


print(Constants(pi, 0) + Constants(R, 0))
"""
Avogadro’s constant (𝐿𝐿 or 𝑁𝑁𝐴𝐴) = 6.02 × 1023 mol−1
Gas constant (𝑅𝑅) = 8.31 J K−1 mol−1
Molar volume of an ideal gas at STP = 2.27 × 10−2 m3 mol−1 = 22.7 dm3 mol−1
1 dm3 = 1 litre = 1 × 10−3 m3 = 1 × 103 cm3
STP conditions = 273 K and 100 kPa
SATP conditions = 298 K and 100 kPa
Speed of light = 3.00 × 108 ms−1
Specific heat capacity of water = 4.18 kJ kg−1K−1 = 4.18 J g−1 K−1
Planck’s constant (ℎ) = 6.63 × 10−34 J s
Faraday’s constant (𝐹𝐹) = 9.65 × 104 C mol−1
Ionic product constant for water (𝐾𝐾w) = 1.00 × 10−14 mol2 dm−6 at 298 K
1 amu = 1.66 × 10−27 kg
"""

z = 1 + 2j
print(z * 2)
