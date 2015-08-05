import os.path
from _thread import start_new_thread, allocate_lock
from django.core.management.base import BaseCommand
from RDFs.models import Page
from RDFsFromWikitables.settings import PROJECT_DIR
import requests
from lxml import html
from lxml.html.clean import Cleaner
from django.db import IntegrityError

import time

THREAD_MAX = 8

num_threads = 0
lock = allocate_lock()
db_lock = allocate_lock()

class Command(BaseCommand):
    def handle(self, *args, **options):
        global num_threads, lock, db_lock
        runner = 0
        try:
            urlsFile = os.path.join(PROJECT_DIR, "data/URLs.txt")
            print(urlsFile)
            with open(urlsFile) as f:
                content = f.readlines()
            print(str(len(content)) + ' lines in file')

            start = time.time()
            for line in content:
                runner += 1
                if runner < 6000000:
                    print(str(runner) + ' current line')
                    line = ('http://localhost:8888/' + line[7:]).rstrip()
                    while(True):
                        lock.acquire()
                        if num_threads < THREAD_MAX:
                            break
                        lock.release()

                    num_threads += 1
                    start_new_thread(savePageFrom,(line,))
                    lock.release()

        except Exception as inst:
            print("Couldn´t open file in given directory")


def savePageFrom(url):
    global num_threads, db_lock

    try:
        wiki_page = requests.get(url)
        full_text = wiki_page.text.rstrip('\n')

        # try to get the title with lxml
        title = 'url: ' + str(url)
        try:
            tree = html.fromstring(full_text)
            titles = tree.xpath('/html/head/title/text()')
            if titles:
                # get the wiki title and delete the standard marker
                # or '- XOWA' in local development circumstances
                title = titles[0][:-7]
                if title == 'Bad title - XOWA':
                    lock.acquire()
                    num_threads -= 1
                    lock.release()
                    return
        except:
            print("Error while finding title")

        try:
            cleaner = Cleaner(scripts=True, javascript=True, comments=True, style=True)
            full_text = cleaner.clean_html(full_text)
        except:
            print("Couldn't clean HTML")

        pg = Page(link=url, title=title, html=full_text, from_xowa=True).save()
    except IntegrityError:
        print("Article already existing")

    except:
        print("Couldn't open given URL " + str(url))

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
