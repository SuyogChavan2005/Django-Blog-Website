from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail

from .models import *


def index(request):
    return render(request, "index.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already Exists")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already Exists")
                return redirect('signup')

            User.objects.create_user(
                username=username,
                email=email,
                password=password
            ).save()

            return redirect('signin')

        else:
            messages.info(request, "Password should match")
            return redirect('signup')

    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            auth.login(request, user)
            return redirect("index")

        else:
            messages.info(
                request,
                'Username or Password is incorrect'
            )
            return redirect("signin")

    return render(request, "signin.html")


def logout(request):
    auth.logout(request)
    return redirect('index')


def blog(request):
    return render(request, "blog.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def create(request):

    if request.method == 'POST':

        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category = request.POST['category']
            image = request.FILES['image']

            Post.objects.create(
                postname=postname,
                content=content,
                category=category,
                image=image,
                user=request.user
            )

        except Exception as e:
            print(e)

        return redirect('index')

    return render(request, "create.html")


def profile(request, id):

    return render(request, 'profile.html', {
        'user': User.objects.get(id=id),
        'posts': Post.objects.all(),
        'media_url': settings.MEDIA_URL,
    })


def profileedit(request, id):

    if request.method == 'POST':

        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']

        user = User.objects.get(id=id)

        user.first_name = firstname
        user.last_name = lastname
        user.email = email

        user.save()

        return profile(request, id)

    return render(request, "profileedit.html", {
        'user': User.objects.get(id=id),
    })


def increaselikes(request, id):

    if request.method == 'POST':

        post = Post.objects.get(id=id)
        post.likes += 1
        post.save()

    return redirect("index")


def post(request, id):

    post = Post.objects.get(id=id)

    return render(request, "post-details.html", {

        "user": request.user,
        "post": post,

        'recent_posts':
            Post.objects.all().order_by("-id"),

        'media_url':
            settings.MEDIA_URL,

        'comments':
            Comment.objects.filter(post_id=post.id),

        'total_comments':
            len(Comment.objects.filter(post_id=post.id))
    })


def savecomment(request, id):

    post = Post.objects.get(id=id)

    if request.method == 'POST':

        content = request.POST['message']

        Comment.objects.create(
            post_id=post.id,
            user_id=request.user.id,
            content=content
        )

        return redirect("index")


def deletecomment(request, id):

    comment = Comment.objects.get(id=id)

    postid = comment.post.id

    comment.delete()

    return post(request, postid)


def editpost(request, id):

    post = Post.objects.get(id=id)

    if request.method == 'POST':

        post.postname = request.POST['postname']
        post.content = request.POST['content']
        post.category = request.POST['category']

        post.save()

        return profile(request, request.user.id)

    return render(request, "postedit.html", {
        'post': post
    })


def deletepost(request, id):

    Post.objects.get(id=id).delete()

    return profile(request, request.user.id)



# ===============================
# CONTACT FORM WITH BREVO SMTP
# ===============================

def contact_us(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")


        try:

            # Save contact message
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )


            email_message = f"""
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


            # Send email using Brevo SMTP
            send_mail(

                subject=f"New Contact Form: {subject}",

                message=email_message,

                from_email=settings.EMAIL_HOST_USER,

                recipient_list=[
                    settings.HOST_USER_RECIPIENT
                ],

                fail_silently=False,
            )


            messages.success(
                request,
                "Thanks for contacting us!"
            )


        except Exception as e:

            print("EMAIL ERROR:", e)

            messages.error(
                request,
                "Message saved but email sending failed."
            )


    return render(
        request,
        "contact.html"
    )
