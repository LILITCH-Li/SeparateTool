from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import importlib
from . import version, config

importlib.reload(version)



class SeparateDialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.resize(300, 300)
		self.setWindowTitle(f'Separate Tool {version.__version__}')

		self.mainLayout = QtWidgets.QVBoxLayout()
		self.setLayout(self.mainLayout)

		self.inputInfoLayout = QtWidgets.QGridLayout()
		self.mainLayout.addLayout(self.inputInfoLayout)


		self.buttonLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(self.buttonLayout)


		self.separateButton = QtWidgets.QPushButton('Separate')
		self.combineButton = QtWidgets.QPushButton('Combine')
		self.sepAndCombButton = QtWidgets.QPushButton('Separate&Combine')
		self.cancelButton = QtWidgets.QPushButton('Cancel')
		self.cancelButton.clicked.connect(self.close)

		self.buttonLayout.addWidget(self.separateButton)
		self.buttonLayout.addWidget(self.combineButton)
		self.buttonLayout.addWidget(self.sepAndCombButton)
		self.buttonLayout.addWidget(self.cancelButton)

def run():
	global ui
	try:
		ui.close()
	except:
		pass

	mayaMainWindow = omui.MQtUtil.mainWindow()
	ptr = wrapInstance(int(mayaMainWindow), QtWidgets.QWidget)
	ui = SeparateDialog(parent=ptr)
	ui.show()