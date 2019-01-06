from PIL import Image
import os
import urllib.request
import re
import urllib.parse

size_300 = (300,300)


def main():
    nameimage()
    isimage()


def nameimage():

    filepath = 'Date1_File.txt'
    downloadimage(filepath)
    filepath = 'Date2_File.txt'
    downloadimage(filepath)
    filepath = 'Date3_File.txt'
    downloadimage(filepath)


def downloadimage(filepath):
    Name = None
    with open(filepath) as r:
        Name = r.read().split('\n')[1]
        open(filepath).close()

    try:
        url = 'https://www.google.com/search?q=' + Name + '&source=lnms&tbm=isch&sa='

        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)
        respData = resp.read()

        paragraphs = re.findall(r'<div class="rg_meta notranslate">(.*?)</div>', str(respData))

        alllinks = re.findall('"(.*?)"', str(paragraphs))

        for eachlink in alllinks:
            try:
                re.search('https://(.*?).png', str(eachlink)).group()
                link = eachlink
                requestlink(link, Name)
                print(link)
                return

            except Exception:
                pass


    except Exception as e:
        print(str(e))
        return


def requestlink(link, Name):

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)


    try:
        urllib.request.urlretrieve(link, str(Name) + ".png")

    except Exception as e:
        print(str(e))
        # os.mkdir('it failed')

def isimage():
    for f in os.listdir('.'):
        if f.endswith('png'):
            createdelete(f)
        if f.endswith('jpeg'):
            createdelete(f)


def createdelete(f):
    i = Image.open(f)
    fn, fext = os.path.splitext(f)
    i.thumbnail(size_300)
    if not os.path.exists('images/'):
        os.mkdir('images/')
    i.save('images/{}{}'.format(fn, fext))
    if os.path.exists(f):
        os.remove(f)


main()
