import os.path
from _thread import start_new_thread, allocate_lock
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page
from RDFsFromWikitables.settings import PROJECT_DIR

import time

THREAD_MAX = 16

num_threads = 0
lock = allocate_lock()

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            global num_threads, lock
            titlesFile = os.path.join(PROJECT_DIR,"data/Titles.txt")
            print(titlesFile)
            with open(titlesFile) as f:
                content = f.readlines()
            print(str(len(content)) + ' lines in file')
            try:
                for line in content:
                    while(True):
                        lock.acquire()
                        if num_threads < THREAD_MAX:
                            break
                        lock.release()
                    start_new_thread(generateRDFsFor,(line,))
                    num_threads += 1
                    lock.release()
            except:
                print("Failure")
        except:
            print("Couldn´t open file in given directory")

def generateRDFsFor(title):
    global num_threads, lock

    try:
        # CODE HERE
        print(title)
        time.sleep(5)

    except:
        print("FAILED with title: " + str(title))

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
