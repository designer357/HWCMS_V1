from django.db import models
#from datagrid import DataGrid
#class RealGrid(DataGrid):
    #name = Column()
    #publisher = Column()
    #recommended_by = Column()
# Create your models here.
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    date_of_birth = models.DateField()

class Parameter:
    def __init__(self,supp,cond,lift,kulc,ir):
        self.min_supp=supp
        self.min_cond=cond
        self.min_lift=lift
        self.min_kulc=kulc
        self.thresh_ir=ir
class FileList:
    def __init__(self,filename,filedate,filetype,check):
        self.filename=filename
        self.filedate=filedate
        self.filetype=filetype
        self.check=check