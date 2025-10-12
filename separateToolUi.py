try:
	from PySide6 import QtCore, QtWidgets, QtGui
	from shiboken6 import wrapInstance
except:
	from PySide2 import QtCore, QtWidgets, QtGui
	from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import importlib
from . import version
import maya.cmds as cmds
importlib.reload(version)



class SeparateDialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.resize(300, 300)
		self.setWindowTitle(f'Separate Tool {version.__version__}')

		self.mainLayout = QtWidgets.QVBoxLayout()
		self.setLayout(self.mainLayout)
		self.setStyleSheet(
			'''
				font-family: Courier;
				background-color: pink;
			'''
		)

		self.selectionLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(self.selectionLayout)

		self.selectLabel = QtWidgets.QLabel('Select')
		self.selectedName = QtWidgets.QLabel('None')

		self.selectionLayout.addWidget(self.selectLabel)
		self.selectionLayout.addWidget(self.selectedName)

		self.buttonLayout = QtWidgets.QVBoxLayout()
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

		self.optionsLayout = QtWidgets.QVBoxLayout()
		self.mainLayout.addLayout(self.optionsLayout)

		self.centerPivot_cb = QtWidgets.QCheckBox('Center Pivot')
		self.centerPivot_cb.setChecked(True)

		self.freeze_transform_cb = QtWidgets.QCheckBox('Freeze Transformations')
		self.freeze_transform_cb.setChecked(True)

		self.delete_history_cb = QtWidgets.QCheckBox('Delete History')
		self.delete_history_cb.setChecked(True)

		self.optionsLayout.addWidget(self.centerPivot_cb)
		self.optionsLayout.addWidget(self.freeze_transform_cb)
		self.optionsLayout.addWidget(self.delete_history_cb)

		self.mainLayout = QtWidgets.QVBoxLayout()
		self.mainLayout.addLayout(self.selectionLayout)

		self.setLayout(self.mainLayout)

		self.update_selection()

		self.mainLayout.addStretch()

	def update_selection(self):
		selected = cmds.ls(selection=True)
		if selected:
			objectSel = self.selectedName.setText(selected[0])
		else:
			self.selectedName.setText('None')


def run():
	global ui
	try:
		ui.close()
	except:
		pass

	mayaMainWindow = omui.MQtUtil.mainWindow()
	ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
	ui = SeparateDialog(parent=ptr)
	ui.show()