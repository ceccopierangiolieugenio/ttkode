#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Eugenio Parodi <ceccopierangiolieugenio AT googlemail DOT com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import sys
import argparse

import appdirs

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter, Terminal256Formatter, TerminalTrueColorFormatter

from TermTk import TTk, TTkK, TTkLog, TTkCfg, TTkColor, TTkTheme, TTkTerm, TTkHelper
from TermTk import TTkString
from TermTk import TTkColorGradient
from TermTk import pyTTkSlot, pyTTkSignal

from TermTk import TTkFrame, TTkButton
from TermTk import TTkTabWidget
from TermTk import TColor, TText
from TermTk import TTkAbstractScrollArea, TTkAbstractScrollView
from TermTk import TTkFileDialogPicker
from TermTk import TTkFileTree, TTkTextEdit

from TermTk import TTkGridLayout
from TermTk import TTkSplitter

from .cfg  import *
from .about import *
from .kodetab import KodeTab
# from .options import optionsFormLayout, optionsLoadTheme

def main():
    TTKodeCfg.pathCfg = appdirs.user_config_dir("ttkode")

    parser = argparse.ArgumentParser()
    # parser.add_argument('-f', help='Full Screen', action='store_true')
    parser.add_argument('-c', help=f'config folder (default: "{TTKodeCfg.pathCfg}")', default=TTKodeCfg.pathCfg)
    parser.add_argument('filename', type=str, nargs='*',
                    help='the filename/s')
    args = parser.parse_args()

    TTkLog.use_default_file_logging()

    TTKodeCfg.pathCfg = args.c
    TTkLog.debug(f"Config Path: {TTKodeCfg.pathCfg}")

    TTKodeCfg.load()

    # if 'theme' not in TTKodeCfg.options:
    #     TTKodeCfg.options['theme'] = 'NERD'
    # optionsLoadTheme(TTKodeCfg.options['theme'])

    TTkTheme.loadTheme(TTkTheme.NERD)

    root = TTk( layout=TTkGridLayout(), title="TTkode",
                sigmask=(
                    TTkTerm.Sigmask.CTRL_Q |
                    TTkTerm.Sigmask.CTRL_S |
                    TTkTerm.Sigmask.CTRL_Z |
                    TTkTerm.Sigmask.CTRL_C ))

    splitter = TTkSplitter(parent=root)
    layoutLeft = TTkGridLayout()
    splitter.addItem(layoutLeft, 15)

    hSplitter = TTkSplitter(parent=splitter,  orientation=TTkK.HORIZONTAL)

    menuFrame = TTkFrame(border=False, maxHeight=1)
    fileMenu = menuFrame.menubarTop().addMenu("&File")
    fileMenu.addMenu("Open")
    fileMenu.addMenu("Close")
    fileMenu.addMenu("Exit").menuButtonClicked.connect(lambda _:TTkHelper.quit())
    layoutLeft.addWidget(menuFrame, 0,0)
    fileTree = TTkFileTree(path='.')
    layoutLeft.addWidget(fileTree, 1,0)
    layoutLeft.addWidget(quitbtn := TTkButton(border=True, text="Quit", maxHeight=3), 2,0)
    quitbtn.clicked.connect(root.quit)

    kt = KodeTab(parent=hSplitter, border=False, closable=True)

    def _openFile(file):
        KodeTab.lastUsed.openFile(file)

    for file in args.filename:
        _openFile(file)

    fileTree.fileActivated.connect(lambda x: _openFile(x.path()))

    root.mainloop()
