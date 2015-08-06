import os.path
from _thread import start_new_thread, allocate_lock
from collections import defaultdict
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page
from RDFsFromWikitables.settings import PROJECT_DIR
from wikitables.page import Page as wikipage
import wikipedia

import time

THREAD_MAX = 1

num_threads = 0
lock = allocate_lock()
db_lock = allocate_lock()

averageCrawl = 0
countCrawl = 0

averageExtr = 0
countExtr = 0

averageDb = 0
countDb = 0

# Thomas TODO:
# For each Page: -> All Tables of page: Title, HTML
#       -> Get Page Object by Title, HTML
# page = Page(title, pageid=id, html=dbHtml, link=dbLink)

"""
from RDFs.models import *

for pg in Page.objects.all():
    html = pg.html
    #construct wikipage element called wikipg

```

alex [11:12 AM]
```     index = 0
     for table in wikipg.tables:
          Table(page=pg, table_number=index, number_of_tablerows=len(table.rows???)).save()
          index += 1
"""

class Command(BaseCommand):
    def handle(self, *args, **options):
        runner = 0
        try:
            global num_threads, lock, db_lock
            db_lock.acquire()
            pages = Page.objects.all()
            db_lock.release()
            print(str(len(pages)) + ' pages found')
            try:
                f = open('logAverageValues.txt', 'w')
                for pg in pages:
                    runner += 1
                    print(str(runner) + ' current page')
                    while(True):
                        lock.acquire()
                        if num_threads < THREAD_MAX:
                            # Log average values
                            f.seek(0)
                            f.write(str(averageCrawl) + ' ('+str(countCrawl)+')' + "\n" +
                                    str(averageExtr) + ' ('+str(countExtr)+')' + "\n" +
                                    str(averageDb) + ' ('+str(countDb)+')')
                            break
                        lock.release()

                    #db_lock.acquire()
                    #if not Page.objects.filter(title=str(line)):
                    #    db_lock.release()
                    num_threads += 1
                    start_new_thread(generateRDFsFor,(pg,))
                    #else:
                    #    db_lock.release()
                    lock.release()

            except Exception as inst:
                print("Error appeared: " + str(type(inst)))
                print(inst.args)
                print("Failure")
        except Exception as inst:
            print("Error appeared: " + str(type(inst)))
            print(inst.args)
            print("Failure")

def generateRDFsFor(page):
    global num_threads, lock, db_lock, averageCrawl, countCrawl, averageExtr, countExtr, averageDb, countDb

    print("Link: "+ str(page.link).strip())
    url = page.link
    title = page.title
    html = page.html
    #fromXowa = page.from_xowa
    try:
        wpage = None
        try:
            t0 = time.time()

            wpage = wikipage(title, link=url, html=html)

            deltaT = time.time() - t0
            averageCrawl = (countCrawl * averageCrawl + deltaT) / (countCrawl+1)
            countCrawl += 1
        except:
            print("\n------------------------------\n" +
                    "Couldn\'t find wikipedia page with this title\n" +
                    "FAILED for page with title: " + str(title).strip() + "\n" +
                    "------------------------------")

        acquired = False
        print('Has Table: ')
        print(wpage.hasTable())
        if wpage.hasTable():
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
                        #t0 = time.time()

                        RDF(table=table, rdf_subject=rdf[0], rdf_predicate=rdf[1], rdf_object=rdf[2],
                                object_column_name=rdf[3], relative_occurency=rdf[4],
                                subject_is_tablekey=rdf[5], object_is_tablekey=rdf[6],
                                table_number=i, number_of_tablerows=rdf[7]).save()

                        #deltaT = time.time() - t0
                        #averageDb = (countDb * averageDb + deltaT) / (countDb+1)
                        #countDb += 1
                    db_lock.release()
                    acquired = False
        else:
            print('Page with title \''+str(title).strip()+'\' has no tables')
            page.delete()
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
