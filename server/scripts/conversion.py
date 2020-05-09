from decimal import Decimal
from locale import atof


def sigfigs(o):
    temp = str(o)
    print(temp)
    if isinstance(o, float):
        if {'0'} == set(temp[temp.index('.') + 1:]):
            return len(temp) - 1
    return len(atof(temp, Decimal).as_tuple().digits)


print(sigfigs(3))




