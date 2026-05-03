import numpy as np
import matplotlib.pyplot as plt

Rc = np.arange(5, 40, 5)
Tf = []

for rc in Rc:
    Tf.append(1000/rc + np.random.normal(0,20))

plt.plot(Rc, Tf, marker="o")
plt.xlabel("Communication Range Rc")
plt.ylabel("First Passage Time Tf")
plt.title("First Passage Time vs Communication Range")
plt.grid()
plt.show()
