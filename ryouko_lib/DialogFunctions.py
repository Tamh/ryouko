#! /usr/bin/env/python

import os, sys
from PyQt4 import QtCore, QtGui
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)
from Python23Compat import *
from QStringFunctions import *
from TranslationManager import *

def centerWidget(widget):
    fg = widget.frameGeometry()
    cp = QtGui.QDesktopWidget().availableGeometry().center()
    fg.moveCenter(cp)
    widget.move(fg.topLeft())

def message(title="Alert", content="This is a message.", icon="info"):
    message = QtGui.QMessageBox()
    message.setWindowTitle(title)
    message.setText(qstring(str(content)))
    message.addButton(QtGui.QMessageBox.Ok)
    if str(icon).lower() == "info" or str(icon).lower() == "information":
        message.setIcon(QtGui.QMessageBox.Information)
    elif str(icon).lower() == "warn" or str(icon).lower() == "warning":
        message.setIcon(QtGui.QMessageBox.Warning)
    elif str(icon).lower() == "critical":
        message.setIcon(QtGui.QMessageBox.Question)
    elif str(icon).lower() == "query" or str(icon).lower() == "question":
        message.setIcon(QtGui.QMessageBox.Question)
    elif str(icon).lower() == "query" or str(icon).lower() == "question":
        message.setIcon(QtGui.QMessageBox.Question)
    elif str(icon).lower() == "none" or str(icon).lower() == "noicon":
        message.setIcon(QtGui.QMessageBox.NoIcon)
    else:
        message.setIcon(QtGui.QMessageBox.Information)
    message.exec_()

def saveDialog(fname="", filters = "All files (*)"):
    saveDialog = QtGui.QFileDialog.getSaveFileName(None, tr("saveAsDialog"), os.path.join(os.getcwd(), fname), filters)
    return saveDialog

def inputDialog(title="Query", content="Enter a value here", value=""):
    text = QtGui.QInputDialog.getText(None, title, content, QtGui.QLineEdit.Normal, value)
    if text[1]:
        if unicode(text[0]) != "":
            return text[0]
        else:
            return ""
    else:
        return ""

