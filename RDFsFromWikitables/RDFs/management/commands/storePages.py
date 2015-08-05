import os.path
from _thread import start_new_thread, allocate_lock
from django.core.management.base import BaseCommand
from RDFs.models import Page
from RDFsFromWikitables.settings import PROJECT_DIR
import requests
from lxml import html
from lxml.html.clean import clean_html

THREAD_MAX = 3

num_threads = 0
lock = allocate_lock()
db_lock = allocate_lock()

class Command(BaseCommand):
    def handle(self, *args, **options):
        #"""
        global num_threads, lock, db_lock
        runner = 0
        try:
            urlsFile = os.path.join(PROJECT_DIR, "data/URLs.txt")
            print(urlsFile)
            with open(urlsFile) as f:
                content = f.readlines()
            print(str(len(content)) + ' lines in file')
            try:
                for line in content:
                    runner += 1
                    print(str(runner) + ' current line')
                    line = (line[:4] + 's' + line[4:]).rstrip()
                    while(True):
                        lock.acquire()
                        if num_threads < THREAD_MAX:
                            break
                        lock.release()

                    num_threads += 1
                    start_new_thread(savePageFrom,(line,))
                    lock.release()

            except Exception as inst:
                print("Error appeared: " + str(type(inst)))
                print(inst.args)
                print("Failure")
        except Exception as inst:
            print("Couldn´t open file in given directory")
        #"""


        page = requests.get('https://en.wikipedia.org/wiki/AdolfHitler')
        tree = html.fromstring(page.text)
        title = tree.xpath('/html/head/title/text()')
        print(title)
        #print(page.text)


def savePageFrom(url):
    global num_threads, db_lock

    print("current url: " + str(url))

    try:
        wiki_page = requests.get(url)
        full_text = wiki_page.text
        print("got file")

        # try to get the title with lxml
        title = ''
        try:
            tree = html.fromstring(full_text)
            titles = tree.xpath('/html/head/title/text()')
            print(titles)
            if titles:
                # get the wiki title and delete the standard marker
                # '- Wikipedia, the free encyclopedia'
                title = titles[0][:-35]
                if title == 'Bad title - Wikipedia, the free encyclopedia':
                    lock.acquire()
                    num_threads -= 1
                    lock.release()
                    return
        except:
            print("Error while finding title")

        pg = Page(link=url, title=title, html=full_text)
        print(pg)
        #print(page.text)

    except:
        print("Couldn't open given URL" + str(url))

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
