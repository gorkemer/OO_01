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

''' 28 March 2018 
Localizer program in python to locate MT+, MST, MST separately using dot motion fields.
Program description: MT localizer use four conditions (in this program it is called "a set") 
                    each lasting 12 seconds totaling 48 seconds (TR = 2.000 ms). 
Program terminology: 
    one Set = 'L', 'R', 'B', 'S' meaning 4 items
    randDots =  means foilDots (non-target ones)
    block = one "L", lasts 12 seconds
Design: Factorial design with combinations of DotCondition (moving or stationary) x TargetSide (left or both sides)
Used parameters: 
    6 sets of 4 conditions lasting 288 seconds, 144 TR
    24 seconds of initial blank, 12 TR
    totaling 156 TR (number of slices)
# nSets*nBlocks #nBlock = 4, nMotions = 6, here we will have 6*4*6 = 144 (each motion lasts 2 seconds, totaling 244 seconds
#print(numpy.ravel(motionList))
'''

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
fieldSize = 4 # if you put 3 here it means 3 in diameter but the total rectangular shape has 6 degree (-3 to 3)
elemSize = 0.20
speed = 7/60 # 7 degree/seconds
chanceToDie_atEachFrame = 0.01
centerDissappearence = 0.2
deathBorder = fieldSize - elemSize


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
randDotsX = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))
randDotsY = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(dotsN,))

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

randDots = visual.ElementArrayStim(win,
                                   nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                   colors=(1.0, 1.0, 1.0), xys=numpy.array([randDotsX, randDotsY]).transpose(),
                                   colorSpace='rgb', elementMask='circle',
                                   fieldSize=(fieldSize, fieldSize),fieldShape = 'sqr')

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
    
def BothStaticDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block):
    ''' function for the block that presents stationary dots at periphery '''
    
    rotDots.setFieldPos([posX * targetSide, 0])
    transDots.setFieldPos([posX * targetSide, 0])
    randDots.setFieldPos([posX * -targetSide, 0])

    
    for counter, motion in enumerate(motionList_for_block):
        
        doThreeTimes = 0
        magicFrame = choice(range(0, 90)) #initialize random magic frame
        colorPresented = choice(['yellow', 'red'])
        fixationColored.color = colorPresented
        colorlist.append(colorPresented)
        
        for frameN in range(durTrial):
            #lifetime
            dieScoreArray = numpy.random.rand(dotsN)  # generating array of float numbers
            deathDots = (dieScoreArray <= chanceToDie_atEachFrame) #each dot have maximum of 10 frames life
            
            #randDotsX[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
            #randDots.setXYs(numpy.array([randDotsX, randDotsY]).transpose())
            
            
            #dotsY[deathDots] = numpy.random.uniform(low=-fieldSize, high=fieldSize,size=(sum(deathDots,)))
            #transDots.setXYs(numpy.array([dotsX, dotsY]).transpose())
            
            #checking if it is magicFrame
            if frameN >= magicFrame and doThreeTimes <= 3: # 0 , 1 , 2 =  3 times
                fixa = fixationColored
                doThreeTimes += 1
                if doThreeTimes == 3:
                    Color_started = True
            else:
                fixa = fixationRegular
            
            transDots.draw()
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

def BothMovingDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block):
    ''' function for a block where both sides at the periphery moves '''
    
    rotDots.setFieldPos([posX * targetSide, 0])
    transDots.setFieldPos([posX * targetSide, 0])
    randDots.setFieldPos([posX * -targetSide, 0])
    
    
    for counter, motion in enumerate(motionList_for_block): 
        m0 = time.time()  # record the start time
        
        #motion = choice_without_repetition(motionList)
        
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
                randDots.setXYs(numpy.array([dotsX, dotsY]).transpose())
                stim = transDots

            else:
                polarDotMove(dotsRadius, dotsTheta, rotDots, speed, deathDots, moveSign, motion)
                thetaX, radiusY = pol2cart(dotsTheta, dotsRadius)
                randDots.setXYs(numpy.array([thetaX, radiusY]).transpose())
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
motionTypes = ['angular'], ['radial']
BlockList = []
motionList = []
list_of_selected_motions = []
nBlocks_in_one_set = 4

startValue= 0
endValue=6

list_of_selected_motions = []

for times in range(nSets):
    BlockList.extend(['B'])

#print BlockList

for times in range(nSets*6): ##Here 4 means there are 4 types of motion types in a block of 6 motions. #nSets*4(L,R,B,S) = 24 blocks in total: each block has 6 motion. With this equation we find that number of motionType set is multiplication of nSets. (nSets = 5; nTimes = 30)
    motionList.extend(motionTypes)

#defining sets of motion for each block, 6 li bir liste
for times in range(len(BlockList)): 
    list_of_selected_motions.append(motionList[startValue+times*6:endValue+times*6])

#print list_of_selected_motions

##TRIGGER BOX & INITIAL BLANK
if expInfo['practice'] == 0:
    event.waitKeys(keyList = ['6'])

    ##24 sec wait
    for times in range(durInitialBlank):
        fixation.draw()
        win.flip()


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
        BothMovingDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block)
    elif currentState == 'S':
        targetSide = 1 #arbitrary
        BothStaticDots(dotsRadius, dotsTheta, transDots, rotDots, randDots, speed, targetSide, motionList_for_block)
    
    b1 = time.time()
    blockDuration = b1-b0
    #print "blockDuration:", blockDuration



rows = zip(colorlist,responses,keyList)
with open(fileName+'DotsLocalizer.csv', 'wb') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

win.close()
core.quit()