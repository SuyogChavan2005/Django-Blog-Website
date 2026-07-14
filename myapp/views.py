from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import threading

from .models import *



# ===============================
# HOME PAGE
# ===============================

def index(request):

    return render(request, "index.html", {

        'posts':
            Post.objects.filter(
                user_id=request.user.id
            ).order_by("id").reverse(),

        'top_posts':
            Post.objects.all().order_by("-likes"),

        'recent_posts':
            Post.objects.all().order_by("-id"),

        'user':
            request.user,

        'media_url':
            settings.MEDIA_URL

    })



# ===============================
# SIGNUP
# ===============================

def signup(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']


        if password == password2:


            if User.objects.filter(username=username).exists():

                messages.info(
                    request,
                    "Username already Exists"
                )

                return redirect("signup")



            if User.objects.filter(email=email).exists():

                messages.info(
                    request,
                    "Email already Exists"
                )

                return redirect("signup")



            User.objects.create_user(

                username=username,

                email=email,

                password=password

            ).save()


            return redirect("signin")



        else:

            messages.info(
                request,
                "Password should match"
            )

            return redirect("signup")



    return render(
        request,
        "signup.html"
    )



# ===============================
# LOGIN
# ===============================

def signin(request):

    if request.method == "POST":

        username=request.POST['username']

        password=request.POST['password']


        user=authenticate(

            request,

            username=username,

            password=password

        )



        if user:

            auth.login(
                request,
                user
            )

            return redirect("index")


        else:

            messages.info(

                request,

                "Username or Password is incorrect"

            )

            return redirect("signin")



    return render(
        request,
        "signin.html"
    )



# ===============================
# LOGOUT
# ===============================

def logout(request):

    auth.logout(request)

    return redirect("index")



# ===============================
# BLOG
# ===============================

def blog(request):

    return render(request,"blog.html",{

        'posts':
            Post.objects.filter(
                user_id=request.user.id
            ).order_by("id").reverse(),


        'top_posts':
            Post.objects.all().order_by("-likes"),


        'recent_posts':
            Post.objects.all().order_by("-id"),


        'user':
            request.user,


        'media_url':
            settings.MEDIA_URL

    })



# ===============================
# CREATE POST
# ===============================

def create(request):

    if request.method=="POST":

        try:

            Post.objects.create(

                postname=request.POST['postname'],

                content=request.POST['content'],

                category=request.POST['category'],

                image=request.FILES['image'],

                user=request.user

            )


        except Exception as e:

            print(e)



        return redirect("index")


    return render(
        request,
        "create.html"
    )



# ===============================
# PROFILE
# ===============================

def profile(request,id):

    return render(request,"profile.html",{

        "user":
            User.objects.get(id=id),

        "posts":
            Post.objects.all(),

        "media_url":
            settings.MEDIA_URL

    })



# ===============================
# PROFILE EDIT
# ===============================

def profileedit(request,id):

    if request.method=="POST":

        user=User.objects.get(id=id)

        user.first_name=request.POST['firstname']

        user.last_name=request.POST['lastname']

        user.email=request.POST['email']

        user.save()


        return profile(
            request,
            id
        )


    return render(request,"profileedit.html",{

        "user":
            User.objects.get(id=id)

    })



# ===============================
# LIKE
# ===============================

def increaselikes(request,id):

    if request.method=="POST":

        post=Post.objects.get(id=id)

        post.likes+=1

        post.save()


    return redirect("index")



# ===============================
# POST DETAILS
# ===============================

def post(request,id):

    post=Post.objects.get(id=id)


    return render(request,"post-details.html",{

        "user":
            request.user,

        "post":
            post,

        "recent_posts":
            Post.objects.all().order_by("-id"),

        "media_url":
            settings.MEDIA_URL,

        "comments":
            Comment.objects.filter(
                post_id=post.id
            ),

        "total_comments":
            Comment.objects.filter(
                post_id=post.id
            ).count()

    })



# ===============================
# COMMENT
# ===============================

def savecomment(request,id):

    post=Post.objects.get(id=id)


    if request.method=="POST":

        Comment.objects.create(

            post_id=post.id,

            user_id=request.user.id,

            content=request.POST['message']

        )


    return redirect("index")



def deletecomment(request,id):

    comment=Comment.objects.get(id=id)

    postid=comment.post.id

    comment.delete()


    return post(
        request,
        postid
    )



# ===============================
# EDIT POST
# ===============================

def editpost(request,id):

    post=Post.objects.get(id=id)


    if request.method=="POST":


        post.postname=request.POST['postname']

        post.content=request.POST['content']

        post.category=request.POST['category']


        post.save()


        return profile(
            request,
            request.user.id
        )


    return render(request,"postedit.html",{

        "post":post

    })



# ===============================
# DELETE POST
# ===============================

def deletepost(request,id):

    Post.objects.get(id=id).delete()


    return profile(
        request,
        request.user.id
    )



# =================================================
# SEND EMAIL FUNCTION (BACKGROUND THREAD)
# =================================================

def send_contact_email(name,email,subject,message):

    try:


        email_body=f"""

New Contact Form Submission


Name:
{name}


Email:
{email}


Subject:
{subject}


Message:
{message}

"""


        send_mail(

            subject=f"New Contact Form: {subject}",

            message=email_body,

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[
                settings.HOST_USER_RECIPIENT
            ],

            fail_silently=False

        )


        print(
            "EMAIL SENT SUCCESSFULLY"
        )


    except Exception as e:


        print(
            "EMAIL ERROR:",
            e
        )




# ===============================
# CONTACT PAGE
# ===============================

def contact_us(request):

    if request.method=="POST":


        name=request.POST.get("name")

        email=request.POST.get("email")

        subject=request.POST.get("subject")

        message=request.POST.get("message")



        try:


            Contact.objects.create(

                name=name,

                email=email,

                subject=subject,

                message=message

            )



            thread=threading.Thread(

                target=send_contact_email,

                args=(

                    name,

                    email,

                    subject,

                    message

                )

            )


            thread.start()



            messages.success(

                request,

                "Thanks for contacting us!"

            )



        except Exception as e:


            print(
                "CONTACT ERROR:",
                e
            )


            messages.error(

                request,

                "Something went wrong."

            )



    return render(
        request,
        "contact.html"
    )
