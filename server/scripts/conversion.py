import autograd.numpy as np
from autograd import grad
import autograd as ad
from autograd import elementwise_grad as egrad  # for functions that vectorize over inputs
import matplotlib.pyplot as plt


def func(x):
    return np.cos(x) + np.sin(x)


def tanh(x):  # Define a function
    y = np.exp(-x)
    return (1.0 - y) / (1.0 + y)
#
# def tanh(x):
#     return (1.0 - np.exp(-x))  / (1.0 + np.exp(-x))

x = np.linspace(-7, 7, 200)
plt.plot(x, tanh(x),
         x, egrad(tanh)(x),                                     # first derivative
         x, egrad(egrad(tanh))(x),                              # second derivative
         x, egrad(egrad(egrad(tanh)))(x),                       # third derivative
         x, egrad(egrad(egrad(egrad(tanh))))(x),                # fourth derivative
         x, egrad(egrad(egrad(egrad(egrad(tanh)))))(x),         # fifth derivative
         x, egrad(egrad(egrad(egrad(egrad(egrad(tanh))))))(x))  # sixth derivative

plt.axis('off')
plt.savefig("tanh.png")
plt.show()

# gradient = grad(func)
# print(gradient(np.pi))
# print(np.cos(np.pi) - np.sin(np.pi))
