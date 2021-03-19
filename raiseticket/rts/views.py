from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth,User
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required 
from .models import *
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.db.models import Q
# Create your views here.

def index(request):
    head = 'RAISE TICKET SYSTEM'
    user = request.user
    all_post = Paginator(Post.objects.all(),3)
    page = request.GET.get('page')
    try:
        posts = all_post.page(page)
    except PageNotAnInteger:
        posts = all_post.page(1)
    except EmptyPage:
        posts = all_post.page(all_post.num_pages)
    parms = {
        'head':head,
        'tickets': posts,
    }
    return render(request,'index.html',parms)

def contact(request):
    if request.method == 'POST':
        name = f"{request.POST.get('fname')} {request.POST.get('lname')}"
        email = request.POST.get('email')
        mob = request.POST.get('mob')
        mess = request.POST.get('mess','default')
        Contact(name=name,email=email,mob=mob,mess=mess).save()
        messages.success(request,'Contact Sent')
    parms = {
        'head': 'RTS | Contact',
        }
    return render(request, 'contact.html', parms)



def feedback(request):
    head = "RTS | Feedback"
    user  = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            feed = request.POST['feed']
            Feedback.objects.create(userid=user.id,feed=feed)
            messages.info(request,"Feedback Sent")
    return render(request,'feedback.html',{"head":head})

def createticket(request):
    head = "RTS | Create Ticket"
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            title = request.POST['title']
            overview = request.POST['overview']
            slug = request.POST['slug']
            body_text = request.POST['body_text']
            Post.objects.create(title=title,overview=overview,slug=slug,body_text=body_text,auther=user)
            messages.success(request,'Ticket Submitted')
        parms = {
            'head':head,
        }
        return render(request,'createticket.html',parms)
    else:
        messages.error(request,'Login First')
        return redirect('login')
    return render(request,'createticket.html',{'head':head})

def about(request):
    head = "RTS | ABOUT"
    parms = {
        'head':head,
    }
    return render(request, 'about.html', parms)

def register(request):
    head = "RTS | REGISTER"
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username,password=password1,email=email).save()
                user = auth.authenticate(username=username,password=password1)
                auth.login(request,user)
                us = request.user
                us.is_active = False
                us.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('registration/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                messages.info(request,'Check email and Verify your account')
                return redirect(index)
        else:
            messages.info(request,'Password not matched')
            return redirect('register')
    return render(request,'signup.html',{'head':head})

def login(request):
    head = "RTS | LOGIN"
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            messages.info(request,'Logged In Successfully')
            return redirect('dashboard')
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('login')

    else:
        return render(request,'login.html',{'head':head})

def logouts(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    head = "RTS | User Dashboard"
    user = request.user
    if user.is_authenticated:
        tickets = Post.objects.filter(auther=user)
        names = []
        reads = []
        for ticket in tickets:
            names.append(ticket.title)
            reads.append(ticket.read)
        return render(request,'dashboard.html',{'head':head,'tickets':tickets,'names':names,'reads':reads})
    else:
        messages.error(request,'Login First')
        return redirect('login')
    return render(request,'dashboard.html',{'head':head}) 

def search(request):
	q = request.GET.get('q')
	if q is None:
		q = ' '
	posts = Post.objects.filter(
		Q(title__icontains = q) |
		Q(overview__icontains = q)
		).distinct()

	parms = {
		'posts':posts,
        'head': 'RTS | SEARCH',
		'title':f'Search Results for {q}',
		}

	return render(request, 'search.html', parms)

def deleteticket(request,id):
    title = "RTS | DELETE TICKET"
    user = request.user
    if user.is_authenticated:
        posti = Post.objects.get(id=id)
        userid = posti.auther.id
        if user.id == userid:
            post = Post.objects.filter(id=id).delete()
            messages.success(request,'Ticket Deleted Successfully!')
            return redirect('dashboard')
        else:
            messages.error(request,'Not Your Ticket!')
    else:
        messages.error(request,'Login First')
        return redirect('login')
    parms = {
        'head':title,
    }
    return render(request,'deleteticket.html',parms)

def editticket(request,id):
    head = "RTS | EDIT TICKET"
    user = request.user
    if user.is_authenticated:
        posti = Post.objects.get(id=id)
        userid = posti.auther.id
        if user.id == userid:
            try:
                old = Post.objects.get(id=id)
            except ObjectDoesNotExist:
                return HttpResponse('Blog Not Found')
            if request.method == 'POST':
                title = request.POST['title']
                overview = request.POST['overview']
                slug = request.POST['slug']
                body_text = request.POST['body_text']
                Post(id=old.id,title=title,overview=overview,slug=slug,body_text=body_text,auther=user,time_upload=datetime.datetime.now()).save()
                messages.success(request,"Ticket Updated!")
                return redirect('post',id,slug)
        else:
            messages.error(request,'Not Your Ticket!')
        parms = {
            'head':head,
            'old':old,
        }
        return render(request,'editticket.html',parms)
    else:
        messages.error(request,'Login First')
        return redirect('login')
    parms = {
        'head':head,
    }
    return render(request,'editticket.html',parms)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def post(request, id, slug):
    head = "RTS | Ticket"
    try:
        post = Post.objects.get(pk=id, slug=slug)
    except:
        raise Http404("Ticket Does Not Exist")	
    if request.method == 'POST':
        comm = request.POST.get('comm')
        comm_id = request.POST.get('comm_id') #None

        if comm_id:
            SubComment(post=post,
                    user = request.user,
                    comm = comm,
                    comment = Comment.objects.get(id=int(comm_id))
                ).save()
        else:
            Comment(post=post, user=request.user, comm=comm).save()    
    post.read+=1
    post.save()
    comments = []
    for c in Comment.objects.filter(post=post):
        comments.append([c, SubComment.objects.filter(comment=c)])

    post_author = post.auther

    parms = {
        'comments':comments,
        'post':post,
        'head':head,
        }
    return render(request, 'ticket-single.html', parms)