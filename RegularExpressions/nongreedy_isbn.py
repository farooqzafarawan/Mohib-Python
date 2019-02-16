"""
XML parsing: regular expressions (no robust or general)
"""
import re, pprint

text = '''
<catalog>
<book isbn="0-596-00128-2">
<title>Python &amp; XML</title>
<date>December 2001</date>
<author>Jones, Drake</author>
</book>
<book isbn="0-596-15810-6">
<title>Programming Python, 4th Edition</title>
<date>October 2010</date>
<author>Lutz</author>
</book>
<book isbn="0-596-15806-8">
<title>Learning Python, 4th Edition</title>
<date>September 2009</date>
<author>Lutz</author>
</book>
<book isbn="0-596-15808-4">
<title>Python Pocket Reference, 4th Edition</title>
<date>October 2009</date>
<author>Lutz</author>
</book>
<book isbn="0-596-00797-3">
<title>Python Cookbook, 2nd Edition</title>
<date>March 2005</date>
<author>Martelli, Ravenscroft, Ascher</author>
</book>
<book isbn="0-596-10046-9">
<title>Python in a Nutshell, 2nd Edition</title>
<date>July 2006</date>
<author>Martelli</author>
</book>
<!-- plus many more Python books that should appear here -->
</catalog> '''

#text = open('books.xml').read() # str if str pattern
pattern = '(?s)isbn="(.*?)".*?<title>(.*?)</title>' # *?=nongreedy
found = re.findall(pattern, text) # (?s)=dot matches /n
mapping = {isbn: title for (isbn, title) in found} # dict from tuple list
pprint.pprint(mapping)