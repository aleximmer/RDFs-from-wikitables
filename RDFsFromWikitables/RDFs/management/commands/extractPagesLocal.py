import os.path
from _thread import start_new_thread, allocate_lock
from collections import defaultdict
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page
from RDFsFromWikitables.settings import PROJECT_DIR
from wikitables.localpage import LocalPage
import wikipedia

import time

THREAD_MAX = 1

num_threads = 0
lock = allocate_lock()
db_lock = allocate_lock()

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
        global num_threads, lock, db_lock

        for pg in Page.objects.all():
            runner += 1
            print(str(runner) + ' current page number')
            while(True):
                lock.acquire()
                if num_threads < THREAD_MAX:
                    break
                lock.release()
            generateRDFsFor(pg)


def generateRDFsFor(pg):
    global num_threads, lock, db_lock

    loc_pg = LocalPage(pg.html, pg.link)

    index = 0
    for table in loc_pg.tables:
        tb = Table(page=pg, table_number=index, number_of_tablerows=len(table.rows))
        tb.save()

        rdfs = table.generateRDFs()
        print(str(len(rdfs)) + ' new RDFs generated for table ' + str(title).strip())
        for rdf in rdfs:
            db_lock.acquire()
            # exclude errors like empty subject, predicate or object and
            # errors such as subject != resource
            if rdf[0] and rdf[1] and rdf[2] and ('/resource/' in rdf[0]):
                RDF(table=table, rdf_subject=rdf[0], rdf_predicate=rdf[1], rdf_object=rdf[2],
                        object_column_name=rdf[3], relative_occurency=rdf[4],
                        subject_is_tablekey=rdf[5], object_is_tablekey=rdf[6],
                        table_number=i, number_of_tablerows=rdf[7]).save()

            db_lock.release()
            acquired = False

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
