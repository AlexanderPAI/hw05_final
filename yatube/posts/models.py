from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Выберите группу'
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите изображение',
    )

    # Аргумент upload_to указывает директорию,
    # в которую будут загружаться пользовательские файлы.

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Пост, к которому оставляется комментарий'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор комментария'
    )

    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )

    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Пользователь, который подписался на автора'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='following',
        verbose_name='Автор'
    )
