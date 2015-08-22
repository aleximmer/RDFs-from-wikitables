import os.path
from _thread import start_new_thread, allocate_lock
from collections import defaultdict
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page, Table
from RDFsFromWikitables.settings import PROJECT_DIR
from wikitables.localpage import LocalPage
import wikipedia

import time

THREAD_MAX = 16

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

    index = 0
    for table in loc_pg.tables:
        try:
            tb = Table.objects.get(page=pg, table_number=index)

            rdfs = table.generateRDFs()
            print(str(len(rdfs)) + ' new RDFs generated for table')

            for rdf in rdfs:
                db_lock.acquire()
                # exclude errors like empty subject, predicate or object and
                # errors such as subject != resource
                # remove wikiPageWikiLink as its not on public SPARQL Endpoint
                if rdf[0] and rdf[1] and rdf[2] and ('/resource/' in rdf[0]) and not ('http://dbpedia.org/ontology/wikiPageWikiLink' in rdf[1]):
                    RDF(table=tb, rdf_subject=rdf[0], rdf_predicate=rdf[1], rdf_object=rdf[2],
                            object_column_name=rdf[3], relative_occurency=rdf[4],
                            subject_is_tablekey=rdf[5], object_is_tablekey=rdf[6]).save()
                db_lock.release()
        except:
            print('Unexpected error occurred during RDF-generating')

        index += 1
    if index == 0:
        print('page has no tables')

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
