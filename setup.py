""" setup
"""
import setuptools

with open("README.md", "r") as fh:
	LONG_DESC = fh.read()

with open("VERSION", "r") as fh:
	VERSION = fh.read().strip()

setuptools.setup(
	name="pqgit",
	version=VERSION,
	author="Radu Vatav",
	author_email="radu@vatav.cc",
	description="Python Qt Git browser",
	long_description=LONG_DESC,
	long_description_content_type="text/markdown",
	url="https://github.com/raduvatav/pqgit",
	package_dir={'': 'src'},
	package_data={
		'pqgit': ['Git-Icon-White.png'],
	},
	packages=setuptools.find_packages(where='src'),
	install_requires=[
		'pygit2',
		'PySide2',
	],
	entry_points={
		'gui_scripts': [
			'pqgit=pqgit:run_pqgit',
		],
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.8',
)
