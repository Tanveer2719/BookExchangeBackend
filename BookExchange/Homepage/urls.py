from django.urls import path
from . import views

urlpatterns = [
    # homepage/
    path('', views.showHomePage, name='homepage'),
    
    # handle book request
    path('getbooks/', views.getBooksRequestHandler, name='getBooksRequestHandle'),

    # homepage/showbook/<id> 
    path('getbook/<int:id>/', views.bookDetails, name='book_details'),         
    
    # add the book to the dataBase 
    path('addbook/', views.addBookRequestHandle, name='addBookHandle'),  
    
    # add the user to the DB
    path('signup/', views.addUserRequestHandle, name='addUser'),
    
    # for login authentication
    path('login/', views.loginRequestHandle, name='loginHandle'),
    
    # for user information
    path('userinfo/', views.getUserInfo, name='getUserInfo'),
    
    #for book request
    path('request/', views.addRequest, name='addRequest'),
    
    #for otp send
    path('sendotp/',views.sendOTP, name='sendotp'),
    
    # for otp confirm
    path('confirmotp/',views.confirmOTP, name='confirmotp'),
    
    # for user profile
    path('getUser/',views.getProfile, name='userProfile'),
    
]