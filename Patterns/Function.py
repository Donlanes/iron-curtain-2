'''
Functions are functions used to modify patterns. They take a pattern or multiple
patterns, besides arguments,  and output a different pattern.

Metafunctions take a function, and output a different function

Patterns are functions that take a PatternInput and return a PatternInput 
'''
import colorsys
import functools
from functools import wraps
import copy

_dict_of_functions={}
_dict_of_meta_functions={}
def function(name):
    '''
    To add your function to the dictionary of functions
    add the decorator @function(name) on your pattern.
    '''
    def builder(patternFunction):
        _dict_of_functions[name]=patternFunction
        return patternFunction
    return builder

def metaFunction(name):
    '''
    To add your metaFunction to the dictionary of metaFunctions
    add the decorator @metaFunction(name) on your pattern.
    '''
    def builder(metaFunction):
        _dict_of_meta_functions[name]=metaFunction
        return metaFunction
    return builder

def getFunctionDict():
    return _dict_of_functions

def getMetaFunctionDict():
    return _dict_of_meta_functions

@metaFunction("compose")
def compose(*functions):
    '''
    Composes one or more functions
    '''
    if len(functions)==1:
        return functions[0]
    elif len(functions)==2:
        return lambda patternInput: functions[0](functions[1](patternInput))
    else:
        nHalfFunctions = len(functions)/2
        return lambda patternInput: compose(*functions[0:nHalfFunctions])(compose(*functions[nHalfFunctions:])(patternInput))


def functionize(myFunction):
    '''
    Turns a function that takes a patternInput and returns a patternInput
    into a function that takes a pattern and returns a pattern with
    its patternInput modified
    '''
    @wraps(myFunction) #preserves __name__ and __doc__
    def function(pattern):
        return compose(myFunction,pattern)
    return function

def rFunctionize(myFunction):
    '''
    Turns a function that takes a patternInput and returns a patternInput
    into a function that takes a pattern and runs the pattern on the modified
    patternInput
    '''
    @wraps(myFunction) #preserves __name__ and __doc__
    def function(pattern):
        return compose(pattern,myFunction)
    return function

def metaFunctionize(myMetaFunction):
    '''
    Takes a function that takes a pattern and returns a pattern
    and returns a metaFunction that takes a function and returns a function
    '''
    @wraps(myMetaFunction) #preserves __name__ and __doc__
    def metaFunction(function):
        return compose(myMetaFunction,function)
    return metaFunction

def rMetaFunctionize(myMetaFunction):
    '''
    Takes a function that takes a pattern and returns a pattern
    and returns a metaFunction that takes a function and returns a function
    See rFunctionize
    '''
    @wraps(myMetaFunction) #preserves __name__ and __doc__
    def metaFunction(function):
        return compose(function,myMetaFunction)
    return metaFunction

@metaFunction('defaultArgs')
def defaultArguments(**kwargs):
    '''
    usage: defaultArgs(arg=value)(function) -> function
    defaultArgs(arg=value)(function)(pattern) -> pattern
    order of execution: function(pattern(applyDefaultArguments))
    '''
    hasRun=[False]

    @rMetaFunctionize
    @rFunctionize
    def runOnceApplyDefaultArguments(patternInput):
        if hasRun[0]==False or any([not patternInput.has_key(key) for key in kwargs.keys()]):
            hasRun[0]=True
            patternInput.update(kwargs)
            return patternInput
        else:
            return patternInput
    return runOnceApplyDefaultArguments

def defaultArgsP(**kwargs):
    '''
    usage: defaultArgs(arg=value)(function) -> function
    defaultArgs(arg=value)(function)(pattern) -> pattern
    order of execution: function(pattern(applyDefaultArguments))
    '''
    hasRun=[False]

    @rFunctionize
    def runOnceApplyDefaultArguments(patternInput):
        if hasRun[0]==False or any([not patternInput.has_key(key) for key in kwargs.keys()]):
            hasRun[0]=True
            patternInput.update(kwargs)
            return patternInput
        else:
            return patternInput
    return runOnceApplyDefaultArguments

@metaFunction('constArgs')
def constantArguments(**kwargs):
    '''
    usage: constantArgs(arg=value)(function) -> function
    constantArgs(arg=value)(function)(pattern) -> pattern
    order of execution: function(pattern(applyArguments))
    '''
    @rMetaFunctionize
    @functionize
    def applyArguments(patternInput):
        newPatternInput=copy.copy(patternInput)
        newPatternInput.update(kwargs)
        return newPatternInput
    return applyArguments

            
@function('constant')
def constant(pattern):
    '''
    Gets the output canvas once, always send the same output canvas
    '''
    cache = [None]
    @wraps(pattern) #preserves __name__ and __doc__
    def cached_f(patternInput):
        if cache[0]==None:
            cache[0] = copy.deepcopy(pattern(patternInput)['canvas'])
        patternInput['canvas']=copy.deepcopy(cache[0])
        return patternInput
    return cached_f


@function('step')
def step(pattern0, pattern1):
    '''
    On first run it runs pattern0. On every
    following run it runs pattern1
    '''
    step = [False]
    def steppedPattern(patternInput):
        if step[0]==False:
            step[0]=True
            return pattern0(patternInput)
        else:
            return pattern1(patternInput)
    steppedPattern.__name__= "Stepped: " + str(pattern0.__name__) + "->"+str(pattern1.__name__)
    return steppedPattern

 

'''
End of meta functions
'''

@function('isolate')
def isolate(pattern):
    '''
    Runs the pattern in its own environment
    It updates the frame in each update
    '''
    previousInput = [None]
    @wraps(pattern) #preserves __name__ and __doc__
    def isolated(patternInput):
        if previousInput[0]==None:
            previousInput[0] = copy.deepcopy(patternInput)
        else:
            previousInput[0]['frame']+=1
        return copy.deepcopy(pattern(previousInput[0]))
    return isolated

@function('isolateCanvas')
def isolateCanvas(pattern):
    '''
    Runs the pattern in its own canvas environment
    '''
    previousCanvas = [None]
    @wraps(pattern) #preserves __name__ and __doc__
    def isolated(patternInput):
        if previousCanvas[0]==None:
            previousCanvas[0] = copy.deepcopy(patternInput['canvas'])
        isolatedPatternInput = copy.copy(patternInput)
        isolatedPatternInput['canvas']=previousCanvas[0]
        patternOutput = pattern(isolatedPatternInput)
        previousCanvas[0]=copy.deepcopy(patternOutput['canvas'])
        return patternOutput
    return isolated


@function('movingHue')
@defaultArguments(hueFrameRate=0.01)
@functionize
def movingHue(patternInput):
    hueFrameRate=patternInput["hueFrameRate"]
    def shifter(rgb,y,x):
        amount=patternInput["frame"]*hueFrameRate
        return hsvShifter(rgb,amount)
    canvas=patternInput["canvas"]
    canvas.mapFunction(shifter)
    return patternInput


@function('hueShift')
@defaultArguments(hue=0.01)
@functionize
def movingHue(patternInput):
    hue=patternInput["hue"]
    def shifter(rgb,y,x):
        amount=hue
        return hsvShifter(rgb,amount)
    canvas=patternInput["canvas"]
    canvas.mapFunction(shifter)
    return patternInput

@function('rainbownize')
@defaultArguments(nRainbows=1)
@functionize
def rainbownize(patternInput):
    numberOfRainbows=patternInput["nRainbows"]
    width=patternInput["width"]
    xHueShift =1./width
    def shifter(rgb,y,x):
        amount=xHueShift*x*numberOfRainbows
        return hsvShifter(rgb,amount)
    canvas=patternInput["canvas"]
    canvas.mapFunction(shifter)
    return patternInput

@function('vRainbownize')
@defaultArguments(nVRainbows=1)
@functionize
def vRainbownize(patternInput):
    '''
    Vertical rainbownize
    '''
    numberOfRainbows=patternInput["nVRainbows"]
    height=patternInput["height"]
    yHueShift =1./height
    def shifter(rgb,y,x):
        amount=yHueShift*y*numberOfRainbows
        return hsvShifter(rgb,amount)
    canvas=patternInput["canvas"]
    canvas.mapFunction(shifter)
    return patternInput


def combineCanvas(colorCombiner):
    def combineFunction(*patterns):
        def combinedPattern(patternInput):
            patternOutputs=[]
            for pattern in patterns:
                patternOutputs.append(pattern(copy.deepcopy(patternInput)))
            canvass=[]
            for patternOutput in patternOutputs:
                canvass.append(patternOutput['canvas'])
            def combiner(rgb,y,x):
                return colorCombiner(*[canvas[y,x] for canvas in canvass])
            canvas=patternInput['canvas']

            for patternOutput in patternOutputs:
                patternInput.update(patternOutput)
                
            canvas.mapFunction(combiner)
            patternInput['canvas']=canvas
            return patternInput
        return combinedPattern
    return combineFunction


@function('meanP')
@combineCanvas
def meaner(*colors):
    colorOutput= tuple([sum(color)/len(colors) for color in zip(*colors)])
    return colorOutput

@function('addP')
@combineCanvas
def addPattern(*colors):
    colorOutput= tuple([sum(color) for color in zip(*colors)])
    return colorOutput

@function('mask')
@combineCanvas
def masker(color0, color1, color2):
    if any(color0):
        colorOutput= color1
    else:
        colorOutput=color2
    return colorOutput


import math
import collections

@function('arg')
def arg(strInstructionToEval):
    @rFunctionize
    def updateArg(patternInput):
        execInPattern(strInstructionToEval, patternInput)
        return patternInput
    return updateArg

def getArgDicts(patternInput):
    return patternInput

def execInPattern(strInstructionToEval, patternInput):
    defaultDict =collections.defaultdict(int)
    defaultDict['abs']=abs
    defaultDict.update(math.__dict__)
    exec strInstructionToEval in defaultDict, patternInput

def hsvShifter(rgb,amount):
    h,s,v=colorsys.rgb_to_hsv(*rgb)
    h +=amount
    return colorsys.hsv_to_rgb(h,s,v)

@function('timeChanger')
def timechange(patternnArray, timeArray):
    totalTime = sum(timeArray)
    startTime=getCurrentTime()

    def timeChangedPattern(patternInput):
        timeElapsed=(getCurrentTime()-startTime)
    
        timeElapsed%=totalTime

        for i in xrange(len(timeArray)):
            time=timeArray[i]
            if timeElapsed>time:
                timeElapsed = timeElapsed-time
            else:
                return patternnArray[i](patternInput)
        return lambda x: x #Should never happen
    return timeChangedPattern

        

import time
def getCurrentTime():
    return time.time()



@function('translate')
@defaultArguments(xTranslate=0, yTranslate=0)
@functionize
def translate(patternInput):
    '''
    percentage translator. args('xTranslate=0; yTranslate=0')
    '''
    height=patternInput["height"]
    width=patternInput["width"]
    xTranslate=patternInput["xTranslate"]
    yTranslate=patternInput["yTranslate"]

    xTranslate = round(xTranslate*width)
    yTranslate = round(yTranslate*height)
    oldcanvas = copy.deepcopy(patternInput["canvas"])

    def translator(rgb,y,x):
        positionY=int((y+yTranslate)%height)
        positionX=int((x+xTranslate)%width)
        color = oldcanvas[positionY, positionX]
        return color
    canvas=patternInput["canvas"]
    canvas.mapFunction(translator)
    patternInput['canvas']=canvas
    return patternInput



@function('blur')
@functionize
def blur(patternInput):
    '''
    blures image
    '''

    oldcanvas = copy.deepcopy(patternInput["canvas"])

    def blurer(rgb,y,x):
        color =tuple([sum(color)/9 for color in zip(*[oldcanvas[y+i,x+j] for i in [-1,0,1] for j in [-1,0,1]])])
        return color
    canvas=patternInput["canvas"]
    canvas.mapFunction(blurer)
    patternInput['canvas']=canvas
    return patternInput
