# pqgit (Python Qt Git)
pqgit is a graphical git browser. It shows the branches and the commit log of a repo. It also shows diffs or launches an external differ (default: meld) to do that.


## Installation

You need python3 and also probably have to `pip install pygit2 PySide2`. Then just run `python pqgit.py`.

(not sure about minimum python version; I wrote this with 3.8)

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

## Freezing (build an executable)

This seems to work for both Linux and Windows:
```
pip install pyinstaller
pyinstaller --hidden-import=_cffi_backend pqgit.py
```
If everything goes well, find your executable under `dist/pqgit/pqgit[.exe]`

## Screenshot

![Alt text](screenshot.png?raw=true)
