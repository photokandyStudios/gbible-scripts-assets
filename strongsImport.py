#!/usr/bin/python

from xml.dom.minidom import parse
import sqlite3

sourceXML = '/Users/kerrishotts/SkyDrive/gib/strongsgreek.xml'
targetDB = '/Users/kerrishotts/SkyDrive/gib/bibleContent'

print " Strong's Greek Dictionary Importer v 1.1 "
print "=========================================="
print ""
print "The Strong's Dictionary comes from https://github.com/morphgnt/strongs-dictionary-xml/downloads"
print ""
print " Source: ", sourceXML
print " Target: ", targetDB
print ""

print "... Opening XML and Parsing..."
dom = parse(sourceXML)

print "... Opening target database..."
dbConn = sqlite3.connect(targetDB)

print "... ... Dropping Existing Table..."
dbConn.execute("DROP TABLE [strongsgr]")

print "... ... Recreating Table..."
dbConn.execute("create table [strongsgr] ([key] VARCHAR (10) PRIMARY KEY NOT NULL, [lemma] VARCHAR (512), [pronunciation] VARCHAR (512), [definition] VARCHAR (4096))")

strongsLookup = {}


def strongsref(node):
    #
    # returns a strong's reference, like so:
    #    G25 (agapo)
    #
    prefix = ""
    theValueToPrint = ""
    if node.getAttribute('language') == 'GREEK':
        prefix += 'G'
    else:
        prefix += 'H'
    theIndex = node.getAttribute('strongs').strip()
    theValueToPrint = prefix + theIndex
    if node.getAttribute('language') == 'GREEK':
        theValueToPrint += ' (' + strongsLookup[node.getAttribute('strongs').strip()] + ') '
    return theValueToPrint


def renderNode(node):
    #
    # prints a node. The node may contain <strongs/> references,
    # <greek/> text, and simple text.
    #
    theValueToPrint = ''
    for eachNode in node.childNodes:
        if eachNode.nodeType == 3:
            theValueToPrint += eachNode.nodeValue.strip() + ' '
        else:
            if eachNode.nodeName == 'strongsref':
                theValueToPrint = strongsref(eachNode)
            if eachNode.nodeName == 'greek':
                theValueToPrint += eachNode.getAttribute('unicode').strip() + ' '
    return theValueToPrint


def textContent(node):
    if node.nodeName in ["pronunciation", "see", "strongs"]:
        return ""
    if node.nodeName in ["greek"]:
        return node.getAttribute("unicode").strip()
    if node.nodeName in ["strongsref"]:
        return strongsref(node)
    if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
        return node.nodeValue
    return ''.join(textContent(n) for n in node.childNodes)


print "... Creating Greek Index..."
for entry in dom.getElementsByTagName("entry"):
    index = entry.getElementsByTagName("strongs")[0].childNodes[0].nodeValue.strip()
    if entry.getElementsByTagName("greek").length > 0:
        lemma = entry.getElementsByTagName("greek")[0].getAttribute("unicode").strip()
        strongsLookup[index] = lemma

print "... Processing Greek Entries..."
i = 0
for entry in dom.getElementsByTagName("entry"):
    i = i + 1
    index = entry.getElementsByTagName("strongs")[0].childNodes[0].nodeValue.strip()
    lemma = ""
    pronunciation = ""
    definition = ""
    if i % 1000 == 0:
        print '... ... ', i, 'entries processed...'
    if entry.getElementsByTagName("greek").length > 0:
        lemma = entry.getElementsByTagName("greek")[0].getAttribute("unicode").strip()
        pronunciation = entry.getElementsByTagName("pronunciation")[0].getAttribute("strongs").strip()
        definition = textContent(entry)
#        for node in entry.childNodes:
#            if node.nodeType == 3:
#                definition += node.nodeValue.strip() + ' '
#            else:
#                if node.nodeName == 'strongs_derivation' or \
#                   node.nodeName == 'strongs_def' or \
#                   node.nodeName == 'kjv_def' or \
#                   node.nodeName == 'see':
#                    definition += renderNode(node).strip() + ' '
#                if node.nodeName == 'strongsref':
#                    definition += strongsref(node) + ' '
#                if node.nodeName == 'greek':
#                    definition += node.getAttribute('unicode').strip() + ' '
        definition = definition.replace("\n", "").replace("\t", " ")
        while '  ' in definition:
            definition = definition.replace('  ', ' ')
        dbConn.execute("insert into [strongsgr] values ( ?, ?, ?, ? )",
                       ('G' + index,
                        lemma.strip(),
                        pronunciation.strip(),
                        definition.strip().replace("\n", "").replace("\t", " "), ))

print "... Committing..."
dbConn.commit()

print "... Closing..."
dbConn.close()

print ""
print "Complete."
print ""
