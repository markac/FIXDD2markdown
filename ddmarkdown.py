from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import logging
import re
import os

logger = logging.getLogger('MARKDOWN')


class DDMarkdownBlockProcessor(BlockProcessor):
    RE = re.compile(r'''
    (?::fix)\s*                     # ::fix
    (?P<msgType>[a-zA-Z0-9]+)\s*    # FIX messageType (tag 35)
    (?P<path>[^\s]*)\s*             # Path to FIX data dictionary
    ''', re.VERBOSE)

    def test(self, parent, block):
        return self.RE.search(block)

    def run(self, parent, blocks):
        block = blocks.pop(0)

        # Parse configuration params
        m = self.RE.search(block)
        msgtype = m.group('msgType')
        dd_path = m.group('path')

        logging.info(os.getcwd())

        root = etree.parse(dd_path).getroot()
        message = root.find('messages/message[@msgtype=\'' + msgtype + '\']')

        table = etree.SubElement(parent, "table")
        thead = etree.SubElement(table, "thead")
        tbody = etree.SubElement(table, "tbody")
        self.createFullWidthRow(thead, "fix-table-msg-header",
          "&lt;" + message.get('name') + "&gt; MsgType (35)=" + msgtype,
          "th")
        self.createRow(thead, "fix-field-header", "th", "Tag", "Field Name", "Type", "Req")

        self.createFullWidthRow(tbody, "fix-message-header", "&lt;Standard Header&gt;")

        self.handleNode(tbody, root, message, "")

        self.createFullWidthRow(tbody, "fix-message-footer", "&lt;Standard Footer&gt;")

        # self.parser.parseChunk(parent, """
        # | title 1   | title 2   |
        # |-----------|-----------|
        # | content 1 | content 2 |
        #
        # **blah**
        # """)

    def handleNode(self, parent, root, node, indent):
        for child in node:
            if child.tag == 'field':
                fieldName = child.get('name')
                self.handleField(parent, fieldName, child.get('required'), root, indent)
            elif child.tag == 'component':
                componentName = child.get('name')
                component = root.find('components/component[@name=\'' + componentName + '\']')
                self.createComponentRow(parent, "fix-component-start", indent + " Start component &lt;" + componentName + "&gt;", child.get('required'))
                self.handleNode(parent, root, component, indent)
                self.createFullWidthRow(parent, "fix-component-end", indent + " End component &lt;" + componentName + "&gt;")
            elif child.tag == 'group':
                groupName = child.get('name')
                increasedIndent = indent + "&gt;"
                self.handleField(parent, groupName, child.get('required'), root, increasedIndent)
                self.handleNode(parent, root, child, increasedIndent)


    def handleField(self, parent, fieldName, required, root, indent):
        field = root.find('fields/field[@name=\'' + fieldName + '\']')
        self.createRow(parent, "fixField", "td",
            indent + " " + field.get('number'),
            field.get('name'),
            field.get('type'),
            required )


    def createComponentRow(self, parent, rowClass, componentName, required):
        tr = self.createRow(parent, rowClass, "td", componentName, required)
        list(tr)[0].set("colspan", "3")
        return tr

    def createFullWidthRow(self, parent, rowClass, text, tagType="td"):
        tr = self.createRow(parent, rowClass)
        td = etree.SubElement(tr, tagType)
        td.set("colspan", "4")
        td.text = text
        return tr


    def createRow(self, parent, rowClass, tagType="td", *cellText):
        row = etree.SubElement(parent, "tr")
        row.set("class", rowClass)

        for text in cellText:
            self.createCell(row, text, tagType)

        return row

    def createCell(self, parent, text, tagType="td"):
        cell = etree.SubElement(parent, tagType)
        cell.text = text
        return cell


class DDMarkdownExtension(Extension):
    """ Add FIX message definititions to markdown documents """

    def extendMarkdown(self, md):
        """ Add DDMarkdownBlockProcessor to Markdown instance. """
        blockprocessor = DDMarkdownBlockProcessor(md.parser)
        blockprocessor.config = self.getConfigs()
        md.parser.blockprocessors.add('dd', blockprocessor, '>code')


def makeExtension(**kwargs):   # pragma: no cover
    return DDMarkdownExtension(**kwargs)
