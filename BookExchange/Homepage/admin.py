from django.contrib import admin
# ID : tanveer
# pass: P9XSDFNJ
 
# Register your models here.

from .models import *

# show Book table in admin page
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(CustomUser)
admin.site.register(BooksForSale)
admin.site.register(PresentAddress)
admin.site.register(BooksRequested)
admin.site.register(Notification)
admin.site.register(BooksBought)

