import wikipedia
from bs4 import BeautifulSoup
import requests
from .table import Table
from lxml import html

class LocalPage(object):

    def __init__(self, html, link):
        self.url = link

        self._tables = None
        self._html = html
        self._soup = None

    def __repr__(self):
        return "Title:\n\t%s\n\t%s\nTables:\n\t" % (self.title, self.url) + "\n\t".join([str(t) for t in self.tables])

    def html(self):
        return self.html

    @property
    def html(self):
        return self._html

    @property
    def soup(self):
        if not self._soup:
            self._soup = BeautifulSoup(self.html, "lxml")
        return self._soup

    @property
    def tables(self):
        if not self._tables:
            self._tables = [Table(table, self) for table in self.soup.findAll('table', 'wikitable')]
        return self._tables

    """properties which are necessary for local use as they cannot be fetched from the API"""
    @property
    def title(self):
        if not self._title:
            tree = html.fromstring(full_text)
            # TODO: verify, sollte irgendwie so gehen...
            self._title = tree.xpath('/html/head/title/text()')[0]
        return self._title

    @property
    def summary(self):
        if not self._summary:
            # TODO
            self._summary = 'XYSDFASDF'
        return self._summary

    @property
    def categories(self):
        if not self._categories:
            # TODO wirklich liste?
            self._categories = []
        return self._categories

    def hasTable(self):
        return True if self.tables else False

    def predicates(self, relative=True, omit=False):
        return {
            'page': self.title,
            'no. of tables': len(self.tables),
            'tables': [
                {
                    'table': repr(table),
                    'colums': table.columnNames,
                    'predicates': table.predicatesForAllColumns(relative, omit)
                } for table in self.tables if not table.skip()]
        }

    def browse(self):
        """Open page in browser."""
        import webbrowser

        webbrowser.open(self.url, new=2)
