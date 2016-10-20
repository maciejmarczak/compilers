import os
import sys
import re
import codecs


# Transform list of matching strings into one, separated by a comma, string.
def concatResults(list):
    return ', '.join(list)


# Fetch values from META tags.
def getFromMeta(content, data):
    results = re.compile('^<META NAME="' + data + '" CONTENT="(.+)">$', re.MULTILINE | re.IGNORECASE).findall(content)
    return concatResults(results)


# Fetch values from the rest of the document.
mailRegex = re.compile('\b[A-Za-z0-9](([_\.\-]?[a-zA-Z0-9]+)*)@([A-Za-z0-9]+)(([\.\-]?[a-zA-Z0-9]+)*)\.([A-Za-z]{2,})\b')

htmlTagPattern = '<[^>]*/?>'

# In case of 'strict mode': '(?:[A-Za-z]{4,}|\w [0-9\"\')]+)(?:(?:' + htmlTagPattern + ')*(?:[.!?]+(?: [A-Z0-9]|$)|$))'.
endOfSentenceRegex = re.compile('(?:[A-Za-z]{4,}|\w[ \t]*[0-9\"\')]+)[ \t]*(?:(?:' + htmlTagPattern + '[ \t]*)*(?:[.!?]+[ \t]*(?: [A-Z0-9]|$)|[ \t]*$))', re.MULTILINE)

intRegex = re.compile(
    r'(?:(?<=[\s(\"\'])|(?:^))(?:0*)(-?(?:\d{1,4}|[0-2]\d{1,4}|3[0-1]\d{1,3}|32[0-6]\d{1,2}|327[0-5]\d|3276[0-7])|-32768)(?=$|[\s);,\"\'])', re.MULTILINE)

floatRegex = re.compile('(?:^|[\s(\"\'])(?:\d+\.|\.\d+)(?:\d*(?:[Ee][+-]?\d+)?)(?:[\s)\"\';,][^A-Z0-9]|[ \t]*$)', re.MULTILINE)

shortcutRegex = re.compile('\s[A-Za-z]{1,3}\.')

date_30months_pattern = r'(04|06|09|11)'
date_31months_pattern = r'(01|03|05|07|08|10|12)'
date_days_base_pattern = r'(?:[0-2][1-9]|10|20)'
date_29days_pattern = r'(' + date_days_base_pattern + ')'
date_30days_pattern = r'(' + date_days_base_pattern + '|30)'
date_31days_pattern = r'(' + date_days_base_pattern + '|30|31)'
date_validate_regex = re.compile(
    r'(?:[^\d]|^)'
    + r'(?:' + date_31days_pattern + r'(?P<sepA>[./-])' + date_31months_pattern
    + r'|' + date_30days_pattern + r'(?P<sepB>[./-])' + date_30months_pattern
    + r'|' + date_29days_pattern + r'(?P<sepC>[./-])(02))'
    + r'(?:(?P=sepA)|(?P=sepB)|(?P=sepC))([\d]{4})'
    + r'|([\d]{4})(?P<sep2>[./-])'
    + r'(?:' + date_31months_pattern + r'(?P=sep2)' + date_31days_pattern
    + r'|' + date_30months_pattern + r'(?P=sep2)' + date_30days_pattern
    + r'|(02)(?P=sep2)' + date_29days_pattern + r')'
    + r'(?:[^\d]|$)'
)


def countDifferentDates(content):
    def format_date(date):
        filtered = filter(lambda x: x not in ['-', '.', '/', ''], date)
        return filtered if len(filtered[0]) == 2 else filtered[::-1]

    return len(set([format_date(match) for match in date_validate_regex.findall(content)]))


def countOccurrences(content, regex):
    return len(regex.findall(content))

def countDifferentOccurrences(content, regex):
    return len(set(regex.findall(content)))

def processFile(filepath):
    fp = codecs.open(filepath, 'rU', 'iso-8859-2')
    content = fp.read()
    fp.close()

    nonMetaContent = re.search('<P>(.*?)<META', content, re.DOTALL).group(1)

    print("nazwa pliku:", filepath)
    print("autor: %s" % getFromMeta(content, 'AUTOR'))
    print("dzial: %s" % getFromMeta(content, 'DZIAL'))
    print("slowa kluczowe: %s" % getFromMeta(content, 'KLUCZOWE_\d+'))
    print("liczba zdan: %s" % countOccurrences(nonMetaContent, endOfSentenceRegex))
    print("liczba skrotow: %s" % countDifferentOccurrences(nonMetaContent, shortcutRegex))
    print("liczba liczb calkowitych z zakresu int: %s" % countDifferentOccurrences(nonMetaContent, intRegex))
    print("liczba liczb zmiennoprzecinkowych: %s" % countDifferentOccurrences(nonMetaContent, floatRegex))
    print("liczba dat: %s" % countDifferentDates(nonMetaContent))
    print("liczba adresow email: %d" % countDifferentOccurrences(nonMetaContent, mailRegex))
    print("\n")


try:
    path = sys.argv[1]
except IndexError:
    print("Brak podanej nazwy katalogu")
    sys.exit(0)

tree = os.walk(path)

for root, dirs, files in tree:
    for f in files:
        if f.endswith(".html"):
            filepath = os.path.join(root, f)
            processFile(filepath)
