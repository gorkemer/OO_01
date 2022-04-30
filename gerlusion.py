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


win = visual.Window([800, 400], units='deg',
                    monitor='testMonitor', color='black', fullscr = False)
win.setRecordFrameIntervals(True)
win._refreshThreshold=1/60


timerClock = core.Clock()
# Display Options
refRate = 60  # 1 second
nTrials = 5
second = refRate  # stimulus duration = 2 seconds
dotsN = 250
fieldSize = 5  # 3x3 square dot field
shapeFieldSize = 3
elemSize = 0.25
speed =  1/60 #13/60 # 7 degree/seconds
posX = 9.06
posY = 0

dotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))  # array of random float numbers between fieldSize range
dotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))
transOutfieldDotsY = numpy.logical_or((dotsY >= fieldSize), (dotsY <= -fieldSize))
transOutfieldDotsX = numpy.logical_or((dotsX >= fieldSize), (dotsX <= -fieldSize))

randDotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
alpha= numpy.random.uniform(low=0, high=2*pi,size=(dotsN,))
veloX = speed * cos(alpha)
veloY = speed * sin(alpha)

outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))

transVertiStims = []
transVertiFrameList= []
randomFrameList = []

# initializing experiment stimuli

fixation = visual.GratingStim(win, size=1, pos=[0,0], sf=0,color = 'gray', opacity = 0.1)

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
    
def transVertiDotMove(dotsX, dotsY, transDots, speed, transOutfieldDotsY, transOutfieldDotsX, deathDots,moveSign):
    dotsX += speed * moveSign
    dotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
    transOutfieldDotsX = numpy.logical_or((dotsX >= fieldSize), (dotsX <= -fieldSize))
    dotsX[transOutfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(transOutfieldDotsX,)))
    transMove = True
    return (dotsX, dotsY)


def outFieldDots(deathDots):
    outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsY,)))
    outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))
    randDotsX[outfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsX,)))
    randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))

def inShapeDots():

    # inShapeDots(
    # get the index numbers of these people?
    # then subset those dots
    pass



def randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, outfieldDotsY, outfieldDotsX, deathDots):


    #veloX #bunu de aktive edince sadece X ekseninde hareket oluyor fena gozukmuyor

    outfieldDotsY = numpy.logical_or((randDotsY >= fieldSize), (randDotsY <= -fieldSize))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsY,)))
    outfieldDotsX = numpy.logical_or((randDotsX >= fieldSize), (randDotsX <= -fieldSize))
    randDotsX[outfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(outfieldDotsX,)))
    #randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))

    #shapeOutFieldX = numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX < -shapeFieldSize))#numpy.where(numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    #shapeOutFieldY = numpy.logical_or((randDotsY >= shapeFieldSize), (randDotsY < -shapeFieldSize))

    shapeInFieldX =  numpy.logical_and((randDotsX <= shapeFieldSize), (randDotsX > -shapeFieldSize)) #numpy.where(numpy.logical_or((randDotsX <= shapeFieldSize), (randDotsX >= -shapeFieldSize))) #numpy.logical_or((randDotsX >= shapeFieldSize), (randDotsX <= -shapeFieldSize))
    shapeInFieldY = numpy.logical_and((randDotsY <= shapeFieldSize), (randDotsY > -shapeFieldSize))

    shapeIn = numpy.logical_and(shapeInFieldX, shapeInFieldY)

    randDotsX += veloX
    randDotsY += veloY

    randDotsX[shapeIn] += (speed*2) * cos(alpha[shapeIn])
    randDotsY[shapeIn] += (speed*2) * sin(alpha[shapeIn])

    #np.invert(a) to invert boolean statements
    #randDotsY[shapeOutFieldX] += (speed) * cos(alpha[shapeOutFieldX])
    #randDotsX[shapeOutFieldY] += (speed) * sin(alpha[shapeOutFieldY])

    #randDotsX[shapeInFieldX] += veloX/2
    inShapeDots()

    return (randDotsX, randDotsY)

## this is for randomDots ##
for times in range(120*5):
    dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
    deathDots = (dieScoreArray < 0.01) #each dot have maximum of 10 frames life
    randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, outfieldDotsY, outfieldDotsX, deathDots)
    randXY = numpy.array([randDotsX, randDotsY]).transpose()
    randomFrameList.append(randXY)

## this is for transVertical ## 
for times in range(120):
    if times >= 60:
        moveSign = 1
        inverted = False
    else:
        moveSign = -1
        inverted = True
    dieScoreArray = numpy.random.rand(dotsN)
    deathDots = (dieScoreArray < 0.01)
    transVertiDotMove(dotsX, dotsY, transDots, speed, transOutfieldDotsY, transOutfieldDotsX, deathDots,moveSign)
    transXY = numpy.array([dotsX, dotsY]).transpose()
    transVertiFrameList.append(transXY)
    
# transVertiStims


for trials in range(nTrials):
    t0 = time.time()
#    if trials % 3 == 0 or trials % 2 == 0: # 'or' used here to account for blank condition 
#        targetSide = 1
#    else:
#        targetSide = -1
#    transDots.setFieldPos([posX * -targetSide, 0])
#    randDots.setFieldPos([posX * targetSide, 0])
    # Frame Loop

    ## this is for randomDots ##
    for times in range(120):
        dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
        deathDots = (dieScoreArray < 0.01) #each dot have maximum of 10 frames life
        randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, outfieldDotsY, outfieldDotsX, deathDots)
        randXY = numpy.array([randDotsX, randDotsY]).transpose()
        randomFrameList.append(randXY)
    for frameN in range(len(randomFrameList)):
        c0 = time.time()
        randDots.setXYs(randomFrameList[frameN])
        #transDots.setXYs(transVertiFrameList[frameN])
        
        fixation.draw()
        randDots.draw()

        win.flip()
        c1 = time.time()

    t1 = time.time()
    trialDuration = t1-t0
    #print "trialDuration:", trialDuration

    keys = event.getKeys(keyList=["escape"] )
    for keys in keys:
        if keys == 'escape':
            win.close()
            core.quit()

win.close()

