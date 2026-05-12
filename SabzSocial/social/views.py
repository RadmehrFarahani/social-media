from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,get_object_or_404,redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .models import *
from taggit.models import Tag
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib import messages

# Create your views here.
def log_out(request):
    logout(request)
    # return redirect('blog:index')
    return render(request,'Registration/logout.html')
@login_required
def profile(request):
    user = User.objects.prefetch_related('followers','following').get(id=request.user.id)
    posts = Post.objects.filter(author=user)
    return render(request, 'social/profile.html', {'posts': posts})

@login_required
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_user(request):
    if request.method== "POST" :
        user_form=UserEditForm(request.POST,instance=request.user, files=request.FILES)
        if user_form.is_valid :
            user_form.save()
            return redirect('social:profile')

    else:
        user_form = UserEditForm(instance=request.user)

    context={
        'user_form':user_form
    }


    return render(request,'registration/edit_user.html',context)

@login_required
def ticket(request):

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data

            message=f"{cd['name']}\n{cd['email']}\n{cd['phone']}\n\n{cd['message']}"

            send_mail(cd['subject'],message,'radmehrfarahani82@gmail.com',
                      ['rojanfara@gmail.com'], fail_silently=False,)
            messages.success(request,'ایمیل شما ارسال شد')


    else:
        form=TicketForm()
    return render(request,"forms/ticket.html", {'form':form})

@login_required
def post_list(request,tag_slug=None):
    posts=Post.objects.select_related('author').order_by('-total_likes')
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])

    page=request.GET.get('page')
    paginator=Paginator(posts,2)
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=[]

    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        return render(request, "social/list_ajax.html",{'posts':posts})
    context={
        'posts':posts,
        'tag':tag
    }
    return render(request,"social/list.html",context )

@login_required
def create_post(request):
    if request.method== "POST" :
        form=CreatePostForm(request.POST)
        if form.is_valid :
            post=form.save(commit=False)
            post.author=request.user
            post.save()
            form.save_m2m()
            return redirect('social:profile')
    else:
        form=CreatePostForm()

    return render(request,'forms/create_post.html',{'form':form})

@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:2]

    context = {
        'post': post,
        'similar_posts': similar_posts,
    }
    return render(request, "social/detail.html", context)


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')

    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        post_likes_count = post.likes.count()

        return JsonResponse({
            'liked': liked,
            'likes_count': post_likes_count
        })

    return JsonResponse({'error': 'Invalid Post Id'})


@login_required
def user_list(request):
    users=User.objects.filter(is_active=True)
    return render(request,'user/user_list.html',{'users':users})

@login_required
def user_detail(request,username):
    user=get_object_or_404(User,username=username,is_active=True)
    return render(request,'user/user_detail.html',{'user':user})

# @login_required
# @require_POST
# def user_follow(request):
#     user_id = request.POST.get('id')
#
#     if user_id:
#         try:
#             user=User.objects.get(id=user_id)
#             if request.user in user.followers.all():
#                 Contact.objects.filter(user_from=request.user,user_to=user).delete()
#                 follow=False
#             else:
#                Contact.objects.get_or_create(user_from=request.user, user_to=user)
#                follow=True
#             following_count = user.following.count()
#             followers_count = user.followers.count()
#             return JsonResponse({'follow':follow,'following_count':following_count,
#                                  'followers_count':followers_count})
#         except User.DoesNotExist:
#             return JsonResponse({'error': 'User Doesnt Exist'})
#
#     return JsonResponse({'error': 'Invalid Request'})



@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    if not user_id:
        return JsonResponse({'error': 'Invalid Request'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User Does Not Exist'}, status=404)

    if request.user == user:

        return JsonResponse({'error': "You can't follow yourself"}, status=400)


    contact, created = Contact.objects.get_or_create(user_from=request.user, user_to=user)
    if not created:

        contact.delete()
        follow = False
    else:
        follow = True

    following_count = user.following.count()
    followers_count = user.followers.count()

    return JsonResponse({
        'follow': follow,
        'following_count': following_count,
        'followers_count': followers_count,
    })
