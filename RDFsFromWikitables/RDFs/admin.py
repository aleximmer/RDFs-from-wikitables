from django.contrib import admin
from .models import *

class RDFAdmin(admin.ModelAdmin):
    list_display = ['rdf_subject', 'rdf_predicate', 'rdf_object', 'relative_occurency']
    list_display_link = ['rdf_predicate']
    ordering = ['relative_occurency']
