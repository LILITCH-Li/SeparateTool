try:
	from PySide6 import QtCore, QtWidgets, QtGui
	from shiboken6 import wrapInstance
except:
	from PySide2 import QtCore, QtWidgets, QtGui
	from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from maya import OpenMaya as om
import maya.cmds as cmds
import importlib
from . import version
importlib.reload(version)

class SeparateDialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.resize(300, 350)
		self.setWindowTitle(f'Separate Tool {version.__version__}')

		self.mainLayout = QtWidgets.QVBoxLayout()
		self.setLayout(self.mainLayout)
		self.setStyleSheet(
			'''
				font-family: Courier;
				background-color: pink;
			'''
		)

		self.selectLabel = QtWidgets.QLabel('Selected Items:')
		self.mainLayout.addWidget(self.selectLabel)

		self.selectionList = QtWidgets.QListWidget()
		self.selectionList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.mainLayout.addWidget(self.selectionList)

		self.callback_id = None

		self.renameLayout = QtWidgets.QVBoxLayout()
		self.mainLayout.addLayout(self.renameLayout)

		self.prefixLabel = QtWidgets.QLabel('Prefix')
		self.prefixLineEdit = QtWidgets.QLineEdit('Separated_obj')
		self.suffixLabel = QtWidgets.QLabel('Suffix will be number of objects there separated')

		self.mainLayout.addWidget(self.prefixLabel)
		self.mainLayout.addWidget(self.prefixLineEdit)
		self.mainLayout.addWidget(self.suffixLabel)

		self.buttonLayout = QtWidgets.QVBoxLayout()
		self.mainLayout.addLayout(self.buttonLayout)

		self.separateButton = QtWidgets.QPushButton('Separate')
		self.combineButton = QtWidgets.QPushButton('Combine')
		self.sepAndCombButton = QtWidgets.QPushButton('Separate&Combine')

		self.buttonLayout.addWidget(self.separateButton)
		self.buttonLayout.addWidget(self.combineButton)
		self.buttonLayout.addWidget(self.sepAndCombButton)

		self.checkboxGroup = QtWidgets.QGroupBox('Options')
		self.checkboxLayout = QtWidgets.QVBoxLayout()
		'''self.mainLayout.addLayout(self.checkboxLayout)'''

		self.deleteHis_cb = QtWidgets.QCheckBox('Delete History')
		self.freezeTran_cb = QtWidgets.QCheckBox('Freeze Transfrom')
		self.centerPv_cb = QtWidgets.QCheckBox('Center Pivot')

		self.checkboxLayout.addWidget(self.deleteHis_cb)
		self.checkboxLayout.addWidget(self.freezeTran_cb)
		self.checkboxLayout.addWidget(self.centerPv_cb)
		self.checkboxGroup.setLayout(self.checkboxLayout)

		self.mainLayout.addWidget(self.checkboxGroup)

		self.update_ui_from_selection()
		self.create_callback()
		self.connect_signals()

	def create_callback(self):
		if self.callback_id is None:
			self.callback_id = om.MEventMessage.addEventCallback(
				"SelectionChanged", self.update_ui_from_selection
			)
			print(f"Callback created with ID: {self.callback_id}")

	def remove_callback(self):
		if self.callback_id is not None:
			try:
				om.MMessage.removeCallback(self.callback_id)
				print(f"Callback ID: {self.callback_id} removed.")
				self.callback_id = None
			except Exception as e:
				print(f"Error removing callback: {e}")

	def update_ui_from_selection(self, *args):

		self.selectionList.blockSignals(True)

		self.selectionList.clear()

		selected_objects = cmds.ls(selection=True)

		if selected_objects:
		    self.selectionList.addItems(selected_objects)
		    
		self.selectionList.blockSignals(False)

	def closeEvent(self, event):
		print("Closing UI, removing callback...")
		self.remove_callback()
		super(SelectionDisplayUI, self).closeEvent(event)

	def connect_signals(self):
		self.separateButton.clicked.connect(self.separate_logic)

	def separate_logic(self):

		selection = cmds.ls(selection=True, long=True)

		if not selection:
			cmds.warning("Please select a mesh object to separate.")
			return

		target_object = selection[0]

		shape_nodes = cmds.listRelatives(target_object, shapes=True, type='mesh', fullPath=True)
		if not shape_nodes:
			cmds.warning(f"'{target_object}' is not a valid mesh object. Please select an object with mesh geometry.")
			return

		try:
			separated_objects = cmds.polySeparate(target_object)
			if not separated_objects:
				cmds.warning("Separation failed. The object might already be a single shell.")
				return
		except Exception as e:
			cmds.error(f"An error occurred during separation: {e}")
			return
		    
		print(f"Successfully separated '{target_object}' into {len(separated_objects)} objects.")

		if separated_objects:
			for new_obj in separated_objects:
				if self.deleteHis_cb.isChecked():
					cmds.delete(new_obj, constructionHistory=True)
					print(f"Deleted history on '{new_obj}'")

				if self.centerPv_cb.isChecked():
					cmds.xform(new_obj, centerPivots=True)
					print(f"Centered pivot on '{new_obj}'")

				if self.centerPv_cb.isChecked():
					cmds.makeIdentity(new_obj, apply=True, translate=1, rotate=1, scale=1, normal=0)
					print(f"Froze transformations on '{new_obj}'")

		QtWidgets.QMessageBox.information(self, "Success", f"Separated into {len(separated_objects)} objects!")

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