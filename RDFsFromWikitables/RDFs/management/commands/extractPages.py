import os.path
from _thread import start_new_thread, allocate_lock
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page
from RDFsFromWikitables.settings import PROJECT_DIR
from wikitables.page import Page as wikipage

import time

THREAD_MAX = 16

num_threads = 0
lock = allocate_lock()

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            global num_threads, lock
            titlesFile = os.path.join(PROJECT_DIR, "data/Titles.txt")
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
                    start_new_thread(generateRDFsFor(line))
                    num_threads += 1
                    lock.release()
            except:
                print("Failure")
        except:
            print("Couldn´t open file in given directory")

def generateRDFsFor(title):
    global num_threads, lock

    try:
        print("Title: "+ str(title))
        wpage = wikipage(title)
        #pg = Page(title=title, link=wpage.url)
        #pg.save()
        if wpage.hasTable():
            i = -1
            for table in wpage.tables():
                i += 1
                # generate RDFS and store in following variables:
                    # rdf_subject, rdf_predicate, rdf_object, object_column_name, relative_occurency,
                    # subject_is_tablekey, object_is_tablekey, table_number, number_of_tablerows
                rdfs = table.generateRDFs()
                print(str(len(rdfs)) + ' new RDFs generated')
                for rdf in rdfs:
                    # save the data:
                    # rdf = [subColumn[i], predicate, objColumn[i], objColumnName, relCount[predicate], subIsKey, objIsKey, rowCount]
                    print('RDF: ' + str(rdf))
                    RDF(related_page=pg, rdf_subject=rdf[0], rdf_predicate=rdf[1], rdf_object=rdf[32,
                        object_column_name=rdf[3], relative_occurency=rdf[4],
                        subject_is_tablekey=rdf[5], object_is_tablekey=rdf[6],
                        table_number=i, number_of_tablerows=rdf[7]).save()"""
        else:
            print('Page has no tables')
    except Exception as inst:
        print(type(inst))     # the exception instance
        print(inst)      # arguments stored in .args
        print("FAILED with title: " + str(title))
        #raise Exception('shit fuck it')

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
