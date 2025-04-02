from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from .forms import PostForm, CommentForm, ProfileForm, CustomUserCreationForm
from .models import Post, Comment, Profile, Category, College
from django.urls import reverse
from PIL import Image  # Import for image resizing

# Display a list of posts (University-wide & College-specific)
def post_list(request):
    # Fetch all colleges from the College model
    colleges = College.objects.all()
    categories = Category.objects.all()

    selected_college = request.GET.get('college', '')
    selected_category = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'newest')

    posts = Post.objects.all()

    if selected_college:
        posts = posts.filter(author__profile__college__name=selected_college)
    if selected_category:
        posts = posts.filter(category__name=selected_category)

    if sort_by == 'oldest':
        posts = posts.order_by('created_at')
    else:
        posts = posts.order_by('-created_at')

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {
        'posts': page_obj,
        'colleges': colleges,
        'categories': categories,
        'selected_college': selected_college,
        'selected_category': selected_category,
        'sort_by': sort_by,
    })


# Show post details and allow commenting
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to comment.")
            return redirect(f"{reverse('login')}?next={request.path}")
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Your comment has been posted.")
            return redirect('post_detail', post_id=post.pk)
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })

# User registration with automatic assignment to "blog users" group
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('post_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'blog/register.html', {'form': form})

# User login view
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('post_list')
        else:
            messages.error(request, "Login failed. Please check your credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

# User profile page
@login_required
def profile(request):
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        user_profile = None
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=user_profile)
    return render(request, 'blog/profile.html', {'form': form})

# Resize uploaded image
def resize_image(image_path, max_size=(800, 800)):
    """Resize the uploaded image to a max size (800x800) while maintaining aspect ratio."""
    img = Image.open(image_path)
    img.thumbnail(max_size)  # Resize while maintaining aspect ratio
    img.save(image_path)  # Overwrite the original image

# Create a post (Restricted: only staff or "leaders" group)
@login_required
def post_create(request):
    # Only allow staff or users in the 'leaders' group to create a post.
    if not request.user.is_staff and not request.user.groups.filter(name='leaders').exists():
        messages.error(request, "You do not have permission to create a post.")
        return redirect('post_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # For non-admin users, if the college is not provided, use the college from their profile.
            if not request.user.is_staff and not post.college:
                if hasattr(request.user, 'profile'):
                    post.college = request.user.profile.college

            post.save()

            # Resize the uploaded image if present
            if hasattr(post, 'image') and post.image:
                resize_image(post.image.path)

            messages.success(request, "Post created successfully!")
            return redirect('post_list')
    else:
        form = PostForm(user=request.user)
    
    return render(request, 'blog/post_create.html', {'form': form})

# Edit a post (Allowed for the author, staff, or "leaders" group)
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author and not (request.user.is_staff or request.user.groups.filter(name='leaders').exists()):
        messages.error(request, "You do not have permission to edit this post.")
        return redirect('post_list')
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            post = form.save()

            # Resize new uploaded image
            if post.image:
                resize_image(post.image.path)

            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', post_id=post.pk)
    else:
        form = PostForm(instance=post, user=request.user)
    return render(request, 'blog/post_edit.html', {'form': form, 'post': post})

# Delete a post (Allowed for the author, staff, or "leaders" group)
@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author and not (request.user.is_staff or request.user.groups.filter(name='leaders').exists()):
        messages.error(request, "You do not have permission to delete this post.")
        return redirect('post_list')
    
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('post_list')

    return render(request, 'blog/post_delete.html', {'post': post})
