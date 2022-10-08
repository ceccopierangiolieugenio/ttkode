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

from pygments.formatter import Formatter
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace

from TermTk import TTkString, TTkColor

#: Map token types to a tuple of color values for light and dark
#: backgrounds.
TTKODE_COLORS = {
    Token:              TTkColor.RST, # ('',            ''),

    Whitespace:         TTkColor.fg('#888888') , # ('gray',   'brightblack'),
    Comment:            TTkColor.fg('#888888') , # ('gray',   'brightblack'),
    Comment.Preproc:    TTkColor.fg('#00FFFF') , # ('cyan',        'brightcyan'),
    Keyword:            TTkColor.fg('#0000FF') , # ('blue',    'brightblue'),
    Keyword.Type:       TTkColor.fg('#00FFFF') , # ('cyan',        'brightcyan'),
    Operator.Word:      TTkColor.fg('#FF8800') , # ('magenta',      'brightmagenta'),
    Name.Builtin:       TTkColor.fg('#00FFFF') , # ('cyan',        'brightcyan'),
    Name.Function:      TTkColor.fg('#00FF00') , # ('green',   'brightgreen'),
    Name.Namespace:     TTkColor.fg('#00FFFF') , # ('_cyan_',      '_brightcyan_'),
    Name.Class:         TTkColor.fg('#00FF00') , # ('_green_', '_brightgreen_'),
    Name.Exception:     TTkColor.fg('#00FFFF') , # ('cyan',        'brightcyan'),
    Name.Decorator:     TTkColor.fg('#888888') , # ('brightblack',    'gray'),
    Name.Variable:      TTkColor.fg('#888888') , # ('red',     'brightred'),
    Name.Constant:      TTkColor.fg('#888888') , # ('red',     'brightred'),
    Name.Attribute:     TTkColor.fg('#00FFFF') , # ('cyan',        'brightcyan'),
    Name.Tag:           TTkColor.fg('#0000FF') , # ('brightblue',        'brightblue'),
    String:             TTkColor.fg('#FFFF00') , # ('yellow',       'yellow'),
    Number:             TTkColor.fg('#0000FF') , # ('blue',    'brightblue'),

    Generic.Deleted:    TTkColor.fg('#FF0000') , # ('brightred',        'brightred'),
    Generic.Inserted:   TTkColor.fg('#00FF00') , # ('green',  'brightgreen'),
    Generic.Heading:    TTkColor.fg('#888888') , # ('**',         '**'),
    Generic.Subheading: TTkColor.fg('#FF8800') , # ('*magenta*',   '*brightmagenta*'),
    Generic.Prompt:     TTkColor.fg('#888888') , # ('**',         '**'),
    Generic.Error:      TTkColor.fg('#FF0000') , # ('brightred',        'brightred'),

    Error:              TTkColor.fg('#FF0000') , # ('_brightred_',      '_brightred_'),
}

class EuFormatter(Formatter):
    __slots__ = ('_dl')
    def __init__(self, dl):
        self._dl = dl
        super().__init__()
    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            # TTkLog.debug (f"{ttype=}")
            # TTkLog.debug (f"{value=}")
            color = TTKODE_COLORS.get(ttype, TTkColor.RST)
            if value == '\n':
                self._dl.append(TTkString())
            else:
                values = value.split('\n')
                self._dl[-1] += TTkString(values[-1],color)
                self._dl += [TTkString(t,color) for t in values[1:]]
            # self._dl += [TTkString(t) for t in value.split('\n')]