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
dotsN = 1000
fieldSize = 15  # 3x3 square dot field
shapeFieldSize = 3
elemSize = 0.2 #0.25
speed =  1/60 #13/60 # 7 degree/seconds
posX = 9.06
posY = 0
centerDissappearence = 3#0.2
deathBorder = fieldSize - elemSize
trialDur = refRate * 5
fixSize = 5
fixOpa = 1
posX = -4

# wind :D 
wind = 3

transVertiStims = []
transVertiFrameList= []
randomFrameList = []


# initial dot location assignments
dotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))  # array of random float numbers between fieldSize range
dotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))

randDotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))

dotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
dotsRadius = numpy.random.rand(dotsN) * fieldSize

# speed and direction 
alpha= numpy.random.uniform(low=pi, high=2*pi,size=(dotsN,))
veloX = speed * cos(alpha)
veloY = speed * sin(alpha)

# death-border assignment
transOutfieldDotsY = numpy.logical_or((dotsY >= fieldSize), (dotsY <= -fieldSize))
transOutfieldDotsX = numpy.logical_or((dotsX >= fieldSize), (dotsX <= -fieldSize))
outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))

# initializing experiment stimuli
fixation = visual.GratingStim(win, size=fixSize, pos=[0,0], sf=0,color = 'black', opacity = fixOpa)

transDots = visual.ElementArrayStim(win,
                                    nElements=dotsN, sizes=elemSize, elementTex=None,
                                    colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]) * fieldSize,
                                    colorSpace='rgb', elementMask='circle',
                                    fieldSize=fieldSize)                                    
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

def outFieldDots(deathDots):
    outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsY,)))
    outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))
    randDotsX[outfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsX,)))
    randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))

def inShapeDots():

    # handle structure-from-motion 
    shapeXBorders =  numpy.logical_and((randDotsX <= -3), (randDotsX > -5)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    shapeYBorders = numpy.logical_and((randDotsY <= 1), (randDotsY > -3))
    shapeIn = numpy.logical_and(shapeXBorders, shapeYBorders)
    randDotsX[shapeIn] += (speed*wind) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 
    randDotsY[shapeIn] += (speed*wind) *  sin(numpy.random.uniform(low=0, high=2*pi)) #sin(alpha[shapeIn])

def inShapeDotsPolar():

    # handle structure-from-motion 
    print(max(dotsTheta))
    print(min(dotsRadius))
    shapeXBorders =  numpy.logical_and((dotsRadius <= 8), (dotsRadius > 6)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    shapeYBorders = numpy.logical_and((dotsTheta <= 60), (dotsTheta >= 30))
    shapeIn = numpy.logical_and(shapeXBorders, shapeYBorders)
    dotsRadius[shapeIn] += (speed*wind) * cos(numpy.random.uniform(low=0, high=2*pi)) #cos(alpha[shapeIn]) 
    dotsTheta[shapeIn] += (speed*wind) #*  sin(numpy.random.uniform(low=0, high=2*pi)) #sin(alpha[shapeIn])
 

def transVertiDotMove(dotsX, dotsY, transDots, speed, transOutfieldDotsY, transOutfieldDotsX, deathDots,transMoveSign):
    dotsX += speed * transMoveSign
    dotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
    transOutfieldDotsX = numpy.logical_or((dotsX >= fieldSize), (dotsX <= -fieldSize))
    dotsX[transOutfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(transOutfieldDotsX,)))
    transMove = True
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

    # 
    inShapeDots()

    return (randDotsX, randDotsY)

def polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion):
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
        dotsTheta += speed/dotsRadius * moveSign

        dotsTheta[deathDots] = numpy.random.rand(sum(deathDots)) * 360
        outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * fieldSize
    inShapeDotsPolar()
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
    for frameN in range(trialDur):
        c0 = time.time()

        # get the pre-determined frame deets for dot movements
        randDots.setXYs(randomFrameList[frameN])
        transDots.setXYs(transVertiFrameList[frameN])
        
        # seperately move the radial motion
        motion = ['radial']
        moveSign = 1 # this is for polar movement
        polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion)

        # draw stim #
        #randDots.draw()
        rotDots.draw()
        #transDots.draw()
        #fixation.draw()

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

win.close()

