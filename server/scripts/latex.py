import subprocess


def copy(data):
    subprocess.run("pbcopy", universal_newlines=True, input=data)


class Latex:
    def __init__(self, num):
        self.num = str(num)

    def __add__(self, other):
        return Latex('%s+%s' % (self.num, other))

    def __sub__(self, other):
        return Latex('%s-%s' % (self.num, other))

    def __truediv__(self, other):
        return Latex('\\frac{%s}{%s}' % (self.num, other))

    def __str__(self):
        return '$$%s$$' % self.num


L = Latex
t1 = (L(1) / 5) + 2 - 1
print(str(t1))
copy(str(t1))
