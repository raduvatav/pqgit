# pqgit (Python Qt Git)
pqgit is a graphical git browser. It shows the branches and the commit log of a repo. It also shows diffs or launches an external differ (default: meld) to do that.


## Installation

You need python3 (not sure about minimum version; I wrote this with 3.8) and also probably have to 

```pip install pygit2 PySide2``` 

Install Qt if you don't already have it. Your distro should have it (if not, you probably don't need instructions)

Then run `python pqgit.py`.

## Releases

I'm including a precompiled windows executable with the releases. It's pretty big (~40 MB) since it has all needed dll's (Qt, Python, etc.) in one file.

The linux executable would be even bigger (~140 MB) and it doesn't make much sense. I plan to make an Arch package soon.


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
pyinstaller pqgit.spec
```
If everything goes well, find your executable under `dist/pqgit[.exe]`

## Screenshot

![Alt text](screenshot.png?raw=true)
