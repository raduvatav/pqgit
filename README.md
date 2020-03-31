# pqgit (Python Qt Git)
pqgit is a graphical git browser. It shows the branches and the commit log of a repo. It also shows diffs or launches an external differ (default: meld) to do that.


## Installation

```pip install pqgit``` 


## Usage

When you first run pqgit, it shows a file open dialog; open the .git directory of your project. Change project with Ctrl+O.

You can select one or two commits in the history panel (diff to parent or to each other).

Double-click on some file to open the external differ.

Change branch by selecting one. Be aware that **this actually does a checkout!** It will not delete your working files (I hope :D), but will leave the repo on that branch. I don't like it, but that's how pygit2 behaves (at least I couldn't find out how to just display some branch without checking it out)

## Configuration

Not much at the moment.

To change the default diff tool, set it in `~/.config/pqgit/config.ini`, like:

```
[General]
diff_tool=bcompare
...
```

## Screenshot

![Alt text](screenshot.png?raw=true)

## Contributing
This project uses **tabs**. Please use the included `.style.yapf` and `.pylintrc`

If you want to change the UI, edit `pqgit.ui` with Qt Designer, then run:
```
pyside2-uic pqgit.ui >| src/pqgit/ui.py
```

## Wheel package (for PyPi / installing with pip)
### Install locally
```
pip install -e .
```
### Create packages for PyPi

```
python3 setup.py sdist bdist_wheel
pip install --force-reinstall --no-deps dist/pqgit-<VERSION>-py3-none-any.whl
```
