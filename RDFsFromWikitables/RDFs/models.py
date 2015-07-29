from django.db import models

class Page(models.Model):
    link = models.URLField(max_length=512, unique=True)
    title = models.CharField(max_length=512)

class RDF(models.Model):
    related_page = models.ForeignKey('Page')
    rdf_subject = models.CharField(max_length=512)
    rdf_predicate = models.CharField(max_length=512)
    rdf_object = models.CharField(max_length=512)
    object_column_name = models.CharField(max_length=256)
    relative_occurency = models.DecimalField(max_digits=4, decimal_places=3)
    subject_is_tablekey = models.BooleanField()
    object_is_tablekey = models.BooleanField()
    table_number = models.IntegerField()
    number_of_tablerows = models.IntegerField()
