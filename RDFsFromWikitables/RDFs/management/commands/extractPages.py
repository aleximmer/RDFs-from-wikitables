import os.path
from _thread import start_new_thread, allocate_lock
from collections import defaultdict
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page
from RDFsFromWikitables.settings import PROJECT_DIR
from wikitables.page import Page as wikipage
import wikipedia

import time

THREAD_MAX = 16

num_threads = 0
lock = allocate_lock()
db_lock = allocate_lock()

averageCrawl = 0
countCrawl = 0

averageExtr = 0
countExtr = 0

averageDb = 0
countDb = 0

# MY TODO:
# For each Page: -> All Tables of page: Title, HTML
#       -> Get Page Object by Title, HTML

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            global num_threads, lock, db_lock
            titlesFile = os.path.join(PROJECT_DIR, "data/Titles.txt")
            print(titlesFile)
            with open(titlesFile) as f:
                content = f.readlines()
            print(str(len(content)) + ' lines in file')
            try:
                f = open('logAverageValues.txt', 'w')
                for line in content:
                    while(True):
                        lock.acquire()
                        if num_threads < THREAD_MAX:
                            break
                        lock.release()
                        # Log average values
                        f.seek(0)
                        f.write(str(averageCrawl) + ' ('+str(countCrawl)+')' + "\n" +
                                str(averageExtr) + ' ('+str(countExtr)+')' + "\n" +
                                str(averageDb) + ' ('+str(countDb)+')')

                    db_lock.acquire()
                    if not Page.objects.filter(title=str(line)):
                        db_lock.release()
                        num_threads += 1
                        start_new_thread(generateRDFsFor,(line,))
                    else:
                        db_lock.release()
                    lock.release()

            except Exception as inst:
                print("Error appeared: " + str(type(inst)))
                print(inst.args)
                print("Failure")
        except Exception as inst:
            print("Couldn´t open file in given directory")

def generateRDFsFor(title):
    global num_threads, lock, db_lock, averageCrawl, countCrawl, averageExtr, countExtr, averageDb, countDb

    print("Title: "+ str(title).strip())

    try:
        wpage = None
        try:

            t0 = time.time()
            pgn = wikipedia.page(title)
            print(pgn.url)
            pgn.html()
            deltaT = time.time() - t0

            wpage = wikipage(title)

            averageCrawl = (countCrawl * averageCrawl + deltaT) / (countCrawl+1)
            countCrawl += 1
        except:
            print("\n------------------------------\n" +
                    "Couldn\'t find wikipedia page with this title\n" +
                    "FAILED for page with title: " + str(title).strip() + "\n" +
                    "------------------------------")

        acquired = False
        db_lock.acquire()
        if wpage and not Page.objects.filter(link=(str(wpage.url))):
            db_lock.release()
            pg = Page(title=str(title), link=str(wpage.url), tables=len(wpage.tables))
            pg.save()
            if wpage.hasTable:
                i = -1
                for table in wpage.tables:
                    i += 1
                    t0 = time.time()

                    rdfs = table.generateRDFs()

                    deltaT = time.time() - t0
                    averageExtr = (countExtr * averageExtr + deltaT) / (countExtr+1)
                    countExtr += 1

                    print(str(len(rdfs)) + ' new RDFs generated for table ' + str(title).strip())
                    for rdf in rdfs:
                        # save the data:
                        db_lock.acquire()
                        acquired = True
                        # exclude errors like empty subject, predicate or object and
                        # errors such as subject != resource
                        if rdf[0] and rdf[1] and rdf[2] and ('/resource/' in rdf[0]):
                            t0 = time.time()

                            RDF(related_page=pg, rdf_subject=rdf[0], rdf_predicate=rdf[1], rdf_object=rdf[2],
                                    object_column_name=rdf[3], relative_occurency=rdf[4],
                                    subject_is_tablekey=rdf[5], object_is_tablekey=rdf[6],
                                    table_number=i, number_of_tablerows=rdf[7]).save()

                            deltaT = time.time() - t0
                            averageDb = (countDb * averageDb + deltaT) / (countDb+1)
                            countDb += 1
                        db_lock.release()
                        acquired = False
            else:
                print('Page with title \''+str(title).strip()+'\' has no tables')
        else:
            db_lock.release()
            print('Page with title \'' + str(title).strip() + '\' has been extracted already')
    except Exception as inst:
        print("\n------------------------------\n" +
                "Error appeared: " + str(type(inst)) + "\n" +
                str(inst.args) + "\n" +
                "FAILED for page with title: " + str(title).strip() + "\n" +
                "------------------------------")
    except:
        print("\n------------------------------\n" +
                "Unknown error appeared for page with title: " + str(title).strip() + "\n" +
                "------------------------------")

    if acquired:
        db_lock.release()

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
