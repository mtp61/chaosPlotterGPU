import numpy as np
import pygame
import time

magnets = [
    (-56, 1, 10),
    (55, 2, 10),
    (0, 55, -10),
    (-58, 56, -10),
    (55, 57, -10),
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
resX = 20
resY = 20

numPoints = resX * resY
gapX = (maxX - minX) / (resX - 1)
gapY = (maxY - minY) / (resY - 1)

# generate arm starting locations
armX = np.empty(numPoints, dtype=np.single)
armY = np.empty(numPoints, dtype=np.single)
for i in range(resX):
    for j in range(resY):
        armX[i * resY + j] = minX + i * gapX
        armY[i * resY + j] = minY + j * gapY

# velocity
velX = np.zeros(numPoints)
velY = np.zeros(numPoints)

# setup pygame
pygame.init()
screen = pygame.display.set_mode([800, 800])

# tick
i = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # draw
    screen.fill((255, 255, 255))

    pygame.draw.circle(screen, (0, 0, 0), (400, 400), 5)
    pygame.draw.circle(screen, (100, 100, 100), (int(armX[0]) + 400, int(armY[0]) + 400), 10)
    for (x, y, c) in magnets:
        pygame.draw.circle(screen, (255, 0, 0) if c > 0 else (0, 0, 255), (x + 400, y + 400), 10)

    pygame.display.update()

    for _ in range(5): # TODO
        i += 1
        if i % 100 == 0:
            print(i)
        
        # acceleration
        accX = np.zeros(numPoints)
        accY = np.zeros(numPoints)
        
        # add for home (assuming at (0, 0))
        deltaX = np.zeros(numPoints) - armX
        deltaY = np.zeros(numPoints) - armY
        
        # mag = np.power(np.power(deltaX, 2) + np.power(deltaY, 2), .5)
        # accX += (homeCoef / 10000) * (deltaX * mag)
        # accY += (homeCoef / 10000) * (deltaY * mag)  

        magSquared = np.power(deltaX, 2) + np.power(deltaY, 2)
        mag = np.sqrt(magSquared)
        force = np.minimum((homeCoef / 10000) * magSquared, np.repeat(maxForce, numPoints))
        accX += force * deltaX / mag
        accY += force * deltaY / mag

        # add for magnets
        for (x, y, c) in magnets:
            deltaX = np.repeat(x, numPoints) - armX
            deltaY = np.repeat(y, numPoints) - armY

            # mag32 = np.power(np.power(deltaX, 2) + np.power(deltaY, 2), 1.5)
            # accX += (c * 10000) * (deltaX / mag32)
            # accY += (c * 10000) * (deltaY / mag32)

            magSquared = np.power(deltaX, 2) + np.power(deltaY, 2)
            mag = np.sqrt(magSquared)
            force = np.minimum((c * 10000) / magSquared, np.repeat(maxForce, numPoints))
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

    time.sleep(1 / 60)
