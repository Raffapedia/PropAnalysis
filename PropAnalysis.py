#TODO: Do some type of analysis using KV of motor which is 350 and battery voltage of 6s lipo

import numpy as np
from matplotlib import pyplot as plt


#Very rudimentary parser but works
class Parser:
    def __init__(self, fileName):
        self.fileName = fileName
        self.dataDict = {}

    #Place numpy arrays into dictionary where the key is RPM and value of numpy array of data
    #Array is Velocity, Power, Torque, Thrust
    def parseData(self):
        with open(self.fileName, 'r') as file:
            for line in file:
                if line.__contains__("PROP RPM"):
                    temp = line.split()
                    RPM = temp[3]
                    data = np.zeros([4,29])
                    
                    line = file.__next__()
                    line = file.__next__()
                    line = file.__next__()
                    
                    for i in range(29):
                        line = file.__next__()
                        temp = line.split()
                        data[0, i] = temp[0]
                        data[1, i] = temp[8]
                        data[2, i] = temp[9]
                        data[3, i] = temp[10]
                    
                    self.dataDict[int(RPM)] = data


#Use velocityIndex = 0 for static thrust
#Example of how to use data to make a plot
def plotAgainstRpm(rpmArr, data, velocityIndex = 0):
    power = np.zeros(rpmArr.shape)
    torque = np.zeros(rpmArr.shape)
    thrust = np.zeros(rpmArr.shape)

    i = 0
    for rpm in rpmArr:
        power[i] = data[rpm][1][velocityIndex]
        torque[i] = data[rpm][2][velocityIndex]
        thrust[i] = data[rpm][3][velocityIndex]
        i += 1
    
    plt.plot(rpmArr, power, label = "Power")
    plt.plot(rpmArr, torque, label = "Torque")
    plt.plot(rpmArr, thrust, label = "Thrust")
    plt.legend()
    plt.show()


RPM = np.array([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])

dat1 = Parser("PropData/PER3_27x13E.dat")
dat1.parseData()

dat2 = Parser("PropData/PER3_20x14.dat")
dat2.parseData()

plotAgainstRpm(RPM, dat1.dataDict)
plotAgainstRpm(RPM, dat2.dataDict)