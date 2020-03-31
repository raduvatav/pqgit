""" model
"""

# from typing import List
from datetime import datetime
from dataclasses import dataclass
from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt
# from collections import namedtuple


@dataclass
class Branch():
	""" one branch """
	name: str
	ref: str
	c_o: bool


@dataclass
class Commit():
	""" one commit """
	id: str
	tree_id: str
	author: str
	dt: int
	dt_offs: int
	message: str


@dataclass
class Patch():
	""" differences for one file """
	path: str
	status: str
	new_file_id: str
	old_file_id: str


class BranchesModel(QtCore.QAbstractTableModel):
	""" branches """
	def __init__(self):
		super(BranchesModel, self).__init__()
		self.branches = []

	def rowCount(self, parent=QtCore.QModelIndex()):
		del parent
		return len(self.branches)

	def columnCount(self, parent=QtCore.QModelIndex()):
		del parent
		return 2

	def data(self, index, role):
		row = index.row()
		col = index.column()

		branch = self.branches[row]

		ret = None
		if role == Qt.DisplayRole:
			if col == 0:
				if branch.ref.startswith('refs/tags'):
					ret = 'tag'
				# else:
				# 	ret = 'branch'
			elif col == 1:
				ret = branch.name

		elif role == Qt.ToolTipRole:
			if col == 1:
				ret = branch.ref

		return ret

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			return ['', 'name'][section]
		return None

	def update(self, branches):
		""" update """
		self.beginResetModel()

		self.branches = branches

		self.endResetModel()


class HistoryModel(QtCore.QAbstractTableModel):
	""" commits	"""
	def __init__(self):
		super(HistoryModel, self).__init__()
		self.commits = []

	def rowCount(self, parent=QtCore.QModelIndex()):
		del parent
		return len(self.commits)

	def columnCount(self, parent=QtCore.QModelIndex()):
		del parent
		return 4

	def update(self, commits):
		""" update """
		self.beginResetModel()

		self.commits = commits

		self.endResetModel()

	def data(self, index, role):
		row = index.row()
		col = index.column()

		commit = self.commits[row]

		ret = None
		if role == Qt.DisplayRole:
			if col == 0:
				if commit.id:
					ret = commit.id[:7]
			elif col == 1:
				ret = commit.message
			elif col == 2 and commit.author:
				names = commit.author.name.split(' ')
				ret = ''.join(x[:1] for x in names)
			elif col == 3 and commit.dt:
				secs = commit.dt + commit.dt_offs * 60
				ret = datetime.utcfromtimestamp(secs).isoformat().replace('T', ' ')[:-3]
		elif role == Qt.ToolTipRole:
			if col == 0:
				ret = commit.id
			elif col == 2:
				ret = commit.author.name + ' <' + commit.author.email + '>'
		elif role == Qt.FontRole and col == 0:
			ret = QtGui.QFont('Monospace')

		return ret

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			return ['id', 'message', '', 'date'][section]
		return None


class FilesModel(QtCore.QAbstractTableModel):
	""" files """
	def __init__(self):
		super(FilesModel, self).__init__()
		self.patches = []

	def rowCount(self, parent):
		del parent
		return len(self.patches)

	def columnCount(self, parent=QtCore.QModelIndex()):
		del parent
		return 2

	def update(self, patches):
		""" update """
		self.beginResetModel()

		self.patches = patches

		self.endResetModel()

	def data(self, index, role):
		row = index.row()
		col = index.column()
		ret = None
		if role == Qt.DisplayRole:
			if col == 0:
				ret = self.patches[row].status
			if col == 1:
				ret = self.patches[row].path
		elif role == Qt.ForegroundRole:
			if self.patches[row].status == 'D':
				ret = QtGui.QColor(Qt.red)
			elif self.patches[row].status == 'A':
				ret = QtGui.QColor(Qt.green)
			elif self.patches[row].status == 'I':
				ret = QtGui.QColor(Qt.gray)

		return ret

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			# return {0: '', 1: 'file', 2: 'rel. path', 3: 'renamed'}[section]
			return ['', 'file', 'rel. path', 'renamed'][section]
		return None
