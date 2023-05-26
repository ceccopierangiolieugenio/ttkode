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

from TermTk import TTkK, TTkLog, TTkCfg, TTkTheme, TTkTerm, TTkHelper
from TermTk import TTkString
from TermTk import TTkColor, TTkColorGradient
from TermTk import pyTTkSlot, pyTTkSignal

from TermTk import TTkFrame, TTkButton
from TermTk import TTkTabWidget
from TermTk import TTkTextEdit

from TermTk import TTkSplitter

from .cfg  import *
from .about import *
from .kodetextedit import KodeTextEditView
from .kodetextdocument import KodeTextDocument

class _KolorFrame(TTkFrame):
    __slots__ = ('_fillColor')
    def __init__(self, *args, **kwargs):
        TTkFrame.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , '_KolorFrame')
        self._fillColor = kwargs.get('fillColor', TTkColor.RST)

    def setFillColor(self, color):
        self._fillColor = color

    def paintEvent(self, canvas):
        w,h = self.size()
        for y in range(h):
            canvas.drawText(pos=(0,y),text='',width=w,color=self._fillColor)
        return super().paintEvent(canvas)

class KodeTab(TTkTabWidget):
    lastUsed = None
    documents = {}
    kodeTabs = []

    __slots__ = ('_frameOverlay')
    def __init__(self, *args, **kwargs):
        super().__init__(args, **kwargs)
        self._frameOverlay = _KolorFrame('visible',False)
        self._frameOverlay.setBorderColor(TTkColor.fg("#00FFFF")+TTkColor.bg("#000044"))
        self._frameOverlay.setFillColor(TTkColor.bg("#000088", modifier=TTkColorGradient(increment=-2)))
        self.rootLayout().addWidget(self._frameOverlay)
        self.focusChanged.connect(self._kodeFocus)
        self.tabCloseRequested.disconnect(self.removeTab)
        #self.tabCloseRequested.connect(self._kodeClosedTab)
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
            doc = KodeTab.documents[filePath]['doc']
        else:
            with open(filePath, 'r') as f:
                content = f.read()
            doc = KodeTextDocument(text=content, filePath=filePath)
            KodeTab.documents[filePath] = {'doc':doc,'tabs':[]}
        tview = KodeTextEditView(document=doc, readOnly=False)
        tedit = TTkTextEdit(textEditView=tview, lineNumber=True)
        doc.kodeHighlightUpdate.connect(tedit.update)
        label = TTkString(TTkCfg.theme.fileIcon.getIcon(filePath),TTkCfg.theme.fileIconColor) + TTkColor.RST + " " + os.path.basename(filePath)

        KodeTab.lastUsed.addTab(tedit, label)
        KodeTab.lastUsed.setCurrentWidget(tedit)

    def addTab(self, widget, label, data=None):
        widget.focusChanged.connect(self._kodeFocus)
        filePath = widget.document().filePath()
        KodeTab.documents[filePath]['tabs'].append(widget)
        super().addTab(widget, label, data)

    def removeTab(self, index):
        TTkLog.debug(f"Removing: {index} -> {self.widget(index)}")
        widget = self.widget(index)
        filePath = widget.document().filePath()
        TTkLog.debug(KodeTab.documents[filePath]['tabs'])
        KodeTab.documents[filePath]['tabs'].remove(widget)
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
            KodeTab.lastUsed = self
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
                kt.addTab(widget,tb.text())

            if x<w//4:
                _processDrop(index, TTkK.HORIZONTAL, 0)
            elif x>w*3//4:
                _processDrop(index, TTkK.HORIZONTAL, 1)
            elif y<h//4:
                _processDrop(index, TTkK.VERTICAL, 0)
            elif y>h*3//4:
                _processDrop(index, TTkK.VERTICAL, 1)
            else:
                KodeTab.lastUsed = self
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
