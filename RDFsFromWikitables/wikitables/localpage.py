import wikipedia
from bs4 import BeautifulSoup
import requests
from .table import Table
from lxml import html
import re

class LocalPage:

    def __init__(self, title, html, link):
        self.url = link

        self._title = title
        self._tables = None
        self._html = html
        self._soup = None
        self._summary = None
        self._categories = None


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
            self._title = self.soup.find("h1", {"class": "firstHeading"}).text
        return self._title

    @property
    def summary(self):
        if not self._summary:
            content = self.soup.find("div", {"id": "mw-content-text"})
            summaryParts = []
            for c in content.findChildren():
                if c.name == "p":
                    summaryParts.append(c.text)
                elif c.name == "div" and c.get("id") == "toc":
                    # Arrived at TOC -> End of summary
                    break;
            self._summary = " ".join(summaryParts)
        return self._summary

    @property
    def categories(self):
        if not self._categories:
            self._categories = re.findall('title="Category:([^"]*)"',str(self.soup.find('div', {'class': 'mw-normal-catlinks'})))
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
