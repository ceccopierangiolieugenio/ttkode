#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2022 Eugenio Parodi <ceccopierangiolieugenio AT googlemail DOT com>
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

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter, Terminal256Formatter, TerminalTrueColorFormatter

from TermTk import TTk, TTkK, TTkLog, TTkCfg, TTkTheme, TTkTerm, TTkHelper
from TermTk import TTkString
from TermTk import TTkColor, TTkColorGradient
from TermTk import pyTTkSlot, pyTTkSignal

from TermTk import TTkTextDocument

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
    lastUsed = None
    documents = {}
    kodeTabs = []

    __slots__ = ('_frameOverlay')
    def __init__(self, *args, **kwargs):
        TTkTabWidget.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'KodeTab')
        self._frameOverlay = _KolorFrame('visible',False)
        self._frameOverlay.setBorderColor(TTkColor.fg("#00FFFF")+TTkColor.bg("#000044"))
        self._frameOverlay.setFillColor(TTkColor.bg("#000088", modifier=TTkColorGradient(increment=-2)))
        self.rootLayout().addWidget(self._frameOverlay)
        self.focusChanged.connect(self._kodeFocus)
        self.tabCloseRequested.connect(self._kodeClosedTab)
        KodeTab.lastUsed = self
        KodeTab.kodeTabs.append(self)

    @pyTTkSlot(int)
    def _kodeClosedTab(self, index):
        # Remove the widget and/or all the cascade empty splitters
        if not self._tabWidgets and len(KodeTab.kodeTabs)>1:
            KodeTab.kodeTabs.pop(KodeTab.kodeTabs.index(self))
            if KodeTab.lastUsed == self:
                KodeTab.lastUsed = KodeTab.kodeTabs[0]
            widget = self
            splitter = widget.parentWidget()
            while splitter.count() == 1:
                widget = splitter
                splitter = widget.parentWidget()
            splitter.removeWidget(widget)

    @pyTTkSlot(bool)
    def _kodeFocus(self, focus):
        TTkLog.debug(f"Focus: {focus}")
        if focus:
            KodeTab.lastUsed = self

    def openFile(self, filePath):
        filePath = os.path.realpath(filePath)
        if filePath in KodeTab.documents:
            doc = KodeTab.documents[filePath]
        else:
            with open(filePath, 'r') as f:
                content = f.read()
            txt = highlight(content, PythonLexer(), TerminalTrueColorFormatter(style='rrt'))
            doc = TTkTextDocument(text=txt)
            KodeTab.documents[filePath] = doc

        KodeTab.lastUsed.addTab(te:=TTkTextEdit(document=doc),os.path.basename(filePath))
        KodeTab.lastUsed.setCurrentWidget(te)
        te.setReadOnly(False)

    def addTab(self, widget, label):
        label = TTkString(TTkCfg.theme.fileIcon.getIcon(label),TTkCfg.theme.fileIconColor) + TTkColor.RST + " " + label
        widget.focusChanged.connect(self._kodeFocus)
        super().addTab(widget, label)

    def removeTab(self, index):
        self.widget(index).focusChanged.disconnect(self._kodeFocus)
        return super().removeTab(index)

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
                splitter.insertWidget(index+offset, kt:=KodeTab(border=False, closable=True))
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
        if not tw._tabWidgets and len(KodeTab.kodeTabs)>1:
            KodeTab.kodeTabs.pop(KodeTab.kodeTabs.index(tw))
            if KodeTab.lastUsed == tw:
                KodeTab.lastUsed = KodeTab.kodeTabs[0]
            widget = tw
            splitter = widget.parentWidget()
            while splitter.count() == 1:
                widget = splitter
                splitter = widget.parentWidget()
            splitter.removeWidget(widget)

        return ret
