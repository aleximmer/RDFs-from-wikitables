import os.path
from _thread import start_new_thread, allocate_lock
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page
from RDFsFromWikitables.settings import PROJECT_DIR

#something like
#from wikitables.page import Page as wikipage

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
        wpage = wikipage(title)
        pg = Page(title=title, link=wpage.url)
        pg.save()

        for table in wpage.tables:
            # generate RDFS and store in following variables:
                # rdf_subject, rdf_predicate, rdf_object, object_column_name, relative_occurency,
                # subject_is_tablekey, object_is_tablekey, table_number, number_of_tablerows
            # save the data:
            RDF(related_page=pg, rdf_subject=rdf_subject, rdf_predicate=rdf_predicate, rdf_object=rdf_object,
                object_column_name=object_column_name, relative_occurency=relative_occurency,
                subject_is_tablekey=subject_is_tablekey, object_is_tablekey=object_is_tablekey,
                table_number=table_number, number_of_tablerows=number_of_tablerows).save()

    except:
        print("FAILED with title: " + str(title))

    lock.acquire()
    num_threads -= 1
    lock.release()
    return
