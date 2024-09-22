from django.db import models

# Create your models here.

class Vendor(models.Model):
    Vid = models.AutoField(primary_key=True)
    vname = models.CharField(max_length=255)
    phno = models.CharField(max_length=10)
    GSTNo = models.CharField(max_length=15)
    Address = models.TextField()
    Email = models.EmailField() 

    class Meta:
        db_table = 'Vendor' 


class Stock(models.Model):
    sid = models.AutoField(primary_key=True)
    sname = models.CharField(max_length=255)
    Model = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sprice = models.DecimalField(max_digits=10, decimal_places=2)
    Qty = models.IntegerField()
    Vid = models.ForeignKey('Vendor', on_delete=models.CASCADE, db_column='vid')

    class Meta:
        db_table = 'Stock'

class Order(models.Model):
    oid = models.AutoField(primary_key=True)
    Qty = models.IntegerField()
    Model = models.CharField(max_length=255)
    vid = models.ForeignKey('Vendor', on_delete=models.CASCADE, db_column='vid')
    sid = models.ForeignKey('Stock', on_delete=models.CASCADE, db_column='sid')
    

    class Meta:
        db_table = 'Order' 