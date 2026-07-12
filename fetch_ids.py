import urllib.request
from html.parser import HTMLParser

class MyParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag in ['input', 'select', 'textarea']:
            attr_dict = dict(attrs)
            if 'name' in attr_dict:
                print(f"{tag} name='{attr_dict['name']}' id='{attr_dict.get('id', 'NONE')}'")

html = urllib.request.urlopen('http://127.0.0.1:8000/trips/new/').read().decode('utf-8')
parser = MyParser()
parser.feed(html)
