from django.db import models

class Book(models.Model):


    def __str__(self):
        return self.title


class Role(models.Model):
    title = models.CharField(max_length=50)

class BookAuthor(models.Model):
    role = models.OneToOneField(Role, on_delete=models.CASCADE)