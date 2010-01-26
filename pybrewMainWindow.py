# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pybrewMainWindow.ui'
#
# Created: Tue Jan 26 11:35:26 2010
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(553, 495)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.targetTempLineEdit = QtGui.QLineEdit(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.targetTempLineEdit.sizePolicy().hasHeightForWidth())
        self.targetTempLineEdit.setSizePolicy(sizePolicy)
        self.targetTempLineEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.targetTempLineEdit.setMaximumSize(QtCore.QSize(131, 28))
        self.targetTempLineEdit.setObjectName("targetTempLineEdit")
        self.horizontalLayout_2.addWidget(self.targetTempLineEdit)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tempQwtPlot = Qwt5.QwtPlot(self.centralwidget)
        self.tempQwtPlot.setObjectName("tempQwtPlot")
        self.horizontalLayout.addWidget(self.tempQwtPlot)
        self.Thermo = Qwt5.QwtThermo(self.centralwidget)
        self.Thermo.setAlarmEnabled(True)
        self.Thermo.setAlarmLevel(45.0)
        self.Thermo.setScalePosition(Qwt5.QwtThermo.RightScale)
        self.Thermo.setFillColor(QtGui.QColor(170, 0, 0))
        self.Thermo.setMaxValue(100.0)
        self.Thermo.setMinValue(0.0)
        self.Thermo.setProperty("value", QtCore.QVariant(23.0))
        self.Thermo.setObjectName("Thermo")
        self.horizontalLayout.addWidget(self.Thermo)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.valveButtonLayout = QtGui.QHBoxLayout()
        self.valveButtonLayout.setObjectName("valveButtonLayout")
        self.verticalLayout.addLayout(self.valveButtonLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 553, 24))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionSet_temp = QtGui.QAction(MainWindow)
        self.actionSet_temp.setObjectName("actionSet_temp")
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.toolBar.addAction(self.actionSet_temp)
        self.label.setBuddy(self.targetTempLineEdit)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.toolBar, QtCore.SIGNAL("actionTriggered(QAction*)"), MainWindow.setTargetTempEvent)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "pyBrew", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Target temp", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "°C", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSet_temp.setText(QtGui.QApplication.translate("MainWindow", "Set temp", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSet_temp.setToolTip(QtGui.QApplication.translate("MainWindow", "Set temperature", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import Qwt5

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)

        self.setupUi(self)

