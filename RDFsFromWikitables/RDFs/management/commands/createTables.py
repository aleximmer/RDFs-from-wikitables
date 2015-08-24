import os.path
from _thread import start_new_thread, allocate_lock
from collections import defaultdict
from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page, Table
from wikitables.localpage import LocalPage
import wikipedia

THREAD_MAX = 16

num_threads = 0
lock = allocate_lock()
db_lock = allocate_lock()

class Command(BaseCommand):
    def handle(self, *args, **options):
        runner = 0
        global num_threads, lock, db_lock

        for runner in range(1, 8556448):
            while(True):
                lock.acquire()
                if num_threads < THREAD_MAX:
                    break
                lock.release()
            lock.release()
            try:
                pg = Page.objects.get(id=runner)
                num_threads += 1
                start_new_thread(storeTables,(pg, runner))
            except:
                print('No page with that id')


def storeTables(pg, number):
    global num_threads, lock, db_lock

    loc_pg = LocalPage(pg.title, pg.html, pg.link)

    index = 0
    for table in loc_pg.tables:
        db_lock.acquire()
        tb = Table(page=pg, table_number=index, number_of_tablerows=len(table.rows)).save()
        db_lock.release()

        index += 1

    print(str(index) + ' tables')

    print('page number ' + str(number) + ' fully extracted')
    lock.acquire()
    num_threads -= 1
    lock.release()
    return
