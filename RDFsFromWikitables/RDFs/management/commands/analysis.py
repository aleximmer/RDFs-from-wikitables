from django.core.management.base import BaseCommand
from RDFs.models import RDF, Page, Table

class Command(BaseCommand):
    def handle(self, *args, **options):
        # start scripts/methods at this point


def analyseExtent():
    tables_size = Table.objects.all().count()
    pages_size = Page.objects.all().count()
    # can be found out differently
    pages_with_tables = Page.objects.filter(html_icontains='wikitable').count()

    print('Amount of Tables: ' + str(tables_size))
    print('Amount of Pages: ' str(pages_size))
    print('Amount of Pages with tables: ' + str(pages_with_tables))
    print('Tables per Page: ' + str(tables_size/pages_size))
    print('Tables per Page containing at least one table: ' + str(tables_size/pages_with_tables))

def analyseTriples():
    start = 0.05
    while start <= 1:
        threshold_count = append(RDF.objects.filter(relative_occurency__lte=start).count())
        print('Threshold ' + str(start) + ' with ' str(threshold_count) + ' triples')
