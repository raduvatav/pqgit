# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pqgit.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(974, 781)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_9 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.hist_splitter = QSplitter(self.centralwidget)
        self.hist_splitter.setObjectName(u"hist_splitter")
        self.hist_splitter.setOrientation(Qt.Vertical)
        self.diff_splitter = QSplitter(self.hist_splitter)
        self.diff_splitter.setObjectName(u"diff_splitter")
        self.diff_splitter.setOrientation(Qt.Horizontal)
        self.branches_groupbox = QGroupBox(self.diff_splitter)
        self.branches_groupbox.setObjectName(u"branches_groupbox")
        self.verticalLayout_8 = QVBoxLayout(self.branches_groupbox)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.tvBranches = QTableView(self.branches_groupbox)
        self.tvBranches.setObjectName(u"tvBranches")

        self.verticalLayout_8.addWidget(self.tvBranches)

        self.diff_splitter.addWidget(self.branches_groupbox)
        self.history_groupbox = QGroupBox(self.diff_splitter)
        self.history_groupbox.setObjectName(u"history_groupbox")
        self.verticalLayout = QVBoxLayout(self.history_groupbox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tvHistory = QTableView(self.history_groupbox)
        self.tvHistory.setObjectName(u"tvHistory")

        self.verticalLayout.addWidget(self.tvHistory)

        self.diff_splitter.addWidget(self.history_groupbox)
        self.cinf_splitter = QSplitter(self.diff_splitter)
        self.cinf_splitter.setObjectName(u"cinf_splitter")
        self.cinf_splitter.setOrientation(Qt.Vertical)
        self.files_groupbox = QGroupBox(self.cinf_splitter)
        self.files_groupbox.setObjectName(u"files_groupbox")
        self.verticalLayout_2 = QVBoxLayout(self.files_groupbox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tvFiles = QTableView(self.files_groupbox)
        self.tvFiles.setObjectName(u"tvFiles")

        self.verticalLayout_2.addWidget(self.tvFiles)

        self.cinf_splitter.addWidget(self.files_groupbox)
        self.commit_groupbox = QGroupBox(self.cinf_splitter)
        self.commit_groupbox.setObjectName(u"commit_groupbox")
        self.verticalLayout_3 = QVBoxLayout(self.commit_groupbox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.teCommit = QTextEdit(self.commit_groupbox)
        self.teCommit.setObjectName(u"teCommit")
        self.teCommit.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.teCommit)

        self.cinf_splitter.addWidget(self.commit_groupbox)
        self.diff_splitter.addWidget(self.cinf_splitter)
        self.hist_splitter.addWidget(self.diff_splitter)
        self.diff_groupbox = QGroupBox(self.hist_splitter)
        self.diff_groupbox.setObjectName(u"diff_groupbox")
        self.verticalLayout_4 = QVBoxLayout(self.diff_groupbox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.teDiff = QTextEdit(self.diff_groupbox)
        self.teDiff.setObjectName(u"teDiff")
        self.teDiff.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.teDiff)

        self.hist_splitter.addWidget(self.diff_groupbox)

        self.verticalLayout_9.addWidget(self.hist_splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 974, 30))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.branches_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"Branches", None))
        self.history_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"History", None))
        self.files_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"Files", None))
        self.commit_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"Commit", None))
        self.diff_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"Diff", None))
    # retranslateUi

