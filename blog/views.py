# blog/views.py
from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag
from django.db.models import Count
from blog.serializers import serialize_post, serialize_tag


def index(request):
    most_popular_posts = Post.objects.popular().with_related_data()[:5]
    fresh_posts = Post.objects.with_related_data().order_by('-published_at')[:5]
    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post, optimized=True) for post in most_popular_posts],
        'page_posts': [
            serialize_post(post, optimized=True) for post in fresh_posts],
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags],
    }

    return render(request, 'index.html', context)


def get_likes_count(post):
    return post.likes.count()


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.with_related_data(), slug=slug)
    serialized_post = serialize_post(post, optimized=True)
    likes_count = post.likes_count
    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'post': serialized_post,
        'likes_count': likes_count,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }

    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)
    most_popular_tags = Tag.objects.popular()[:5]
    related_posts = tag.posts.with_related_data()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags],
        'posts': [
            serialize_post(post, optimized=True) for post in related_posts],
    }

    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
