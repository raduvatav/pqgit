""" Python Qt Git
"""
import os
import sys
import tempfile
import subprocess
import difflib
import re

from dataclasses import dataclass

import pygit2

from PySide2.QtWidgets import (
	QApplication, QMainWindow, QHeaderView, QAbstractItemView, QMessageBox, QShortcut, QFileDialog
)

from PySide2.QtCore import (
	QItemSelectionModel, QItemSelection, QSettings, QPoint, QSize, QTimer, QDir, QFileSystemWatcher, Qt
)

from PySide2.QtGui import QFont, QIcon, QKeySequence

from pqgit import ui
from pqgit.model import BranchesModel, HistoryModel, FilesModel, Branch, Commit, Patch
from pqgit.util import STYLES, GIT_STATUS, parse_tree_rec

import pkg_resources  # part of setuptools
VERSION = pkg_resources.require("pqgit")[0].version

# modify difflib colors
_html_diff = difflib.HtmlDiff(tabsize=4)  #pylint: disable=invalid-name
_html_diff._styles = STYLES  #pylint: disable=protected-access


@dataclass
class Proc():
	""" hold started process (difftool) information """
	proc: type
	old_f: type
	new_f: type
	running: bool


class Pqgit(QMainWindow):
	""" main class / entry point """
	def __init__(self):
		super().__init__()
		self.setAttribute(Qt.WA_DeleteOnClose)  # let Qt delete stuff before the python garbage-collector gets to work
		self.repo = None
		self.branches_model = None

		# instantiate main window
		self.ui = ui.Ui_MainWindow()
		self.ui.setupUi(self)

		self.fs_watch = QFileSystemWatcher(self)
		self.fs_watch.fileChanged.connect(self.on_file_changed)
		self.fs_watch.directoryChanged.connect(self.on_dir_changed)

		self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, 'pqgit', 'config')

		# for comparison
		self.new_c_id, self.old_c_id = None, None

		# window icon
		cwd = os.path.dirname(os.path.realpath(__file__))
		self.setWindowIcon(QIcon(os.path.join(cwd, 'Git-Icon-White.png')))
		self.setWindowTitle('pqgit')

		# size and position
		self.move(self.settings.value('w/pos', QPoint(200, 200)))
		self.resize(self.settings.value('w/size', QSize(1000, 1000)))
		self.ui.hist_splitter.setSizes([int(s) for s in self.settings.value('w/hist_splitter', [720, 360])])
		self.ui.cinf_splitter.setSizes([int(s) for s in self.settings.value('w/cinf_splitter', [360, 360])])
		self.ui.diff_splitter.setSizes([int(s) for s in self.settings.value('w/diff_splitter', [150, 1200, 230])])

		# open repo dir
		open_shortcut = QShortcut(QKeySequence('Ctrl+O'), self)
		open_shortcut.activated.connect(self.open_dir)

		# set-up ui
		self.branches_model = BranchesModel()
		self.ui.tvBranches.setModel(self.branches_model)
		self.ui.tvBranches.selectionModel().selectionChanged.connect(self.branches_selection_changed)
		self.ui.tvBranches.resizeColumnsToContents()

		self.history_model = HistoryModel()
		self.ui.tvHistory.setModel(self.history_model)
		self.ui.tvHistory.selectionModel().selectionChanged.connect(self.history_selection_changed)

		self.files_model = FilesModel()
		self.ui.tvFiles.setModel(self.files_model)
		self.ui.tvFiles.selectionModel().selectionChanged.connect(self.files_selection_changed)

		self.ui.tvFiles.doubleClicked.connect(self.on_file_doubleclicked)

		for view in (self.ui.tvBranches, self.ui.tvHistory, self.ui.tvFiles):
			view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
			view.setSelectionBehavior(QAbstractItemView.SelectRows)
			view.setShowGrid(False)
			view.verticalHeader().setDefaultSectionSize(QApplication.font().pointSize() + 2)
			view.verticalHeader().hide()

		self.ui.teDiff.setFont(QFont('Monospace'))

		self.difftools = []

		timer = QTimer(self)
		timer.timeout.connect(self.on_timer)
		timer.start(5000)

		self.dir_name = self.settings.value('last_opened_repo', None)

		try:
			pygit2.Repository(self.dir_name)
		except Exception:  #pylint: disable=broad-except
			self.open_dir()
			return

		self.open_repo()

	def open_dir(self):
		""" show open dir dialog and open repo """
		last_dir = self.settings.value('last_fileopen_dir', '')

		fd = QFileDialog(self, 'Open .git', last_dir)
		fd.setFileMode(QFileDialog.DirectoryOnly)
		fd.setFilter(QDir.Filters(QDir.Dirs | QDir.Hidden | QDir.NoDot | QDir.NoDotDot))

		while True:
			if not fd.exec():
				return
			self.dir_name = fd.selectedFiles()[0]
			parent = os.path.dirname(self.dir_name)
			self.settings.setValue('last_fileopen_dir', parent)
			self.settings.setValue('last_opened_repo', self.dir_name)

			try:
				pygit2.Repository(self.dir_name)
				break
			except pygit2.GitError:
				QMessageBox(self, text='Cannot open repo: ' + self.dir_name).exec()

		self.open_repo()

	def open_repo(self):
		""" called either on start or after open dialog """

		self.setWindowTitle(f'{self.dir_name} - pqgit ({VERSION})')
		self.repo = pygit2.Repository(self.dir_name)

		# remove existing files and folder from watch
		if self.fs_watch.files():
			self.fs_watch.removePaths(self.fs_watch.files())
		if self.fs_watch.directories():
			self.fs_watch.removePaths(self.fs_watch.directories())

		wd = self.repo.workdir
		self.fs_watch.addPath(wd)

		# get head tree for list of files in repo
		target = self.repo.head.target
		last_commit = self.repo[target]
		tree_id = last_commit.tree_id
		tree = self.repo[tree_id]
		# add those files and folder to watch
		self.fs_watch.addPaths([wd + o[0] for o in parse_tree_rec(tree, True)])
		# get files/folders not in repo from status
		self.fs_watch.addPaths([wd + p for p, f in self.repo.status().items() if GIT_STATUS[f] != 'I'])
		# (doesn't matter some are in both lists, already monitored ones will not be added by Qt)

		# local branches
		branches = []
		selected_branch_row = 0
		for idx, b_str in enumerate(self.repo.branches.local):
			b = self.repo.branches[b_str]
			if b.is_checked_out():
				selected_branch_row = idx
			branches.append(Branch(name=b.branch_name, ref=b.name, c_o=b.is_checked_out()))

		# tags
		regex = re.compile('^refs/tags')
		tags = list(filter(regex.match, self.repo.listall_references()))

		branches += [Branch(name=t[10:], ref=t, c_o=False) for t in tags]

		self.branches_model.update(branches)

		idx1 = self.branches_model.index(selected_branch_row, 0)
		idx2 = self.branches_model.index(selected_branch_row, self.branches_model.columnCount() - 1)
		self.ui.tvBranches.selectionModel().select(QItemSelection(idx1, idx2), QItemSelectionModel.Select)

		self.ui.tvHistory.resizeColumnsToContents()

	def on_timer(self):
		""" poll opened diff tools (like meld) and close temp files when finished """
		for dt in self.difftools:
			if subprocess.Popen.poll(dt.proc) is not None:
				if dt.old_f:
					dt.old_f.close()
				if dt.new_f:
					dt.new_f.close()
				dt.running = False

		self.difftools[:] = [dt for dt in self.difftools if dt.running]

	def on_file_changed(self, path):
		""" existing files edited """
		patch = self.files_model.patches[self.ui.tvFiles.selectionModel().selectedRows()[0].row()]
		if self.repo.workdir + patch.path == path:
			self.files_selection_changed()

	def on_dir_changed(self, path):
		""" file added/deleted; refresh history to show it in 'working' """
		# remember history selection
		history_ids = []
		for idx in self.ui.tvHistory.selectionModel().selectedRows():
			history_ids.append(self.history_model.commits[idx.row()].id)

		bak_path = self.files_model.patches[self.ui.tvFiles.selectionModel().selectedRows()[0].row()].path

		self.refresh_history()

		# restore history selection
		for i in history_ids:
			for row, c in enumerate(self.history_model.commits):
				if c.id == i:
					idx1 = self.history_model.index(row, 0)
					idx2 = self.history_model.index(row, self.history_model.columnCount() - 1)
					self.ui.tvHistory.selectionModel().select(QItemSelection(idx1, idx2), QItemSelectionModel.Select)

		# restore file selection
		if not bak_path:
			return
		for row, patch in enumerate(self.files_model.patches):
			if patch.path == bak_path:
				idx1 = self.files_model.index(row, 0)
				idx2 = self.files_model.index(row, self.files_model.columnCount() - 1)

				self.ui.tvFiles.selectionModel().select(QItemSelection(idx1, idx2), QItemSelectionModel.Select)
				break

	def refresh_history(self):
		""" called and branch check-out (which is also called during start-up) to populate commit log """

		commits = []
		# working directory
		status = self.repo.status()
		if len(status.items()) > 0:
			commits.append(Commit('working', 'working', None, None, None, None))

		for c in self.repo.walk(self.repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
			commit = Commit(
				id=c.id.hex,
				tree_id=c.tree_id.hex,
				author=c.author,
				dt=c.commit_time,
				dt_offs=c.commit_time_offset,
				message=c.message.strip()
			)
			commits.append(commit)

		self.history_model.update(commits)
		self.ui.tvHistory.resizeColumnsToContents()

	def branches_selection_changed(self):
		""" checkout selected branch """
		selected_row = self.ui.tvBranches.selectionModel().selectedRows()[0].row()
		self.repo.checkout(self.branches_model.branches[selected_row].ref, strategy=pygit2.GIT_CHECKOUT_SAFE)
		self.refresh_history()

	def on_file_doubleclicked(self, index):
		""" get files contents for revisions and start diff tool """

		patch = self.files_model.patches[index.row()]
		if not patch.old_file_id:
			msg_box = QMessageBox(self)
			msg_box.setText("Nothing to compare to.")
			msg_box.exec()
			return

		old_f = tempfile.NamedTemporaryFile(prefix=f'old_{self.old_c_id[:7]}__')
		old_f.write(self.repo[patch.old_file_id].data)
		old_f.flush()

		new_f = None
		if patch.new_file_id:
			# compare 2 revisions
			new_f = tempfile.NamedTemporaryFile(prefix=f'new_{self.new_c_id[:7]}__')
			new_f.write(self.repo[patch.new_file_id].data)
			new_f.flush()
			new_f_name = new_f.name
		else:
			# compare some revision with working copy
			new_f_name = self.repo.workdir + patch.path.strip()

		proc = subprocess.Popen([self.settings.value('diff_tool', 'meld'), old_f.name, new_f_name])
		self.difftools.append(Proc(proc, old_f, new_f, True))

	def history_selection_changed(self, selected):
		""" docstring """

		self.ui.teDiff.setText('')
		self.new_c_id, self.old_c_id = None, None

		selection_model = self.ui.tvHistory.selectionModel()
		selected_rows = selection_model.selectedRows()
		self.ui.teCommit.setPlainText('')

		commit = None
		fst_tid, fst_obj = None, None
		snd_tid, snd_obj = None, None

		if len(selected_rows) < 1:
			# nothing to do
			return

		if len(selected_rows) > 2:
			# don't allow more than 2 selected lines
			selection_model.select(selected, QItemSelectionModel.Deselect)
			return

		if len(selected_rows) == 1:
			# single revision selected

			commit = self.history_model.commits[selected_rows[0].row()]
			fst_tid = commit.tree_id

			if selected_rows[0].row() + 1 < self.history_model.rowCount():
				# there is a parent, get it's id to compare to it
				snd_commit = self.history_model.commits[selected_rows[0].row() + 1]
				snd_tid = snd_commit.tree_id
				self.new_c_id = commit.id
				self.old_c_id = snd_commit.id

			# set commit details in view
			if commit.tree_id != 'working':
				text = 'Commit: ' + commit.id + '\n\n'
				text += 'Author: ' + commit.author.name + ' <' + commit.author.email + '>\n\n'
				text += commit.message + '\n'
				self.ui.teCommit.setPlainText(text)

		else:
			# 2 revisions selected
			fst_row, snd_row = tuple(sorted([selected_rows[0].row(), selected_rows[1].row()]))
			commit = self.history_model.commits[fst_row]
			fst_tid = commit.tree_id
			snd_commit = self.history_model.commits[snd_row]
			snd_tid = snd_commit.tree_id
			self.new_c_id = commit.id
			self.old_c_id = snd_commit.id

		if fst_tid != 'working':
			fst_obj = self.repo.revparse_single(fst_tid)

		if snd_tid:
			snd_obj = self.repo.revparse_single(snd_tid)

		diff = None
		if fst_tid == 'working':
			# diff for working directory only shows... some files; get them anyway, then insert the ones from status
			diff = self.repo.diff(snd_obj, None)  # regardless of snd_obj being something or None
			patches = [
				Patch(
					p.delta.new_file.path.strip(),  #
					p.delta.status_char(),
					None,  # p.delta.new_file.id.hex is 'some' id, but it's somehow not ok...
					p.delta.old_file.id.hex if p.delta.old_file.id.hex.find('00000') < 0 else None,
				) for p in diff
			]
			inserted = [p.delta.new_file.path for p in diff]
			status = self.repo.status()
			for path, flags in status.items():
				if path not in inserted:
					patches.append(Patch(path.strip(), GIT_STATUS[flags], None, None))

		elif snd_obj:
			diff = self.repo.diff(snd_obj, fst_obj)

			patches = [
				Patch(
					p.delta.new_file.path.strip(),  #
					p.delta.status_char(),
					p.delta.new_file.id.hex if p.delta.new_file.id.hex.find('00000') < 0 else None,
					p.delta.old_file.id.hex if p.delta.old_file.id.hex.find('00000') < 0 else None,
				) for p in diff
			]

		else:
			# initial revision
			patches = [Patch(o[0], 'A', o[1], None) for o in parse_tree_rec(fst_obj)]

		patches = sorted(patches, key=lambda p: p.path)
		self.files_model.update(patches)
		self.ui.tvFiles.resizeColumnsToContents()

	def files_selection_changed(self):
		""" show diff (or file content for new, ignored, ... files) """
		patch = self.files_model.patches[self.ui.tvFiles.selectionModel().selectedRows()[0].row()]

		nf_data, of_data = None, None  # new_file, old_file
		if patch.new_file_id:
			nf_data = self.repo[patch.new_file_id].data.decode('utf-8')
		if patch.old_file_id:
			of_data = self.repo[patch.old_file_id].data.decode('utf-8')

		if nf_data and of_data:
			html = _html_diff.make_file(
				fromlines=nf_data.splitlines(),  #
				tolines=of_data.splitlines(),
				fromdesc=f'old ({self.old_c_id[:7]})',
				todesc=f'new ({self.new_c_id[:7]})',
				context=True
			)
			self.ui.teDiff.setHtml(html)
		elif nf_data:
			self.ui.teDiff.setText(nf_data)
		elif of_data:
			if patch.status == 'M':
				# this should be working directory compared to something else
				with open(self.repo.workdir + patch.path.strip()) as f:
					nf_data = f.read()
				html = _html_diff.make_file(
					fromlines=nf_data.splitlines(),
					tolines=of_data.splitlines(),
					fromdesc=f'old ({self.old_c_id[:7]})',
					todesc=f'new ({self.new_c_id[:7]})',
					context=True
				)
				self.ui.teDiff.setHtml(html)
			else:
				self.ui.teDiff.setText(of_data)
		else:
			with open(self.repo.workdir + patch.path.strip()) as f:
				self.ui.teDiff.setPlainText(f.read())

		self.ui.diff_groupbox.setTitle('Diff' if nf_data and of_data else 'File')

	def closeEvent(self, event):  # pylint: disable=invalid-name, no-self-use
		""" event handler for window closing; save settings """
		del event
		self.settings.setValue('w/pos', self.pos())
		self.settings.setValue('w/size', self.size())
		self.settings.setValue('w/hist_splitter', self.ui.hist_splitter.sizes())
		self.settings.setValue('w/cinf_splitter', self.ui.cinf_splitter.sizes())
		self.settings.setValue('w/diff_splitter', self.ui.diff_splitter.sizes())

		# delete any left temp files
		self.on_timer()


def pqgit_main():
	""" main """
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)

	k = Pqgit()
	k.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	pqgit_main()
