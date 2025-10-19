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

		self.resize(300, 500)
		self.setWindowTitle(f'Separate Tool {version.__version__}')

		self.mainLayout = QtWidgets.QVBoxLayout()
		self.setLayout(self.mainLayout)
		self.setStyleSheet(
			'''
				font-family: Courier;
				background-color: navy;
			'''
		)

		self.selectLabel = QtWidgets.QLabel('Selected Items:')
		self.mainLayout.addWidget(self.selectLabel)

		self.selectionList = QtWidgets.QListWidget()
		self.selectionList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.mainLayout.addWidget(self.selectionList)

		self.callback_id = None

		self.separateGroup = QtWidgets.QGroupBox('Separate Option')
		self.separateLayout = QtWidgets.QVBoxLayout()

		self.prefixLabel = QtWidgets.QLabel('Prefix')
		self.prefixLineEdit = QtWidgets.QLineEdit('Separated_obj')
		self.sep_delHis_cb = QtWidgets.QCheckBox('Delete History')
		self.sep_delHis_cb.setChecked(True)
		self.sep_freeze_cb = QtWidgets.QCheckBox('Freeze Transfrom')
		self.sep_freeze_cb.setChecked(True)
		self.sep_center_cb = QtWidgets.QCheckBox('Center Pivot')
		self.sep_center_cb.setChecked(True)
		self.separateButton = QtWidgets.QPushButton('Separate')

		self.separateLayout.addWidget(self.prefixLabel)
		self.separateLayout.addWidget(self.prefixLineEdit)
		self.separateLayout.addWidget(self.sep_delHis_cb)
		self.separateLayout.addWidget(self.sep_freeze_cb)
		self.separateLayout.addWidget(self.sep_center_cb)
		self.separateLayout.addWidget(self.separateButton)
		self.separateGroup.setLayout(self.separateLayout)
		self.mainLayout.addWidget(self.separateGroup)

		self.combineGroup = QtWidgets.QGroupBox('Combine Option')
		self.combineLayout = QtWidgets.QVBoxLayout()
		
		self.renameLabel = QtWidgets.QLabel('Set Name')
		self.renameLineEdit = QtWidgets.QLineEdit('Combined_obj')
		self.com_del_cb = QtWidgets.QCheckBox('Delete History')
		self.com_del_cb.setChecked(True)
		self.com_freeze_cb = QtWidgets.QCheckBox('Freeze Transfrom')
		self.com_freeze_cb.setChecked(True)
		self.com_center_cb = QtWidgets.QCheckBox('Center Pivot')
		self.com_center_cb.setChecked(True)
		self.combineButton = QtWidgets.QPushButton('Combine')

		self.combineLayout.addWidget(self.renameLabel)
		self.combineLayout.addWidget(self.renameLineEdit)
		self.combineLayout.addWidget(self.com_del_cb)
		self.combineLayout.addWidget(self.com_freeze_cb)
		self.combineLayout.addWidget(self.com_center_cb)
		self.combineLayout.addWidget(self.combineButton)
		self.combineGroup.setLayout(self.combineLayout)
		self.mainLayout.addWidget(self.combineGroup)

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
		super(SeparateDialog, self).closeEvent(event)

	def connect_signals(self):
		self.separateButton.clicked.connect(self.separate_logic)
		self.combineButton.clicked.connect(self.combine_logic)

	def separate_logic(self):
		selection = cmds.ls(selection=True, long=True, type='transform')

		if not selection:
			cmds.warning("Please select a mesh object to separate.")
			return

		target_object = selection[0]
		shape_nodes = cmds.listRelatives(target_object, shapes=True, type='mesh', fullPath=True)

		if not shape_nodes:
			cmds.warning(f"'{target_object}' is not a valid mesh object. Please select an object with mesh geometry.")
			return

		try:
			separated_objects = cmds.polySeparate(target_object, constructionHistory=False)
			if not separated_objects:
				cmds.warning("Separation failed. The object might already be a single shell.")
				cmds.select(target_object)
				return
		except Exception as e:
			cmds.error(f"An error occurred during separation: {e}")
			return

		print(f"Successfully separated '{target_object}' into {len(separated_objects)} objects.")

		prefix = self.prefixLineEdit.text()
		fsep_obj = []

		for i, obj in enumerate(separated_objects):
			newName = cmds.rename(obj, f"{prefix}_{i+1:03}")

			if self.sep_delHis_cb.isChecked():
				cmds.delete(newName, constructionHistory=True)

			if self.sep_center_cb.isChecked():
				cmds.xform(newName, centerPivots=True)

			if self.sep_freeze_cb.isChecked():
				cmds.makeIdentity(newName, apply=True, translate=1, rotate=1, scale=1, normal=0)

			fsep_obj.append(newName)
		QtWidgets.QMessageBox.information(self, "Success", f"Separated into {len(separated_objects)} objects!")

	def combine_logic(self):
		selection = cmds.ls(selection=True, long=True)

		if len(selection) <2:
			cmds.warning("Please select at least two mesh objects to combine.")
		
		valid_meshes = []
		
		for obj in selection:
			if cmds.listRelatives(obj, shapes=True, type='mesh', fullPath=True):
				valid_meshes.append(obj)
			else:
				cmds.warning(f"Skipping '{obj}' as it is not a valid mesh.")

		if len(valid_meshes) < 2:
			cmds.warning("Not enough valid mesh objects selected to perform a combine.")
			return

		try:
			combined_result = cmds.polyUnite(valid_meshes, constructionHistory=True)
			new_object = combined_result[0]
		except Exception as e:
			cmds.error(f"An error occurred during combination: {e}")
			return

		print(f"Successfully combined {len(valid_meshes)} objects into '{new_object}'.")
		self._post_process([new_object])

		rename = self.renameLineEdit.text()
		final_name = cmds.rename(new_object, rename)

		if self.com_del_cb.isChecked():
			cmds.delete(final_name, constructionHistory=True)

		if self.com_center_cb.isChecked():
			cmds.xform(final_name, centerPivots=True)

		if self.com_center_cb.isChecked():
			cmds.makeIdentity(final_name, apply=True, translate=1, rotate=1, scale=1, normal=0)

		QtWidgets.QMessageBox.information(self, "Success", f"Successfully combined objects into '{new_object}'!")

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