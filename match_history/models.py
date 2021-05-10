from django.db import models

class Item(models.Model):
    JSON_Data = models.JSONField('Item data in JSON format', 'Data')
    pass


class Hero(models.Model):
    Name = models.TextField("Hero Name", "Name", default="Hero")
    JSON_Data : models.JSONField = models.JSONField('Hero data in JSON format', 'Data')
    def __str__(self):
        return self.Name
    pass