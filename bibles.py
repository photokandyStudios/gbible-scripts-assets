#!/usr/bin/python

from xml.dom.minidom import parse
import sys
import sqlite3

abbreviations = ["Gen", "Exo", "Lev", "Num", "Deu", "Jos", "Jdg", "Rut",
                 "1Sa", "2Sa", "1Ki", "2Ki", "1Ch", "2Ch",
                 "Ezr", "Neh", "Est", "Job", "Psa", "Pro", "Ecc",
                 "Sos", "Isa", "Jer", "Lam", "Eze", "Dan",
                 "Hos", "Joe", "Amo", "Oba", "Jon", "Mic", "Nah", "Hab",
                 "Zep", "Hag", "Zec", "Mal",
                 "Mat", "Mar", "Luk", "Joh", "Act", "Rom", "1Co",
                 "2Co", "Gal", "Eph", "Phi", "Col",
                 "1Th", "2Th", "1Ti", "2Ti", "Tit",
                 "Phl", "Heb", "Jas", "1Pe", "2Pe", "1Jo", "2Jo",
                 "3Jo", "Jud", "Rev"]

OSISRefs = ["Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth",
                 "1Sam", "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr",
                 "Ezra", "Neh", "Esth", "Job", "Ps", "Prov", "Eccl",
                 "Song", "Isa", "Jer", "Lam", "Ezek", "Dan",
                 "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab",
                 "Zeph", "Hag", "Zech", "Mal",
                 "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor",
                 "2Cor", "Gal", "Eph", "Phil", "Col",
                 "1Thess", "2Thess", "1Tim", "2Tim", "Titus",
                 "Phlm", "Heb", "Jas", "1Pet", "2Pet", "1John", "2John",
                 "3John", "Jude", "Rev"]


def printHelp():
    print "Greek Interlinear Bible Database Modifier v 0.1"
    print "==============================================="
    print ""
    print "  Usage: bibles.py database command"
    print ""
    print "The following commands are recognized:"
    print "  list              no arguments"
    print "                    list avaialable Bibles. List is abbreviation, index, title."
    print ""
    print "  search            bible-abbreviation phrase"
    print "                    search the specified Bible for the phrase. Phrase should be wrapped in %...%"
    print ""
    print "  show-verse        bible-abbreviation book-abbrevation chapter:verse"
    print "                    display verse from given Bible for book, chapter, and verse reference."
    print ""
    print "  show-strongs      language key"
    print "                    display the Strong's entry for the given language and key."
    print ""
    print "  verse-change-word bible-abbreviation book-abbrevation chapter:verse word-to-change value"
    print "                    alters the verse by changing the requested word to the supplied word."
    print ""
    print "  add-bible-entry   bible-id bible-abbreviation 'bible-title' 'bible-info' 'bible-side'"
    print ""
    print "  drop-bible-content bible-abbreviation"
    print "                    removes all content for the specified bible."
    print ""
    print "  import-bible      bible-abbreviation bible-format path-to-file"
    print ""
    print ""
    print "Add 'commit' as an argument to commit any changes."
    print ""


def ref2text(book, chapter, verse):
    return abbreviations[book - 1] + " " + str(chapter) + ":" + str(verse)


def bookNumberForAbbreviation(abbr):
    return abbreviations.index(abbr) + 1


def splitReference(ref):
    vcSplit = ref.split(":")
    chapterRef = vcSplit[0]
    verseRef = vcSplit[1]
    return [chapterRef, verseRef]


def bibleIDforAbbreviation(abbr):
    sql = 'SELECT * FROM bibles WHERE bibleAbbreviation=?'
    for row in dbConn.execute(sql, [abbr]):
        return row[3]


def bibleBookChapterVerse(offset):
    bible = bibleIDforAbbreviation(sys.argv[3 + offset])
    book = bookNumberForAbbreviation(sys.argv[4 + offset])
    ref = splitReference(sys.argv[5 + offset])
    chapter = ref[0]
    verse = ref[1]
    return [bible, book, chapter, verse]


def textContent(node):
    if node.nodeName == "note":
        return ""
    if node.nodeName == "RF":
        return ""
    if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
        return node.nodeValue
    else:
        #if node.tagName != "note":
        return ''.join(textContent(n) for n in node.childNodes)

if len(sys.argv) < 3:
    printHelp()
    sys.exit(0)

dbConn = sqlite3.connect(sys.argv[1])

# create any tables necessary
try:
    print "Creating tables, if necessary..."
    dbConn.execute("CREATE TABLE bibles (bibleAbbreviation TEXT, bibleAttribution TEXT, bibleSide TEXT, bibleID INTEGER PRIMARY KEY, bibleName TEXT, bibleParsedID NUMERIC)")
    dbConn.execute("CREATE TABLE [content] ([bibleID] NUMERIC, [bibleReference] TEXT, [bibleText] TEXT, [bibleBook] INT, [bibleChapter] INT, [bibleVerse] INT, PRIMARY KEY ([bibleID] ASC, [bibleBook] ASC, [bibleChapter] ASC, [bibleVerse] ASC))")
    dbConn.execute("CREATE UNIQUE INDEX [idx_content] ON [content] ([bibleChapter] ASC, [bibleBook] ASC, [bibleVerse] ASC, [bibleID] ASC)")
    print "Tables created."
except:
    print "Tables already exist."

command = sys.argv[2]

if command == 'help':
    printHelp()

if command == 'list':
    sql = 'SELECT * FROM bibles ORDER BY 4'
    for row in dbConn.execute(sql):
        print row[3], row[0], row[4]
if command == 'search':
    bible = bibleIDforAbbreviation(sys.argv[3])
    phrase = sys.argv[4]
    sql = "select * from content where bibleID=? and bibleText like ? order by 4,5,6"
    for row in dbConn.execute(sql, [bible, phrase]):
        print ref2text(row[3], row[4], row[5]), row[2]
if command == 'show-verse':
    ref = bibleBookChapterVerse(0)
    sql = "select * from content where bibleID=? and bibleBook=? and bibleChapter=? and bibleVerse=? order by 4,5,6"
    for row in dbConn.execute(sql, ref):
        print row[2]
if command == 'show-strongs':
    language = sys.argv[3]
    key = sys.argv[4]
    if language in ["gr", "he"]:
        sql = "select * from strongs" + language + " where key=?"
        for row in dbConn.execute(sql, [key]):
            print "Lemma: " + row[1]
            print "Pronunciation: " + row[2]
            print "Definition: " + row[3]
    else:
        print "Unrecognized language; use gr or he."
if command == 'verse-change-word':
    ref = bibleBookChapterVerse(0)
    sql = "select * from content where bibleID=? and bibleBook=? and bibleChapter=? and bibleVerse=? order by 4,5,6"
    for row in dbConn.execute(sql, ref):
        verse = row[2]
        print verse, "=>"
        verse = verse.replace(sys.argv[6], sys.argv[7])
        print verse
        sql = "update content set bibleText=? where bibleID=? and bibleBook=? and bibleChapter=? and bibleVerse=?"
        dbConn.execute(sql, [verse, ref[0], ref[1], ref[2], ref[3]])
if command == 'add-bible-entry':
    bibleID = sys.argv[3]
    bibleAbbreviation = sys.argv[4]
    bibleTitle = sys.argv[5]
    bibleInfo = sys.argv[6]
    bibleSide = sys.argv[7]
    sql = "insert into bibles values ( ?, ?, ?, ?, ?, NULL )"
    dbConn.execute(sql, [bibleAbbreviation, bibleInfo, bibleSide, bibleID, bibleTitle])
    print "Bible entry added."
if command == 'drop-bible-content':
    bible = bibleIDforAbbreviation(sys.argv[3])
    sql = "delete from bibles where bibleID=?"
    dbConn.execute(sql, [bible])
    print "Bible content dropped."
if command == 'import-bible':
    bible = bibleIDforAbbreviation(sys.argv[3])
    format = sys.argv[4]
    path = sys.argv[5]
    print "... Import Bible from " + path + " using format " + format
    if format == 'osis':
        dom = parse(path)
        i = 0
        ii = 0
        sql = "insert into content values ( ?, ?, ?, ?, ?, ?)"
        for entry in dom.getElementsByTagName("verse"):
            i = i + 1
            if i % 1000 == 0:
                print '... ... ', i, 'entries processed...'
            vRef = entry.getAttribute("osisID")
            vRefSplit = vRef.split('.')
            bookAbbr = vRefSplit[0]
            chapter = vRefSplit[1]
            verse = vRefSplit[2]
            book = OSISRefs.index(bookAbbr) + 1
            testament = "O" if (book < 40) else "N"
            bookRef = str(book) + testament + "." + chapter + "." + verse
            if book < 10:
                bookRef = "0" + bookRef
            if book >= 40:
                ii = ii + 1
                verseText = textContent(entry)
                while '  ' in verseText:
                    verseText = verseText.replace('  ', ' ')
                dbConn.execute(sql, [bible, bookRef, verseText, book, chapter, verse])

if sys.argv[len(sys.argv) - 1] == 'commit':
    print "Comitted."
    dbConn.commit()
else:
    print "No commit."

dbConn.close()
