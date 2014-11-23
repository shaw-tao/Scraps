#!/usr/bin/python2
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from Xlib.display import Display
from Xlib import X, Xatom,Xutil
from ast import literal_eval
from subprocess import Popen, PIPE
import Xlib
import sys
import time
import calendar
import alsaaudio

display = None
root = None
app = QtGui.QApplication(sys.argv)
launch_list = []

class Task(QtGui.QPushButton):
    middleClicked = QtCore.pyqtSignal()
    rightClicked = QtCore.pyqtSignal()
    leftClicked = QtCore.pyqtSignal()

    def __init__(self):
        super(QtGui.QPushButton, self).__init__()

    def mousePressEvent(self, mouseEvent):
        QtGui.QPushButton.mousePressEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() == QtCore.Qt.MidButton:
            self.middleClicked.emit()
        if mouseEvent.button() == QtCore.Qt.RightButton:
            self.rightClicked.emit()
        if mouseEvent.button() == QtCore.Qt.LeftButton:
            self.leftClicked.emit()
        QtGui.QPushButton.mouseReleaseEvent(self, mouseEvent)

class Tasklist(QtGui.QTabBar):
    middleClicked = QtCore.pyqtSignal(int)
    rightClicked = QtCore.pyqtSignal(int)
    leftClicked = QtCore.pyqtSignal(int)

    def __init__(self):
        super(QtGui.QTabBar, self).__init__()
        self.previousMiddleIndex = -1

    def mousePressEvent(self, mouseEvent):
        self.previousIndex = self.tabAt(mouseEvent.pos())
        QtGui.QTabBar.mousePressEvent(self, mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() == QtCore.Qt.MidButton and \
            self.previousIndex == self.tabAt(mouseEvent.pos()):
            self.middleClicked.emit(self.previousIndex)

        if mouseEvent.button() == QtCore.Qt.RightButton and \
            self.previousIndex == self.tabAt(mouseEvent.pos()):
            self.rightClicked.emit(self.previousIndex)

        if mouseEvent.button() == QtCore.Qt.LeftButton and \
            self.previousIndex == self.tabAt(mouseEvent.pos()):
            self.leftClicked.emit(self.previousIndex)
        self.previousIndex = -1
        QtGui.QTabBar.mouseReleaseEvent(self, mouseEvent)

class Taskbar(QtGui.QWidget):

    def __init__(self):
        super(Taskbar, self).__init__()
        self.initUI()

    def initUI(self):

#Tasklist
        self.tasks = []#these will be button objects
        self.middleMapper = QtCore.QSignalMapper()
        self.rightMapper = QtCore.QSignalMapper()
        self.leftMapper = QtCore.QSignalMapper()

#Worspaces
        self.workspaces = []
        for i in range(getWorkspaceCount()-1):
            b = QtGui.QPushButton(QtCore.QString.fromUtf8(getWorkspaceNames()[i])) ; b.setFixedSize(15,20) ; b.setFont(self.fontSmall)
            self.workspaces.append(b)
            self.workspaceLayout.addWidget(self.workspaces[i])
        self.mapper = mapSignals(self.workspaces, setActiveWorkspace)

    def updateTasks(self):
        active_window = getActiveWindow()
        window_list = getWindowList()
        occupied_workspaces = []

        for x in range(len(self.tasks)):
            self.tasks[0].hide()
            self.taskLayout.removeWidget(self.tasks[0])
            del self.tasks[0]
            self.middleMapper.removeMappings(self.middleMapper.mapping(x))
            #Add other mappers or remove this one if redundant

        for x in window_list:
            b = Task() ; b.setFixedSize(60,20) ; b.setFont(self.fontSmall) ; b.setText(x.get_wm_class()[1])
            if getWindowWorkspace(x) == 9:
                b.setStyleSheet("""QPushButton { background-color: #1A1111; color: #96958A }""")
            self.tasks.append(b)
            self.taskLayout.addWidget(self.tasks[window_list.index(x)])
            occupied_workspaces.append(getWindowWorkspace(x))
        if active_window in window_list:
                active_index = window_list.index(active_window)
                self.tasks[active_index].setStyleSheet("""QPushButton { background-color: #F50B30; color: #FFFFFF }""")

        for i in self.workspaces:
            if self.workspaces.index(i) == getActiveWorkspace():
                i.setStyleSheet("""QPushButton { background-color: #F50B30; color: #FFFFFF }""")
            elif self.workspaces.index(i) not in occupied_workspaces:
                i.setStyleSheet("""QPushButton { background-color: #1A1111; color: #96958A }""")
            else:
                i.setStyleSheet(self.styleSheet)

        for item in self.tasks:
            self.middleMapper.setMapping(item, self.tasks.index(item))
            self.rightMapper.setMapping(item, self.tasks.index(item))
            self.leftMapper.setMapping(item, self.tasks.index(item))
            item.middleClicked.connect(self.middleMapper.map)
            item.rightClicked.connect(self.rightMapper.map)
            item.leftClicked.connect(self.leftMapper.map)

    def onTabMiddleClick(self, index):
        sendEventBSPWM(index, '-c')

    def onTabRightClick(self, index):
        print "Right clicked tab", index

    def onTaskLeftClick(self, index):
        toggleMinimizeViaWorkspace(index)
        self.updateTasks()

# --------------
# Main structure
# --------------
def getActiveWorkspace():
    return root.get_full_property(display.intern_atom("_NET_CURRENT_DESKTOP"), Xatom.CARDINAL).value[0]

def setActiveWorkspace(index):
    sendEvent(root, [index, X.CurrentTime], display.intern_atom("_NET_CURRENT_DESKTOP"))
    display.flush()

def getWindowWorkspace(window):
    return window.get_full_property(display.intern_atom("_NET_WM_DESKTOP"), Xatom.CARDINAL).value[0]

def getWorkspaceCount():
    return root.get_full_property(display.intern_atom("_NET_NUMBER_OF_DESKTOPS"), 0).value[0]

def getWorkspaceNames():
    names = root.get_full_property(display.intern_atom("_NET_DESKTOP_NAMES"), 0)
    if hasattr(names, "value"):
        names = names.value.split("\x00")
    else:
        names = []
        for x in range(getWorkspaceCount()):
            names.append(str(x))
    return names

def getActiveWindow():
    return display.create_resource_object("window", root.get_full_property(display.intern_atom('_NET_ACTIVE_WINDOW'), 0).value[0])

def getWindowList():
    return [display.create_resource_object("window", w) for w in root.get_full_property(display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW).value]

def getWindowNames(window_list):
    return ['{:10s}'.format(x.get_wm_name())[0:10] for x in window_list]

def getWindowClass(window_list):
    return [x.get_wm_class() for x in window_list]

def sendEventBSPWM(index, command):
    window_id = root.get_full_property(display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW).value[index]
    Popen(['bspc', 'window', str(hex(window_id))[:-1], command])

def getTiledFocusBSPWM(index):
    pipe = Popen(['bspc', 'query', '-W', '-w', 'focused.tiled'], stdout=PIPE)
    window = pipe.communicate()[0]
    return window

def takeScreenshot():
    QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId()).save('screenshot.png', 'png')

def mapSignals(items, function):
    mapper = QtCore.QSignalMapper()
    for item in items:
        mapper.setMapping(item, items.index(item))
        item.clicked.connect(mapper.map)
    mapper.mapped[int].connect(function)
    return mapper

def sendEvent(win, data, ctype, mask = None):
    data = (data+[0]*(5-len(data)))[:5]
    ev = Xlib.protocol.event.ClientMessage(window=win, client_type=ctype, data=(32,(data)))
    if not mask:
        mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
        root.send_event(ev, event_mask=mask)

def toggleMinimize(index):
    window_list = getWindowList()
    if getActiveWindow() == window_list[index]:#Minimize if active
        sendEvent(window_list[index], [2, display.intern_atom("_NET_WM_STATE_HIDDEN")], display.intern_atom("_NET_WM_STATE"))
        sendEvent(window_list[index], [Xutil.IconicState], display.intern_atom('WM_CHANGE_STATE'))
    elif display.intern_atom("_NET_WM_STATE_HIDDEN") in window_list[index].get_full_property(display.intern_atom("_NET_WM_STATE"), Xatom.ATOM).value:#Maximize if hidden
        sendEvent(window_list[index], [2, display.intern_atom("_NET_WM_STATE_HIDDEN")], display.intern_atom("_NET_WM_STATE"))
        window_list[index].map()#possibly not required
        window_list[index].configure(stack_mode=X.Above)
        display.flush()
        window_list[index].set_input_focus(X.RevertToNone, X.CurrentTime)
    else:#Bring to front
        window_list[index].configure(stack_mode=X.Above)
        window_list[index].set_input_focus(X.RevertToNone, X.CurrentTime)

def toggleMinimizeViaWorkspace(index):
    window_list = getWindowList()
    if getActiveWindow() == window_list[index]:                              #If window is active
        sendEvent(window_list[index], [9], display.intern_atom("_NET_WM_DESKTOP"))
    elif getWindowWorkspace(window_list[index]) == getActiveWorkspace():     #If window is on the current workspace...
        sendEventBSPWM(index, '-f')
        if str(getTiledFocusBSPWM(index))[2:-1] == str.upper(hex(root.get_full_property(display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW).value[index])[2:-1]):
            sendEvent(window_list[index], [9], display.intern_atom("_NET_WM_DESKTOP"))
    elif getWindowWorkspace(window_list[index]) == 9:                        #If window is on a different workspace
        sendEvent(window_list[index], [getActiveWorkspace()], display.intern_atom("_NET_WM_DESKTOP"))
        sendEventBSPWM(index, '-f')
    else:                                                                    #If window is active on another workspace
        setActiveWorkspace(getWindowWorkspace(window_list[index]))
        sendEventBSPWM(index, '-f')

def main():
    global display,root,app
    display = Display()
    root = display.screen().root
    root.change_attributes(event_mask = (X.PropertyChangeMask))
    taskbar = Taskbar()
    taskbar.updateTasks()
    taskbar.middleMapper.mapped[int].connect(taskbar.onTabMiddleClick)
    taskbar.rightMapper.mapped[int].connect(taskbar.onTabRightClick)
    taskbar.leftMapper.mapped[int].connect(taskbar.onTaskLeftClick)

    Popen(['feh', '--bg-scale', '/home/shaw/.python/Theta/background.png'])
    Popen(['mpd'])

    while 1:
        taskbar.clock.setText(time.strftime("%a "+"%b "+"%d, "+"%H"+":"+"%M"))

        QtGui.QApplication.processEvents()
        time.sleep(0.01)
        while display.pending_events():
            event = display.next_event()
            taskbar.updateTasks()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
