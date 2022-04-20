from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui, tools, filters
from psychopy.visual import filters
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal #shuffle
import os  # handy system and path functions
from random import choice, randrange, shuffle, uniform, sample
#from psychopy.tools.coordinatetools import pol2cart, cart2pol
import time
from psychopy.tools.filetools import fromFile, toFile
import csv

#data handling
try: #try to get a previous parameters file
    expInfo = fromFile('lastParams.pickle')
except:#if not there then use a default set
    expInfo = {'trial_duration':2, 'practice': 1} #add more if you want # 'InitialPosition':0
expInfo['dateStr']= data.getDateStr() #add the current time
#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Gabor', fixed=['dateStr'])
if dlg.OK == False: #quiting if the user pressed 'cancel'
    core.quit()

# Display Options
refRate = 60  # 1 second
second = refRate  # stimulus duration = 2 seconds

dotsN = 200
elemSize = 0.05
baselineSpeed = 7/60 # 7 degree/seconds
chanceToDie_atEachFrame = 0.01
centerDissappearence = 0
fieldSize = 2.3
deathBorder = fieldSize - elemSize
speed = 1/60 # 7/60 means 7 degree/seconds
trialDuration = int(expInfo['trial_duration']) * second
print (trialDuration)
flag = -1 #1 ekliyor loop un icine girdiginde, niye yapiyor anlamadim ama ellipse listesindeki sayinin 1 eksigini girmelisin
stim1_list_ordered = []
stim2_list_ordered = []
YdisplacesmentValue = 0 #positive values moves the stim1 to the top, and stim2 to the bottom
XdisplacesmentValue = 5 #positive values moves the stim1 to the right, and stim2 to the left

dot1_xys = []
dot2_xys = []

#initializing window & stimuli
win = visual.Window([1920, 800], units='deg',
                    monitor='testMonitor', color='gray', fullscr = False, allowStencil=True)

#dotsX = np.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))  # array of random float numbers between fieldSize range
#dotsY = np.random.uniform(low=-fieldSize, high=fieldSize, size=(dotsN,))

for dot in range(dotsN):

    dot1_x = uniform(-fieldSize + XdisplacesmentValue, fieldSize + XdisplacesmentValue)
    dot1_y = uniform(-fieldSize+YdisplacesmentValue,fieldSize+YdisplacesmentValue)

    dot1_xys.append([dot1_x, dot1_y])

    dot2_x = uniform(-fieldSize-XdisplacesmentValue, fieldSize-XdisplacesmentValue)
    dot2_y = uniform(-fieldSize-YdisplacesmentValue,fieldSize-YdisplacesmentValue)

    dot2_xys.append([dot2_x, dot2_y])


fixation = visual.GratingStim(win, size=0.1, pos=[0,0], sf=0,color = 'black')
invCircle = filters.makeMask(1024,'circle')*-1 #1 makes inside white, -1 makes outside white, raisedCosine da olur

ellipseDimensionList = [4.6,4.5,4.3,4.2,4.05,3.75,3.6,3.45,3.3,3.15,3,2.85,2.55,2.4,2.25,2.1,2.05,1.95,1.9,1.75]

for i in range(len(ellipseDimensionList)):
    index = i+1
    stim1_list_ordered.append(visual.GratingStim(win, tex=None, name='firstEllipse', mask=invCircle,
    size=(ellipseDimensionList[i],ellipseDimensionList[-index]), color = 'gray', pos=(XdisplacesmentValue,YdisplacesmentValue), texRes = 1024))

    stim2_list_ordered.append(visual.GratingStim(win, tex=None, name='firstEllipse', mask=invCircle,
    size=(ellipseDimensionList[i],ellipseDimensionList[-index]), color = 'gray', pos=(XdisplacesmentValue*-1,YdisplacesmentValue*-1), texRes = 1024))
    #print(stim1_list_ordered[i].size)


stim_list1 = sample(stim1_list_ordered, len(stim1_list_ordered))
stim_list2 = sample(stim2_list_ordered, len(stim2_list_ordered))

#lineColor='blue'
#def createDebugSquare(stimEllipse_size):
#    debugSquare = visual.Rect(win,
#        width=(stimEllipse_size[0]),
#        height=(stimEllipse_size[1]),
#        lineWidth=1,
#        pos = [0,0],
#        closeShape=False
#        )
#    return debugSquare

debugDotsFieldSize = visual.Rect(
    win=win,
    width= fieldSize*2,
    height=fieldSize*2,
    lineColor='red',
    pos= [-10,0])

def createAperture(stimEllipse_size):
    aperture = visual.Aperture(win, size=[stimEllipse_size[0],stimEllipse_size[1]], shape='circle')
    return aperture


transDots_debug = visual.ElementArrayStim(win, #colors=(1.0, 1.0, 1.0)
                                    nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                    colors='white', xys=dot1_xys,
                                    colorSpace='rgb', elementMask='circle',
                                    fieldSize=fieldSize, fieldShape = 'sqr') #(fieldSize, fieldSize)


transDots = visual.ElementArrayStim(win, #colors=(1.0, 1.0, 1.0)
                                    nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                    colors='white', xys=dot1_xys,
                                    colorSpace='rgb', elementMask='circle',
                                    fieldSize=fieldSize, fieldShape = 'sqr') #(fieldSize, fieldSize)

transDots2 = visual.ElementArrayStim(win, #colors=(1.0, 1.0, 1.0)
                                    nElements=dotsN, units = 'deg', sizes=elemSize, elementTex=None,
                                    colors='white', xys=dot2_xys,
                                    colorSpace='rgb', elementMask='circle',
                                    fieldSize=fieldSize, fieldShape = 'sqr') #(fieldSize, fieldSize)


t1= time.time()  # record the start time
for frameN in range(trialDuration):
            if frameN % 60 == 0:
                flag += 1
                print (flag)

                dot1_x = np.random.uniform(low=-fieldSize + XdisplacesmentValue, high=fieldSize + XdisplacesmentValue - elemSize, size=(dotsN,))  # array of random float numbers between fieldSize range
                dot1_y = np.random.uniform(low=-fieldSize + YdisplacesmentValue, high=fieldSize + YdisplacesmentValue, size=(dotsN,))

                dot2_x = np.random.uniform(low=-fieldSize -XdisplacesmentValue, high=fieldSize - XdisplacesmentValue - elemSize, size=(dotsN,))  # array of random float numbers between fieldSize range
                dot2_y = np.random.uniform(low=-fieldSize - YdisplacesmentValue, high=fieldSize - YdisplacesmentValue, size=(dotsN,))

            #selecting the stimulus from a list
            stimEllipse1 = stim_list1[flag]
            stimEllipse2 = stim_list2[flag]

            #defining death areas
            dieScoreArray = np.random.rand(dotsN)  # generating array of float numbers
            deathDots = (dieScoreArray <= chanceToDie_atEachFrame) #each dot have maximum of 10 frames life %10 percent of all the dots are removed in every frame

            #applying speed
            dot1_y += speed * 1 #move sign atayabilirsin loop icinde 1 veya -1
            dot2_y += speed * -1 #move sign atayabilirsin 1 veya -1

            #boundary definitions #elemsize cikarildi ki borden biraz daraltildi
            ellipse1_Boundary_X = np.logical_or((dot1_x >= (stimEllipse1.size[0]/2)+ XdisplacesmentValue-elemSize), (dot1_x <= (-stimEllipse1.size[0]/2)+ XdisplacesmentValue +elemSize))
            ellipse1_Boundary_Y = np.logical_or((dot1_y >= (stimEllipse1.size[1]/2)+ YdisplacesmentValue-elemSize), (dot1_y <= (-stimEllipse1.size[1]/2)+ YdisplacesmentValue+elemSize))

            #from stim 2##
            ellipse2_Boundary_X = np.logical_or((dot2_x >= (stimEllipse2.size[0]/2)-XdisplacesmentValue-elemSize), (dot2_x <= (-stimEllipse2.size[0]/2)-XdisplacesmentValue+elemSize))
            ellipse2_Boundary_Y = np.logical_or((dot2_y >= (stimEllipse2.size[1]/2)- YdisplacesmentValue-elemSize), (dot2_y <= (-stimEllipse2.size[1]/2)- YdisplacesmentValue+elemSize))


            #creating new dots after hitting boundaries
            dot1_x[ellipse1_Boundary_X] = np.random.uniform(low=-stimEllipse1.size[0]/2+XdisplacesmentValue, high=stimEllipse1.size[0]/2 +XdisplacesmentValue,size=(sum(ellipse1_Boundary_X,)))
            dot1_y[ellipse1_Boundary_Y] = np.random.uniform(low=-stimEllipse1.size[1]/2+ YdisplacesmentValue, high=stimEllipse1.size[1]/2+ YdisplacesmentValue,size=(sum(ellipse1_Boundary_Y,)))
            dot1_y[deathDots] = np.random.uniform(low=-stimEllipse1.size[1]/2+ YdisplacesmentValue, high=stimEllipse1.size[1]/2+ YdisplacesmentValue,size=(sum(deathDots,)))

            # For Stim 2 ## creating new dots after hitting boundaries
            dot2_x[ellipse2_Boundary_X] = np.random.uniform(low=-stimEllipse2.size[0]/2 -XdisplacesmentValue, high=stimEllipse2.size[0]/2 - XdisplacesmentValue,size=(sum(ellipse2_Boundary_X,)))
            dot2_y[ellipse2_Boundary_Y] = np.random.uniform(low=-stimEllipse2.size[1]/2- YdisplacesmentValue, high=stimEllipse2.size[1]/2- YdisplacesmentValue,size=(sum(ellipse2_Boundary_Y,)))
            dot2_y[deathDots] = np.random.uniform(low=-stimEllipse2.size[1]/2- YdisplacesmentValue, high=stimEllipse2.size[1]/2- YdisplacesmentValue,size=(sum(deathDots,)))


            #debugEllipse = createDebugSquare(stimEllipse1.size)

            transDots.setXYs(np.array([dot1_x, dot1_y]).transpose())
            transDots2.setXYs(np.array([dot2_x, dot2_y]).transpose())

            stim = transDots

            #debug stimuli
            #debugEllipse.draw()
            #debugDotsFieldSize.draw()
            transDots2.draw()

            stim.draw()
            stimEllipse1.draw()
            stimEllipse2.draw()
            #drawing experiment stimuli

            fixation.draw()
            win.flip()
t2= time.time()
print(t2-t1)