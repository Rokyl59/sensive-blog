from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class CommentQuerySet(models.QuerySet):
    def with_post_info(self):
        return self.select_related('post', 'author')


class CommentManager(models.Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(posts_count=Count('posts')
                             ).order_by('-posts_count')

    def with_posts_count(self):
        return self.annotate(posts_count=Count('posts'))


class TagManager(models.Manager):
    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()

    def with_posts_count(self):
        return self.get_queryset().with_posts_count()


class PostQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(likes_count=Count('likes')
                             ).order_by('-likes_count')

    def with_related_data(self):
        return self.select_related('author').prefetch_related(
            Prefetch('tags', queryset=Tag.objects.with_posts_count()),
            Prefetch('comments', queryset=Comment.objects.all())
        ).annotate(
            comments_count=Count('comments'),
            likes_count=Count('likes')
        )


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def popular(self):
        return self.get_queryset().popular()

    def with_related_data(self):
        return self.get_queryset().with_related_data()


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagManager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')
    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    objects = CommentManager()

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
