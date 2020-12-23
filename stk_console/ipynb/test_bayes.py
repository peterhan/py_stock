from thinkbayes import *
from matplotlib import pyplot as plt
hypos=xrange(1,1001)

class Train(Suite):
    def Likelihood(self, data, hypo ):
        if hypo<data:
            return 0
        else:
            return 1.0/hypo
            
suite=Train(hypos)
print suite.d
for i in range(50,120,10):
    suite.Update(i)
    print suite.Prob(100)
    plt.plot(suite.d.values())

plt.plot(suite.d.values())
plt.show()
