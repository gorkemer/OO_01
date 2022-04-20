"""
19 Nisan 2022

S22 project script. 
Design TBD
    
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.visual import filters
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal #shuffle
import os  # handy system and path functions
from random import choice, randrange, shuffle, uniform
#from psychopy.tools.coordinatetools import pol2cart, cart2pol
import time
from psychopy.tools.filetools import fromFile, toFile
import csv

#data handling
try: #try to get a previous parameters file
    expInfo = fromFile('lastParams.pickle')
except:#if not there then use a default set
    expInfo = {'observer':'', 'practice': 1} #add more if you want # 'InitialPosition':0
expInfo['dateStr']= data.getDateStr() #add the current time
#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Gabor', fixed=['dateStr'])
if dlg.OK == False: #quiting if the user pressed 'cancel'
    core.quit()

#make a text file to save data
fileName = expInfo['observer'] + expInfo['dateStr']

# Display Options
refRate = 60  # 1 second
second = refRate  # stimulus duration = 2 seconds
posX = 8.2 # in real experiment: 8, supposed to be 9.06
posY = 0 # 0

# Dot parameters
dotsN = 100
fieldSize = 5 # if you put 3 here it means 3 in diameter but the total rectangular shape has 6 degree (-3 to 3)
elemSize = 0.20
speed = 7/60 # 7 degree/seconds
chanceToDie_atEachFrame = 0.01
centerDissappearence = 0.2
deathBorder = fieldSize - elemSize

# 2022
fieldSize_rand = 50


# Desing Parameters
nSets = 6
nTrials = 6
durTrial  = second*2
durInitialBlank = 24 *second
nMotions_in_one_block = 6

# important lists for experiment handling
condTypeTime =[]
motionTime = []
trialTime = []

responses = []
colorlist = []
keyList = []
response = None

motionTypes = ['transVertical'], ['transHorizontal'], ['angular'], ['radial']
#motion = choice(motionList)


#initializing window & stimuli
win = visual.Window([1920, 1080], units='deg',
                    monitor='testMonitor', color='black', fullscr = False, allowStencil=True)

dotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize - elemSize, size=(dotsN,))  # array of random float numbers between fieldSize range
dotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))
dotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
dotsRadius = numpy.random.rand(dotsN) * fieldSize
randDotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
randDotsRadius = numpy.random.rand(dotsN) * fieldSize

randDotsX = numpy.random.uniform(low=-fieldSize_rand, high=fieldSize_rand,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-fieldSize_rand, high=fieldSize_rand,size=(dotsN,))

alpha= numpy.random.uniform(low=0, high=2*pi,size=(dotsN,))
veloX = speed * cos(alpha)
veloY = speed * sin(alpha)

outfieldDotsY = numpy.logical_or((randDotsY >= deathBorder), (randDotsY <= -deathBorder))
outfieldDotsX = numpy.logical_or((randDotsX >= deathBorder), (randDotsX <= -deathBorder))

# initializing experiment stimuli

invCircle = filters.makeMask(512,'circle')*-1 #-1 means black, 1: white
maskStim1 = visual.GratingStim(win,tex=None,mask=invCircle, size=fieldSize*2+elemSize, contrast=-1, pos=(posX, posY)) #-1 contrast for blackness
maskStim2 = visual.GratingStim(win,tex=None,mask=invCircle, size=fieldSize*2+elemSize, contrast=-1, pos=(-posX, -posY))

transDots = visual.ElementArrayStim(win,
                                    nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                    colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]) * fieldSize,
                                    colorSpace='rgb', elementMask='circle',
                                    fieldSize=fieldSize, fieldShape = 'sqr') #(fieldSize, fieldSize)

rotDots = visual.ElementArrayStim(win,
                                  nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                  colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]),
                                  colorSpace='rgb', elementMask='circle', texRes=128,
                                  fieldSize=fieldSize, fieldShape = 'sqr')

polarRandomDots = visual.ElementArrayStim(win,
                                  nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                  colors=(1.0, 1.0, 1.0), xys=random([dotsN, 2]),
                                  colorSpace='rgb', elementMask='circle', texRes=128,
                                  fieldSize=fieldSize_rand, fieldShape = 'sqr')

randDots = visual.ElementArrayStim(win,
                                   nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                   colors=(1.0, 1.0, 1.0), xys=numpy.array([randDotsX, randDotsY]).transpose(),
                                   colorSpace='rgb', elementMask='circle',
                                   fieldSize=fieldSize_rand,fieldShape = 'sqr')

fixation = visual.GratingStim(win, size=0.2, pos=[0,0], sf=0,color = 'gray')
fixationColored = visual.GratingStim(win, size=0.2, pos=[0,0], sf=0,color = 'red')
fixationRegular = visual.GratingStim(win, size=0.2, pos=[0,0], sf=0,color = 'gray')

#functions
def pol2cart(theta, rho):
    x = rho * numpy.cos(theta)
    y = rho * numpy.sin(theta)
    return x, y
    
def choice_without_repetition(lst):
    prev = None
    while True:
        i = choice(lst)
        if i != prev:
            return i
            prev = i

def polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion):
    ''' just a small function of initiating radial and angular movement '''
    
    if motion == ['radial']:
        dotsRadius += speed * moveSign
        if moveSign == 1:
            outFieldRadius = (dotsRadius >= deathBorder)
        else:
            outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * fieldSize
        dotsRadius[deathDots] = numpy.random.rand(sum(deathDots)) * fieldSize
    else: #elif motion == ['angular']
        dotsTheta += speed/dotsRadius * moveSign
        if moveSign == 1:
            outFieldRadius = (dotsRadius >= deathBorder)
        dotsTheta[deathDots] = numpy.random.rand(sum(deathDots)) * 360
        outFieldRadius = (dotsRadius <= centerDissappearence)
        dotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * fieldSize
    thetaX, radiusY = pol2cart(dotsTheta, dotsRadius)
    rotDots.setXYs(numpy.array([thetaX, radiusY]).transpose())

def polarRandDotMove(randDotsRadius, randDotsTheta, polarRandomDots, speed, deathDots, moveSign, motion):
    ''' random movement'''
    speed = 1
    randDotsRadius += speed+randDotsRadius * moveSign
    if moveSign == 1:
        outFieldRadius = (randDotsRadius >= deathBorder)
    #randDotsTheta[deathDots] = numpy.random.rand(sum(deathDots)) * 360
    outFieldRadius = (randDotsRadius <= centerDissappearence)
    #randDotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * fieldSize
    
    #randThetaX, randRadiusY = pol2cart(randDotsTheta, randDotsRadius)
    #polarRandomDots.setXYs(numpy.array([randThetaX, randRadiusY]).transpose())
    #print(numpy.array([randThetaX, randRadiusY]).transpose())

def cartRandDotMove(randDotsRadius, randDotsTheta, cartRandomDots, speed, deathDots, moveSign, motion):
    ''' random movement'''
    speed = 1
    randDotsRadius += speed+randDotsRadius * moveSign
    if moveSign == 1:
        outFieldRadius = (randDotsRadius >= deathBorder)
    #randDotsTheta[deathDots] = numpy.random.rand(sum(deathDots)) * 360
    outFieldRadius = (randDotsRadius <= centerDissappearence)
    #randDotsRadius[outFieldRadius] = numpy.random.rand(sum(outFieldRadius)) * fieldSize
    
    #randThetaX, randRadiusY = pol2cart(randDotsTheta, randDotsRadius)
    #polarRandomDots.setXYs(numpy.array([randThetaX, randRadiusY]).transpose())
    #print(numpy.array([randThetaX, randRadiusY]).transpose())


def BothStaticDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block):
    ''' function for the block that presents stationary dots at periphery '''
    
    rotDots.setFieldPos([posX * targetSide, 0])
    transDots.setFieldPos([posX * targetSide, 0])
    randDots.setFieldPos([0, 0])

    randDotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
    randDotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
    randomWeight = numpy.random.uniform(0,1)

    randomArrayX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,)) * randomWeight
    randomArrayY = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,)) * (1 - randomWeight)

    print(randomArrayX)
    for counter, motion in enumerate(motionList_for_block):
        
        doThreeTimes = 0
        magicFrame = choice(range(0, 90)) #initialize random magic frame
        colorPresented = choice(['yellow', 'red'])
        fixationColored.color = colorPresented
        colorlist.append(colorPresented)
        
        for frameN in range(durTrial):
            #lifetime
            dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
            transOutfieldDotsY = numpy.logical_or((randDotsY >= deathBorder), (randDotsY <= -deathBorder))
            transOutfieldDotsX = numpy.logical_or((randDotsX >= deathBorder), (randDotsX <= -deathBorder))
            deathDots = (dieScoreArray <= chanceToDie_atEachFrame) #each dot have maximum of 10 frames life
            randDotsY[transOutfieldDotsY] = numpy.random.uniform(low=-fieldSize_rand, high=fieldSize_rand,size=(sum(transOutfieldDotsY,)))
            randDotsX[transOutfieldDotsX] = numpy.random.uniform(low=-fieldSize_rand, high=fieldSize_rand,size=(sum(transOutfieldDotsX,)))
            #randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize_rand, high=fieldSize_rand,size=(sum(deathDots,)))
            
            
            randDotsX += randomArrayX #(speed * randomWeight)
            randDotsY += randomArrayY #(speed * (1 - randomWeight))
            print(randomArrayX)

            
            randDots.setXYs(numpy.array([randDotsX, randDotsY]).transpose())

            #checking if it is magicFrame
            if frameN >= magicFrame and doThreeTimes <= 3: # 0 , 1 , 2 =  3 times
                fixa = fixationColored
                doThreeTimes += 1
                if doThreeTimes == 3:
                    Color_started = True
            else:
                fixa = fixationRegular
            
            #transDots.draw()
            randDots.draw()
            fixa.draw()
            maskStim1.draw()
            maskStim2.draw()
            win.flip()

        #collect responses
        keys = event.getKeys(keyList=["1", "4", "escape"] )
        for key in keys:
            if key == '1' and Color_started:  #
                if colorPresented == 'red':
                    response = 1
                elif colorPresented =='yellow':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == '4' and Color_started:
                if colorPresented == 'yellow':
                    response = 1
                elif colorPresented == 'red':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == 'escape':
                   win.close()
                   core.quit()
            else:
                response = None
                responses.append(response)

def BothMovingDots(dotsRadius, dotsTheta, randDotsRadius, randDotsTheta, transDots, rotDots, randDots, polarRandomDots, speed, targetSide, motionList_for_block):
    ''' function for a block where both sides at the periphery moves '''
    
    rotDots.setFieldPos([posX * targetSide, 0])
    transDots.setFieldPos([posX * targetSide, 0])
    randDots.setFieldPos([0, 0])

    polarRandomDots.setFieldPos([0, 0])



    for counter, motion in enumerate(motionList_for_block): 
        m0 = time.time()  # record the start time
        
        #motion = choice_without_repetition(motionList)
        print("motion GORKI:", motion)
        print(motion in [['transVertical'],['transHorizontal']])
        doThreeTimes = 0
        magicFrame = choice(range(0, 90)) #initialize random magic frame
        colorPresented = choice(['yellow', 'red'])
        fixationColored.color = colorPresented
        colorlist.append(colorPresented)

        # resetting dot locations: to eleminate countinuations of previous trial to the next
        dotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))  # array of random float numbers between fieldSize range
        dotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))
        randDotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
        randDotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
        dotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
        dotsRadius = numpy.random.rand(dotsN) * fieldSize


        # Frame Loop
        for frameN in range(durTrial):
            
            dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
            deathDots = (dieScoreArray <= chanceToDie_atEachFrame) #each dot have maximum of 10 frames life
            
            #lifetime for stationary dots
            randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize_rand, high=fieldSize_rand,size=(sum(deathDots,)))
            randDots.setXYs(numpy.array([randDotsX, randDotsY]).transpose())
            
            if frameN < second:
                moveSign = 1
            else:
                moveSign = -1
            if motion in [['transVertical'],['transHorizontal']]:
                transOutfieldDotsY = numpy.logical_or((dotsY >= deathBorder), (dotsY <= -deathBorder))
                transOutfieldDotsX = numpy.logical_or((dotsX >= deathBorder), (dotsX <= -deathBorder))
                if motion == ['transHorizontal']:
                    dotsY += speed * moveSign
                    dotsY[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
                    dotsY[transOutfieldDotsY] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(transOutfieldDotsY,)))
                else:
                    dotsX += speed * moveSign
                    
                    dotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
                    dotsX[transOutfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(transOutfieldDotsX,)))
                transDots.setXYs(numpy.array([dotsX, dotsY]).transpose())
                stim = transDots

                # random movement
                print(speed)
                randDotsX += speed #* moveSign
                randDotsY += speed #* moveSign
                randDots.setXYs(numpy.array([randDotsX, randDotsY]).transpose())
            else:
                polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion)
                thetaX, radiusY = pol2cart(dotsTheta, dotsRadius)
                stim = rotDots 
            
            #checking if it is magicFrame
            if frameN >= magicFrame and doThreeTimes <= 3: # 0 , 1 , 2 =  3 times
                fixa = fixationColored
                doThreeTimes += 1
                if doThreeTimes == 3:
                    Color_started = True
            else:
                fixa = fixationRegular
            
            #polarRandDotMove(randDotsRadius, randDotsTheta, polarRandomDots, speed, deathDots, moveSign, motion)
            #randThetaX, randRadiusY = pol2cart(randDotsTheta, randDotsRadius)
            #polarRandomDots.setXYs(numpy.array([randThetaX, randRadiusY]).transpose())
            #polarRandomDots.draw()
            
            #stim.draw()
            fixa.draw()
            randDots.draw()
            #maskStim1.draw()
            #maskStim2.draw()
            
            win.flip()

        #collect responses
        keys = event.getKeys(keyList=["1", "4", "escape"] )
        for key in keys:
            if key == '1' and Color_started:  #
                if colorPresented == 'red':
                    response = 1
                elif colorPresented =='yellow':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == '4' and Color_started:
                if colorPresented == 'yellow':
                    response = 1
                elif colorPresented == 'red':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == 'escape':
                   win.close()
                   core.quit()
            else:
                response = None
                responses.append(response)

def LeftMovingDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList):
    ''' function for initiating movement at one and SINGLE location at either side (left or right) at the periphery 
    here the targetDots is the moving one and the targetSide changes in accordance with the block specification'''
    
    rotDots.setFieldPos([posX * targetSide, 0])
    transDots.setFieldPos([posX * targetSide, 0])
    randDots.setFieldPos([posX * -targetSide, 0])
    
    
    
    for counter, motion in enumerate(motionList_for_block): 
        m0 = time.time()  # record the start time
        
        #print motion
        
        doThreeTimes = 0
        magicFrame = choice(range(0, 90)) #initialize random magic frame
        colorPresented = choice(['yellow', 'red'])
        fixationColored.color = colorPresented
        colorlist.append(colorPresented)
        
        # resetting dot locations: to eleminate countinuations of previous trial to the next
        dotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))  # array of random float numbers between fieldSize range
        dotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))
        dotsTheta = numpy.random.rand(dotsN) * 360  # array with shape (500,)
        dotsRadius = numpy.random.rand(dotsN) * fieldSize
        
        # Frame Loop
        for frameN in range(durTrial):
            dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
            deathDots = (dieScoreArray <= chanceToDie_atEachFrame) #each dot have maximum of 10 frames life
            
            #lifetime for stationary dots
            #randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
            #randDots.setXYs(numpy.array([randDotsX, randDotsY]).transpose())
            
            if frameN < second:
                moveSign = 1
            else:
                moveSign = -1
            if motion in [['transVertical'],['transHorizontal']]:
                transOutfieldDotsY = numpy.logical_or((dotsY >= deathBorder), (dotsY <= -deathBorder))
                transOutfieldDotsX = numpy.logical_or((dotsX >= deathBorder), (dotsX <= -deathBorder))
                if motion == ['transHorizontal']:
                    dotsY += speed * moveSign
                    dotsY[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
                    dotsY[transOutfieldDotsY] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(transOutfieldDotsY,)))
                else:
                    dotsX += speed * moveSign
                    dotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
                    dotsX[transOutfieldDotsX] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(transOutfieldDotsX,)))
                transDots.setXYs(numpy.array([dotsX, dotsY]).transpose())
                stim = transDots
            else:
                polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion)
                stim = rotDots 
            
            #checking if it is magicFrame
            if frameN >= magicFrame and doThreeTimes <= 3: # 0 , 1 , 2 =  3 times
                fixa = fixationColored
                doThreeTimes += 1
                if doThreeTimes == 3:
                    Color_started = True
            else:
                fixa = fixationRegular
            
            stim.draw()
            randDots.draw()
            fixa.draw()
            maskStim1.draw()
            maskStim2.draw()
            win.flip()

        #collect responses
        keys = event.getKeys(keyList=["1", "4", "escape"] )
        for key in keys:
            if key == '1' and Color_started:  #
                if colorPresented == 'red':
                    response = 1
                    #yazdir
                elif colorPresented =='yellow':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == '4' and Color_started:
                if colorPresented == 'yellow':
                    response = 1
                elif colorPresented == 'red':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == 'escape':
                   win.close()
                   core.quit()
            else:
                response = None
                responses.append(response)
        
        
        m1 = time.time()
        motionTime = m1-m0
        #print "motion Time was:", motionTime

#List Creation
motionTypes = [['transVertical']]#['transVertical'], ['transHorizontal'], ['angular'], ['radial']
BlockList = []
motionList = []
list_of_selected_motions = []
nBlocks_in_one_set = 4

startValue= 0
endValue=6

list_of_selected_motions = []

for times in range(nSets):
    BlockList.extend(['S']) #    BlockList.extend(['L','R','B','S'])

#print BlockList

for times in range(nSets*6): ##Here 4 means there are 4 types of motion types in a block of 6 motions. #nSets*4(L,R,B,S) = 24 blocks in total: each block has 6 motion. With this equation we find that number of motionType set is multiplication of nSets. (nSets = 5; nTimes = 30)
    motionList.extend(motionTypes)

#defining sets of motion for each block, 6 li bir liste
for times in range(len(BlockList)): 
    list_of_selected_motions.append(motionList[startValue+times*6:endValue+times*6])

#print list_of_selected_motions

print(motionList)
### EXPERIMENT BEGINS ###
for counter, currentState in enumerate(BlockList):
    b0 = time.time()
    #identify motion list here (tuple of 6 items) and it should be different for every block
    
    motionList_for_block = list_of_selected_motions[counter]
    #print motionList_for_block
    
    # alternating x position at every trial (left vs right)
    if currentState == 'L':
        targetSide = -1
        LeftMovingDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block) #no update on randDots
    elif currentState == 'R':
        targetSide = 1
        LeftMovingDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block) #no update on randDots
    elif currentState == 'B':
        targetSide = 1 #arbitrary
        BothMovingDots(dotsRadius, dotsTheta, randDotsRadius, randDotsTheta, transDots, rotDots, randDots,polarRandomDots, speed, targetSide, motionList_for_block)
    elif currentState == 'S':
        targetSide = 1 #arbitrary
        BothStaticDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block)
    
    b1 = time.time()
    blockDuration = b1-b0
    #print "blockDuration:", blockDuration


### save data ###
rows = zip(colorlist,responses,keyList)
with open(fileName+'DotsLocalizer.csv', 'wb') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

win.close()
core.quit()







""" globalClock = core.Clock()

#Data Handling
try: #try to get a previous parameters file
    expInfo = fromFile('lastParams.pickle')
except:#if not there then use a default set
    expInfo = {'observer':'','practice': 1} #add more if you want
expInfo['dateStr']= data.getDateStr() #add the current time
#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Gabor', fixed=['dateStr'])
if dlg.OK == False:
    core.quit()

#make a text file to save data
fileName = expInfo['observer'] + expInfo['dateStr']

#display options
refRate = 60  # 1 second
second = refRate
posX = 8.02
posY = 0

# Desing parameters
durInitialBlank = 24 * second
nSets = 6 #how many large-small sets? 6 means 288 seconds
nTrials = 6 # 6 * blockDuration = 6*2 = 12 seconds in total at each trial
durTrial  = second*2 # 1 round equals 4 seconds motion, inverting after 2 second
BlockList = ['BM','B']

# Grating options
smallStim = 1.67
largeStim = 8.05


# some important list for the experiment handling
responses = []
colorlist = []
keyList = []
response = None
rows = []

#stimuli & window initializing 
win = visual.Window([1920, 1080], units = 'deg', monitor = 'testMonitor', color = 'gray',fullscr=False)
win.setRecordFrameIntervals(True)

fixation = visual.GratingStim(win, size=0.2, pos=[0,0], sf=0,color = 'black')
fixationColored = visual.GratingStim(win, size=0.2, pos=[0,0], sf=0,color = 'red')
fixationRegular = visual.GratingStim(win, size=0.2, pos=[0,0], sf=0,color = 'black')




targetGaborLarge = visual.GratingStim(win, mask='gauss', sf=1, name='gabor', color = 1, size=largeStim, pos = (posX,posY), ori = 90, contrast = 0.99, texRes = 512)
targetGaborSmall = visual.GratingStim(win, mask='gauss', sf=1, name='gabor', color = 1, size=smallStim, pos = (posX,posY), ori = 90, contrast = 0.99, texRes = 512)
foilGaborLarge = visual.GratingStim(win, mask='gauss', sf=1, name='gabor', color = 1, size=largeStim, pos = (posX,posY), ori = 90,contrast = 0.99,  texRes = 512)
foilGaborSmall = visual.GratingStim(win, mask='gauss', sf=1, name='gabor', color = 1, size=smallStim, pos = (posX,posY), ori = 90,contrast = 0.99, texRes = 512)


def SingleMovingGrating(targetGabor, foilGabor, targetSide):
    ''' moves single Grating at the targetSide specified for the block '''
    
    targetGabor.setPos([posX*targetSide, posY]) 
    foilGabor.setPos([posX*-targetSide, posY])
    
    for trial in range(nTrials):
        t0= time.time()
        #keys = event.getKeys(keyList=["1", "4", "escape"])
        doThreeTimes = 0
        magicFrame = choice(range(0, 90)) #initialize random magic frame
        colorPresented = choice(['yellow', 'red'])
        fixationColored.color = colorPresented
        colorlist.append(colorPresented)
        
        for frameN in range(durTrial):
            if trial%2 == 0:# 0-120
                targetGabor.setPhase(0.1,'+')
                #foilGabor.setPhase(0.1,'+') #FOIL DOES NOT MOVE
            else: # 120 - 240
                targetGabor.setPhase(0.1,'-')
                #foilGabor.setPhase(0.1,'-') #FOILD DOES NOT MOVE
            
            #checking if it is magicFrame            
            if frameN >= magicFrame and doThreeTimes < 3: # 0 , 1 , 2 =  3 times
                fixa = fixationColored
                doThreeTimes += 1
                if doThreeTimes == 3:
                    Color_started = True
            else:
                fixa = fixationRegular
            targetGabor.draw()
            foilGabor.draw()
            fixa.draw()
            win.flip()
        
        
        #collect responses
        keys = event.getKeys(keyList=["1", "4", "escape"])
        for key in keys:
            if key == '1' and Color_started:  #
                if colorPresented == 'red':
                    response = 1
                elif colorPresented =='yellow':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == '4' and Color_started:
                if colorPresented == 'yellow':
                    response = 1
                elif colorPresented == 'red':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == 'escape':
                    win.close()
                    core.quit()
            else:
                response = None
                responses.append(response)

        t1 = time.time()
        trialLasts = t1-t0 # it should be 2 seconds
        #print "trial lasts:", trialLasts


def BothMovingGratings(targetGabor, foilGabor, targetSide, BothMove):
    ''' moves (or not) both grating at the periphery '''
    
    targetGabor.setPos([posX*targetSide, posY]) 
    foilGabor.setPos([posX*-targetSide, posY])
    
    for trial in range(nTrials):
        t0 = time.time()
        #selecting MagicFrame
        doThreeTimes = 0
        magicFrame = choice(range(0, 90)) #initialize random magic frame
        colorPresented = choice(['yellow', 'red'])
        fixationColored.color = colorPresented
        colorlist.append(colorPresented)
        
        for frameN in range(durTrial):
            if trial%2== 0: # round = 0,2,4; 0-120 (first 2 seconds)
                if BothMove == True:
                    targetGabor.setPhase(0.1,'+')
                    foilGabor.setPhase(0.1,'+') 
            else: # round 1,3,5 = move opposite direction
                if BothMove == True:
                    targetGabor.setPhase(0.1,'-')
                    foilGabor.setPhase(0.1,'-') #FOILD DOES NOT MOVE
            
            #checking if it is magicFrame
            if frameN >= magicFrame and doThreeTimes < 3: # 0 , 1 , 2 =  3 times
                fixa = fixationColored
                doThreeTimes += 1
                if doThreeTimes == 3:
                    Color_started = True
            else:
                fixa = fixationRegular
            targetGabor.draw()
            foilGabor.draw()
            fixa.draw()
            win.flip()
        
        
        #collect responses
        keys = event.getKeys(keyList=["1", "4", "escape"])
        for key in keys:
            if key == '1' and Color_started:  #
                if colorPresented == 'red':
                    response = 1
                elif colorPresented =='yellow':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == '4' and Color_started:
                if colorPresented == 'yellow':
                    response = 1
                elif colorPresented == 'red':
                    response = -1
                responses.append(response)
                keyList.append(key)
            elif key == 'escape':
                    win.close()
                    core.quit()
            else:
                response = None
                responses.append(response)

        t1 = time.time()
        trialLasts = t1-t0 # it should be 2 seconds
        #print "trial lasts:", trialLasts
    


#print BlockList

##TRIGGER BOX
if expInfo['practice'] == 0:
    event.waitKeys(keyList = ['6'])

    ##24 sec wait
    for times in range(durInitialBlank):
        fixation.draw()
        win.flip()


#### TRIAL LOOP ####
for set in range(nSets): #1 set equals to 4 conditions
    t0 = time.time()
    if set % 2 == 0:
        targetGabor = targetGaborLarge
        foilGabor = foilGaborLarge
    else:
        targetGabor = targetGaborSmall
        foilGabor = foilGaborSmall

    for currentState in BlockList:
        s0 = time.time()
        #keys = event.getKeys(keyList=["1", "4", "escape"] )
    
        # alternating x position at every trial (left vs right)
        if currentState == 'L':
            targetSide = -1
            SingleMovingGrating(targetGabor, foilGabor, targetSide)
        elif currentState == 'R':
            targetSide = 1
            SingleMovingGrating(targetGabor, foilGabor, targetSide)
        elif currentState == 'BM':
            targetSide = 1 #arbitrary
            BothMove = True
            BothMovingGratings(targetGabor, foilGabor, targetSide, BothMove)
        elif currentState == 'BS':
            targetSide = 1 #arbitrary
            BothMove = False
            BothMovingGratings(targetGabor, foilGabor, targetSide, BothMove)
        elif currentState =='B':
            for times in range(6):
                t0 = time.time()
                doThreeTimes = 0
                magicFrame = choice(range(0, 90)) #initialize random magic frame
                colorPresented = choice(['yellow', 'red'])
                fixationColored.color = colorPresented
                colorlist.append(colorPresented)
                #selecting MagicFrame
                for frameN in range(durTrial):
                    #checking if it is magicFrame
                    if frameN >= magicFrame and doThreeTimes < 3: # 0 , 1 , 2 =  3 times
                        fixa = fixationColored
                        doThreeTimes += 1
                        if doThreeTimes == 3:
                            Color_started = True
                    else:
                        fixa = fixationRegular
                    fixa.draw()
                    win.flip()
        
        s1 = time.time()
        trialDuration = s1-s0
        #print "trialDuration:", trialDuration

rows = zip(colorlist,responses,keyList)
with open(fileName + 'Gabor.csv', 'wb') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

win.close()
core.quit() """