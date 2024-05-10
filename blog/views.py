from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Prefetch, Count


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count
    }


def get_likes_count(post):
    return post.likes.count()


def index(request):
    tags_prefetch = Prefetch(
        'tags', queryset=Tag.objects.annotate(posts_count=Count('posts'))
    )

    comments_prefetch = Prefetch('comments', queryset=Comment.objects.all())

    most_popular_posts = Post.objects.annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments')
    ).select_related('author').prefetch_related(
        comments_prefetch,
        tags_prefetch
    ).order_by('-likes_count')[:5]

    fresh_posts = Post.objects.annotate(
        comments_count=Count('comments')
    ).select_related('author').prefetch_related(
        comments_prefetch,
        tags_prefetch
    ).order_by('-published_at')[:5]

    most_popular_tags = Tag.objects.annotate(
        posts_count=Count('posts')
    ).order_by('-posts_count')[:5]

    context = {
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        'page_posts': [
            serialize_post_optimized(post) for post in fresh_posts
        ],
        'popular_tags': [
            serialize_tag_optimized(tag) for tag in most_popular_tags
        ],
    }

    return render(request, 'index.html', context)


def serialize_post_optimized(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title if post.tags.all().exists() else None,
    }


def post_detail(request, slug):
    post = Post.objects.prefetch_related(
        Prefetch('comments', queryset=Comment.objects.select_related(
            'author'
        )),
        Prefetch('tags', queryset=Tag.objects.annotate(
            posts_count=Count('posts')
        ))
    ).get(slug=slug)

    serialized_post = serialize_post(post)

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }

    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]
    related_posts = tag.posts.annotate(
        comments_count=Count('comments')
    ).select_related('author').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.annotate(
            posts_count=Count('posts')
        ))
    )[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
    }

    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
