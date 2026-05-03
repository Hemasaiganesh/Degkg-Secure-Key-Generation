import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Swarm parameters
N = 10
AREA = 100
v = 1
lp = 10

# Initialize drones
x = np.random.rand(N) * AREA
y = np.random.rand(N) * AREA
theta = np.random.rand(N) * 2*np.pi

def move():
    global x, y, theta
    x += v * np.cos(theta)
    y += v * np.sin(theta)

    # boundary reflect
    x[:] = np.clip(x, 0, AREA)
    y[:] = np.clip(y, 0, AREA)

    # random scatter
    mask = np.random.rand(N) < (1/lp)
    theta[mask] += np.random.uniform(-np.pi, np.pi, np.sum(mask))

# Animation
fig, ax = plt.subplots()
scat = ax.scatter(x, y, c="red")

def update(frame):
    move()
    scat.set_offsets(np.c_[x, y])
    ax.set_xlim(0, AREA)
    ax.set_ylim(0, AREA)
    ax.set_title("Drone Swarm Temporal Network Simulation")
    return scat,

ani = animation.FuncAnimation(fig, update, interval=200)
plt.show()
