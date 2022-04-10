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

from TermTk import *

from TermTk import TTk, TTkK, TTkLog, TTkColor, TTkTheme
from TermTk import pyTTkSlot, pyTTkSignal
from TermTk import TTkFrame
from TermTk import TColor, TText
from TermTk import TTkAbstractScrollArea, TTkAbstractScrollView
from TermTk import TTkFileDialogPicker
from TermTk import TTkFileTree, TTkTextEdit

from .cfg  import *
from .about import *
# from .options import optionsFormLayout, optionsLoadTheme

class _KolorFrame(TTkFrame):
    __slots__ = ('_fillColor')
    def __init__(self, *args, **kwargs):
        TTkFrame.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , '_KolorFrame')
        self._fillColor = kwargs.get('fillColor', TTkColor.RST)

    def setFillColor(self, color):
        self._fillColor = color

    def paintEvent(self):
        w,h = self.size()
        for y in range(h):
            self._canvas.drawText(pos=(0,y),text='',width=w,color=self._fillColor)
        return super().paintEvent()

class KodeTab(TTkTabWidget):
    __slots__ = ('_frameOverlay')
    def __init__(self, *args, **kwargs):
        TTkTabWidget.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'KodeTab')
        self._frameOverlay = _KolorFrame('visible',False)
        self._frameOverlay.setBorderColor(TTkColor.fg("#00FFFF")+TTkColor.bg("#000044"))
        self._frameOverlay.setFillColor(TTkColor.bg("#000088", modifier=TTkColorGradient(increment=-2)))
        self.rootLayout().addWidget(self._frameOverlay)


    def dragEnterEvent(self, evt) -> bool:
        self.currentWidget().lowerWidget()
        return True

    def dragLeaveEvent(self, evt) -> bool:
        self._frameOverlay.hide()
        return True

    def dragMoveEvent(self, evt) -> bool:
        x,y = evt.x, evt.y
        w,h = self.size()
        if y<2:
            return super().dragMoveEvent(evt)
        h-=2
        y-=2

        def _processDrag(x,y,w,h):
            self._frameOverlay.show()
            self._frameOverlay.resize(w,h)
            self._frameOverlay.move(x, y)

        if x<w//4:
            _processDrag(0,2,w//4,h)
        elif x>w*3//4:
            _processDrag(w-w//4,2,w//4,h)
        elif y<h//4:
            _processDrag(0,2,w,h//4)
        elif y>h*3//4:
            _processDrag(0,2+h-h//4,w,h//4)
        else:
            self._frameOverlay.hide()
        return True

    def dropEvent(self, evt) -> bool:
        self._frameOverlay.hide()
        x,y = evt.x, evt.y
        ret = True
        data = evt.data()
        tb = data.tabButton()
        tw = data.tabWidget()
        if y<2:
            ret = super().dropEvent(evt)
        else:
            w,h = self.size()
            h-=2
            y-=2
            index  = tw._tabBar._tabButtons.index(tb)
            widget = tw._tabWidgets[index]

            def _processDrop(index, orientation, offset):
                tw.removeTab(index)
                splitter = self.parentWidget()
                index = splitter.indexOf(self)
                if splitter.orientation() != orientation:
                    splitter.replaceWidget(index, splitter := TTkSplitter(orientation=orientation))
                    splitter.addWidget(self)
                    index=offset
                splitter.insertWidget(index+offset, kt:=KodeTab(border=False))
                kt.addTab(widget,tb.text)

            if x<w//4:
                _processDrop(index, TTkK.HORIZONTAL, 0)
            elif x>w*3//4:
                _processDrop(index, TTkK.HORIZONTAL, 1)
            elif y<h//4:
                _processDrop(index, TTkK.VERTICAL, 0)
            elif y>h*3//4:
                _processDrop(index, TTkK.VERTICAL, 1)
            else:
                ret = super().dropEvent(evt)

        # Remove the widget and/or all the cascade empty splitters
        if not tw._tabWidgets:
            widget = tw
            splitter = widget.parentWidget()
            while splitter.count() == 1:
                widget = splitter
                splitter = widget.parentWidget()
            splitter.removeWidget(widget)

        return ret

def main():
    TTKodeCfg.pathCfg = appdirs.user_config_dir("ttkode")

    parser = argparse.ArgumentParser()
    # parser.add_argument('-f', help='Full Screen', action='store_true')
    parser.add_argument('-c', help=f'config folder (default: "{TTKodeCfg.pathCfg}")', default=TTKodeCfg.pathCfg)
    parser.add_argument('filename', type=str, nargs='+',
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

    root = TTk(layout=TTkGridLayout(), title="TTkode")

    splitter = TTkSplitter(parent=root)
    splitter.addWidget(fileTree:=TTkFileTree(path='.'), 15)

    hSplitter = TTkSplitter(parent=splitter,  orientation=TTkK.HORIZONTAL)
    kt = KodeTab(parent=hSplitter, border=False)

    def _openFile(file):
        with open(file, 'r') as f:
            content = f.read()
        kt.addTab(te:=TTkTextEdit(),os.path.basename(file))
        kt.setCurrentWidget(te)
        te.setReadOnly(False)
        te.setText(highlight(content, PythonLexer(), TerminalTrueColorFormatter(style='rrt')))

    for file in args.filename:
        _openFile(file)

    fileTree.fileActivated.connect(lambda x: _openFile(x.path()))

    root.mainloop()
