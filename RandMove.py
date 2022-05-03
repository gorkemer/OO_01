from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
from random import choice, randrange, shuffle, uniform
#from psychopy.tools.coordinatetools import pol2cart, cart2pol
import time
from psychopy.tools.filetools import fromFile, toFile
import csv
import os
import pylab
from psychopy.tools.coordinatetools import pol2cart, cart2pol

# assign window #
win = visual.Window([1440, 800], units='deg',
                    monitor='testMonitor', color='black', fullscr = False)
win.setRecordFrameIntervals(True)
win._refreshThreshold=1/60

timerClock = core.Clock()
# Experiment Parameters #
refRate = 60  # 1 second
nTrials = 5
second = refRate  # stimulus duration = 2 seconds
dotsN = 2400
fieldSize = 15  # 3x3 square dot field
transFieldSize = 3
shapeFieldSize = 3
elemSize = 0.2 #0.25
speed =  1/60 #13/60 # 7 degree/seconds
posX = 9.06
posY = 0
centerDissappearence = 3#0.2
deathBorder = fieldSize - elemSize
trialDur = refRate * 5
restDur = refRate * 2
fixSize = 0.3
fixOpa = 1
posX = -4

# wind :D 
winds = [4,2]
targetAnglePlus = 30 # targetAngle plus this angle

# stim list to store frames of motion
transVertiStims = []
transVertiFrameList= []
randomFrameList = []

# initial dot location assignments
transDotsX = numpy.random.uniform(low=-transFieldSize, high=transFieldSize, size=(dotsN,))  # array of random float numbers between fieldSize range
transDotsY = numpy.random.uniform(low=-transFieldSize, high=transFieldSize, size=(dotsN,))

randDotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))

dotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
dotsRadius = numpy.random.rand(dotsN) * fieldSize


# speed and direction 
alpha= numpy.random.uniform(low=0, high=2*pi,size=(dotsN,))
veloX = speed * cos(alpha)
veloY = speed * sin(alpha)



# death-border assignment
transOutfieldDotsY = numpy.logical_or((transDotsY >= transFieldSize), (transDotsY <= -transFieldSize))
transOutfieldDotsX = numpy.logical_or((transDotsX >= transFieldSize), (transDotsX <= -transFieldSize))
outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))

# initializing experiment stimuli
fixation = visual.GratingStim(win, size=fixSize, pos=[0,0], sf=0,color = 'gray', opacity = fixOpa)

transDots = visual.ElementArrayStim(win,
                                    nElements=dotsN, sizes=elemSize, elementTex=None,
                                    colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]) * transFieldSize,
                                    colorSpace='rgb', elementMask='circle',
                                    fieldSize=transFieldSize)                                    
randDots = visual.ElementArrayStim(win,
                                   nElements=dotsN, sizes=elemSize, elementTex=None,
                                   colors=(1.0, 1.0, 1.0), xys=numpy.array([randDotsX, randDotsY]).transpose(),
                                   colorSpace='rgb', elementMask='circle',
                                   fieldSize=fieldSize)
rotDots = visual.ElementArrayStim(win,
                                  nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                  colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]),
                                  colorSpace='rgb', elementMask='circle', texRes=128,
                                  fieldSize=fieldSize, fieldShape = 'sqr')


rotDots.setFieldPos([0, 0])
transDots.setFieldPos([0, 0])

def outFieldDots(deathDots):
    outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsY,)))
    outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))
    randDotsX[outfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsX,)))
    randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))

def inShapeDots(randDotsY, randDotsX):



    #rand_thetaX, rand_radiusY = cart2pol(randDotsY, randDotsX)

    # handle structure-from-motion 
    #shapeXBorders =  numpy.logical_and((rand_radiusY <= 8), (rand_radiusY > 6)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    #shapeYBorders = numpy.logical_and((rand_thetaX <= 90), (rand_thetaX > 0))
    #shapeIn = numpy.logical_and(shapeXBorders, shapeYBorders)

    #rand_thetaX += 100
    #rand_radiusY += 100

    #randDotsY, randDotsX = pol2cart(rand_thetaX, rand_radiusY)

    
    #randDotsX[shapeIn] += (speed*winds[0]) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 
    #randDotsY[shapeIn] += (speed*winds[0]) *  sin(numpy.random.uniform(low=0, high=2*pi)) #sin(alpha[shapeIn])
    pass


def inShapeDotsPolar():
    # handle structure-from-motion 
    shapeXBorders =  numpy.logical_and((dotsRadius <= 8), (dotsRadius > 6)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    shapeYBorders_1 = numpy.logical_and((dotsTheta <= 90), (dotsTheta >= 0))
    shapeYBorders_2 = numpy.logical_and((dotsTheta <= 180), (dotsTheta >= 90))
    shapeYBorders_3 = numpy.logical_and((dotsTheta <= 270), (dotsTheta >= 180))
    shapeYBorders_4 = numpy.logical_and((dotsTheta <= 360), (dotsTheta >= 270))
    shapeYBorders_1 = numpy.logical_or(shapeYBorders_1, shapeYBorders_2)
    shapeYBorders_2 = numpy.logical_or(shapeYBorders_3, shapeYBorders_4)
    shapeIn_1 = numpy.logical_and(shapeXBorders, shapeYBorders_1)
    shapeIn_2 = numpy.logical_and(shapeXBorders, shapeYBorders_2)
    dotsRadius[shapeIn_1] += (speed*winds[0]) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 
    dotsRadius[shapeIn_2] += (speed*winds[1]) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 
    #dotsTheta[shapeIn] += speed/dotsRadius[shapeIn] #*  sin(numpy.random.uniform(low=0, high=2*pi)) #sin(alpha[shapeIn])
    #        dotsTheta += speed/dotsRadius * moveSign

def targetShapeDetermine(targetAngle):
    # handle structure-from-motion 
    targetRadiusRange =  numpy.logical_and((dotsRadius <= 8), (dotsRadius > 6)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    targetAngleRange = numpy.logical_and((dotsTheta <= targetAngle + targetAnglePlus), (dotsTheta >= targetAngle))

    targetIn = numpy.logical_and(targetRadiusRange, targetAngleRange)
    dotsRadius[targetIn] += (speed*winds[0] * 2) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 


def transVertiDotMove(dotsX, dotsY, transDots, speed, transOutfieldDotsY, transOutfieldDotsX, deathDots,transMoveSign):
    dotsX += speed * transMoveSign
    dotsX[deathDots] = numpy.random.uniform(low=-transFieldSize, high=transFieldSize,size=(sum(deathDots,)))
    transOutfieldDotsX = numpy.logical_or((dotsX >= transFieldSize), (dotsX <= -transFieldSize))
    dotsX[transOutfieldDotsX] = numpy.random.uniform(low=-transFieldSize, high=transFieldSize,size=(sum(transOutfieldDotsX,)))
    return (dotsX, dotsY)

def randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, outfieldDotsY, outfieldDotsX, deathDots):

    outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsY,)))
    outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))
    randDotsX[outfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsX,)))
    randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))

    #veloX #bunu de aktive edince sadece X ekseninde hareket oluyor fena gozukmuyor
    randDotsX += veloX
    randDotsY += veloY
    
    xIn = numpy.logical_or((randDotsX >= -fieldSize / 3), (randDotsX <= fieldSize / 3))
    yIn = numpy.logical_or((randDotsY >= -fieldSize / 3), (randDotsY <= fieldSize/ 3))
    inside = numpy.logical_and(xIn, yIn)
    
    randDotsY[inside] += speed * sin(2*pi)

    #print(len(randDotsY[inside]))
    #randDotsY[inside] += numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(randDotsY[inside],)))
#veloY / 2 # * sin(numpy.random.uniform(low=pi, high=2*pi)) #cos(alpha[shapeIn]) 


    #print(fieldSize)

    return (randDotsX, randDotsY)

def polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion, cookGroup, targetAngle, rest, winds):
    ''' just a small function of initiating radial and angular movement '''
    
    if motion == ['radial']:
        dotsRadius += speed * moveSign
        if moveSign == 1:
            outFieldRadius = (dotsRadius >= deathBorder)
        else:
            outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * fieldSize
        #dotsRadius[deathDots] = numpy.random.rand(sum(deathDots)) * fieldSize
    else: #elif motion == ['angular']
        #dotsTheta += speed * moveSign #speed/dotsRadius * moveSign

        dotsTheta[deathDots] = numpy.random.rand(sum(deathDots)) * 360
        outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * fieldSize
        #dotsRadius += veloX
        dotsTheta += speed/dotsRadius * moveSign #* sin(numpy.random.uniform(low=0, high=2*pi))
        #randDotsX += veloX
        #randDotsY += veloY
    # if (cookGroup):
    #     inShapeDotsPolar()
    # elif (not(rest)):
    #     targetShapeDetermine(targetAngle)
    thetaX, radiusY = pol2cart(dotsTheta, dotsRadius)
    rotDots.setXYs(numpy.array([thetaX, radiusY]).transpose())

# initializing dot locations before the experiment loop # 
## this is for randomDots ##
for times in range(trialDur):

    transMoveSign = -1

    dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
    deathDots = (dieScoreArray < 0.0001) #each dot have maximum of 10 frames life
    randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, outfieldDotsY, outfieldDotsX, deathDots)
    randXY = numpy.array([randDotsX, randDotsY]).transpose()
    randomFrameList.append(randXY)

    transVertiDotMove(dotsX, dotsY, transDots, speed, transOutfieldDotsY, transOutfieldDotsX, deathDots,transMoveSign)
    transXY = numpy.array([dotsX, dotsY]).transpose()
    transVertiFrameList.append(transXY)

for trials in range(nTrials):

    t0 = time.time()
    targetAngle = numpy.random.uniform(low=0, high=360)
    colorPresented = choice(['red'])
    print(colorPresented)
    cookGroup = True
    fixation.color = "gray"
    rest = False
    winds = [numpy.random.uniform(low=2, high=4), numpy.random.uniform(low=2, high=4)]
    for frameN in range(trialDur):
        c0 = time.time()
        if (frameN >= 4*trialDur/5): # test-time
            fixation.color = colorPresented
            cookGroup = False

        # get the pre-determined frame deets for dot movements
        randDots.setXYs(randomFrameList[frameN])
        transDots.setXYs(transVertiFrameList[frameN])
        
        # seperately move the radial motion
        motion = ['angular']
        moveSign = 1 # this is for polar movement

        #polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion, cookGroup, targetAngle, rest, winds)

        # draw stim #
        randDots.draw()
        #rotDots.draw()
        #transDots.draw()
        fixation.draw()

        win.flip()
        c1 = time.time()

        keys = event.getKeys(keyList=["escape"] )
        for keys in keys:
            if keys == 'escape':
                win.close()
                core.quit()

    t1 = time.time()
    trialDuration = t1-t0
    print("trialDuration:", trialDuration)
    # rest block ###
    # rest = True
    # cookGroup = False
    # fixation.color = "yellow"
    # for frameN in range(restDur):
    #     polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion, cookGroup, targetAngle, rest, winds)
    #     rotDots.draw()
    #     fixation.draw()
    #     win.flip()
    # end of rest block ###

    

win.close()

