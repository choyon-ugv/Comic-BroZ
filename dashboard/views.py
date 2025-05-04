from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from users.models import  User, Movie, Blog, Comic, Profile, Like, Comment
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.db.models import Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import BlogForm, ComicForm, CommentForm
from users.forms import PasswordChangeForm, ProfileForm, RegisterForm
from users.models import CharacterCard


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None and (user.is_staff or user.is_superuser):
            auth_login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not authorized.")

    return render(request, 'custom_admin/admin_login.html', {})

@login_required(login_url='admin_login')
def admin_logout(request):
    auth_logout(request)
    return redirect('admin_login')

@login_required(login_url='admin_login')
def admin_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password was successfully updated! Please login again.')
            auth_logout(request)
            return redirect('admin_login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'custom_admin/admin_change_password.html', {'form': form})

@login_required
def profile_settings(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        username = request.POST.get('username')
        email = request.POST.get('email')
        if form.is_valid():
            # Update User model
            user = request.user
            user.username = username
            user.email = email
            try:
                user.save()
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile_settings')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profile/profile_settings.html', {
        'form': form,
        'user': request.user
    })

@login_required
def profile_list(request):
    profiles = Profile.objects.filter(user__is_superuser = False, user__is_staff = False)
    context = {
        'profiles' : profiles,
        'active_menu': 'profile',
    }
    return render(request, 'profile/profile_list.html', context)


@login_required
def profile_datatable_view(request):
    # Get DataTables parameters
    draw = int(request.POST.get('draw', 1))
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    order_column = int(request.POST.get('order[0][column]', 0))
    order_dir = request.POST.get('order[0][dir]', 'asc')

    # Map column index to field
    columns = ['id', 'user__username', 'user__email', 'bio', 'level', 'progress']
    order_field = columns[order_column]
    if order_dir == 'desc':
        order_field = f'-{order_field}'

    # Build queryset
    queryset = Profile.objects.filter(user__is_superuser = False, user__is_staff = False)
    if search_value:
        queryset = queryset.filter(
            Q(user__username__icontains=search_value) |
            Q(user__email__icontains=search_value) |
            Q(bio__icontains=search_value)
        )

    # Apply ordering
    queryset = queryset.order_by(order_field)

    # Paginate
    paginator = Paginator(queryset, length)
    page_number = (start // length) + 1
    page_obj = paginator.get_page(page_number)

    # Prepare data
    data = []
    for index, profile in enumerate(page_obj, start=start + 1):
        view_url = reverse('profile_view', args=[profile.pk])
        edit_url = reverse('profile_edit', args=[profile.pk])
        delete_url = reverse('profile_delete', args=[profile.pk])
        data.append({
            'id': index,
            'username': profile.user.username,
            'email': profile.user.email,
            'bio': profile.bio or 'N/A',
            'level': profile.level,
            'progress': f"{profile.progress}%",
            'action': (
                f'<a href="{view_url}" class="btn btn-sm btn-info">View</a> '
                f'<a href="{edit_url}" class="btn btn-sm btn-warning">Edit</a>'
                f'<a href="{delete_url}" class="btn btn-sm btn-danger m-1">Delete</a>'
            )
        })

    # Response
    return JsonResponse({
        'draw': draw,
        'recordsTotal': Profile.objects.filter(user__is_superuser=False, user__is_staff=False).count(),
        'recordsFiltered': paginator.count,
        'data': data
    })


class ProfileView(DetailView):
    model = Profile
    template_name = 'profile/profile_view.html'
    


class ProfileEditView(UpdateView):
    model = Profile
    fields = ['bio', 'level', 'progress', 'profile_image']
    template_name = 'profile/profile_edit.html'
    success_url = reverse_lazy('profile_list')


class ProfileDeleteView(DeleteView):
    model = Profile
    template_name = 'profile/profile_confirm_delete.html'
    success_url = reverse_lazy('profile_list')


# Blogs

def add_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)

        if form.is_valid():
            blog = form.save(commit=False)  # Don't save yet
            blog.author = request.user  # Set the author as the logged-in user
            blog.save()  # Now save it
            return redirect('blog_list')  # Redirect after saving
    else:
        form = BlogForm()

    return render(request, 'add_blog.html', {'form': form})

def blog_list(request):
    blogs = Blog.objects.all().select_related('author')
    print(f"Number of blogs fetched: {blogs.count()}")  # Debug output
    context = {
        'blogs' : blogs,
        'active_menu': 'profile',
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    context = {
        'blog' : blog,
        'active_menu': 'profile',
    }
    return render(request, 'blog/blog_detail.html', context)

def blog_edit(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blog/blog_form.html', {'form':form})

def blog_delete(request, pk ):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        blog.delete()
        return redirect('blog_list')
    return render(request, 'blog/blog_delete.html', {'blog': blog})


# Comics

def add_comic(request):
    if request.method == 'POST':
        form = ComicForm(request.POST, request.FILES)

        if form.is_valid():
            comic = form.save(commit=False)  # Don't save yet
            comic.save()  # Now save it
            return redirect('comic_list')  # Redirect after saving
    else:
        form = ComicForm()

    return render(request, 'add_comic.html', {'form': form})


def comic_list(request):
    comics = Comic.objects.annotate(
        read_count=Count('read_by'),
        favorite_count=Count('favorited_by')
    )

    max_read = comics.order_by('-read_count').first()
    max_favorite = comics.order_by('-favorite_count').first()

    context = {
        'comics': comics,
        'max_read_id': max_read.id if max_read else None,
        'max_favorite_id': max_favorite.id if max_favorite else None,
    }
    return render(request, 'comic/comic_list.html', context)

def comic_detail(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    context = {
        'comic' : comic
    }
    return render(request, 'comic/comic_detail.html', context)


def comic_edit(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    if request.method == 'POST':
        form = ComicForm(request.POST, request.FILES, instance=comic)
        if form.is_valid():
            form.save()
            return redirect('comic_list')
    else:
        form = ComicForm(instance=comic)
    return render(request, 'comic/comic_edit.html', {'form': form, 'comic': comic})

def comic_delete(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    if request.method == 'POST':
        comic.delete()
        return redirect('comic_list')
    return render(request, 'comic/comic_delete.html', {'comic': comic})


# Like

def like_list(request):
    likes = Like.objects.all()
    context = {
        'likes' : likes
    }
    return render(request, 'like/like_list.html', context)


def edit_like(request, like_id):
    like = get_object_or_404(Like, id=like_id)
    blogs = Blog.objects.all() 

    if request.method == 'POST':

        user = request.user
        blog_id = request.POST.get('blog')
        blog = Blog.objects.get(id=blog_id)
        

        if Like.objects.filter(user=user, blog=blog).exists():

            return render(request, 'like/edit_like.html', {
                'like': like,
                'blogs': blogs,
                'error_message': 'You have already liked this blog.'
            })

        like.blog = blog
        like.save()

        return redirect('like_list') 

    return render(request, 'like/edit_like.html', {'like': like, 'blogs': blogs})


def delete_like(request, like_id):
    like = get_object_or_404(Like, id=like_id)
    
    if request.method == 'POST':
        like.delete()  
        return redirect('like_list')
    
    return render(request, 'like/delete_like.html', {'like': like})
        


# Comment

def comment_list(request):
    comments = Comment.objects.all()
    context = {
        'comments' : comments
    }
    return render(request, 'comment/comment_list.html', context)


def comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    context = {
        'comment':comment
    }
    return render(request, 'comment/comment_view.html', context)


def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method =="POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('comment_list')
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment
    }
    return render(request, 'comment/comment_edit.html', context)

def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method =="POST":
        comment.delete()
        return redirect('comment_list')
    context = {
        'comment' : comment
    }
    return render(request, 'comment/delete_comment.html', context)

# admin dashboard customize
@login_required(login_url='admin_login')
@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_movies = Movie.objects.count()
    total_blog = Blog.objects.count()
    total_comic = Comic.objects.count()
    
    context ={
        'total_users': total_users,
        'total_movies': total_movies,
        'total_blog': total_blog,
        'total_comic': total_comic, 
    }
    return render(request, 'custom_admin/admin_index.html', context)



def character_card_list(request):
    characters = CharacterCard.objects.all()
    return render(request, 'card/card_list.html', {'character_cards': characters})