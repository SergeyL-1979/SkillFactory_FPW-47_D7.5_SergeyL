from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.text import slugify


class Author(models.Model):
    """ Модель Автора. Модель рейтинга с дефолтным значение равное 0"""
    author_user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Автор')
    author_rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг автора')

    " Функция подсчета рейтинга пользователя "
    def update_rating(self):
        rating_post = self.post_set.aggregate(postRating=Sum('post_rating'))
        postRat = 0
        postRat += rating_post.get('postRating')
        print(postRat)

        rating_comment = self.author_user.comment_set.aggregate(commentRating=Sum('comment_rating'))
        comRat = 0
        comRat += rating_comment.get('commentRating')

        self.author_rating = postRat * 3 + comRat
        self.save()

    " Возвращает автора с наивысшим рейтингом "
    @staticmethod
    def best_author():
        return Author.objects.all().order_by('-author_rating')[0]

    def __str__(self):
        return f"{self.author_user}"

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Category(models.Model):
    """ Модель Category(КАТЕГОРИЯ) связующая модель CategorySubscribers(ПОДПИСЧИКОВ НА КАТЕГОРИЮ) """
    category_name = models.CharField(max_length=64, unique=True, verbose_name='Имя категории')
    subscribers = models.ManyToManyField(User, blank=True, through='CategorySubscribers')

    def __str__(self):
        # return f"Категория: {self.category_name}"
        return '{}'.format(self.category_name)

    def save(self, *args, **kwargs):
        if not self.category_name:
            self.category_name = slugify(str(self.category_name))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class CategorySubscribers(models.Model):
    """ Модель ПОДПИСКИ на КАТЕОРИЮ """
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, verbose_name='Категория')
    subscriber_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name='Подписчик')
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    # subscriber_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Подписчик')

    def __str__(self):
        # return f"Подписка на категорию: {self.category}, {self.subscriber_user}"
        return f'{self.subscriber_user} подписан на категорию {self.category}'

    class Meta:
        verbose_name = 'Категория подписки'
        verbose_name_plural = 'Категории подписок'


class Post(models.Model):
    """ Модель выбора публикации СТАТЬИ или НОВОСТИ.
     Эта модель должна содержать в себе статьи или новости, которые создают пользователи"""
    post_article = 'PA'
    post_news = 'PN'

    POSITIONS = ((post_article, 'Статья'), (post_news, 'Новость'))
    position = models.CharField('Тип', max_length=2, choices=POSITIONS, default=post_article)

    post_author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    slug = models.CharField(max_length=250, db_index=True)

    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_date = models.DateTimeField(auto_now=True)
    post_category = models.ManyToManyField(Category, through='PostCategory', help_text='Соединить категорию')
    headline = models.CharField(max_length=128, name=False, verbose_name='Заголовок')
    post_text = models.TextField(null=False, verbose_name='Текст')
    post_rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг')

    " Добавим абсолютный путь чтобы после создания нас перебрасывало на главную страницу "
    def get_absolute_url(self):
        # return reverse('news:post_detail', kwargs={"slug": self.slug})
        return reverse('post_detail', kwargs={"pk": self.pk})  # возможен переход по id статьи\новости

    def save(self, *args, **kwargs):
        value = self.headline
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        # return self.headline[0:124] + '...'
        return '{0}...{1}'.format(self.headline[0:124], "...")

    " Строковое отображение поста "
    def __str__(self):
        return f"Автор: {self.post_author.author_user.first_name}, Заголовок: {self.headline}, Текст: {self.post_text}, Рейтинг: {self.post_rating}"

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class PostCategory(models.Model):
    """ Промежуточная модель для связи «многие ко многим» """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост в категории')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    def __str__(self):
        return f'{self.category}, Пост: {self.post}'

    class Meta:
        verbose_name = 'Связь категории'
        verbose_name_plural = 'Связь категории'


class Comment(models.Model):
    """ Модуль хранения комментариев под постами """
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост')
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    comment_text = models.TextField(verbose_name='Текст комментария')
    comment_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата написания')
    comment_rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг комментария')

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()

    # " Выводит все комментарии из поста с наивысшим рейтингом "
    # @staticmethod
    # def all_comments_for_best_post():
    #     best_post = Comment.objects.filter(post=Post.find_best_post())
    #     for i in best_post:
    #         print(i)

    " Строковое отображение комментария "
    def __str__(self):
        return 'Пользователь: {} Текст: {} Рейтинг: {} * '.format(self.comment_user, self.comment_text, self.comment_rating)
        # return f'Пользователь: {self.comment_user}, Текст: {self.comment_text}, Рейтинг: {self.comment_rating}, {self.comment_post}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


# =================== GROUP ==============================
# @receiver(user_signed_up)
# def user_signed_up_(request, user, **kwargs):
#     Group.objects.get(name='common').user_set.add(user)
#     user.save()
