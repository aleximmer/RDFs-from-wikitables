from django.db import models

# Create your models here.
class RDF(models.Model):
    rdf_subject = models.CharField(max_length=512)
    rdf_predicate = models.CharField(max_length=512)
    rdf_object = models.CharField(max_length=512)
    object_column_name = models.CharField(max_length=256)
    relative_occurency = models.DecimalField(max_digits=4, decimal_places=3)
    subject_is_tablekey = models.BooleanField()
    object_is_tablekey = models.BooleanField()
    page_link = models.URLField(max_length=512)
    page_title = models.CharField(max_length=512)
    table_number = models.IntegerField()
    number_of_tablerows = models.IntegerField()
