import os
import sys
sys.path.append(os.getcwd())

from libs.message_parser import MessageParser

parser = MessageParser()

while True:
    text = raw_input("Enter text to parse: ").decode(sys.stdin.encoding)

    parsed = parser.parse(text)

    print
    print "Original: %s" % parsed['original']
    print "Intent: %s" % parsed['intent']
    print "Entities: %s" % parsed['entities']
    print