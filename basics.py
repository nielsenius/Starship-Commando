# basics.py
# Matthew Nielsen, Section H, mqn


from Tkinter import *

class Animation(object):

    def init(self): pass
    def timerFired(self): pass
    def mousePressed(self): pass
    def keyPressed(self): pass
    def redrawAll(self): pass

    def startTimerFired(self):
        if (self.timerFiredIsRunning == False):
            self.timerFiredIsRunning = True
            self.timerFiredWrapper()

    def stopTimerFired(self):
        if (self.timerFiredIsRunning == True):
            self.timerFiredIsRunning = False

    def timerFiredWrapper(self):
        self.timerFired()
        self.redrawAll()
        if (self.timerFiredIsRunning == True):
            self.canvas.after(self.timerDelay, lambda :
                              self.timerFiredWrapper())

    def run(self):
        # create the root and the canvas
        root = Tk()
        self.canvasWidth = 640
        self.canvasHeight = 480
        self.canvas = Canvas(root, width = self.canvasWidth,
                             height =  self.canvasHeight)
        self.canvas.pack()
        # Set up canvas data and call init
        self.timerDelay = 500
        self.timerFiredIsRunning = False
        self.init()  # init(canvas) # DK: init() --> init(canvas)
        # set up events
        root.bind("<KeyPress>", lambda event: self.keyPressed(event))
        root.bind("<KeyRelease>", lambda event: self.keyReleased(event))
        self.startTimerFired()
        # and launch the app
        root.mainloop()
