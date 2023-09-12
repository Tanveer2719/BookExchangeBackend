from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token


"""
what is models ?
    It is basically the blueprint of the database
    It helps to know how you are going to store data for this app
"""
# Create your models here.

class Author(models.Model):
    authorName = models.CharField(max_length=255)
    profileUrl = models.CharField(max_length=500)

    def __str__(self):
        return self.authorName

class Book(models.Model):
    title = models.CharField(max_length=255)
    edition = models.IntegerField()
    publisher = models.CharField(max_length=255) 
    imageUrl = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    authorsOfBook = models.ManyToManyField(Author)

    def __str__(self):
        return self.title

class CustomUser(AbstractUser):
    fullName = models.CharField(max_length=250, null=True)
    institution = models.CharField(max_length=100)
    dateOfRes = models.DateField(auto_now_add=True)
    phoneNo = models.CharField(max_length=11)
    email = models.EmailField(max_length=254)
    rating = models.IntegerField(null=True)

    def __str__(self):
        return self.username
 
class BooksForSale(models.Model):
    bookId = models.ForeignKey(Book, on_delete=models.CASCADE) 
    ownerId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price = models.IntegerField()
    availability = models.CharField(max_length=50)

    
class PresentAddress(models.Model):
    userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    place = models.CharField(max_length=255)
    upzilla = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    
class BooksRequested(models.Model):
    requesterId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bookTitle = models.CharField(max_length=255)

class Notification(models.Model):
    userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    msg = models.CharField(max_length=500)
    
class BooksBought(models.Model):
    userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bookId = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    
    
    
    