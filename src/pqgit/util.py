""" util
"""
import pygit2

# difflib colors
STYLES = '''
        table.diff {font-family:Monospace; border:medium;}
        .diff_header{font-weight: bold; padding-right:10}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#0daa0d}
        .diff_chg {background-color:#888800}
        .diff_sub {background-color:#c00000}'''

# libgit constants mapped to status chars (to be shown)
GIT_STATUS = {
	pygit2.GIT_STATUS_INDEX_NEW: 'iA',  #
	pygit2.GIT_STATUS_INDEX_MODIFIED: 'iM',
	pygit2.GIT_STATUS_INDEX_DELETED: 'iD',
	pygit2.GIT_STATUS_WT_NEW: 'A',
	pygit2.GIT_STATUS_WT_MODIFIED: 'M',
	pygit2.GIT_STATUS_WT_DELETED: 'D',
	pygit2.GIT_STATUS_IGNORED: 'I',
	pygit2.GIT_STATUS_CONFLICTED: 'C',
}


def parse_tree_rec(tree, include_dirs=False, path=''):
	""" generator over git tree; returns [tuple(file_path, file_id)] """
	for obj in tree:
		if obj.type_str == 'blob':
			yield (path + obj.name, obj.id.hex)
		else:
			if include_dirs:
				yield (path + obj.name, obj.id.hex)
			yield from parse_tree_rec(obj, include_dirs, f'{path}{obj.name}/')
