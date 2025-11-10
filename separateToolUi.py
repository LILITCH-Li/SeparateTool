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
from . import separateToolUtil
importlib.reload(version)
importlib.reload(separateToolUtil)
import os

class SeparateDialog(QtWidgets.QDialog):
	def get_icon_path(self, icon_name):
		current_dir = os.path.dirname(os.path.abspath(__file__))
		icon_folder = os.path.join(current_dir, 'images')
		final_path = os.path.join(icon_folder, icon_name).replace('\\', '/')
		print(f"Trying to load icon from: {final_path}")
		return final_path


	def __init__(self, parent=None):
		super().__init__(parent)

		self.resize(300, 500)
		self.setWindowTitle(f'Separate Tool {version.__version__}')

		self.mainLayout = QtWidgets.QVBoxLayout()
		self.setLayout(self.mainLayout)
		self.setStyleSheet(
			'''
				font-family: Terminal;
			'''
		)
		self.selectLabel = QtWidgets.QLabel('Selected Items:')
		self.selectionList = QtWidgets.QListWidget()
		self.selectionList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.mainLayout.addWidget(self.selectLabel)
		self.mainLayout.addWidget(self.selectionList)

		self.callback_id = None

		self.processGroup = QtWidgets.QGroupBox("Processing Options")
		self.processLayout = QtWidgets.QVBoxLayout()

		self.prefixLabel = QtWidgets.QLabel('Name Prefix')
		self.prefixLineEdit = QtWidgets.QLineEdit('processed_Obj')
		self.deleteHis_cb = QtWidgets.QCheckBox('Delete History')
		self.deleteHis_cb.setChecked(True)		

		self.centerPv_cb = QtWidgets.QCheckBox('Center Pivot')
		self.centerPv_cb.setChecked(True)

		self.processLayout.addWidget(self.prefixLabel)
		self.processLayout.addWidget(self.prefixLineEdit)
		self.processLayout.addWidget(self.deleteHis_cb)		

		self.processLayout.addWidget(self.centerPv_cb)

		self.buttonLayout = QtWidgets.QHBoxLayout()

		self.separateButton = QtWidgets.QPushButton('')
		self.combineButton = QtWidgets.QPushButton('')
		self.button_size = QtCore.QSize(140, 140)
		self.separateButton.setFixedSize(self.button_size)
		self.combineButton.setFixedSize(self.button_size)

		sep_normal_icon = self.get_icon_path('slime1-1v1.png')
		sep_hover_icon = self.get_icon_path('slime1-2v2.png')
		button_bg = self.get_icon_path('slime1bg.png')
		pressed = self.get_icon_path('clicked2.png')

		self.separateButton.setStyleSheet(f'''
			QPushButton {{
				image: url({sep_normal_icon});
				image-position: center;
				border-radius: 12px;
				background-image: url({button_bg});
				background-position: center;
			}}
			QPushButton:hover {{
				image: url({sep_hover_icon});
				border: 3px solid yellow;
			}}
			QPushButton:pressed{{
				image: url({pressed});
			}}
		''')

		com_normal_icon = self.get_icon_path('slime2v1.png')
		com_hover_icon = self.get_icon_path('slime2-1v1.png')

		self.combineButton.setStyleSheet(f'''
			QPushButton {{
				image: url({com_normal_icon});
				image-position: center;
				border-radius: 12px;
				background-image: url({button_bg});
				background-position: center;
			}}
			QPushButton:hover {{
				image: url({com_hover_icon});
				border: 3px solid yellow;
			}}
			QPushButton:pressed{{
				image: url({pressed});
			}}
		''')
		
		self.buttonLayout.addWidget(self.separateButton)
		self.buttonLayout.addWidget(self.combineButton)

		self.processLayout.addLayout(self.buttonLayout)
		self.processGroup.setLayout(self.processLayout)
		self.mainLayout.addWidget(self.processGroup)

		self.update_ui_from_selection()
		self.create_callback()
		self.onClick()

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

	def onClick(self):
		self.separateButton.clicked.connect(self.on_separate_clicked)
		self.combineButton.clicked.connect(self.on_combine_clicked)

	def on_separate_clicked(self):
		selection = cmds.ls(selection=True, long=True, type='transform')
		prefix = self.prefixLineEdit.text()
		delete_history = self.deleteHis_cb.isChecked()
		center_pivot = self.centerPv_cb.isChecked()

		processed_objects, count = separateToolUtil.separate_logic(
			selection, prefix, delete_history, center_pivot
		)

		if processed_objects:
			QtWidgets.QMessageBox.information(self, "Success", f"Separation complete. Processed {count} object(s).")
		else:
			QtWidgets.QMessageBox.warning(self, "Separation Failed", "No valid objects were processed. Check script editor for details.")

	def on_combine_clicked(self):
		selection = cmds.ls(selection=True, long=True)
		prefix = self.prefixLineEdit.text()
		delete_history = self.deleteHis_cb.isChecked()
		center_pivot = self.centerPv_cb.isChecked()

		final_name = separateToolUtil.combine_logic(
			selection, prefix, delete_history, center_pivot
		)

		if final_name:
			QtWidgets.QMessageBox.information(self, "Success", f"Successfully combined objects into '{final_name}'!")
		else:
			QtWidgets.QMessageBox.warning(self, "Combine Failed", "Could not combine objects. Please select at least two valid meshes.")

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