import json
import random
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login,authenticate
from rest_framework.decorators import api_view, renderer_classes
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .models import *
from datetime import date 
from rest_framework.renderers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.core.cache import cache




"""
what is views ?
    It returns some page when the users request 
    It is a python function that accepts request from the user
    and then provides information
    
    Twilio verification code:
    JH_1Y7Z04jCuwD8jnv3d57MX-ovOgdz-H-7-E-o4
    
"""


# Create your views here.
def showHomePage(request):
    return render(request, 'index.html')

@api_view(['GET'])
def bookDetails(request, id):
    try:
        book = BooksForSale.objects.get(id=id)
        
        authorname = ""
        for author in book.bookId.authorsOfBook.all():
            authorname = authorname + author.authorName + '\n'
    
        location = PresentAddress.objects.filter(userId=book.ownerId).first()
        book_dict = {
            'bookName': book.bookId.title,
            'authorName':authorname,
            'edition': book.bookId.edition,
            'imageUrl': book.bookId.imageUrl,
            'publisher': book.bookId.publisher,
            'price': book.price,
            'location': location.place +','+location.upzilla +','+location.district,
            'owner': book.ownerId.fullName,
            'description': book.bookId.description
        }
        return JsonResponse(book_dict, safe= False)  
    except Book.DoesNotExist:
        print('book not found')
        return  Response({'message': 'Book not found'}, status=status.HTTP_401_UNAUTHORIZED )

# handle the jsonRequst of AddBook
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addBookRequestHandle(request):
    user = request.user
    print(user)
    if request.method == 'POST': 
        try:
            json_data = json.loads(request.body)
            
            authors = json_data.get("authors")
            list_of_authors = []

            for author in authors:
                author_name = author.get("name")
                profile_link = author.get("profileLink")
                existing_author = Author.objects.filter(authorName=author_name, profileUrl=profile_link).first()
                if existing_author:
                    list_of_authors.append(existing_author)
                else:
                    list_of_authors.append(Author.objects.create(
                        authorName=author.get("name"),
                        profileUrl=author.get("profileLink")
                    ))
                    
                
            new_book = Book.objects.create(
                title = json_data.get("title"), 
                edition = json_data.get("edition"),
                publisher = json_data.get("publisher"), 
                description = json_data.get("description"),
                imageUrl = json_data.get("image")
            )
            new_book.authorsOfBook.set(list_of_authors)
            
            if json_data.get("type") == 'buy':
                bookForSale = BooksForSale.objects.create(
                    ownerId=user,
                    bookId=new_book,
                    price = json_data.get('price'),
                    availability = 'available'
                )
                
            # check the request Table, if available then push entry to the notification table
            requests = BooksRequested.objects.filter(bookTitle=new_book.title)
            for request in requests:
                Notification.objects.create(
                    userId = request.requesterId,
                    msg = user.username + ' has added your requested Book named '+ request.bookTitle   
                )
                # delete the request since the notification to the user is sent
                request.delete()
                
            
            return JsonResponse({'message': 'Book added successfully'}, status = 201)
        
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON data')
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')

@csrf_exempt
@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def addUserRequestHandle(request):
    if request.method == 'POST': 
        try:
            json_data = json.loads(request.body)
                
            new_user = CustomUser.objects.create(
                fullName = json_data.get("fullName"),
                username = json_data.get("username"), 
                password = make_password(json_data.get("password")),
                institution = json_data.get("institution"), 
                dateOfRes = date.today(), 
                phoneNo = json_data.get("phoneNo"),
                email = json_data.get("email"),
                rating = 0,
            )
            
            new_location = PresentAddress.objects.create(
                userId = new_user,
                place = json_data.get("place"),
                upzilla = json_data.get("upzilla"),
                district = json_data.get('district')
            )
            print("user added successfully")
            return JsonResponse({'message': 'User added successfully'}, status = 201)
        
        except json.JSONDecodeError:
            print("error in adding user")
            return HttpResponseBadRequest('Invalid JSON data')
            
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')
 
# handle getBooksRequest  
@api_view(('GET',)) 
def getBooksRequestHandler(request):
    books = BooksForSale.objects.order_by('?')[:4]
    books_json = []
    for book in books:
        authorname = ""
        for author in book.bookId.authorsOfBook.all():
            authorname += author.authorName + '\n'
        
        location = PresentAddress.objects.filter(userId=book.ownerId).first()

        book_dict = {
            'id':book.bookId.id,
            'bookName': book.bookId.title,
            'authorName':authorname,
            'edition': book.bookId.edition,
            'imageUrl': book.bookId.imageUrl,
            'isGiveaway' : False,
            'price': book.price,
            'place': location.place
        }
        books_json.append(book_dict)
    return JsonResponse(books_json, safe= False)

# handle login request
@csrf_exempt
@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def loginRequestHandle(request):
    if request.method == 'POST': 
        try:
            json_data = json.loads(request.body)

            username = json_data.get("username")
            password = json_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Generate a JWT token
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                return  Response ({'access_token': access_token}, status=status.HTTP_200_OK )
            else:
                return  Response({'message': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED )
            
        except json.JSONDecodeError:
            return HttpResponseBadRequest({'message': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponseBadRequest({'message': 'Only POST requests are allowed'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserInfo(request):
    user = request.user
    print(user)

    # Assuming CustomUser model has a field called 'full_name'
    user_info = {
        'username': user.username,
        'email': user.email,
    }

    return Response(user_info)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    user = request.user
    location = PresentAddress.objects.filter(userId=user).first()
    notifications = Notification.objects.filter(userId=user).all()
    requests = BooksRequested.objects.filter(requesterId=user).all()
    boughts = BooksBought.objects.filter(userId=user).all()
    
    notif =""
    for notification in notifications:
        notif = notif + notification.msg + "\n"
    req=""
    for request in requests:
        req = req + request.bookTitle + "\n"
    bgt = ""
    for bought in boughts:
        bgt = bgt + bought.bookId.title + "\n"
    
    
    userInfo = {
        'fullname': user.fullName,
        'username': user.username,
        'email': user.email,
        'phone':user.phoneNo,
        'location': location.place+','+location.upzilla+','+location.district,
        'institution':user.institution,
        'dateOfRegistration':user.dateOfRes.strftime('%Y-%m-%d'),
        'notifications':notif,
        'request':req,
        'bought': bgt  
    }
    return Response(userInfo)

@csrf_exempt
@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def addRequest(request):
    user = request.user
    print(user)
    if request.method == 'POST': 
        try:
            json_data = json.loads(request.body)
            bookTitle = json_data.get("bookName")
            
            new_request = BooksRequested.objects.create(
                requesterId = user,
                bookTitle = bookTitle, 
            )
            return JsonResponse({'message': 'request added successfully'}, status = 201)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON data')
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')

@csrf_exempt
@api_view(['POST'])
def sendOTP(request):
    if request.method == 'POST': 
        try:
            json_data = json.loads(request.body)
                
            bookId = json_data.get('bookId')
             
            book = BooksForSale.objects.get(id=bookId)
            owner = book.ownerId
            email = owner.email
            number = random.randint(100000, 999999)
            
            send_mail(
                'Buying Confirmation',
                'The otp for confirmation is: '+ str(number),
                'ar137375@gmail.com',  # Sender's email address
                [email],  # List of recipient email addresses
                fail_silently=False,
            )
            
            # Assuming 'number' contains the generated OTP
            cache_key = f'otp_{book.id}'
            cache.set(cache_key, number, timeout=300)  # Set a timeout (in seconds) for the OTP validity (e.g., 300 seconds = 5 minutes)
            
            return JsonResponse({'message': 'otp sent via mail'}, status = 201)
        
        except json.JSONDecodeError:
            print("error in sending mail")
            return HttpResponseBadRequest('Invalid JSON data')
            
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')
    

@csrf_exempt
@api_view(['POST'])
def confirmOTP(request):
    user = request.user
    print(user)
    if request.method == 'POST': 
        try:
            json_data = json.loads(request.body)
                
            bookId = json_data.get('bookId')
            otp = json_data.get('otp')
            
            cache_key = f'otp_{bookId}'
            stored_otp = cache.get(cache_key)
            print(str(stored_otp) + " " + str(otp))
            
            if otp == str(stored_otp):
                book = BooksForSale.objects.get(id=bookId)
                bookBought = BooksBought.objects.create(
                    userId = user,
                    bookId = book.bookId,
                    quantity = 1
                )
                book.delete()
                cache.delete(cache_key)
                return JsonResponse({'message': 'Buying successful'}, status = 201)
            else:
                return HttpResponseBadRequest({'OTP not matched'})
        
        except json.JSONDecodeError:
            print("error in getting bookID")
            return HttpResponseBadRequest('Invalid JSON data')
            
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')