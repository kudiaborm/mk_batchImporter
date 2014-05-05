
import pymel.core as pm
import maya.mel as mel

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

import os
import xml

import maya.OpenMayaUI as mui
import shiboken

import math


def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	if ptr is not None:
		return shiboken.wrapInstance(long(ptr), QtGui.QWidget)
WORK_PATH = pm.workspace.path

def listdir_fullpath(d):
	return [os.path.join(d, f) for f in os.listdir(d)]

def getRoundedMask(width, height):
	path = QtGui.QPainterPath()
	rect = QtCore.QRect(0, 0, width, height)
	path.addRoundedRect(rect, 10.0, 10.0, QtCore.Qt.AbsoluteSize)
	region = QtGui.QRegion(path.toFillPolygon().toPolygon())

	return region


class Window(QtGui.QMainWindow):

	def __init__(self, parent = getMayaWindow()):
		super(Window, self).__init__(parent, QtCore.Qt.Tool)

		blueGradientStyleSheet = "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(127, 197, 255, 255), stop:1\
		rgba(40, 81, 122, 255)); border: rgba(0,0,0,0);"


		# window setup
		self.width = 500
		self.height = 720
		self.setWindowTitle("Batch Image Importer")
		self.setObjectName("imageImporter")
		self.setFixedSize(self.width, self.height)

		self.main_widget = QtGui.QFrame(self)
		self.main_widget.setObjectName("mainWidget")
		self.main_widget.setGeometry(0, 20, self.width, self.height - 20)
		self.main_widget.setStyleSheet("QFrame#mainWidget {border: 5px solid black;\
												border: 2px groove rgba(68, 68, 68, 255);\
												border-radius: 2px;}")
		self.main_widget.setFrameShadow(QtGui.QFrame.Sunken)
		self._createMenuBar()


		# Create Splitter
		self.topSplitter = QtGui.QSplitter(self.main_widget)
		self.topSplitter.setGeometry(4, 4, self.width-5, 395)
		self.topSplitter.setObjectName("topSplitter")
		self.topSplitter.setStyleSheet("QSplitter#topSplitter {background-color: rgb(68, 68, 68)}")


		self.topSplitterLeft = QtGui.QWidget(self.topSplitter)
		self.topSplitterLeftLayout = QtGui.QHBoxLayout(self.topSplitterLeft)
		self.topSplitterLeft.setLayout(self.topSplitterLeftLayout)

		self.topSplitterRight = QtGui.QWidget(self.topSplitter)
		self.topSplitterRightLayout = QtGui.QHBoxLayout(self.topSplitterRight)
		self.topSplitterRight.setLayout(self.topSplitterRightLayout)

		# Create file browser
		self.fileBrowserTreeView = QtGui.QTreeView(self.topSplitterLeft)
		self.topSplitterLeftLayout.addWidget(self.fileBrowserTreeView)
		self.fileBrowserTreeView.setGeometry(0, 5, 200, 390)
		self.fileBrowserModel = QtGui.QFileSystemModel(self.fileBrowserTreeView)
		self.fileBrowserModel.setReadOnly(False)

		self.fileBrowserTreeView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.fileBrowserTreeView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
		self.fileBrowserTreeView.setModel(self.fileBrowserModel)

		self.rootPath = self.fileBrowserModel.setRootPath(WORK_PATH)

		self.fileBrowserTreeView.setRootIndex(self.rootPath)

		# Create Image Preview Scroll area

		self.imagePreviewScrollArea = QtGui.QScrollArea(self.topSplitterRight)
		self.imagePreviewScrollArea.setGeometry(0, 5, 270, 340)
		self.topSplitterRightLayout.addWidget(self.imagePreviewScrollArea)

		self.imagePreviewScrollAreaContents = QtGui.QWidget(self.imagePreviewScrollArea)
		self.imagePreviewScrollAreaContents.setGeometry(0,0, 240, 340)
		self.imagePreviewScrollArea.setWidget(self.imagePreviewScrollAreaContents)
		self.imagePreviewScrollArea.setStyleSheet("background-color: rgb(42, 42, 42)")

		self.imagePreviewGridLayout = QtGui.QGridLayout(self.imagePreviewScrollAreaContents)
		self.imagePreviewGridLayout.setColumnMinimumWidth(0, 95)
		self.imagePreviewGridLayout.setColumnMinimumWidth(1, 95)
		self.imagePreviewGridLayout.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)


		self.layeredTextureLabel = QtGui.QLabel("Layered Texture Name", self.main_widget)
		self.layeredTextureLabel.setGeometry(20, 402, 143, 16)

		self.layeredTextureNameLineEdit = QtGui.QLineEdit(self.main_widget)
		self.layeredTextureNameLineEdit.setGeometry(173, 400, 307, 22)

		self.createTextureFilesButton = QtGui.QPushButton("Create File Texture Nodes", self.main_widget)
		self.createTextureFilesButton.setGeometry(10, 430, 480, 32)
		self.createTextureFilesButton.setStyleSheet(blueGradientStyleSheet)
		self.createTextureFilesButton.setMask(getRoundedMask(self.createTextureFilesButton.width(), self.createTextureFilesButton.height()))

		# create layered texture view area
		self.layeredTextureTreeView = QtGui.QTreeView(self.main_widget)
		self.layeredTextureTreeView.setGeometry(10, 470, 480, 140)
		self.layeredTextureTreeView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self.layeredTextureTreeView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		#self.layeredTextureTreeView.setColumnWidth(0, 400)

		self.layeredTextureTreeModel = QtGui.QStandardItemModel()
		self.layeredTextureTreeModel.setHorizontalHeaderLabels(["Name", "Kind"])
		self.layeredTextureTreeView.setModel(self.layeredTextureTreeModel)
		self.layeredTextureTreeView.setUniformRowHeights(True)

		#create creation and hypershade buttons
		self.openHyperShadeButton = QtGui.QPushButton("Open in Hypershade", self.main_widget)
		self.openHyperShadeButton.setGeometry(10, 620, 480, 32)
		self.openHyperShadeButton.setStyleSheet(blueGradientStyleSheet)
		self.openHyperShadeButton.setMask(getRoundedMask(self.openHyperShadeButton.width(), self.openHyperShadeButton.height()))


		self.assignToSelectedButton = QtGui.QPushButton("Assign to Selected Object", self.main_widget)
		self.assignToSelectedButton.setGeometry(10,662, 350, 32)
		self.assignToSelectedButton.setStyleSheet(blueGradientStyleSheet)
		self.assignToSelectedButton.setMask(getRoundedMask(self.assignToSelectedButton.width(), self.assignToSelectedButton.height()))

		comboStyleSheet = "QComboBox {\
	  	background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(127, 197, 255, 255), stop:1 rgba(40, 81, 122, 255));\
		border: rgba(0,0,0,0);}\
	  	QComboBox::drop-down {border: rgba(0,0,0,0);}\
		"
		self.channelComboBox = QtGui.QComboBox(self.main_widget)
		self.channelComboBox.setGeometry(365, 662, 125, 32)
		self.channelComboBox.addItems(["Diffuse", "Weight", "Transparency", "Reflectivity", "Glossiness","Cutout Opacity" "Bump"])
		self.channelComboBox.setStyleSheet(comboStyleSheet)
		self.channelComboBox.setMask(getRoundedMask(self.channelComboBox.width(), self.channelComboBox.height()))

		# SIGNALS
		treeClickedSlotCmd = lambda: self.fileBrowserIndexChanged(self.fileBrowserTreeView.selectedIndexes())
		self.fileBrowserTreeView.selectionModel().selectionChanged.connect(treeClickedSlotCmd)

		layerTextureListIndexChangedSlotCmd = lambda: self.layerTextureListIndexChanged(self.layeredTextureTreeView.selectedIndexes())
		self.layeredTextureTreeView.selectionModel().selectionChanged.connect(layerTextureListIndexChangedSlotCmd)

		createTexturesSlotCmd = lambda: self.createFileTextureNodes()
		self.createTextureFilesButton.clicked.connect(createTexturesSlotCmd)

		hyperShadeSelectedCmd = lambda: self.hyperShadeSelectedIndex(self.layeredTextureTreeView.selectedIndexes())
		self.openHyperShadeButton.clicked.connect(hyperShadeSelectedCmd)

		assignMaterialCmd = lambda: self.assignToSelected(self.layeredTextureTreeView.selectedIndexes(), self.channelComboBox.currentIndex())
		self.assignToSelectedButton.clicked.connect(assignMaterialCmd)

	def _createMenuBar(self):
		styleSheet = "QMenuBar#windowMenuBar {background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(127, 197, 255, 255), stop:1\
		rgba(40, 81, 122, 255))}\
		QMenuBar::item:selected {background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(127, 197, 255, 0), stop:1\
		rgba(40, 81, 122, 0));\
		color: orange}"

		self.windowMenuBar = QtGui.QMenuBar(self)
		self.windowMenuBar.setGeometry(0, 1, self.width-10, 20)
		self.windowMenuBar.setObjectName("windowMenuBar")
		self.windowMenuBar.setStyleSheet(styleSheet)
		self.windowMenuBar.setFixedSize(self.width, 20)

		self.settingsMenuItem = self.windowMenuBar.addMenu("Settings")
		self.layerTexturesCheckBox = self.settingsMenuItem.addAction("Layer Textures")
		self.previewTexturesCheckBox = self.settingsMenuItem.addAction("Preview Textures")
		self.layerTexturesCheckBox.setCheckable(True)
		self.previewTexturesCheckBox.setCheckable(True)

		self.layerTexturesCheckBox.setToolTip("Import textures and automatically layer them.")


	def fileBrowserIndexChanged(self, indexes):
		#directory list
		imageList = []

		for i in self.imagePreviewScrollArea.findChildren(QtGui.QLabel):
			i.deleteLater()

		for index in list(set(indexes)):
			#append index of the file path of each object at x index
			filePath = self.fileBrowserModel.filePath(index)

			try:
				fDirList = listdir_fullpath(filePath)
				for fileName in fDirList:
					ext = os.path.splitext(fileName)[-1].lower()
					if ext in ('.jpeg', '.jpg', '.gif', '.iff', '.png', '.psd', '.tga', '.tif', '.bmp'):
						imageList.append(fileName)
			except:
				imageList.append(filePath)

		if self.previewTexturesCheckBox.isChecked():
			for index, file in enumerate(list(set(imageList))):

				#row column to prevent "glitch" where images are not loaded properly
				row = math.floor(index/2)
				column = index % 2
				fileName = os.path.basename(file).replace(".", "_")
				texturePreviewLabel = TexturePreview(file, fileName)
				#texturePreviewLabel.setParent(self.imagePreviewGridLayout)
				self.imagePreviewGridLayout.addWidget(texturePreviewLabel, row, column)
				texturePreviewLabel.show()

		self.imageList = imageList
	def hyperShadeSelectedIndex(self, indexes):

		pm.select(cl = True)
		for index in list(set(indexes)):
			# Allow selection of entire rows but prevent duplicate items
			currentItem = self.layeredTextureTreeModel.itemFromIndex(index)
			if type(currentItem) in (TextureSet, Texture):
				try:
					pm.select(currentItem.node, add = True)
					pm.select(currentItem.nodeList, add = True)
				except:
					pass

		pm.mel.eval('HypershadeWindow;')
		pm.evalDeferred('pm.mel.eval(\'hyperShadePanelGraphCommand("hyperShadePanel1", "showUpAndDownstream");\')')



	def createFileTextureNodes(self):
		#imageList = self.imageList
		self.textureSetList = []
		layeredTextureName = self.layeredTextureNameLineEdit.text()
		newTextureSet = TextureSet(layeredTextureName)
		newTextureSet.createSet(self.imageList, self.layerTexturesCheckBox.isChecked(), layeredTextureName)
		self.textureSetList.append(newTextureSet)
		self.layeredTextureTreeModel.appendRow([newTextureSet, newTextureSet.textureSetType])


	def assignToSelected(self, layerIndex, channelIndex):
		for obj in pm.selected():
			materialChannelList = [".diffuse", ".diffuse_weight", ".transparency", ".reflectivity", ".refl_gloss", "cutout_opacity", "bump"]
			shapeNode = pm.listRelatives(obj, c = True, s = True)
			shadingGrp = pm.listConnections(shapeNode, type = "shadingEngine")[0]
			mat = list(set(pm.listConnections(shadingGrp, type = ['mia_material_x', 'mia_material_x_passes', 'lambert', 'phong'])))[0]
			try:
				currentItem = self.layeredTextureTreeModel.itemFromIndex(layerIndex[0]).node
			except:
				pm.cmds.warning("Please select a texture")
			try:
				outAttr = ".outColor"
				if channelIndex not in (0, 5):
					outAttr = ".outAlpha"

				currentItemOutColor = currentItem + outAttr
				materialInput = mat + materialChannelList[channelIndex]
				pm.connectAttr(currentItemOutColor, materialInput, f = True)
			except:
				pm.cmds.warning("Could not connect materials to " + obj)

	def layerTextureListIndexChanged(self, index):
		currentItem = self.layeredTextureTreeModel.itemFromIndex(index)

		pm.select(cl = True)
		try:
			pm.select(currentItem.node, add = True)
		except:
			pass

class TexturePreview(QtGui.QLabel):
	def __init__(self, imageDir, imageName, parent = None):
		super(TexturePreview, self).__init__(parent)

		self.setObjectName(str(imageName))
		self.setBackgroundRole(QtGui.QPalette.Base)
		self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
		self.setScaledContents(True)

		reader = QtGui.QImageReader(imageDir)
		reader.setScaledSize(QtCore.QSize(95, 95))
		scaledImage = QtGui.QImage(reader.read())

		pixmap = QtGui.QPixmap(scaledImage)

		self.setPixmap(pixmap)
		self.setFixedSize(95, 95)

class TextureSet(QtGui.QStandardItem):
	def __init__(self, layeredTextureName):
		super(TextureSet, self).__init__(layeredTextureName)
		self.textureSetType = QtGui.QStandardItem()
		self.textureSetType.setText("Set")
		self.fileTextureList = []
		self.nodeList = []
		self.node = None

	def load(self, layerTexture):
		pass
	def createSet(self, imageList, createLayered, layeredTextureName):
		self.textureSetType.setText("Set")
		self.fileTextureList = []
		self.nodeList = []
		self.node = None

		alphaList = []
		tempAlphaList = []
		alphasExist = False

		if createLayered:
			self.textureSetType.setText("Layered")
			self.LayeredTexture = pm.shadingNode("layeredTexture", asTexture = True, n = layeredTextureName + "_layeredTexture")

			pm.setAttr( (self.LayeredTexture + '.alphaIsLuminance'), 1)
			self.nodeList.append(self.LayeredTexture)
			self.node = self.LayeredTexture


		if len(imageList) == 1:
			file = imageList[0]
			newName = os.path.basename(file)
			newFileTextureNode = Texture(newName)
			newFileTextureNode.fileTextureName = file
			self.nodeList.append(newFileTextureNode.node)
			self.textureSetType.setText("File")
			self.node = newFileTextureNode.node
		# Search for alpha textures
		else:
			if createLayered:

				for i, file in enumerate(imageList):
					filePath = os.path.dirname(file)
					fileName = os.path.basename(file)
					searchName, ext = os.path.splitext(fileName)

					if searchName.endswith("_a") or searchName.endswith("_alpha"):
						imageList.pop(i)
						alphasExist = True
						tempAlphaList.append(file)


				if alphasExist:
					for i, file in enumerate(tempAlphaList):
						filePath = os.path.dirname(file)
						fileName = os.path.basename(file)
						searchName, ext = os.path.splitext(fileName)
						if searchName.endswith("_a"):
							correspondingIndex = imageList.index((filePath + '/' + searchName[:-2] + ext))
							alphaList.append([correspondingIndex, file])

						if searchName.endswith("_alpha"):
							correspondingIndex = imageList.index(filePath + '/' + searchName[:-6] + ext)
							alphaList.append([correspondingIndex, file])
			print alphaList
			for i, file in enumerate(imageList):

				newName = os.path.basename(file)
				newFileTextureNode = Texture(newName)
				newFileTextureNode.fileTextureName = file
				self.nodeList.append(newFileTextureNode.node)

				if createLayered:
					#TODO: set over as default
					newFileTextureAttr = newFileTextureNode.node + '.outColor'
					newLayeredTextureAttr = self.LayeredTexture + '.inputs[{0}].color'.format(i)
					pm.connectAttr(newFileTextureAttr, newLayeredTextureAttr, f = True)

				self.appendRow([newFileTextureNode, QtGui.QStandardItem("Image")])

			for i, file in alphaList:

				newName = os.path.basename(file)
				newFileTextureNode = Texture(newName)
				newFileTextureNode.fileTextureName = file
				self.nodeList.append(newFileTextureNode.node)

				if createLayered:
					if alphasExist:
						newFileTextureAttr = newFileTextureNode.node + '.outAlpha'
						newLayeredTextureAttr = self.LayeredTexture + '.inputs[{0}].alpha'.format(i)
						pm.connectAttr(newFileTextureAttr, newLayeredTextureAttr, f = True)

				self.appendRow([newFileTextureNode, QtGui.QStandardItem("Alpha")])

class Texture(QtGui.QStandardItem):
	def __init__(self, name):
		super(Texture, self).__init__(name)
		self.node = pm.shadingNode("file", asTexture = True, n = name + '_fileTexture')
		self.node.alphaIsLuminance.set(1)
		#TODO: CONNECT SETTING FOR FILTER TYPE
		self.node.filterType.set(0)
		self._path = ""
		self._type = "File"

	@property
	def fileTextureName(self):
		return self._path

	@fileTextureName.setter
	def fileTextureName(self, value):
		self.node.fileTextureName.set(value)
		self._path = value

	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value):
		self._type = QtGui.QStandardItem(value)



#TODO: IMPLEMENT AN ABILITY TO SCALE FIELDS FOR PREVIEW AND BROWSER
#TODO: IMPLEMENT JSON EXPORT OF CONFIG DATA TO IMPORT PREVIOUSLY CREATED LAYERD TEXTURE NODES
#TODO: IMPLEMENT LOAD PREVIOUSLY CREATED LAYERED TEXTURE NODES
#TODO: IMPLEMENT SELECTION OF CHILDREN AND GRAPHING IN HYPERSHADE
#TODO: IMPOLEMENT CUTOUT OPACITY OPTION