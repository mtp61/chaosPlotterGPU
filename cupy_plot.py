import numpy as np
import cupy as cp
import time

from plotter import plotter

iters = 50000
endIters = 100

magnets = [
    [-56, 1, 10],
    [55, 2, 10],
    [0, 55, -10],
    [-58, 56, -10],
    [55, 57, -10],
]

# misc vars
tickrate = 60
friction = .95
homeCoef = 10
maxForce = 1000

# for the plot
minX = -400
maxX = 400
minY = -400
maxY = 400
resX = 200
resY = 200

numPoints = resX * resY
gapX = (maxX - minX) / (resX - 1)
gapY = (maxY - minY) / (resY - 1)

# generate arm starting locations
armX = []
armY = []
for i in range(resX):
    for j in range(resY):
        armX.append(minX + i * gapX)
        armY.append(minY + j * gapY)

armX = cp.array(armX)  # TODO specify dtype?
armY = cp.array(armY)

# velocity
velX = cp.zeros(numPoints)
velY = cp.zeros(numPoints)

# create the arrays beforehand TODO
forceArray = cp.repeat(cp.array([maxForce]), numPoints)
for i in range(len(magnets)):
    magnets[i][0] = cp.repeat(cp.array([magnets[i][0]]), numPoints)
    magnets[i][1] = cp.repeat(cp.array([magnets[i][1]]), numPoints)
finalX = cp.zeros(numPoints)
finalY = cp.zeros(numPoints)

startTime = time.time()

# tick
for i in range(iters):
    if i % 100 == 0:
        print(i)

    # acceleration
    accX = cp.zeros(numPoints)
    accY = cp.zeros(numPoints)
    
    # add for home (assuming at (0, 0))
    deltaX = cp.subtract(cp.zeros(numPoints), armX)
    deltaY = cp.zeros(numPoints) - armY
    
    # mag = np.power(np.power(deltaX, 2) + np.power(deltaY, 2), .5)
    # accX += (homeCoef / 10000) * (deltaX * mag)
    # accY += (homeCoef / 10000) * (deltaY * mag)  

    magSquared = cp.power(deltaX, 2) + cp.power(deltaY, 2)
    mag = cp.sqrt(magSquared)
    force = cp.minimum((homeCoef / 10000) * magSquared, forceArray)
    accX += force * deltaX / mag
    accY += force * deltaY / mag

    # add for magnets
    for (x, y, c) in magnets:
        deltaX = x - armX
        deltaY = y - armY

        # mag32 = np.power(np.power(deltaX, 2) + np.power(deltaY, 2), 1.5)
        # accX += (c * 10000) * (deltaX / mag32)
        # accY += (c * 10000) * (deltaY / mag32)

        magSquared = cp.power(deltaX, 2) + cp.power(deltaY, 2)
        mag = cp.sqrt(magSquared)
        force = cp.minimum((c * 10000) / magSquared, forceArray)
        accX += force * deltaX / mag
        accY += force * deltaY / mag
    
    # not too fast!
    # accMag = np.power(np.power(accX, 2) + np.power(accY, 2), .5)
    # accMagMin = np.minimum(accMag, np.repeat(maxForce, numPoints))
    # accX *= accMagMin / accMag
    # accY *= accMagMin / accMag
    
    # update
    velX = velX + (1 / tickrate) * accX
    velY = velY + (1 / tickrate) * accY
    armX = armX + (1 / tickrate) * velX
    armY = armY + (1 / tickrate) * velY
    velX = (1 - (1 - friction) / tickrate) * velX  # friction
    velY = (1 - (1 - friction) / tickrate) * velY  # friction

    if iters - i < endIters:
        finalX += armX
        finalY += armY

finalX /= endIters
finalY /= endIters

# print time
totalTime = time.time() - startTime
print(f"took {totalTime:.0f}s, {totalTime/numPoints:.8f}s per point and {totalTime/iters:.5f}s per iter")

# save output
finalX = cp.asnumpy(finalX)
finalY = cp.asnumpy(finalY)
with open("output.txt", "w") as f:
    for i in range(numPoints):
        f.write(f"[1, 1, {finalX[i]}, {finalY[i]}]\n")

plotter(finalX, finalY)
