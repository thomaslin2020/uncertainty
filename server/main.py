from server.operators import *
from server.simple import SimpleUncertainty

c = SimpleUncertainty(3, 2)
print(cos(c))
print(eval('log(c)'))

# TODO: Prove that binary is the same as together
