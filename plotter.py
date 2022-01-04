import math
from PIL import Image
import ast

binColors = [(0,0,0),(255,0,0),(0,255,0),(0,0,255),(255,255,255)]
binSize = 20

def plotter(fx, fy):
    bins = []
    binNums = []
    for x in range(len(fx)):
        foundBin = False
        for y in range(len(bins)):
            if bins[y][0] < fx[x] < bins[y][1] and bins[y][2] < fy[x] < bins[y][3]:
                foundBin = True
                binNums[y] += 1
        if foundBin == False:
            bins.append([fx[x]-binSize/2, fx[x]+binSize/2, fy[x]-binSize/2, fy[x]+binSize/2])
            binNums.append(1)        
                
    print(str(len(bins))+" bins")
        
    for x in range(len(bins)):
        print(f"bin: ({bins[x][0] + binSize/2:.0f}, {bins[x][2] + binSize/2:.0f}) has {str(binNums[x])}")

    # create image
    imageSize = int(math.sqrt(len(f)))
    bitmap = Image.new("RGB", (imageSize, imageSize), "white")
    pix = bitmap.load()

    for x in range(imageSize):
        for y in range(imageSize):
            endPos = (fx[x*imageSize+y], fy[x*imageSize+y])
            # find bin
            for z in range(len(bins)):
                if bins[z][0] < endPos[0] < bins[z][1] and bins[z][2] < endPos[1] < bins[z][3]:
                    pointBin = z
            pix[x,y] = binColors[min(pointBin, len(binColors) - 1)]

    # bitmap.show()
    bitmap.save('plot.png','png')

if __name__ == "__main__":
    with open("output.txt", 'r') as file:
        f = file.readlines()

    fx = []
    fy = []
    for x in range(len(f)):
        g = ast.literal_eval(f[x][:-1])
        fx.append(g[2])
        fy.append(g[3])

    plotter(fx, fy)
