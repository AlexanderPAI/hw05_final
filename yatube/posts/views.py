from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Comment, Follow, Group, Post, User
from .forms import CommentForm, PostForm

POSTS: int = 10


def paginator(request, posts):

    paginator = Paginator(posts, POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.select_related('group')
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    page_obj = paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author')
    count = posts.count()
    page_obj = paginator(request, posts)
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists())
    context = {
        'author': author,
        'user': request.user,
        'count': count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.author.posts.count()
    comments = Comment.objects.select_related('post')
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'count': count,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST' or None:
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': False}
        )
    form = PostForm()
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_author: bool = request.user == post.author
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if is_author:
        if request.method == 'POST' or None:
            if form.is_valid():
                form.save()
                return redirect('posts:post_detail', post_id)
            return render(
                request,
                'posts/create_post.html',
                {'form': form, 'is_edit': True}
            )
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': True}
        )
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # Post.objects.filter(author__follower__user=request.user) слишком
    # тяжело далось, теория и ТЗ как будто вообще на это не наводят((.
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(
            user=user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Отписаться от автора
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = get_object_or_404(
        Follow,
        user=user,
        author=author
    )
    follow.delete()
    return redirect('posts:profile', username=username)
