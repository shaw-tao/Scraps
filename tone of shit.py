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

with open('launch_items', 'r') as f:
    for line in f:
        launch_list.append(literal_eval(line.strip()))
    f.close()

#def setXlibPlacebo(display):
    #_WORKSPACE =            display.intern_atom("_NET_WM_DESKTOP")
    #_CURRENT_WORKSPACE =    display.intern_atom("_NET_CURRENT_DESKTOP")
    #_WORKSPACE_COUNT =      display.intern_atom("_NET_NUMBER_OF_DESKTOPS")
    #_ACTIVE_WINDOW =        display.intern_atom('_NET_ACTIVE_WINDOW')
    #_WINDOW_LIST =          display.intern_atom('_NET_CLIENT_LIST')
    #_HIDDEN =               display.intern_atom("_NET_WM_STATE_HIDDEN")
    #_STATE =                display.intern_atom("_NET_WM_STATE")
    #_CHANGE_STATE =         display.intern_atom('WM_CHANGE_STATE')

class MusicPlayer(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MusicPlayer, self).__init__(parent)
        self.initUI()

    def initUI(self):

#Fonts
        fontSmall = QtGui.QFont(); fontSmall.setPointSize(8)
        fontLarge = QtGui.QFont(); fontLarge.setPointSize(13)

#Music player
        self.setGeometry(QtGui.QDesktopWidget().screenGeometry().width() - 246, 30, 236,240)#120 height
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.Popup)

        self.clearMusic()
        self.none = self.getCurrent()
        self.current = self.getCurrent()
        musicTitles = []
        for x in self.getAllMusic():
            x = x.split('/')
            x = x[len(x)-1]
            musicTitles.append(x)
        self.addMusic(self.getAllMusic())
        self.playlistModel = QtGui.QStringListModel(self)
        self.playlistModel.setStringList(musicTitles)

        self.playerProgress = QtGui.QProgressBar(self)#QSlider(self)
        self.playerProgress.setGeometry(10,40, 216, 5)
        #self.playerProgress.setOrientation(QtCore.Qt.Horizontal)
        #self.playerProgress.setFocusPolicy(QtCore.Qt.NoFocus)

        self.playPause = QtGui.QPushButton(QtCore.QString.fromUtf8('⊳'), self)
        self.playPause.setGeometry(10,10, 20, 20)
        self.playPause.clicked.connect(self.mpcToggle)
        self.playPause.setFocusPolicy(QtCore.Qt.NoFocus)

        self.playPrev = QtGui.QPushButton(QtCore.QString.fromUtf8('≪'), self)
        self.playPrev.setGeometry(40,10, 20, 20)
        self.playPrev.clicked.connect(self.mpcPrev)
        self.playPrev.setFocusPolicy(QtCore.Qt.NoFocus)

        self.playNext = QtGui.QPushButton(QtCore.QString.fromUtf8('≫'), self)
        self.playNext.setGeometry(70,10, 20, 20)
        self.playNext.clicked.connect(self.mpcNext)
        self.playNext.setFocusPolicy(QtCore.Qt.NoFocus)

        self.toggleSingle = QtGui.QPushButton(QtCore.QString.fromUtf8('1'), self)
        self.toggleSingle.setGeometry(100,10, 20, 20)
        self.toggleSingle.clicked.connect(self.mpcSingle)
        self.toggleSingle.setFocusPolicy(QtCore.Qt.NoFocus)

        self.toggleRandom = QtGui.QPushButton(QtCore.QString.fromUtf8('r'), self)
        self.toggleRandom.setGeometry(130,10, 20, 20)
        self.toggleRandom.clicked.connect(self.mpcRandom)
        self.toggleRandom.setFocusPolicy(QtCore.Qt.NoFocus)

        self.playlist = QtGui.QListView(self)
        self.playlist.setGeometry(10,55, 216, 175)
        self.playlist.setModel(self.playlistModel)
        self.playlist.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.playlist.doubleClicked.connect(self.mpcSelect)
        self.playlist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.playlist.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.playlist.setFocusPolicy(QtCore.Qt.NoFocus)

    def mpcToggle(self):
        Popen(['mpc', 'toggle', '-q'])
        self.current = self.getCurrent()
        self.setSliderMaximum()

    def mpcPrev(self):
        Popen(['mpc', 'prev', '-q'])
        self.current = self.getCurrent()
        self.setSliderMaximum()

    def mpcNext(self):
        Popen(['mpc', 'next', '-q'])
        self.current = self.getCurrent()
        self.setSliderMaximum()

    def mpcSingle(self):
        Popen(['mpc', 'single', '-q'])

    def mpcRandom(self):
        Popen(['mpc', 'random', '-q'])

    def mpcUpdate(self):
        Popen(['mpc', 'update'])

    def mpcSelect(self):
        index = str(self.playlist.selectedIndexes()[0].row()+1)
        Popen(['mpc', 'play', index])
        self.current = self.getCurrent()
        self.setSliderMaximum()

    def getAllMusic(self):
        pipe = Popen(['mpc', 'listall'], stdout=PIPE)
        music = pipe.communicate()[0]
        return music.splitlines()

    def getCurrent(self):
        pipe = Popen(['mpc', 'current'], stdout=PIPE)
        mpcCurrent = pipe.communicate()[0]
        return str(mpcCurrent)

    def setSliderMaximum(self):
        pipe = Popen(['mpc', '-f', '%time%'], stdout=PIPE)
        time = pipe.communicate()[0]
        time = time.splitlines()[0].split(':')
        time = int(time[0])*60+int(time[1])
        self.playerProgress.setMaximum(time)

    def mpcGetProgress(self):
        pipe = Popen(['mpc'], stdout=PIPE)
        time = pipe.communicate()[0]
        time = time.split('/')[1].rsplit('   ')[1]
        time = time.splitlines()[0].split(':')
        time = int(time[0])*60+int(time[1])
        return time

    def addMusic(self, music):
        for x in music:
            Popen(['mpc', 'add', x])

    def clearMusic(self):
        Popen(['mpc', 'clear'])

###############################################################################

class Menu(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Menu, self).__init__(parent)
        self.initUI()

    def initUI(self):

#Fonts
        fontSmall = QtGui.QFont(); fontSmall.setPointSize(8)
        fontLarge = QtGui.QFont(); fontLarge.setPointSize(13)
#Style
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.X11BypassWindowManagerHint | QtCore.Qt.Popup); self.setGeometry(0, 20, 1366, (QtGui.QDesktopWidget().screenGeometry().height() - 20))
        self.background = QtGui.QLabel(self); self.background.setGeometry(0,-20,1366, (QtGui.QDesktopWidget().screenGeometry().height())); self.background.setPixmap((QtGui.QPixmap("/home/shaw/.python/Theta/background_blur.png")).scaled(self.background.size(), QtCore.Qt.IgnoreAspectRatio))
        self.launcherLayout = QtGui.QHBoxLayout(self); self.launcherScroll = QtGui.QScrollArea(self) ;self.launcherFrame = QtGui.QWidget(self)
        self.vLayout = QtGui.QVBoxLayout(self); self.hLayout = QtGui.QHBoxLayout(self); self.launcherGrid = QtGui.QGridLayout(self)
        self.notesWidget = QtGui.QWidget(self); self.notesWidget.setGeometry(10, 10, 320, 273)
        self.notesEntry = QtGui.QTextEdit(self); self.notesEntry.setGeometry(10, 10, 320, 273); self.notesEntry.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff); self.notesEntry.setParent(self.notesWidget); self.notesEntry.setFont(fontSmall)
        self.organizer = QtGui.QTabWidget(self); self.organizer.setGeometry(10, 445, 330, 293); self.organizer.setFont(fontSmall)
        self.powerTab = QtGui.QPushButton('||', self); self.powerTab.setGeometry(326, 445, 14, 21)
        self.calendar = QtGui.QLabel(self); self.calendar.setGeometry(1120,10,236,120); self.calendarGrid = QtGui.QGridLayout(self); self.calendar.setLayout(self.calendarGrid)
#Launcher
        global launch_list
        self.buttons = []
        for i in xrange(10):
            for j in xrange(3):
                #check for name, else generate index
                b=QtGui.QPushButton((str(i) + ' - ' + str(j))); b.setFont(fontLarge); b.setParent(self.launcherFrame); b.setFixedSize(100, 100); b.setFocusPolicy(QtCore.Qt.NoFocus)
                self.buttons.append(b)
                self.launcherGrid.addWidget(b, i, j)
                self.launcherGrid.setColumnMinimumWidth(j, 100)
            self.launcherGrid.setRowMinimumHeight(i, 100)
        self.launcherGrid.setSpacing(5)
        for i in launch_list: self.buttons[launch_list.index(i)].setText(i[0])

        #x = getWindowList()#test to see if this horse-shit is fixed.
        #Set to global method after class rearange
        self.mapper = QtCore.QSignalMapper()
        for item in self.buttons:
            self.mapper.setMapping(item, self.buttons.index(item))
            item.clicked.connect(self.mapper.map)
        self.mapper.mapped[int].connect(self.launch)

        self.hLayout.addStretch(1); self.hLayout.addLayout(self.launcherGrid); self.hLayout.addStretch(1); self.vLayout.addLayout(self.hLayout)
        self.launcherFrame.setLayout(self.vLayout); self.launcherFrame.setGeometry(0, 0, 330, 5 + 105 * self.launcherGrid.rowCount()); self.launcherFrame.setFixedSize(self.launcherFrame.width(), self.launcherFrame.height())
        self.launcherScroll.setWidget(self.launcherFrame); self.launcherScroll.setGeometry(10, 10, 330, 425); self.launcherScroll.setFixedSize(self.launcherScroll.width(), self.launcherScroll.height()); self.launcherScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

#Index
        self.indexWidget = QtGui.QWidget(self)
#Schedule
        self.scheduleWidget = QtGui.QWidget(self)
#Notes
        self.notes = open('Notes', 'r')
        self.notesEntry.setPlainText(self.notes.read())
        self.notes.close()
#Calculator
        self.calculatorWidget = QtGui.QWidget(self)
#Organizer
        self.organizer.addTab(self.indexWidget,'Index')
        self.organizer.addTab(self.scheduleWidget,'Schedule')
        self.organizer.addTab(self.notesWidget, 'Notes')
        self.organizer.addTab(self.calculatorWidget,'Calculator')
        self.organizer.setCurrentIndex(2)
        self.organizer.setStyleSheet("""
            QTabBar::tab:selected { color: #FFFFFF; background-color: #F50B30; width: 79}
            QTabBar::tab:!selected { color: #FFFFFF; background-color: #1A1111; width: 79}
                                    """)
#Power
        self.powerTab.clicked.connect(self.menuScreenshot)
#Calendar
        c = calendar.monthcalendar(int(time.strftime("%Y")), int(time.strftime("%m")))
        self.days = ['M','T','W','T','F','S','S']
        for i in xrange(7):
            b=QtGui.QLabel(self.days[i])
            b.setAlignment(QtCore.Qt.AlignCenter)
            self.calendarGrid.addWidget(b, 0, i)
        self.dates = []
        for i in range(1,len(c)+1):
            l=[]
            for j in xrange(7):
                if (c[i-1][j]) != 0:
                    b=QtGui.QPushButton(str(c[i-1][j]))
                    b.setParent(self.calendar)
                    b.setFont(fontSmall)
                    b.setFocusPolicy(QtCore.Qt.NoFocus)
                    if (c[i-1][j]) == int(time.strftime("%d")):
                        b.setStyleSheet("""QPushButton { background-color: #F50B30; color: #FFFFFF }""")
                    l.append(b)
                    self.calendarGrid.addWidget(b, i, j)
            self.dates.append(l)
        self.calendarGrid.setSpacing(1)

    def launch(self, index):
        global launch_list
        if index < len(launch_list):
            program = launch_list[index][1]
            Popen(program)
            self.hide()

    def menuScreenshot(self):
        QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId()).save('screenshot_menu.png', 'png')

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
    menu = Menu()
    musicPlayer = MusicPlayer()

    def __init__(self):
        super(Taskbar, self).__init__()
        self.initUI()

    def initUI(self):
#Fonts
        self.fontSmall = QtGui.QFont(); self.fontSmall.setPointSize(8)
#Style
        with open('css', 'r') as f:
            self.styleSheet = f.read()
            f.close()
        self.primeLayout = QtGui.QHBoxLayout(self) ; self.primeLayout.setSpacing(5) ; self.primeLayout.setMargin(0) ; self.primeLayout.setContentsMargins(0,0,0,0)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.X11BypassWindowManagerHint) ; self.setGeometry(0, 0, QtGui.QDesktopWidget().screenGeometry().width(), 20) ; self.setFixedSize(self.width(), self.height())
        self.menuButton = QtGui.QPushButton('Menu') ; self.menuButton.setFixedSize(60, 20) ; self.menuButton.setFont(self.fontSmall) ;
        self.showDesktop = QtGui.QPushButton('', self) ; self.showDesktop.setFixedSize(10, 20) ;
        self.taskLayout = QtGui.QHBoxLayout(self) ; self.taskLayout.setSpacing(0) ; self.taskLayout.setMargin(0) ; self.taskLayout.setContentsMargins(0,0,0,0) ;
        self.barContainer = QtGui.QWidget(self) ; self.barContainer.setFixedSize(100, 20)
        self.vol_bar = QtGui.QProgressBar(self) ; self.vol_bar.setParent(self.barContainer) ; self.vol_bar.setGeometry(0, 10, 100, 1)
        self.vol_control = QtGui.QScrollBar(QtCore.Qt.Horizontal, self) ; self.vol_control.setGeometry(-5, 0, 110, 20) ; self.vol_control.setParent(self.barContainer)
        #self.bat_bar = QtGui.QProgressBar(self) ; self.bat_bar.setParent(self.barContainer) ; self.bat_bar.setGeometry(0, 13, 100, 1)
        self.clock = QtGui.QLabel(self) ; self.clock.setFont(self.fontSmall)
        self.workspaceLayout = QtGui.QHBoxLayout(self) ; self.workspaceLayout.setSpacing(1) ; self.workspaceLayout.setMargin(0) ; self.workspaceLayout.setContentsMargins(0,0,0,0)

#Buttons
        self.menuButton.clicked.connect(self.toggleMenu)
        self.showDesktop.clicked.connect(takeScreenshot)
        self.showDesktop.setStyleSheet(""" QPushButton { background-color: #1A1111; border:none }
                                           QPushButton:pressed { background-color: #F50B30; }
                                       """)
#Tasklist
        self.tasks = []
        self.middleMapper = QtCore.QSignalMapper()
        self.rightMapper = QtCore.QSignalMapper()
        self.leftMapper = QtCore.QSignalMapper()
#Volume
        self.updateVolume()
        self.vol_control_value = self.vol_control.value()#so values can be compared for changes later
        self.vol_control.valueChanged.connect(self.changeVolume)
        self.vol_control.sliderPressed.connect(self.togglePlayer)
        self.vol_control.setStyleSheet("""  QScrollBar { background-color: transparent; color: transparent; border: none; margin: 0px 0px 0 0px }
                                            QScrollBar::handle:horizontal { border:none; min-width: 109px; }
                                            QScrollBar::add-line:horizontal { background-color: transparent; width: 0px; }
                                            QScrollBar::sub-line:horizontal { background-color: transparent; width: 0px; }
                                       """)
#Battery
        #self.bat_bar.setValue(100)#
#Worspaces
        self.workspaces = []
        for i in range(getWorkspaceCount()-1):
            b = QtGui.QPushButton(QtCore.QString.fromUtf8(getWorkspaceNames()[i])) ; b.setFixedSize(15,20) ; b.setFont(self.fontSmall)
            self.workspaces.append(b)
            self.workspaceLayout.addWidget(self.workspaces[i])
        self.mapper = mapSignals(self.workspaces, setActiveWorkspace)

#Out
        self.leftLayout = QtGui.QHBoxLayout(self)
        self.leftLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.leftLayout.addWidget(self.menuButton)
        self.leftLayout.addLayout(self.workspaceLayout)

        self.middleLayout = QtGui.QHBoxLayout(self)
        self.middleLayout.setAlignment(QtCore.Qt.AlignHCenter)
        self.middleLayout.addLayout(self.taskLayout)

        self.rightLayout = QtGui.QHBoxLayout(self)
        self.rightLayout.setAlignment(QtCore.Qt.AlignRight)
        self.rightLayout.addWidget(self.barContainer)
        self.spacer = QtGui.QLabel()
        self.spacer.setFixedSize(8, 20)
        self.rightLayout.addWidget(self.spacer)
        self.rightLayout.addWidget(self.clock)
        self.rightLayout.addWidget(self.showDesktop)

        self.primeLayout.addLayout(self.leftLayout)
        self.primeLayout.addLayout(self.middleLayout)
        self.primeLayout.addLayout(self.rightLayout)
        #self.setLayout(self.primeLayout)

        self.setStyleSheet(self.styleSheet)
        self.menu.setStyleSheet(self.styleSheet)
        self.musicPlayer.setStyleSheet(self.styleSheet)
        self.show()

    def updateVolume(self):
        mixer = alsaaudio.Mixer()
        vol = mixer.getvolume()
        self.vol_bar.setValue(vol[0])

    def changeVolume(self):
        if self.vol_control_value < self.vol_control.value() or (self.vol_control_value & self.vol_control.value()) == 99:
            Popen(['amixer', '-c', '0', 'set', 'Master', '2-'])
        elif self.vol_control_value > self.vol_control.value() or (self.vol_control_value & self.vol_control.value()) == 0:
            Popen(['amixer', '-c', '0', 'set', 'Master', '2+', 'unmute'])
        self.vol_control_value = self.vol_control.value()
        self.updateVolume()

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

    def toggleMenu(self):
        self.notes = open('Notes', 'w')
        self.notes.write(self.menu.notesEntry.toPlainText())
        self.notes.close()
        self.menu.show()
        self.updateTasks()#may be redundant

    def togglePlayer(self):
        print 'PLAYER SHOW'
        self.musicPlayer.show()

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
    if getActiveWindow() == window_list[index]:
        sendEvent(window_list[index], [2, display.intern_atom("_NET_WM_STATE_HIDDEN")], display.intern_atom("_NET_WM_STATE"))
        sendEvent(window_list[index], [Xutil.IconicState], display.intern_atom('WM_CHANGE_STATE'))
    elif display.intern_atom("_NET_WM_STATE_HIDDEN") in window_list[index].get_full_property(display.intern_atom("_NET_WM_STATE"), Xatom.ATOM).value:
        sendEvent(window_list[index], [2, display.intern_atom("_NET_WM_STATE_HIDDEN")], display.intern_atom("_NET_WM_STATE"))
        window_list[index].map()#possibly not required
        window_list[index].configure(stack_mode=X.Above)
        display.flush()
        window_list[index].set_input_focus(X.RevertToNone, X.CurrentTime)
    else:
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
        #if taskbar.musicPlayer.current != taskbar.musicPlayer.none:
            #taskbar.musicPlayer.playerProgress.setValue(taskbar.musicPlayer.mpcGetProgress())
            #if taskbar.musicPlayer.current != taskbar.musicPlayer.getCurrent():
                #taskbar.musicPlayer.current = taskbar.musicPlayer.getCurrent()
                #taskbar.musicPlayer.setSliderMaximum()
                #print 'changed song'

        QtGui.QApplication.processEvents()
        time.sleep(0.01)
        while display.pending_events():
            event = display.next_event()
            taskbar.updateTasks()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
