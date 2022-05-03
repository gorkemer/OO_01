"""
19 Nisan 2022

S22 project script. 
Design TBD
    
"""

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
import math

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
screenSize = 15  # 3x3 square dot field
transFieldSize = 3
shapeFieldSize = 3
elemSize = 0.2 #0.25
speed =  1/60 #13/60 # 7 degree/seconds
posX = 9.06
posY = 0
centerDissappearence = 3#0.2
deathBorder = screenSize - elemSize
trialDur = refRate * 10
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

randDotsX = numpy.random.uniform(low=-screenSize, high=screenSize,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-screenSize, high=screenSize,size=(dotsN,))

dotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
dotsRadius = numpy.random.rand(dotsN) * screenSize


# speed and direction 
alpha= numpy.random.uniform(low=0, high=2*pi,size=(dotsN,))
veloX = speed * cos(alpha)
veloY = speed * sin(alpha)

# death-border assignment

screenBorder_y = numpy.logical_or((randDotsY >= screenSize), (randDotsY <= -screenSize))
screenBorder_x = numpy.logical_or((randDotsY >= screenSize), (randDotsY <= -screenSize))

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
                                   fieldSize=screenSize)
rotDots = visual.ElementArrayStim(win,
                                  nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                  colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]),
                                  colorSpace='rgb', elementMask='circle', texRes=128,
                                  fieldSize=screenSize, fieldShape = 'sqr')


rotDots.setFieldPos([0, 0])
transDots.setFieldPos([0, 0])

apertureCenterX = 0
apertureCenterY = 0

verticalAxis = 4
horizontalAxis = 4

##Calculate the POSITIVE y value of a point on the edge of the ellipse given an x-value
def yValuePositive(x):
    totalX = []
    for i in x:
        xx = i - (apertureCenterX); #Bring it back to the (0,0) center to calculate accurately (ignore the y-coordinate because it is not necessary for calculation)
        workedX = verticalAxis * sqrt(1 - (math.pow(xx, 2) / math.pow(horizontalAxis, 2))) + apertureCenterY; #Calculated the positive y value and added apertureCenterY to recenter it on the screen 
        totalX.append(workedX)
    return totalX
##Calculate the NEGATIVE y value of a point on the edge of the ellipse given an x-value
def yValueNegative(x):
    totalX = []
    for i in x:
        xx = i - (apertureCenterX); #Bring it back to the (0,0) center to calculate accurately (ignore the y-coordinate because it is not necessary for calculation)
        workedX = -verticalAxis * sqrt(1 - (math.pow(xx, 2) / math.pow(horizontalAxis, 2))) + apertureCenterY; #Calculated the negative y value and added apertureCenterY to recenter it on the screen
        totalX.append(workedX)
    return totalX
##Calculate the POSITIVE x value of a point on the edge of the ellipse given a y-value
def xValuePositive(y):
    totalY = []
    for i in y:
        yy = i - (apertureCenterY)
        workedY = horizontalAxis * sqrt(1 - (math.pow(yy, 2) / math.pow(verticalAxis, 2))) + apertureCenterX; #Calculated the positive x value and added apertureCenterX to recenter it on the screen
        
        totalY.append(workedY)
    return totalY

##Calculate the NEGATIVE x value of a point on the edge of the ellipse given a y-value
def xValueNegative(y):
    totalY = []
    for i in y:
        yy = i - (apertureCenterY); #Bring it back to the (0,0) center to calculate accurately (ignore the x-coordinate because it is not necessary for calculation)
        workedY =  -horizontalAxis * sqrt(1 - (math.pow(yy, 2) / math.pow(verticalAxis, 2))) + apertureCenterX; #Calculated the negative x value and added apertureCenterX to recenter it on the screen
        totalY.append(workedY)
    return totalY

def remove_dots_leaving_screen(dotsX, dotsY, deathDots):
    ''' checks the location of X and Y - if extends the screen, kills and respawns'''
    outfieldDotsX = numpy.logical_or((dotsX >= screenSize), (dotsX <= -screenSize))
    outfieldDotsY = numpy.logical_or((dotsY >= screenSize), (dotsY <= -screenSize))

    randDotsX[outfieldDotsX] = numpy.random.uniform(low=-screenSize, high=screenSize,size=(sum(outfieldDotsX,)))
    randDotsY[outfieldDotsY] = numpy.random.uniform(low=-screenSize, high=screenSize,size=(sum(outfieldDotsY,)))
    randDotsX[deathDots] = numpy.random.uniform(low=-screenSize, high=screenSize,size=(sum(deathDots,)))

def inShapeTransDots(randDotsY, randDotsX):


    #dot.x > xValueNegative_foreground(dot.y) && dot.x < xValuePositive_foreground(dot.y) && dot.y > yValueNegative_foreground(dot.x) && dot.y < yValuePositive_foreground(dot.x)) {
    #if (dot.x < xValueNegative(dot.y) || dot.x > xValuePositive(dot.y) || dot.y < yValueNegative(dot.x) || dot.y > yValuePositive(dot.x)) {
    xIn = numpy.logical_and((randDotsX > xValueNegative(randDotsY) ), (randDotsX < xValuePositive(randDotsY)))
    yIn = numpy.logical_and((randDotsY > yValueNegative(randDotsX)), (randDotsY < yValuePositive(randDotsX)))
    inside = numpy.logical_and(xIn, yIn)

    alpha2= pi/2#numpy.random.uniform(low=0, high=pi,size=(len(randDotsX[inside]),))

    #randDotsY[inside] += speed*3 * sin(alpha2) #speed*5 * cos(numpy.random.uniform(low=0, high=pi)) #giving a random direction

    # move randomly but faster
    randDotsY[inside] += speed*2 * cos(alpha[inside])#* sin(alpha2)
    randDotsY[inside] += speed*2 * sin(alpha[inside])


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


def transVertiDotMove(transDotsX, transDotsY, speed,transMoveSign, deathDots):
    transDotsX += speed * transMoveSign #moves right-left
    remove_dots_leaving_screen(transDotsX, transDotsY, deathDots)

    return (transDotsX, transDotsY)

def randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, deathDots):

    remove_dots_leaving_screen(randDotsX, randDotsX, deathDots) # remove dots leaving the screen
    # move the dots to different places

    randDotsX += veloX #    #veloX #bunu de aktive edince sadece X ekseninde hareket oluyor fena gozukmuyor
    randDotsY += veloY

    inShapeTransDots(randDotsY, randDotsX)
    return (randDotsX, randDotsY)

def polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion, cookGroup, targetAngle, rest, winds):

    if motion == ['radial']:
        dotsRadius += speed * moveSign
        if moveSign == 1:
            outFieldRadius = (dotsRadius >= deathBorder)
        else:
            outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * screenSize
        #dotsRadius[deathDots] = numpy.random.rand(sum(deathDots)) * fieldSize
    else: #elif motion == ['angular']
        #dotsTheta += speed * moveSign #speed/dotsRadius * moveSign
        dotsTheta[deathDots] = numpy.random.rand(sum(deathDots)) * 360
        outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * screenSize
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

def define_target_info():
    targetAngle = numpy.random.uniform(low=0, high=360)
    colorPresented = choice(['red'])
    print(colorPresented)
    return targetAngle, colorPresented


#############################################################################
###############################################################
# ####### initializing dot locations before the experiment loop # #######
######################################################################
######################################################################

for times in range(trialDur):

    transMoveSign = -1

    dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
    deathDots = (dieScoreArray < 0.0001) #each dot have maximum of 10 frames life
    randomDotMove(randDotsX, randDotsY, randDots, veloX, veloY, deathDots)
    randXY = numpy.array([randDotsX, randDotsY]).transpose()
    randomFrameList.append(randXY)

    transVertiDotMove(transDotsX, transDotsY, speed, transMoveSign, deathDots)
    transXY = numpy.array([transDotsX, transDotsY]).transpose()
    transVertiFrameList.append(transXY)



###############################################################
######### TRIAL LOOP ##########################################
######################################################################
######################################################################

for trials in range(nTrials):

    t0 = time.time()
    
    define_target_info()

    cookGroup = True
    fixation.color = "gray"
    rest = False
    winds = [numpy.random.uniform(low=2, high=4), numpy.random.uniform(low=2, high=4)]

    for frameN in range(trialDur):
        c0 = time.time()
        if (frameN >= 4*trialDur/5): # test-time
            colorPresented = choice(['red'])
            fixation.color = colorPresented
            cookGroup = False

        # set XY from frame list
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

