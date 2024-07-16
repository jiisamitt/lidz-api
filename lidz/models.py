from django.db import models

# Create your models here.

# Client model
class Client(models.Model):
  name = models.CharField(max_length=200)
  rut = models.CharField(max_length=12)
  salary = models.IntegerField()
  savings = models.IntegerField()
  
  class Meta:
    db_table = 'client'
  
 
 # Message model 
class Message(models.Model):
  text = models.CharField(max_length=2000)
  role = models.CharField(max_length=200)
  client = models.ForeignKey(Client, on_delete=models.CASCADE)
  sent_at = models.DateTimeField()
  
  class Meta:
    db_table = 'message'


# Debt model
class Debt(models.Model):
  institution = models.CharField(max_length=200)
  amount = models.IntegerField()
  due_date = models.DateTimeField()
  client = models.ForeignKey(Client, on_delete=models.CASCADE)
  
  class Meta:
    db_table = 'debt'
    