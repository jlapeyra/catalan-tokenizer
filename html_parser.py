from abc import abstractmethod
from html.parser import HTMLParser
from time import time
import requests
from utils import overlap
import re

class TextHTMLParser(HTMLParser):
    __stack:list
    __count_keys:dict[str,int]
    text:str

    def __init__(self) -> None:
        self.text = ''
        self.__stack = []
        self.__count_keys = {
            'include 1' : 0,
            'include 2' : 0,
            'exclude' : 0
        }
        super().__init__()

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get('class', '').split()
        keys = []
        if 'mw-parser-output' in classes: 
            keys.append('include 1')
        if tag == 'p':
            keys.append('include 2')
        elif (tag in ('sup', 'script', 'style', 'table', 'math') or
            overlap(set(classes), ('mw-editsection', 'reflist', 'citation', 'interProject'))
        ):
            keys.append('exclude')
        for key in keys:
            self.__count_keys[key] += 1
        self.__stack.append((tag, keys))
        

    def handle_endtag(self, tag):
        stack_tag, keys = None, None
        while tag != stack_tag:
            stack_tag, keys = self.__stack.pop()
            for key in keys:
                self.__count_keys[key] -= 1
    
    def handle_data(self, data):
        if (self.__count_keys['include 1'] and
            self.__count_keys['include 2'] and 
            not self.__count_keys['exclude']
        ):
            self.text += data
            #print(self.__count_keys)

class LinksHTMLParser(HTMLParser):
    links:list[str]

    def __init__(self):
        self.links = []
        super().__init__()
    
    def handle_starttag(self, tag, attrs):
        if 'a' == tag and (href := dict(attrs).get('href')) \
        and href.startswith('/wiki/') and ':' not in href:
            self.links.append(href)


def getPlainText(html:str):
    p = TextHTMLParser()
    p.feed(html)
    return p.text
    
def getLinks(html:str):
    p = LinksHTMLParser()
    p.feed(html)
    return p.links

def downloadHTML(url):
    response = requests.get(url)
    return response.content.decode(response.encoding)

if __name__ == '__main__':
    html = downloadHTML('https://ca.wikipedia.org/wiki/Catalunya')
    text = getPlainText(html)
    links = getLinks(html)
    with open('data/catalunya.wiki.links', 'w', encoding='utf-8') as f:
        for l in set(links):
            print(l, file=f)
    with open('data/catalunya.wiki.txt', 'w', encoding='utf-8') as f:
        f.write(text) 