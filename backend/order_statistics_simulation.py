import numpy as np
import matplotlib.pyplot as plt

# Random transmission times
Tf = np.random.exponential(1000, 10000)

Nlist = [1,5,10,20]

for N in Nlist:
    samples = np.min(np.random.choice(Tf, (N, 5000)), axis=0)
    plt.plot(np.sort(samples), label=f"N={N}")

plt.xlabel("Time")
plt.ylabel("Detection Probability")
plt.title("Order Statistics: Multi Message Propagation")
plt.legend()
plt.show()
