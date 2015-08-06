import os.path
from _thread import start_new_thread, allocate_lock
from collections import defaultdict
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page, Table
from RDFsFromWikitables.settings import PROJECT_DIR
from wikitables.localpage import LocalPage
import wikipedia

import time

THREAD_MAX = 1

num_threads = 0
lock = allocate_lock()
db_lock = allocate_lock()

class Command(BaseCommand):
    def handle(self, *args, **options):
        runner = 0
        global num_threads, lock, db_lock

        for pg in Page.objects.all():
            runner += 1
            print(str(runner) + ' current page number')
            while(True):
                lock.acquire()
                if num_threads < THREAD_MAX:
                    break
                lock.release()
            lock.release()
            num_threads += 1
            start_new_thread(generateRDFsFor,(pg,))


def generateRDFsFor(pg):
    global num_threads, lock, db_lock

    loc_pg = LocalPage(pg.title, pg.html, pg.link)
    #print(loc_pg.summary)
    #print(loc_pg.categories)
    title = pg.title

    index = 0
    try:
        if loc_pg.hasTable():
            for table in loc_pg.tables:
                if not Table.objects.filter(page=pg, table_number=index):
                    tb = Table(page=pg, table_number=index, number_of_tablerows=len(table.rows))
                    tb.save()

                    rdfs = table.generateRDFs()
                    print(str(len(rdfs)) + ' new RDFs generated for table') # ' + str(title).strip()
                    for rdf in rdfs:
                        db_lock.acquire()
                        # exclude errors like empty subject, predicate or object and
                        # errors such as subject != resource
                        if rdf[0] and rdf[1] and rdf[2] and ('/resource/' in rdf[0]):
                            RDF(table=tb, rdf_subject=rdf[0], rdf_predicate=rdf[1], rdf_object=rdf[2],
                                    object_column_name=rdf[3], relative_occurency=rdf[4],
                                    subject_is_tablekey=rdf[5], object_is_tablekey=rdf[6]).save()
                        db_lock.release()
                        acquired = False
                else:
                    print('Table ' + str(index) + ' from page with title \'' + str(pg.title).strip() + '\' has been extracted already')
        else:
            print('Page has no tables')
            pg.delete()
    except:
        print('Page failed with Error!')
    lock.acquire()
    num_threads -= 1
    lock.release()
    return
