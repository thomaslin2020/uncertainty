string = 'digraph {\n\t0 [label=\"(2±4)\"]\n\t1 [label=2]\n\t2 [label=\"+\"]\n\t0 -> 2\n\t1 -> 2\n\t3 [label=\"(4±4)\"]\n\t2 -> 3\n}'

temp = ''.join(s for s in string if ord(s) > 31 and ord(s) < 126 or s == '±')
print(temp)
