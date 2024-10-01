#TODO: Do some type of analysis using KV of motor which is 350 and battery voltage of 6s lipo
#All interpolation is linear

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

def makePlot(motorRpm, thrustArr, torqueArr, powerArr, propName = ""):
    plt.style.use("bmh")

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    fig.suptitle("Propeller Data for " + propName)

    ax1.plot(motorRpm, thrustArr)
    ax1.set_xlabel("RPM")
    ax1.set_ylabel("Thrust in Newtons")

    ax2.plot(motorRpm, powerArr)
    ax2.set_xlabel("RPM")
    ax2.set_ylabel("Power in Watts")

    ax3.plot(motorRpm, torqueArr)
    ax3.set_xlabel("RPM")
    ax3.set_ylabel("Torque in Newton Meters")

    plt.show()

def findRpmAtVal(motorRpm, arr, val):
    lowRpm = 0
    highRpm = 0
    lowVal = 0
    highVal = 0

    for i in range(motorRpm.size):
        if (arr[i] <= val):
            lowVal = arr[i]
            lowRpm = motorRpm[i]
        
        if (arr[i] > val):
            highVal = arr[i]
            highRpm = motorRpm[i]
            break
    
    valDifference = highVal - lowVal
    rpmDifference = highRpm - lowRpm

    if (valDifference == 0):
        return lowVal

    valIntermediate = val - lowVal
    valPercent = valIntermediate / valDifference

    rpmVal = (rpmDifference * valPercent) + lowRpm

    return rpmVal

#Similar to findRpmAtVal but slightly different
def findThrustAtRpm(motorRpm, thrustArr, rpmVal):
    lowRpm = 0
    highRpm = 0
    lowVal = 0
    highVal = 0

    for i in range(motorRpm.size):
        if (motorRpm[i] <= rpmVal):
            lowVal = thrustArr[i]
            lowRpm = motorRpm[i]
        
        if (motorRpm[i] > rpmVal):
            highVal = thrustArr[i]
            highRpm = motorRpm[i]
            break
    
    valDifference = highVal - lowVal
    rpmDifference = highRpm - lowRpm

    if (rpmDifference == 0):
        return lowRpm

    rpmIntermediate = rpmVal - lowRpm
    rpmPercent = rpmIntermediate / rpmDifference

    thrust = (valDifference * rpmPercent) + lowVal

    return thrust
    
        
def interpolatedData(propData, mKV = 350, vBat = 25.2, maxWatt = 750, velocityIndex = 0, propName = ""):
    vArr = np.arange(0, vBat, 0.1)
    motorRpm = vArr * mKV
    motorRpm = motorRpm[motorRpm >= 1000]
    thrustArr = np.empty(0)
    powerArr = np.empty(0)
    torqueArr = np.empty(0)

    for i in motorRpm:
        lowRpm = (i // 1000) * 1000
        highRpm = lowRpm + 1000
        percent = (i % 1000) / 1000

        lowVal = propData[lowRpm][3][velocityIndex]
        highVal = propData[highRpm][3][velocityIndex]
        difference = highVal - lowVal
        interpolatedValue = (difference * percent) + lowVal
        thrustArr = np.append(thrustArr, interpolatedValue)

        lowVal = propData[lowRpm][1][velocityIndex]
        highVal = propData[highRpm][1][velocityIndex]
        difference = highVal - lowVal
        interpolatedValue = (difference * percent) + lowVal
        powerArr = np.append(powerArr, interpolatedValue)

        lowVal = propData[lowRpm][2][velocityIndex]
        highVal = propData[highRpm][2][velocityIndex]
        difference = highVal - lowVal
        interpolatedValue = (difference * percent) + lowVal
        torqueArr = np.append(torqueArr, interpolatedValue)

    makePlot(motorRpm, thrustArr, torqueArr, powerArr, propName)


def interpolatedDataMax750Watt(propData, mKV = 350, vBat = 25.2, maxWatt = 750, velocityIndex = 0, propName = ""):
    maxRpm = 0
    for i in range(1000, 9000, 1000):
        if (propData[i][1][velocityIndex]) >= 750:
            maxRpm = i
            break    
    
    vArr = np.arange(0, vBat, 0.1)
    motorRpm = vArr * mKV
    motorRpm = motorRpm[motorRpm >= 1000]
    motorRpm = motorRpm[motorRpm <= maxRpm]
    thrustArr = np.empty(0)
    powerArr = np.empty(0)
    torqueArr = np.empty(0)

    for i in motorRpm:
        lowRpm = (i // 1000) * 1000
        highRpm = lowRpm + 1000
        percent = (i % 1000) / 1000

        lowVal = propData[lowRpm][3][velocityIndex]
        highVal = propData[highRpm][3][velocityIndex]
        difference = highVal - lowVal
        interpolatedValue = (difference * percent) + lowVal
        thrustArr = np.append(thrustArr, interpolatedValue)

        lowVal = propData[lowRpm][1][velocityIndex]
        highVal = propData[highRpm][1][velocityIndex]
        difference = highVal - lowVal
        interpolatedValue = (difference * percent) + lowVal
        powerArr = np.append(powerArr, interpolatedValue)

        lowVal = propData[lowRpm][2][velocityIndex]
        highVal = propData[highRpm][2][velocityIndex]
        difference = highVal - lowVal
        interpolatedValue = (difference * percent) + lowVal
        torqueArr = np.append(torqueArr, interpolatedValue)

    rpmAt750 = findRpmAtVal(motorRpm, powerArr, 750)
    thrustAt750 = findThrustAtRpm(motorRpm, thrustArr, rpmAt750)
    
    print(rpmAt750)
    print(thrustAt750)

    makePlot(motorRpm, thrustArr, torqueArr, powerArr, propName)
    

RPM = np.array([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])

dat1 = Parser("PropData/PER3_27x13E.dat")
dat1.parseData()

dat2 = Parser("PropData/PER3_20x14.dat")
dat2.parseData()

dat3 = Parser("PropData/PER3_28x20-4.dat")
dat3.parseData()

dat4 = Parser("PropData/PER3_26x15E.dat")
dat4.parseData()

dat5 = Parser("PropData/PER3_26x13E.dat")
dat5.parseData()

dat6 = Parser("PropData/PER3_22x12E.dat")
dat6.parseData()

dat7 = Parser("PropData/PER3_25x125E.dat")
dat7.parseData()

dat8 = Parser("PropData/PER3_24x12E.dat")
dat8.parseData()


interpolatedDataMax750Watt(dat2.dataDict, propName="20x14")
interpolatedDataMax750Watt(dat6.dataDict, propName="22x12E")
interpolatedDataMax750Watt(dat8.dataDict, propName="24x12E")
interpolatedDataMax750Watt(dat7.dataDict, propName="25x125E")
interpolatedDataMax750Watt(dat5.dataDict, propName="26x13E")
interpolatedDataMax750Watt(dat4.dataDict, propName="26x15E")
interpolatedDataMax750Watt(dat1.dataDict, propName="27x13E")
interpolatedDataMax750Watt(dat3.dataDict, propName="28x20")
