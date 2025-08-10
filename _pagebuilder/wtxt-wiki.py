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
# --Standard
import argparse
import re
import os
import sys
import inspect

# List to hold information about callable functions
callable_functions = []


def mainFunction(func):
    """Decorator to mark functions as callable and add them to the list."""
    callable_functions.append(func)
    return func


def print_help():
    print("Available callable functions:")
    for func in callable_functions:
        print("- {}: {}".format(func.__name__, func.__doc__))


def print_docstrings():
    print("Docstrings for callable functions:")
    for func in callable_functions:
        print("\nFunction: {}".format(func.__name__))
        docstring = inspect.getdoc(func)
        if docstring:
            encoded_docstring = docstring.encode('utf-8', errors='ignore').decode(sys.stdout.encoding)
            print(encoded_docstring)
        else:
            print("No docstring available.")


def main():
    parser = argparse.ArgumentParser(description="A script to perform various operations on text files.")
    parser.add_argument("--help-functions", action="store_true", help="Print available functions and their docstrings.")
    parser.add_argument("--list-functions", action="store_true", help="List available functions without docstrings.")
    parser.add_argument("--usage", action="store_true", help="Display usage information.")
    parser.add_argument("function", nargs="?", help="The name of the function to execute.")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for the function.")

    args = parser.parse_args()

    if args.usage:
        print("Usage: deleteLibStub.py function [args [args ...]]")
        print("       deleteLibStub.py --help-functions, or help")
        print("       deleteLibStub.py --list-functions, or list")
    elif args.help_functions or args.function == "help":
        print_docstrings()
    elif args.list_functions or args.function == "list":
        print("Available functions:")
        for func in callable_functions:
            print(func.__name__)
    elif args.function:
        function_name = args.function
        for func in callable_functions:
            if func.__name__ == function_name:
                func_args = args.args
                func(*func_args)
                break
        else:
            print("Unknown function: {}".format(function_name))
    else:
        print("No command provided.")


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
<h1 class="grhead1">Main Table Of Contents</h1>
<div id="tableOfContents" class="grid-toc">
    <div class="toc1">
        <h2 class="grhead2"><a href="index.html">1. Introduction</a></h2>
        <h2 class="grhead2"><a href="2-overview.html">2. Overview</a></h2>
        <h2 class="grhead2"><a href="3-basicuse.html">3. xEdit Basic Use</a></h2>
        <h2 class="grhead2"><a href="4-modgroups.html">4. ModGroups</a></h2>
        <h2 class="grhead2"><a href="5-conflict-detection-and-resolution.html">5. Conflict Detection and Resolution</a></h2>
        <h2 class="grhead2"><a href="6-themethod.html">6. The Method</a></h2>
        <h2 class="grhead2"><a href="7-mod-cleaning-and-error-checking.html">7. Mod Cleaning and Error Checking</a></h2>
        <h2 class="grhead2"><a href="8-managing-mod-files.html">8. Managing Mod Files</a></h2>
        <h2 class="grhead2"><a href="9-mod-utilities.html">9. Mod Utilities</a></h2>
    </div>
    <div class="toc2">
        <h2 class="grhead2"><a href="10-fo3edit-faq.html">10. FO3Edit FAQ</a></h2>
        <h2 class="grhead2"><a href="11-appendix.html">11. Appendix</a></h2>
        <h2 class="grhead2"><a href="12-cheat-sheets-and-quick-reference-charts.html">12. Cheat Sheets and Quick Reference Charts</a></h2>
        <h2 class="grhead2"><a href="13-Scripting-Functions.html">13. Scripting Functions</a></h2>
        <h2 class="grhead2"><a href="14-Scripting-Resources.html">14. Scripting Resources</a></h2>
        <h2 class="grhead2"><a href="15-tutorials.html">15. Tutorials</a></h2>
        <h2 class="grhead2"><a href="16-xLODGen.html">16. xLODGen</a></h2>
        <h2 class="grhead2"><a href="17-DynDoLod.html">17. DynDoLod</a></h2>
        <h2 class="grhead2"><a href="18-whatsnew.html">18. xEdit What's New and Version Info</a></h2>
    </div>
</div>
<h1>{{ page.title }}</h1>
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

endMarkdown = """
<p class="empty">&nbsp;</p>
<div>
    <a  href="17-DynDoLod.html" class="drkbtn">&laquo; Previous Page</a>
</div>
"""


# Conversion ------------------------------------------------------------------
@mainFunction
def wtxtToHtml(srcFile, outFile=None, cssDir=''):
    """Generates an html file from a wtxt file. CssDir specifies a directory to search for css files."""
    markdown = False
    if not outFile:
        outFile = '..\\' + os.path.splitext(srcFile)[0] + '.html'
    if srcFile:
        if srcFile == 'index.txt':
            page_number = 1
        elif srcFile == 'whatsnew.md':
            page_number = 18
            markdown = True
            outFile = '..\\18-' + os.path.splitext(srcFile)[0] + '.html'
        else:
            if '-' in srcFile:
                page_number = int(srcFile.split('-', 1)[0])
            else:
                page_number = 0

    # RegEx Independent Routines ------------------------------------
    def anchorReplace(maObject):
        temp = maObject.group(1)
        anchor = reWd.sub('', temp)
        return '<div id="{}"></div>'.format(anchor)

    def boldReplace(maObject):
        state = states['bold'] = not states['bold']
        return ('</B>', '<B>')[state]

    def italicReplace(maObject):
        state = states['italic'] = not states['italic']
        return ('</I>', '<I>')[state]

    def boldItalicReplace(maObject):
        state = states['boldItalic'] = not states['boldItalic']
        return ('</I></B>', '<B><I>')[state]

    def strip_color(text):
        if reTextColor.search(text):
            temp = reTextColor.search(text)
            text_clolor = temp.group(1)
            strip_color = temp.group(0)
            fontClass = ' class="{}"'.format(text_clolor)
            out_text = re.sub(strip_color, '', text)
        else:
            fontClass = ''
            out_text = text
        return fontClass, out_text

    def strip_title(text):
        if reLinkTitle.search(text):
            temp = reLinkTitle.search(text)
            link_title = ' title="{}"'.format(temp.group(1))
            strip_title = temp.group(0)
            out_text = re.sub(strip_title, '', text)
        else:
            link_title = ''
            out_text = text
        return link_title, out_text

    # RegEx ---------------------------------------------------------
    # --Headers
    reHead = re.compile(r'(=+) *(.+)')
    reHeadGreen = re.compile(r'(#+) *(.+)')
    reScriptHead = re.compile(r'(%+) *(.+)')
    headFormat = '<h{} class="header{}" id="{}">{}</h{}>\n'
    headFormatGreen = '<h{} id="{}">{}</h{}>\n'
    headFormatScript = '<h{} class="scriptHeader" id="{}">{}</h{}>\n'
    reHeaderText = re.compile(r'(<h\d {1,3}.+?>)(.*)(<\/h\d>)')
    reHeaderID = re.compile(r'(id="(.+?)")')
    # --List
    reList = re.compile(r'( *)([-!?\.\+\*o]) (.*)')
    # --Misc. text
    reHRule = re.compile(r'^\s*-{4,}\s*$')
    reEmpty = re.compile(r'\s+$')
    reMDash = re.compile(r'-em-')
    rePreBegin = re.compile('<pre>', re.I)
    rePreEnd = re.compile('</pre>', re.I)
    reParagraph = re.compile('<p[\s]+|<p>', re.I)
    reCloseParagraph = re.compile('</p>', re.I)
    # --Bold, Italic, BoldItalic
    reBold = re.compile(r'__')
    reItalic = re.compile(r'~~')
    reBoldItalic = re.compile(r'\*\*')
    states = {'bold': False, 'italic': False, 'boldItalic': False}
    # --Links
    reLink = re.compile(r'\[\[(.+?)\]\]')
    reHttp = re.compile(r' (http:\/\/[\?=_~a-zA-Z0-9\.\/%-]+)| (https:\/\/[\?=_~a-zA-Z0-9\.\/%-]+)')
    reWww = re.compile(r' (www\.[_~a-zA-Z0-9\./%-]+)')
    reWd = re.compile(r'(<[^>]+>|\[[^\]]+\]|\W+)')
    rePar = re.compile(r'^([a-zA-Z\d]|\*\*|~~|__|^\.{1,}|^\*{1,}|^\"{1,})')
    reFullLink = re.compile(r'(:|#|\.[a-zA-Z0-9]{2,4}$)')
    reLinkWithHashtag = re.compile(r'(.*)(#(.*))$')
    # --Tooltip
    reTooltip = re.compile(r'{{tooltip:(.+?)}}')
    # --LinkTitle
    reLinkTitle = re.compile(r'{{title:(.+?)}}')
    # --TextColors
    reTextColor = re.compile(r'{{a:(.+?)}}')
    # --Tags
    reAnchorTag = re.compile('{{nav:(.+?)}}')
    reContentsTag = re.compile(r'\s*{{CONTENTS=?(\d+)}}\s*$')
    reCssTag = re.compile('\s*{{CSS:(.+?)}}\s*$')
    reTitleTag = re.compile(r'^{{PAGETITLE="(.+?)"}}')
    reNoteTag = re.compile(r'^{{note:(.+?)}}')
    reComment = re.compile(r'^\/\*.+\*\/')
    reCTypeBegin = re.compile(r'^\/\*')
    reCTypeEnd = re.compile('\*\/$')
    reSpoilerBegin = re.compile(r'\[\[sb:(.*?)\]\]')
    reSpoilerEnd = re.compile(r'\[\[se:\]\]')
    reBlockquoteBegin = re.compile(r'\[\[bb:(.*?)\]\]')
    reBlockquoteBEnd = re.compile(r'\[\[be:\]\]')
    reNavigationButtonBegin = re.compile(r'{{nbb}}')
    reNavigationButtonEnd = re.compile(r'{{nbe}}')
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', srcFile)
    # --Images
    reImageInline = re.compile(r'{{inline:(.+?)}}')
    reImageOnly = re.compile(r'{{image:(.+?)}}')
    reImageCaption = re.compile(r'{{image-caption:(.+?)}}')
    reImageCaptionUrl = re.compile(r'{{image-cap-url:(.+?)}}')
    # --Exclude from Paragraphs
    # reHtmlBegin = re.compile(r'(^\<font.+?\>)|(^\<code.+?\>)|(^\<a\s{1,3}href.+?\>)|(^\<a\s{1,3}(class=".+?)?href.+?\>)|(^\<img\s{1,3}src.+?\>)|^\u00A9|^\<strong|^\<[bB]\>|(^{% include image)')
    reHtmlNotPar = re.compile(r'\<h\d[>]?|<hr>|{{CONTENTS|class="drkbtn"|<[\/]?div>|<div id=|<div class=|<[\/]?iframe|<[\/]?table|<[\/]?tr>|<[\/]?td>|<[\/]?th>')
    reLiquidOnly = re.compile(r'{% raw %}|{% endraw %}')
    # --Markdown
    rePreMarkdown = re.compile("^```", re.I)
    reOpenCloseMarkdownCode = re.compile(r'`')

    def imageInline(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (max_width, file_name, alt_text) = [chunk.strip() for chunk in image_line.split('|', 2)]
        return '{{% include image-inline.html max-width="{}" file="img/{}" alt="{}" %}}'.format(max_width, file_name, alt_text)

    def imageInclude(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text) = [chunk.strip() for chunk in image_line.split('|', 1)]
        return '{{% include image.html file="img/{}" alt="{}" %}}'.format(file_name, alt_text)

    def imageCaption(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text, caption) = [chunk.strip() for chunk in image_line.split('|', 2)]
        return '{{% include image-caption.html file="img/{}" alt="{}" caption="{}" %}}'.format(file_name, alt_text, caption)

    def imageCaptionUrl(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text, caption, url, urlname) = [chunk.strip() for chunk in image_line.split('|', 4)]
        return '{{% include image-caption-url.html file="img/{}" alt="{}" caption="{}" url="{}" urlname="{}" %}}'.format(file_name, alt_text, caption, url, urlname)

    def spoilerTag(line):
        spoilerID = ''
        spoilerText = ''
        if '|' in line:
            (spoilerID, spoilerText) = [chunk.strip() for chunk in line.split('|', 1)]
        spoilerID = spoilerID.lower()
        return (spoilerID, spoilerText)

    def httpReplace(maObject):
        temp_text = maObject.group(1)
        if inNavigationButtons:
            temp_line = '<a href="{}" class="drkbtn">{}</a>'.format(temp_text, temp_text)
        else:
            temp_line = '<a href="{}">{}</a>'.format(temp_text, temp_text)
        return temp_line

    def wwwReplace(maObject):
        temp_text = line
        if inNavigationButtons:
            temp_line = reWww.sub(r' <a href="http://\1" class="drkbtn">\1</a>', temp_text)
        else:
            temp_line = reWww.sub(r' <a href="http://\1">\1</a>', temp_text)
        return temp_line

    def linkReplace(maObject):
        link_object = maObject.group(1)
        if '|' in link_object:
            (address, text) = [chunk.strip() for chunk in link_object.split('|', 1)]
        else:
            address = text = link_object
        fontClass, text = strip_color(text)
        linkTitle, text = strip_title(text)
        text_only_object = reLinkWithHashtag.search(address)
        if text_only_object:
            group1 = text_only_object.group(1)
            group2 = text_only_object.group(2)
            group3 = text_only_object.group(3)
            # [[#|Implementing The Method]]
            if len(group1) == 0 and len(group3) == 0 and group2 == '#':
                address += reWd.sub('', text)
            # [[#Implementing The Method | Implementing The Method]]
            if len(group1) == 0 and len(group3) > 0 and address.find('#') == 0:
                anchor_out = reWd.sub('', group3)
                address = '#{}'.format(anchor_out)
            # [[5-themethod.html#Implementing The Method | Implementing The Method]]
            if (len(group1) > 0) and (len(group3) > 0) and (address.find('#') > 0) and not (group1.find(':') > 0):
                anchor_out = reWd.sub('', group3)
                address = '{}#{}'.format(group1, anchor_out)
            # [[https://wiki.step-project.com/Guide:Troubleshooting#How_do_I_restore_vanilla_Skyrim.3F | This]]
            if (address.find('#') > 0) and group1.find(':') > 0:
                address = '{}#{}'.format(group1, group3)
        if inNavigationButtons:
            return '<a{} href="{}"{} class="drkbtn">{}</a>'.format(fontClass, address, linkTitle, text)
        else:
            return '<a{} href="{}"{}>{}</a>'.format(fontClass, address, linkTitle, text)

    # --Defaults ----------------------------------------------------------
    level = 1
    spaces = ''
    cssFile = None
    # --Init
    outLines = []
    contents = []  # The list variable for the Table of Contents
    header_match = []  # A duplicate list of the Table of Contents with numbers
    addContents = 0  # When set to 0 headers are not added to the TOC
    inPre = False
    inComment = False
    htmlIDSet = list()
    dupeEntryCount = 1
    blockAuthor = "Unknown"
    inNavigationButtons = False
    inLiquidOnly = False
    openquote = False
    openPreMarkdown = False
    isInPreMarkdown = False
    pageTitle = 'title: Your Content'
    # --Read source file --------------------------------------------------
    ins = open(srcFile, 'r', encoding='utf-8')
    if markdown:
        pageTitle = r"title: xEdit What's New and Version Info"
        firstLine = '<h2 id="Contents">Contents...</h2>\n'
        outLines.append(firstLine)
        secondLine = '{{CONTENTS=5}}\n'
        outLines.append(secondLine)
        addContents = 5
    for line in ins:
        inLiquidOnly = False
        # --CSS
        maCss = reCssTag.match(line)
        if maCss:
            cssFile = maCss.group(1).strip()
            continue
        # --Preformatted Text Block -----------------------------
        maPreBegin = rePreBegin.search(line)
        maPreEnd = rePreEnd.search(line)
        if (inPre and not maPreEnd) or maPreBegin:
            inPre = True
            outLines.append(line)
            continue
        if maPreEnd:
            inPre = False
            outLines.append(line)
            continue
        maPreMarkdown = rePreMarkdown.search(line)
        if maPreMarkdown:
            if not openPreMarkdown:
                line = '<pre>\n'
            if openPreMarkdown:
                line = '</pre>\n'
            outLines.append(line)
            openPreMarkdown = True if not openPreMarkdown else False
            isInPreMarkdown = True if not isInPreMarkdown else False
            continue
        # --Spoiler Tag ---------------------------
        maSpoilerBegin = reSpoilerBegin.match(line)
        maSpoilerEnd = reSpoilerEnd.match(line)
        if maSpoilerBegin:
            spoilerline = maSpoilerBegin.group(1)
            spoilerID, spoilerName = spoilerTag(spoilerline)
            firstLine = '<input type="checkbox" id="{}" />\n'.format(spoilerID)
            outLines.append(firstLine)
            secondLine = '<label for="{}">{}</label>\n'.format(spoilerID, spoilerName)
            outLines.append(secondLine)
            thirdLine = '<div class="main-content">\n'
            outLines.append(thirdLine)
            continue
        if maSpoilerEnd:
            line = '</div>\n'
            outLines.append(line)
            continue
        # --Page Title -------------------------------
        maTitleTag = reTitleTag.match(line)
        if maTitleTag:
            temp = reTitleTag.match(line)
            pageTitle = 'title: {}'.format(temp.group(1))
            continue
        maComment = reComment.match(line)
        maCTypeBegin = reCTypeBegin.match(line)
        maCTypeEnd = reCTypeEnd.search(line)
        if maComment:
            continue
        if inComment or maCTypeBegin or maCTypeEnd or maComment:
            inComment = maCTypeBegin or (inComment and not maCTypeEnd)
            continue
        # --Re Markdown Matches -------------------------------
        maOpenCloseMarkdownCode = reOpenCloseMarkdownCode.search(line)
        if maOpenCloseMarkdownCode:
            builder = ''
            for i in range(len(line)):
                if (line[i] == '`') and not openquote:
                    openquote = True
                    builder = builder + '<code>'
                elif (line[i] == '`') and openquote:
                    openquote = False
                    builder = builder + '</code>'
                elif (line[i] == '<') and openquote:
                    builder = builder + '&lt;'
                elif (line[i] == '>') and openquote:
                    builder = builder + '&gt;'
                else:
                    builder = builder + line[i]
            line = builder
        # --Navigation Buttons ----------------------------------
        maNavigationButtonBegin = reNavigationButtonBegin.match(line)
        maNavigationButtonEnd = reNavigationButtonEnd.match(line)
        if maNavigationButtonBegin:
            line = '<div>\n'
            inNavigationButtons = True
        if maNavigationButtonEnd:
            line = '</div>\n'
            inNavigationButtons = False
        # --Contents ----------------------------------
        maContents = reContentsTag.match(line)
        if maContents:
            temp_var = maContents.group(1)
            addContents = int(temp_var)
        # --Re Note -------------------------------
        maNoteTag = reNoteTag.match(line)
        if maNoteTag:
            note_text = maNoteTag.group(1)
            line = '<p class="note">{}</p>\n'.format(note_text)
        # --Blockquote ---------------------------
        maBlockquoteBegin = reBlockquoteBegin.match(line)
        maBlockquoteEnd = reBlockquoteBEnd.match(line)
        if maBlockquoteBegin:
            firstLine = '<section class="quote">\n'
            outLines.append(firstLine)
            author = maBlockquoteBegin.group(1)
            if len(author) < 1:
                author = blockAuthor
            authorLine = '<p class="attr">{}</p>\n'.format(author)
            outLines.append(authorLine)
            continue
        if maBlockquoteEnd:
            line = '</section>\n'
            outLines.append(line)
            continue
        # --Re Matches -------------------------------
        maHead = reHead.match(line)
        maHeadgreen = reHeadGreen.match(line)
        maScriptHead = reScriptHead.match(line)
        maList = reList.match(line)
        maPar = rePar.match(line)
        maHRule = reHRule.match(line)
        maEmpty = reEmpty.match(line)
        # --Headers
        if maHead:
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
            line = headFormat.format(level, level, anchor, text, level)
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
            line = headFormatGreen.format(level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --Script Header
        elif maScriptHead:
            lead, text = maScriptHead.group(1, 2)
            text = re.sub(' *\%*$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormatScript.format(level, anchor, text, level)
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
            level = int(len(spaces) / 2 + 1)
            line = '{}<p class="list-{}">{}&nbsp; '.format(spaces, level, bullet)
            line = '{}{}</p>\n'.format(line, text)
        # --HRule
        elif maHRule:
            line = '<hr>\n'
        # --Paragraph
        elif maPar:
            line = '<p>' + line.rstrip() + '</p>\n'
        # --Empty line
        elif maEmpty:
            line = spaces + '<p class="empty">&nbsp;</p>\n'
        # --Misc. Text changes --------------------
        line = reMDash.sub('&mdash;', line)
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
        line = reHttp.sub(httpReplace, line)
        # line = reWww.sub(wwwReplace, line)
        # --HTML Font or Code tag first of Line ------------------
        maHtmlNotPar = reHtmlNotPar.search(line)
        maLiquidOnly = reLiquidOnly.search(line)
        if maLiquidOnly:
            if line == '{% raw %}\n' or line == '{% endraw %}\n':
                inLiquidOnly = True
        # --Tooltip
        maTooltip = reTooltip.search(line)
        if maTooltip:
            text_split = maTooltip.group(1)
            text_strip = maTooltip.group(0)
            text_strip = re.sub('\|', '\|', text_strip)
            (tooltip_text, hover_text) = [chunk.strip() for chunk in text_split.split('|', 1)]
            newline = '<div class="tooltip"><p>{}</p>\n'.format(tooltip_text)
            newline = newline + '    <span class="tooltiptext">{}</span>\n'.format(hover_text)
            newline = newline + '</div>\n'
            line = re.sub(text_strip, newline, line)
        if not maHtmlNotPar and not inLiquidOnly:
            maParagraph = reParagraph.search(line)
            maCloseParagraph = reCloseParagraph.search(line)
            if not maParagraph:
                line = '<p>' + line
            if not maCloseParagraph:
                line = re.sub(r'(\n)?$', '', line)
                line = line + '</p>\n'
        # --Save line ------------------
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
    out = open(outFile, 'w', encoding='utf-8', newline='\n')
    out.write('---\nlayout: default\n{}'.format(pageTitle))
    out.write(htmlHead)
    didContents = False
    countlist = [page_number, 0, 0, 0, 0, 0, 0]
    for line in outLines:
        if reContentsTag.match(line):
            if not didContents:
                if markdown:
                    spoilerID = 'spoiler1'
                    spoilerName = 'Contents Spoiler'
                    thirdLine = '<input type="checkbox" id="{}" />\n'.format(spoilerID)
                    out.write(thirdLine)
                    fourthLine = '<label for="{}">{}</label>\n'.format(spoilerID, spoilerName)
                    out.write(fourthLine)
                    fifthLine = '<div class="main-content">\n'
                    out.write(fifthLine)
                if len(contents) > 0:
                    baseLevel = min([level for (level, name, text) in contents])
                else:
                    baseLevel = 1
                previousLevel = baseLevel
                for heading in contents:
                    number = ''
                    level = heading[0] - baseLevel + 1
                    if heading[0] > previousLevel:
                        countlist[level] += 1
                        for i in range(level + 1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] < previousLevel:
                        # Zero out everything not a duplicate
                        for i in range(level + 1, 7):
                            countlist[i] = 0
                        countlist[level] += 1
                        for i in range(level + 1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] == previousLevel:
                        countlist[level] += 1
                        for i in range(level + 1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] <= addContents:
                        out.write('<p class="list-{}">&bull;&nbsp; <a href="#{}">{} {}</a></p>\n'.format(level, heading[1], number, heading[2]))
                        header_match.append((heading[1], number))
                    previousLevel = heading[0]
                didContents = True
                if markdown:
                    firstLine = '</div>\n'
                    out.write(firstLine)
        else:
            maIsHeader = re.search(r'<\/h\d>$', line)
            if maIsHeader:
                header_id_object = reHeaderID.search(line)
                header_id_result = header_id_object.group(2)
                for header_to_match in header_match:
                    if header_to_match[0] == header_id_result:
                        split_line = reHeaderText.split(line)
                        text_replace = '{} - {}'.format(header_to_match[1], split_line[2])
                        line = '{}{}{}\n'.format(split_line[1], text_replace, split_line[3])
                        break
            out.write(line)
    if markdown:
        out.write(endMarkdown)
    out.close()


@mainFunction
def genHtml(fileName, outFile=None, cssDir=''):
    """Generate html from old style etxt file or from new style wtxt file."""
    ext = os.path.splitext(fileName)[1].lower()
    if ext == '.md':
        wtxtToHtml(fileName, outFile=None, cssDir='')
    elif ext == '.txt':
        wtxtToHtml(fileName, outFile=None, cssDir='')
        # docsDir = r'c:\program files\bethesda softworks\morrowind\data files\docs'
        # wtxt.genHtml(fileName, cssDir=docsDir)
    else:
        raise "Unrecognized file type: " + ext


# To run the main function
if __name__ == "__main__":
    main()
