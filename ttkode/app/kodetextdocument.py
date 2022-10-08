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

from threading import Lock

from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import guess_lexer, guess_lexer_for_filename, special
from pygments.formatters import TerminalFormatter, Terminal256Formatter, TerminalTrueColorFormatter

from TermTk import TTk, TTkK, TTkLog, TTkCfg, TTkTheme, TTkTerm, TTkHelper, TTkTimer
from TermTk import TTkString
from TermTk import TTkColor, TTkColorGradient
from TermTk import pyTTkSlot, pyTTkSignal

from TermTk import TTkTextDocument

class KodeTextDocument(TTkTextDocument):
    __slots__ = ('_filePath', '_timerRefresh', 'kodeHighlightUpdate', '_kodeDocMutex', '_lexer')
    def __init__(self, *args, **kwargs):
        self.kodeHighlightUpdate = pyTTkSignal()
        self._kodeDocMutex = Lock()
        self._lexer = None
        super().__init__(*args, **kwargs)
        self._filePath = kwargs.get('filePath',"")
        self._timerRefresh = TTkTimer()
        self._timerRefresh.timeout.connect(self._refreshEvent)
        self._timerRefresh.start(0.3)
        self.contentsChanged.connect(lambda : self._timerRefresh.start(0.5))

    @pyTTkSlot()
    def _refreshEvent(self):
        self._kodeDocMutex.acquire()
        tsl = self._dataLines
        rawl = [l._text for l in tsl]
        rawt = '\n'.join(rawl)
        if not self._lexer:
            # self._lexer = guess_lexer(rawt)
            try:
                self._lexer = guess_lexer_for_filename(self._filePath, rawt)
            except ClassNotFound:
                self._lexer = special.TextLexer()
        TTkLog.debug(f"Refresh {self._lexer.name}")
        # tsl1 = [TTkString()]
        # highlight(rawt, PythonLexer(), EuFormatter(tsl1))
        txt = highlight(rawt, self._lexer, TerminalTrueColorFormatter(style='rrt'))
        tsl1 = [TTkString(t) for t in txt.split('\n')]
        self._dataLines = tsl1 + tsl[len(tsl1):]
        self._kodeDocMutex.release()
        self.kodeHighlightUpdate.emit()

    def getLock(self):
        return self._kodeDocMutex

    def filePath(self):
        return self._filePath