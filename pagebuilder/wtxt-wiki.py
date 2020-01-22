# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Mash.
#
#  Wrye Mash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Mash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Mash copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# =============================================================================
# Imports ----------------------------------------------------------------------
#--Standard
import re
import string
import sys
import types
import os

# ------------------------------------------------------------------------------
class Callables:
    """A singleton set of objects (typically functions or class instances) that
    can be called as functions from the command line.

    Functions are called with their arguments, while object instances are called
    with their method and then their functions. E.g.:
    * bish afunction arg1 arg2 arg3
    * bish anInstance.aMethod arg1 arg2 arg3"""

    # --Ctor
    def __init__(self):
        """Initialization."""
        self.callObjs = {}

    # --Add a callable
    def add(self, callObj, callKey=None):
        """Add a callable object.

        callObj:
            A function or class instance.
        callKey:
            Name by which the object will be accessed from the command line.
            If callKey is not defined, then callObj.__name__ is used."""
        callKey = callKey or callObj.__name__
        self.callObjs[callKey] = callObj

    # --Help
    def printHelp(self, callKey):
        """Print help for specified callKey."""
        print help(self.callObjs[callKey])

    # --Main
    def main(self):
        callObjs = self.callObjs
        # --Call key, tail
        callParts = string.split(sys.argv[1], '.', 1)
        callKey = callParts[0]
        callTail = (len(callParts) > 1 and callParts[1])
        # --Help request?
        if callKey == '-h':
            self.printHelp(self)
            return
        # --Not have key?
        if callKey not in callObjs:
            print "Unknown function/object:", callKey
            return
        # --Callable
        callObj = callObjs[callKey]
        if type(callObj) == types.StringType:
            callObj = eval(callObj)
        if callTail:
            callObj = eval('callObj.' + callTail)
        # --Args
        args = sys.argv[2:]
        # --Keywords?
        keywords = {}
        argDex = 0
        reKeyArg = re.compile(r'^\-(\D\w+)')
        reKeyBool = re.compile(r'^\+(\D\w+)')
        while argDex < len(args):
            arg = args[argDex]
            if reKeyArg.match(arg):
                keyword = reKeyArg.match(arg).group(1)
                value = args[argDex + 1]
                keywords[keyword] = value
                del args[argDex:argDex + 2]
            elif reKeyBool.match(arg):
                keyword = reKeyBool.match(arg).group(1)
                keywords[keyword] = 1
                del args[argDex]
            else:
                argDex = argDex + 1
        # --Apply
        apply(callObj, args, keywords)


# --Callables Singleton
callables = Callables()


def mainFunction(func):
    """A function for adding functions to callables."""
    callables.add(func)
    return func


# ETXT =========================================================================
"""This section of the module provides a single function for converting
wtxt text files to html files."""
etxtHeader = """
<!DOCTYPE html>
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=iso-8859-1">
<TITLE>%s</TITLE>
<STYLE>
H2 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #c6c63c; font-family: "Arial", serif; font-size: 12pt; page-break-before: auto; page-break-after: auto }
H3 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #e6e64c; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
H4 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-size: 10pt; font-style: normal; page-break-before: auto; page-break-after: auto }
H5 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-style: italic; page-break-before: auto; page-break-after: auto }
P { margin-top: 0.01in; margin-bottom: 0.01in; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
P.list-1 { margin-left: 0.15in; text-indent: -0.15in }
P.list-2 { margin-left: 0.3in; text-indent: -0.15in }
P.list-3 { margin-left: 0.45in; text-indent: -0.15in }
P.list-4 { margin-left: 0.6in; text-indent: -0.15in }
P.list-5 { margin-left: 0.75in; text-indent: -0.15in }
P.list-6 { margin-left: 1.00in; text-indent: -0.15in }
.date0 { background-color: #FFAAAA }
.date1 { background-color: #ffc0b3 }
.date2 { background-color: #ffd5bb }
.date3 { background-color: #ffeac4 }
</STYLE>
</HEAD>
<BODY BGCOLOR='#ffffcc'>
"""


@mainFunction
def etxtToHtml(inFileName):
    import time
    """Generates an html file from an etxt file."""
    # --Re's
    reHead2 = re.compile(r'## *([^=]*) ?=*')
    reHead3 = re.compile(r'# *([^=]*) ?=*')
    reHead4 = re.compile(r'@ *(.*)\s+')
    reHead5 = re.compile(r'% *(.*)\s+')
    reList = re.compile(r'( *)([-!?\.\+\*o]) (.*)')
    reBlank = re.compile(r'\s+$')
    reMDash = re.compile(r'--')
    reBoldEsc = re.compile(r'\_')
    reBoldOpen = re.compile(r' _')
    reBoldClose = re.compile(r'(?<!\\)_( |$)')
    reItalicOpen = re.compile(r' ~')
    reItalicClose = re.compile(r'~( |$)')
    reBoldicOpen = re.compile(r' \*')
    reBoldicClose = re.compile(r'\*( |$)')
    reBold = re.compile(r'\*\*([^\*]+)\*\*')
    reItalic = re.compile(r'\*([^\*]+)\*')
    reLink = re.compile(r'\[\[(.*?)\]\]')
    reHttp = re.compile(r' (http://[_~a-zA-Z0-9\./%-]+)')
    reWww = re.compile(r' (www\.[_~a-zA-Z0-9\./%-]+)')
    reDate = re.compile(r'\[([0-9]+/[0-9]+/[0-9]+)\]')
    reContents = re.compile(r'\[CONTENTS=?(\d+)\]\s*$')
    reWd = re.compile(r'\W\d*')
    rePar = re.compile(r'\^(.*)')
    reFullLink = re.compile(r'(:|#|\.[a-zA-Z]{3,4}$)')
    # --Date styling (Replacement function used with reDate.)
    dateNow = time.time()

    def dateReplace(maDate):
        date = time.mktime(
            time.strptime(maDate.group(1), '%m/%d/%Y'))  # [1/25/2005]
        age = int((dateNow - date) / (7 * 24 * 3600))
        if age < 0: age = 0
        if age > 3: age = 3
        return '<span class=date%d>%s</span>' % (age, maDate.group(1))

    def linkReplace(maLink):
        address = text = maLink.group(1).strip()
        if '|' in text:
            (address, text) = [chunk.strip() for chunk in text.split('|', 1)]
        if not reFullLink.search(address):
            address = address + '.html'
        return '<a href="%s">%s</a>' % (address, text)

    # --Defaults
    title = ''
    level = 1
    spaces = ''
    headForm = "<h%d><a name='%s'>%s</a></h%d>\n"
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', inFileName)
    inFile = open(inFileName)
    # --Init
    outLines = []
    contents = []
    addContents = 0
    # --Read through inFile
    for line in inFile.readlines():
        maHead2 = reHead2.match(line)
        maHead3 = reHead3.match(line)
        maHead4 = reHead4.match(line)
        maHead5 = reHead5.match(line)
        maPar = rePar.match(line)
        maList = reList.match(line)
        maBlank = reBlank.match(line)
        maContents = reContents.match(line)
        # --Contents
        if maContents:
            if maContents.group(1):
                addContents = int(maContents.group(1))
            else:
                addContents = 100
        # --Header 2?
        if maHead2:
            text = maHead2.group(1)
            name = reWd.sub('', text)
            line = headForm % (2, name, text, 3)
            if addContents: contents.append((2, name, text))
            # --Title?
            if not title: title = text
        # --Header 3?
        elif maHead3:
            text = maHead3.group(1)
            name = reWd.sub('', text)
            line = headForm % (3, name, text, 3)
            if addContents: contents.append((3, name, text))
            # --Title?
            if not title: title = text
        # --Header 4?
        elif maHead4:
            text = maHead4.group(1)
            name = reWd.sub('', text)
            line = headForm % (4, name, text, 4)
            if addContents: contents.append((4, name, text))
        # --Header 5?
        elif maHead5:
            text = maHead5.group(1)
            name = reWd.sub('', text)
            line = headForm % (5, name, text, 5)
            if addContents: contents.append((5, name, text))
        # --List item
        elif maList:
            spaces = maList.group(1)
            bullet = maList.group(2)
            text = maList.group(3)
            if bullet == '.':
                bullet = '&nbsp;'
            elif bullet == '*':
                bullet = '&bull;'
            level = len(spaces) / 2 + 1
            line = spaces + '<p class=list-' + `level` + '>' + bullet + '&nbsp; '
            line = line + text + '\n'
        # --Paragraph
        elif maPar:
            line = '<p>' + maPar.group(1)
        # --Blank line
        elif maBlank:
            line = spaces + '<p class=list' + `level` + '>&nbsp;</p>'
        # --Misc. Text changes
        line = reMDash.sub('&#150', line)
        line = reMDash.sub('&#150', line)
        # --New bold/italic subs
        line = reBoldOpen.sub(' <B>', line)
        line = reItalicOpen.sub(' <I>', line)
        line = reBoldicOpen.sub(' <I><B>', line)
        line = reBoldClose.sub('</B> ', line)
        line = reBoldEsc.sub('_', line)
        line = reItalicClose.sub('</I> ', line)
        line = reBoldicClose.sub('</B></I> ', line)
        # --Old style bold/italic subs
        line = reBold.sub(r'<B><I>\1</I></B>', line)
        line = reItalic.sub(r'<I>\1</I>', line)
        # --Date
        line = reDate.sub(dateReplace, line)
        # --Local links
        line = reLink.sub(linkReplace, line)
        # --Hyperlink
        line = reHttp.sub(r' <a href="\1">\1</a>', line)
        line = reWww.sub(r' <a href="http://\1">\1</a>', line)
        # --Write it
        # print line
        outLines.append(line)
    inFile.close()
    # --Output file
    outFile = open(inFileRoot + '.html', 'w')
    outFile.write(etxtHeader % (title,))
    didContents = False
    for line in outLines:
        if reContents.match(line):
            if not didContents:
                baseLevel = min([level for (level, name, text) in contents])
                for (level, name, text) in contents:
                    level = level - baseLevel + 1
                    if level <= addContents:
                        outFile.write(
                            '<p class=list-%d>&bull;&nbsp; <a href="#%s">%s</a></p>\n' % (
                            level, name, text))
                didContents = True
        else:
            outFile.write(line)
    outFile.write('</body>\n</html>\n')
    outFile.close()
    # --Done

@mainFunction
def etxtToWtxt(fileName=None):
    """TextMunch: Converts etxt files to wtxt formatting."""
    if fileName:
        ins = open(fileName)
    else:
        import sys
        ins = sys.stdin
    for line in ins:
        line = re.sub(r'^\^ ?', '', line)
        line = re.sub(r'^## ([^=]+) =', r'= \1 ==', line)
        line = re.sub(r'^# ([^=]+) =', r'== \1 ', line)
        line = re.sub(r'^@ ', r'=== ', line)
        line = re.sub(r'^% ', r'==== ', line)
        line = re.sub(r'\[CONTENTS=(\d+)\]', r'{{CONTENTS=\1}}', line)
        line = re.sub(r'~([^ ].+?)~', r'~~\1~~', line)
        line = re.sub(r'_([^ ].+?)_', r'__\1__', line)
        line = re.sub(r'\*([^ ].+?)\*', r'**\1**', line)
        print line,


# Wrye Text ===================================================================
"""This section of the module provides a single function for converting
wtxt text files to html files.

Headings:
= XXXX >> H1 "XXX"
== XXXX >> H2 "XXX"
=== XXXX >> H3 "XXX"
==== XXXX >> H4 "XXX"
Notes:
* These must start at first character of line.
* The XXX text is compressed to form an anchor. E.g == Foo Bar gets anchored as" FooBar".
* If the line has trailing ='s, they are discarded. This is useful for making
  text version of level 1 and 2 headings more readable.

Bullet Lists:
* Level 1
  * Level 2
    * Level 3
Notes:
* These must start at first character of line.
* Recognized bullet characters are: - ! ? . + * o The dot (.) produces an invisible
  bullet, and the * produces a bullet character.

Styles:
  __Text__
  ~~Italic~~
  **BoldItalic**
Notes:
* These can be anywhere on line, and effects can continue across lines.

Links:
 [[file]] produces <a href=file>file</a>
 [[file|text]] produces <a href=file>text</a>

Contents
{{CONTENTS=NN}} Where NN is the desired depth of contents (1 for single level,
2 for two levels, etc.).
"""

htmlHead = """
---
<h1>{{ page.title }}</h1>
<div id="tableOfContents"></div>
<h2>Main Table of Contents</h2>
<ul>
    <li><a href="index.html">1. Introduction</a></li>
    <li><a href="2-overview.html">2. Overview</a></li>
    <li><a href="3-modgroups.html">3. ModGroups</a></li>
    <li><a href="4-conflict-detection-and-resolution.html">4. Conflict Detection and Resolution</a></li>
    <li><a href="5-mod-cleaning-and-error-checking.html">5. Mod Cleaning and Error Checking</a></li>
    <li><a href="6-managing-mod-files.html">6. Managing Mod Files</a></li>
    <li><a href="7-mod-utilities.html">7. Mod Utilities</a></li>
    <li><a href="8-fo3edit-faq.html">8. FO3Edit FAQ</a></li>
    <li><a href="9-appendix.html">9. Appendix</a></li>
    <li><a href="10-cheat-sheets-and-quick-reference-charts.html">10. Cheat Sheets and Quick Reference Charts</a></li>
    <li><a href="11-Scripting-Functions.html">11. Scripting Functions</a></li>
    <li><a href="12-Scripting-Resources.html">12. Scripting Resources</a></li>
    <li><a href="13-tutorials.html">13. Tutorials</a></li>
    <li><a href="whatsnew.html">14. xEdit What's New and Version Info</a></li>
</ul>
"""
defaultCss = """
H1 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #c6c63c; font-family: "Arial", serif; font-size: 12pt; page-break-before: auto; page-break-after: auto }
H2 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #e6e64c; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
H3 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-size: 10pt; font-style: normal; page-break-before: auto; page-break-after: auto }
H4 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-style: italic; page-break-before: auto; page-break-after: auto }
P { margin-top: 0.01in; margin-bottom: 0.01in; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
P.empty {}
P.list-1 { margin-left: 0.15in; text-indent: -0.15in }
P.list-2 { margin-left: 0.3in; text-indent: -0.15in }
P.list-3 { margin-left: 0.45in; text-indent: -0.15in }
P.list-4 { margin-left: 0.6in; text-indent: -0.15in }
P.list-5 { margin-left: 0.75in; text-indent: -0.15in }
P.list-6 { margin-left: 1.00in; text-indent: -0.15in }
PRE { border: 1px solid; background: #FDF5E6; padding: 0.5em; margin-top: 0in; margin-bottom: 0in; margin-left: 0.25in}
CODE { background-color: #FDF5E6;}
BODY { background-color: #ffffcc; }
"""

# Conversion ------------------------------------------------------------------
@mainFunction
def wtxtToHtml(srcFile, outFile=None, cssDir=''):
    """Generates an html file from a wtxt file. CssDir specifies a directory to search for css files."""
    if not outFile:
        import os
        outFile = '..\\' +  os.path.splitext(srcFile)[0] + '.html'
    if srcFile:
        if srcFile == 'index.txt':
            page_number = 1
        else:
            page_number = int(srcFile.split('-', 1)[0])
    # RegEx Independent Routines ------------------------------------
    def anchorReplace(maObject):
        text = maObject.group(1)
        anchor = reWd.sub('', text)
        return '<div id="{}"></div>'.format(text)

    def boldReplace(maObject):
        state = states['bold'] = not states['bold']
        return ('</B>', '<B>')[state]

    def italicReplace(maObject):
        state = states['italic'] = not states['italic']
        return ('</I>', '<I>')[state]

    def boldItalicReplace(maObject):
        state = states['boldItalic'] = not states['boldItalic']
        return ('</I></B>', '<B><I>')[state]

    def check_color(text):
        fontClass = ''
        if '{{a:black}}' in text:
            fontClass = 'class="black"'
        if '{{a:blue}}' in text:
            fontClass = 'class="blue"'
        if '{{a:brown}}' in text:
            fontClass = 'class="brown"'
        if '{{a:cyan}}' in text:
            fontClass = 'class="cyan"'
        if '{{a:dkgray}}' in text:
            fontClass = 'class="dkgray"'
        if '{{a:gray}}' in text:
            fontClass = 'class="gray"'
        if '{{a:green}}' in text:
            fontClass = 'class="green"'
        if '{{a:ltblue}}' in text:
            fontClass = 'class="ltblue"'
        if '{{a:ltgray}}' in text:
            fontClass = 'class="ltgray"'
        if '{{a:ltgreen}}' in text:
            fontClass = 'class="ltgreen"'
        if '{{a:orange}}' in text:
            fontClass = 'class="orange"'
        if '{{a:pink}}' in text:
            fontClass = 'class="pink"'
        if '{{a:purple}}' in text:
            fontClass = 'class="purple"'
        if '{{a:red}}' in text:
            fontClass = 'class="red"'
        if '{{a:tan}}' in text:
            fontClass = 'class="tan"'
        if '{{a:white}}' in text:
            fontClass = 'class="white"'
        if '{{a:yellow}}' in text:
            fontClass = 'class="yellow"'
        return fontClass

    def strip_color(text):
        temp = text
        if '{{a:black}}' in text:
            temp = re.sub('{{a:black}}', '', text)
        if '{{a:blue}}' in text:
            temp = re.sub('{{a:blue}}', '', text)
        if '{{a:brown}}' in text:
            temp = re.sub('{{a:brown}}', '', text)
        if '{{a:cyan}}' in text:
            temp = re.sub('{{a:cyan}}', '', text)
        if '{{a:dkgray}}' in text:
            temp = re.sub('{{a:dkgray}}', '', text)
        if '{{a:gray}}' in text:
            temp = re.sub('{{a:gray}}', '', text)
        if '{{a:green}}' in text:
            temp = re.sub('{{a:green}}', '', text)
        if '{{a:ltblue}}' in text:
            temp = re.sub('{{a:ltblue}}', '', text)
        if '{{a:ltgray}}' in text:
            temp = re.sub('{{a:ltgray}}', '', text)
        if '{{a:ltgreen}}' in text:
            temp = re.sub('{{a:ltgreen}}', '', text)
        if '{{a:orange}}' in text:
            temp = re.sub('{{a:orange}}', '', text)
        if '{{a:pink}}' in text:
            temp = re.sub('{{a:pink}}', '', text)
        if '{{a:purple}}' in text:
            temp = re.sub('{{a:purple}}', '', text)
        if '{{a:red}}' in text:
            temp = re.sub('{{a:red}}', '', text)
        if '{{a:tan}}' in text:
            temp = re.sub('{{a:tan}}', '', text)
        if '{{a:white}}' in text:
            temp = re.sub('{{a:white}}', '', text)
        if '{{a:yellow}}' in text:
            temp = re.sub('{{a:yellow}}', '', text)
        return temp

    # RegEx ---------------------------------------------------------
    # --Headers
    reHead = re.compile(r'(=+) *(.+)')
    reHeadGreen = re.compile(r'(#+) *(.+)')
    headFormat = '<h%d class="header%d" id="%s">%s</h%d>\n'
    headFormatGreen = '<h%d id="%s">%s</h%d>\n'
    # --List
    reList = re.compile(r'( *)([-!?\.\+\*o]) (.*)')
    # --Misc. text
    reHRule = re.compile(r'^\s*-{4,}\s*$')
    reEmpty = re.compile(r'\s+$')
    reMDash = re.compile(r'--')
    rePreBegin = re.compile('<pre>', re.I)
    rePreEnd = re.compile('</pre>', re.I)
    reParagraph = re.compile('<p ?(>)?>', re.I)
    reCloseParagraph = re.compile('</p>', re.I)
    # --Bold, Italic, BoldItalic
    reBold = re.compile(r'__')
    reItalic = re.compile(r'~~')
    reBoldItalic = re.compile(r'\*\*')
    states = {'bold': False, 'italic': False, 'boldItalic': False}
    # --Links
    reLink = re.compile(r'\[\[(.*?)\]\]')
    reHttp = re.compile(r' (http:\/\/[\?=_~a-zA-Z0-9\.\/%-]+)')
    reWww = re.compile(r' (www\.[\?=_~a-zA-Z0-9\./%-]+)')
    reWd = re.compile(r'(<[^>]+>|\[[^\]]+\]|\W+)')
    rePar = re.compile(r'^([a-zA-Z]|\*\*|~~|__)')
    reFullLink = re.compile(r'(:|#|\.[a-zA-Z0-9]{2,4}(\/)?$)')
    # --Tags
    pageTitle = 'title: Your Content'
    reAnchorTag = re.compile('{{nav:(.+?)}}')
    reContentsTag = re.compile(r'\s*{{CONTENTS=?(\d+)}}\s*$')
    reCssTag = re.compile('\s*{{CSS:(.+?)}}\s*$')
    reTitleTag = re.compile(r'({{PAGETITLE=")(.*)("}})$')
    reComment = re.compile(r'^\/\*.+\*\/')
    reCTypeBegin = re.compile(r'^\/\*')
    reCTypeEnd = re.compile('\*\/$')
    reSpoilerBegin = re.compile(r'\[\[sb:(.*?)\]\]')
    reSpoilerEnd = re.compile(r'\[\[se:\]\]')
    reBlockquoteBegin = re.compile(r'\[\[bb:(.*?)\]\]')
    reBlockquoteBEnd = re.compile(r'\[\[be:\]\]')
    reHtmlBegin = re.compile(r'(^\<font.+?\>)|(^\<code.+?\>)|(^\<a\s{1,3}href.+?\>)|(^\<img\s{1,3}src.+?\>)|^\u00A9|^\<strong|^\<[bB]\>|(^{% include image-inline.html)')
    reNavigationButtonBegin = re.compile(r'{{nbb}}')
    reNavigationButtonEnd = re.compile(r'{{nbe}}')
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', srcFile)
    # --TextColors
    reTextColor = re.compile(r'({{a:(.+?)}})')
    # --Images
    reImageInline = re.compile(r'{{inline:.+?}}')
    reImageOnly = re.compile(r'{{image:.+?}}')
    reImageCaption = re.compile(r'({{image-caption:(.+?)}})')
    reImageCaptionUrl = re.compile(r'({{image-cap-url:(.+?)}})')

    def imageInline(maObject):
        var1 = maObject.group(0).strip()
        var1 = re.sub(r'{{inline:(.+?)}}', r'\1', var1)
        var1 = re.sub(r'\n', r'', var1)
        if '|' in var1:
            (max_width, file_name, alt_text) = [chunk.strip() for chunk in var1.split('|', 2)]
        return '{{% include image-inline.html max-width="{}" file="img/{}" alt="{}" %}}\n'.format(max_width, file_name, alt_text)

    def imageInclude(maObject):
        var1 = maObject.group(0).strip()
        var1 = re.sub(r'{{image:(.+?)}}', r'\1', var1)
        var1 = re.sub(r'\n', r'', var1)
        if '|' in var1:
            (file_name, alt_text) = [chunk.strip() for chunk in var1.split('|', 1)]
        return '{{% include image.html file="img/{}" alt="{}" %}}\n'.format(file_name, alt_text)

    def imageCaption(maObject):
        var1 = maObject.group(0).strip()
        var1 = re.sub(r'{{image-caption:(.+?)}}', r'\1', var1)
        var1 = re.sub(r'\n', r'', var1)
        if '|' in var1:
            (file_name, alt_text, caption) = [chunk.strip() for chunk in var1.split('|', 2)]
        return '{{% include image-caption.html file="img/{}" alt="{}" caption="{}" %}}\n'.format(file_name, alt_text, caption)

    def imageCaptionUrl(maObject):
        var1 = maObject.group(0).strip()
        var1 = re.sub(r'{{image-cap-url:(.+?)}}', r'\1', var1)
        var1 = re.sub(r'\n', r'', var1)
        if '|' in var1:
            (file_name, alt_text, caption, url, urlname) = [chunk.strip() for chunk in var1.split('|', 4)]
        return '{{% include image-caption-url.html file="img/{}" alt="{}" caption="{}" url="{}" urlname="{}" %}}\n'.format(file_name, alt_text, caption, url, urlname)

    def spoilerTag(line):
        spoilerID = ''
        spoilerText = ''
        if '|' in line:
            (spoilerID, spoilerText) = [chunk.strip() for chunk in line.split('|', 1)]
        spoilerID = re.sub('\[\[', '', spoilerID)
        spoilerText = re.sub('\]\]', '', spoilerText)
        return (spoilerID, spoilerText)

    def httpReplace(line):
        temp_text = line
        if inNavigationButtons:
            temp_line = reHttp.sub(r' <a href="\1" class="drkbtn">\1</a>', temp_text)
        else:
            temp_line = reHttp.sub(r' <a href="\1">\1</a>', temp_text)
        return temp_line

    def wwwReplace(line):
        temp_text = line
        if inNavigationButtons:
            temp_line = reWww.sub(r' <a href="http://\1" class="drkbtn">\1</a>', temp_text)
        else:
            temp_line = reWww.sub(r' <a href="http://\1">\1</a>', temp_text)
        return temp_line

    def linkReplace(maObject):
        address = text = maObject.group(1).strip()
        skipStrip = False
        if '|' in text:
            (address, text) = [chunk.strip() for chunk in text.split('|', 1)]
            if address == '#':
                fontClass = check_color(text)
                text = strip_color(text)
                address += reWd.sub('', text)
                skipStrip = True
        if not reFullLink.search(address):
            address = address + '.html'
        if not skipStrip:
            fontClass = check_color(text)
            text = strip_color(text)
        if inNavigationButtons:
            return '<a {} href="{}" class="drkbtn">{}</a>'.format(fontClass, address, text)
        else:
            return '<a {} href="{}">{}</a>'.format(fontClass, address, text)

    # --Defaults ----------------------------------------------------------
    level = 1
    spaces = ''
    cssFile = None
    # --Init
    outLines = []
    contents = [] # The list variable for the Table of Contents
    header_match = [] # A duplicate list of the Table of Contents with numbers
    addContents = 0 # When set to 0 headers are not added to the TOC
    inPre = False
    inComment = False
    isInParagraph = False
    htmlIDSet = list()
    dupeEntryCount = 1
    blockAuthor = "Unknown"
    inNavigationButtons = False
    # --Read source file --------------------------------------------------
    ins = file(srcFile)
    for line in ins:
        isInParagraph, wasInParagraph = False, isInParagraph
        # --Preformatted? -----------------------------
        maPreBegin = rePreBegin.search(line)
        maPreEnd = rePreEnd.search(line)
        if inPre or maPreBegin or maPreEnd:
            inPre = maPreBegin or (inPre and not maPreEnd)
            outLines.append(line)
            continue
        maTitleTag = reTitleTag.match(line)
        maCTypeBegin = reCTypeBegin.match(line)
        maCTypeEnd = reCTypeEnd.search(line)
        maComment = reComment.match(line)
        if maComment:
            continue
        if inComment or maCTypeBegin or maCTypeEnd or maComment:
            inComment = maCTypeBegin or (inComment and not maCTypeEnd)
            continue
        if maTitleTag:
            pageTitle = re.sub(r'({{PAGETITLE=")(.*)("}})(\n)?', r'title: \2', line)
        # --Re Matches -------------------------------
        maContents = reContentsTag.match(line)
        maCss = reCssTag.match(line)
        maHead = reHead.match(line)
        maHeadgreen = reHeadGreen.match(line)
        maList = reList.match(line)
        maPar = rePar.match(line)
        maHRule = reHRule.match(line)
        maEmpty = reEmpty.match(line)
        maSpoilerBegin = reSpoilerBegin.match(line)
        maSpoilerEnd = reSpoilerEnd.match(line)
        maBlockquoteBegin = reBlockquoteBegin.match(line)
        maBlockquoteEnd = reBlockquoteBEnd.match(line)
        maNavigationButtonBegin = reNavigationButtonBegin.match(line)
        maNavigationButtonEnd = reNavigationButtonEnd.match(line)
        # --Navigation Buttons ----------------------------------
        if maNavigationButtonBegin:
            line = '<div>\n'
            inNavigationButtons = True
        if maNavigationButtonEnd:
            line = '</div>\n'
            inNavigationButtons = False
        # --Contents ----------------------------------
        if maContents:
            if maContents.group(1):
                addContents = int(maContents.group(1))
            else:
                addContents = 100
            inPar = False
        # --CSS
        elif maCss:
            cssFile = maCss.group(1).strip()
            continue
        # --Headers
        elif maHead:
            lead, text = maHead.group(1, 2)
            text = re.sub(' *=*$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormat % (level, level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --Green Header
        elif maHeadgreen:
            lead, text = maHeadgreen.group(1, 2)
            text = re.sub(' *\#*$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormatGreen % (level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --List item
        elif maList:
            spaces = maList.group(1)
            bullet = maList.group(2)
            text = maList.group(3)
            if bullet == '.':
                bullet = '&nbsp;'
            elif bullet == '*':
                bullet = '&bull;'
            level = len(spaces) / 2 + 1
            line = '{}<p class="list-{}">{}&nbsp; '.format(spaces, level, bullet)
            line = '{}{}</p>\n'.format(line, text)
        # --HRule
        elif maHRule:
            line = '<hr>\n'
        # --Paragraph
        elif maPar:
            if not wasInParagraph: line = '<p>' + line.rstrip() + '</p>\n'
            isInParagraph = True
        # --Empty line
        elif maEmpty:
            line = spaces + '<p class="empty">&nbsp;</p>\n'
        # --Spoiler Tag ---------------------------
        elif maSpoilerBegin:
            line = re.sub('sb:', '', line)
            spoilerID, spoilerName = spoilerTag(line)
            spoilerID = spoilerID.lower()
            firstLine = '<input type="checkbox" id="{}" />\n'.format(spoilerID)
            outLines.append(firstLine)
            secondLine = '<label for="{}">{}</label>\n'.format(spoilerID, spoilerName)
            outLines.append(secondLine)
            thirdLine = '<div class="spoiler">\n'
            outLines.append(thirdLine)
            continue
        elif maSpoilerEnd:
            line = '</div>\n'
        # --Blockquote ---------------------------
        elif maBlockquoteBegin:
            firstLine = '<section class="quote">\n'
            outLines.append(firstLine)
            author = re.sub(r'\[\[bb:(.*?)\]\]\n', r'\1', line)
            if len(author) < 1:
                author = blockAuthor
            authorLine = '<p class="attr">{}</p>\n'.format(author)
            outLines.append(authorLine)
            continue
        elif maBlockquoteEnd:
            line = '</section>\n'
        # --Misc. Text changes --------------------
        line = reMDash.sub('&#150', line)
        line = reMDash.sub('&#150', line)
        # --Bold/Italic subs
        line = reBold.sub(boldReplace, line)
        line = reItalic.sub(italicReplace, line)
        line = reBoldItalic.sub(boldItalicReplace, line)
        # --Wtxt Tags
        line = reAnchorTag.sub(anchorReplace, line)
        # --Images
        line = reImageInline.sub(imageInline, line)
        line = reImageOnly.sub(imageInclude, line)
        line = reImageCaption.sub(imageCaption, line)
        line = reImageCaptionUrl.sub(imageCaptionUrl, line)
        # --Hyperlinks
        line = reLink.sub(linkReplace, line)
        line = httpReplace(line)
        line = wwwReplace(line)
        # --HTML Font or Code tag first of Line ------------------
        maHtmlBegin = reHtmlBegin.match(line)
        if maHtmlBegin:
            maParagraph = reParagraph.match(line)
            maCloseParagraph = reCloseParagraph.search(line)
            if not maParagraph:
                line = '<p>' + line
            if not maCloseParagraph:
                line = re.sub(r'(\n)?$', '', line)
                line = line + '</p>\n'
        # --Save line ------------------
        # print line,
        if maTitleTag:
            pass
        else:
            outLines.append(line)
    ins.close()
    # --Get Css -----------------------------------------------------------
    if not cssFile:
        css = defaultCss
    else:
        cssBaseName = os.path.basename(cssFile)  # --Dir spec not allowed.
        cssSrcFile = os.path.join(os.path.dirname(srcFile), cssBaseName)
        cssDirFile = os.path.join(cssDir, cssBaseName)
        if os.path.splitext(cssBaseName)[-1].lower() != '.css':
            raise "Invalid Css file: " + cssFile
        elif os.path.exists(cssSrcFile):
            cssFile = cssSrcFile
        elif os.path.exists(cssDirFile):
            cssFile = cssDirFile
        else:
            raise 'Css file not found: ' + cssFile
        css = ''.join(open(cssFile).readlines())
        if '<' in css:
            raise "Non css tag in css file: " + cssFile
    # --Write Output ------------------------------------------------------
    out = file(outFile, 'w')
    # out.write(htmlHead % (title, css))
    out.write('---\nlayout: default\n{}'.format(pageTitle))
    out.write(htmlHead)
    didContents = False
    countlist = [page_number, 0, 0, 0, 0, 0, 0]
    for line in outLines:
        if reContentsTag.match(line):
            if not didContents:
                baseLevel = min([level for (level, name, text) in contents])
                previousLevel = baseLevel
                for heading in contents:
                    number = ''
                    level = heading[0] - baseLevel + 1
                    if heading[0] > previousLevel:
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] < previousLevel:
                        # Zero out everything not a duplicate
                        for i in range(level+1, 7):
                            countlist[i] = 0
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] == previousLevel:
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] <= addContents:
                        out.write('<p class="list-{}">&bull;&nbsp; <a href="#{}">{} {}</a></p>\n'.format(level, heading[1], number, heading[2]))
                        header_match.append((heading[1], number, heading[2]))
                    previousLevel = heading[0]
                didContents = True
        else:
            maIsHeader = re.search(r'<\/h\d>$', line)
            if maIsHeader:
                text_search = re.sub(r'^<h.*id="(.*)">.*<\/h\d>', r'\1', line).rstrip('\n')
                for header_to_match in header_match:
                    if header_to_match[0] == text_search:
                        text_replace = '{} - {}'.format(header_to_match[1], header_to_match[2])
                        line = re.sub(r'(<h.*>)(.*)(<\/h\d>)', r'\g<1>'+text_replace+'\g<3>', line)
                        break
            out.write(line)
    # out.write('</div>\n')
    out.close()
	

@mainFunction
def genHtml(fileName, outFile=None, cssDir=''):
    """Generate html from old style etxt file or from new style wtxt file."""
    ext = os.path.splitext(fileName)[1].lower()
    if ext == '.etxt':
        etxtToHtml(fileName)
    elif ext == '.txt':
        wtxtToHtml(fileName, outFile=None, cssDir='')
        # docsDir = r'c:\program files\bethesda softworks\morrowind\data files\docs'
        # wtxt.genHtml(fileName, cssDir=docsDir)
    else:
        raise "Unrecognized file type: " + ext

if __name__ == '__main__':
        callables.main()
