import itertools
from random import randint

key1 = itertools.permutations('QFS01LVmOPZ4G', 5)
rand = randint(1, 154440)
a = [i for i in key1]
key1 = "".join(a[rand])