from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, PermissionDenied
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
# from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.views import generic
from .models import Post, Comment, Category, PostCategory, Author, CategorySubscribers
from .filters import PostFilter
from .forms import PostForm, CommentForm
from NewsPaper.settings import DEFAULT_FROM_EMAIL


class NewsList(generic.ListView):
    """ Вывод из базы данных всех постов. Так же сортировка по дате, от самой свежей новости до старой
    с помощью ordering = ['-create_date'].
    paginate_by - позволяет выводить указанное количество постов на страницу """
    model = Post
    context_object_name = "post_list"
    ordering = ['-create_date']
    paginate_by = 5

    """ get_context_data() - Этот метод используется для заполнения словаря для использования в качестве контекста 
    шаблона. Например, ListViews заполнит результат из get_queryset() как object_list. Вероятно, вы будете чаще 
    всего переопределять этот метод, чтобы добавлять объекты для отображения в ваших шаблонах. """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        " Контекст проверки пользователя является ли он в составе группы 'authors' "
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        " Отображение категорий в выпадающем статус баре "
        context['category_name'] = Category.objects.all()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class NewsDetail(generic.edit.FormMixin, generic.DetailView):
    """ Выводим полностью все данные поста: заголовок поста, дату его создания, сам текст поста, автора поста,
    рейтинги поста и автора. Так же тут видим и комментарии к этому посту, автора комментария и рейтинг комментария. """
    model = Post
    context_object_name = 'post_detail'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        " Отображение категорий в выпадающем статус баре "
        context['category_name'] = Category.objects.all()
        context['comment_list'] = Comment.objects.filter(comment_post=self.kwargs['pk'])
        " Контекст для отображения категории в посте "
        # context['post_category'] = PostCategory.objects.get(post=self.kwargs['pk']).category
        " Тут создан фильтр если выбрано несколько категорий на один пост "
        context['post_category'] = Category.objects.filter(post=self.kwargs['pk'])
        context['form'] = self.get_form()
        return context

    # ========= Реализация добавления комментариев из веб интерфейса ==================
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # @login_required
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.comment_post = self.get_object()
        comment.comment_user = self.request.user  # ОСТАВЛЯЕТ КОММЕНТАРИЙ АВТОРИЗОВАНЫМ ПОЛЬЗОВАТЕЛЕМ
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.kwargs.get('pk')})
    # ========= Конец кода по созданию комментариев из веб интерфейса ===================


class CategoryDetail(LoginRequiredMixin, generic.DetailView):
    """ Выводим список категорий. Далее фильтруем посты по категориям и делаем вывод всех постов
    относящихся к данной категории. """
    model = Category
    context_object_name = 'category_detail'

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        context = super().get_context_data(**kwargs)
        " Контекст отображение категорий в выпадающем статус баре "
        context['category_name'] = Category.objects.all()
        " Контекст для списка постов в текущей категории. "
        context['category_news'] = Post.objects.filter(post_category=id)
        " Контекст постов данной категории. "
        context['post_category'] = PostCategory.objects.get(post=self.kwargs['pk']).category
        " Контекст подписан ли пользователь на текущую категорию. .exists() возвращает булево значение "
        context['is_subscribers'] = CategorySubscribers.objects.filter(category=id, subscriber_user=self.request.user).exists()
        return context


class SearchListViews(NewsList):
    """ Модель создания страницы поиска постов по созданному фильтру в файле filters.py с помощью django_filters.
     Создаем фильтр модель и забираем отфильтрованные объекты переопределяя метод get_context_data
     у наследуемого класса (привет, полиморфизм, мы скучали!!!)
    """
    model = Post
    template_name = 'search_list.html'
    context_object_name = 'search'  # имя списка

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


# =============== Создаем классы UpdateView - обновление, CreateView - создание, DeleteView - удаление ===============
class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    """ С помощью данного класса будет создавать посты взаимодействую с веб интерфейсом.
     LoginRequiredMixin - служит для проверки авторизации пользователя, PermissionRequiredMixin - служит
     для проверки выданных разрешения пользователю. Настраивается через permission_required = 'news.add_post'
    """
    model = Post
    # template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('news.add_post', )

    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), None)

    # def handle_no_permission(self):
    #     if self.raise_exception or self.request.user.is_authenticated:
    #         raise PermissionDenied(self.get_permission_denied_message())
    #     return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

    # ============== КОД ВОЗМОЖНОСТИ СОЗДОВАТЬ НЕСКОЛЬКО СТАТЕЙ В ДЕНЬ ===========================
    def post(self, request, *args, **kwargs):
        """ Берем id пользователя который авторизован """
        user = Author.objects.get(author_user=self.request.user.id)
        " Получаем дату "
        d_from = timezone.now().date().today()
        # print(d_from)
        d_to = d_from + timedelta(days=1)
        " Делаем фильтрацию по дате создания поста и по id авторизованного пользователя "
        posts = Post.objects.filter(create_date__range=(d_from, d_to), ).filter(post_author=user)
        # print(posts)
        " Сравниваем длину по ранее созданному фильтру и если длина больше двух то переходим на страницу пользователя "
        if len(posts) > 2:  # считает индекс постов в их длине
            return redirect(to='/my_post')
        return super().post(request)
    # ============== КОНЕЦ КОДА НЕСКОЛЬКИ СТАТЕЙ В ДЕНЬ ==========================================

    """ Функция для кастомный валидации полей формы модели """
    def form_valid(self, form):
        """ Создаем форму, но не отправляем его в БД, пока просто держим в памяти """
        fields = form.save(commit=False)
        """ Через request передаем недостающую форму, которая обязательно 
        делаем на моменте авторизации и создании прав стать автором """
        fields.post_author = Author.objects.get(author_user=self.request.user)
        """ Наконец сохраняем в БД """
        fields.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        context['time_now'] = datetime.now()
        return context


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    """ С помощью данного класса мы будем редактировать посты взаимодействую с веб интерфейсом.
     LoginRequiredMixin - служит для проверки авторизации пользователя, PermissionRequiredMixin - служит
     для проверки выданных разрешения пользователю. Настраивается через permission_required = 'news.change_post'
     """
    form_class = PostForm
    template_name = 'post_update.html'
    permission_required = ('news.change_post', )
    success_url = '/news/'

    " метод get_object чтобы получить информацию об объекте который мы собираемся редактировать "
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    """ Функция для кастомной валидации полей формы модели """
    def form_valid(self, form):
        """ создаем форму, но не отправляем его в БД, пока просто держим в памяти """
        fields = form.save(commit=False)
        """ Через реквест передаем недостающую форму, которая обязательно 
        делаем на моменте авторизации и создании прав стать автором """
        fields.post_author = Author.objects.get(author_user=self.request.user)
        """ Наконец сохраняем в БД """
        fields.save()
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        context['time_now'] = datetime.now()
        return context


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    """ Класс с помощью, которого можно удалять посты взаимодействую с веб интерфейсом """
    queryset = Post.objects.all()
    permission_required = 'news.delete_post'
    success_url = '/news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        context['time_now'] = datetime.now()
        return context

# ================= Завершение создания классов UpdateView, CreateView, DeleteView =========================


# ==== Начало кода, где буде реализовано вывод постов авторизированного пользователя, который автор =========
class PostAuthorView(generic.ListView):
    """ Вьюшка позволяющая показывать все созданные посты авторизированного пользователя,
    который является автором, после подтверждения и нажатия кнопки 'Хочу стать автором'
    """
    model = Post
    context_object_name = 'post_author_view'

    def get_queryset(self):
        return Author.objects.filter(author_user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        " Отображение категорий в выпадающем статус баре "
        context['category_name'] = Category.objects.all()
        " Контекст который отфильтровывает посты авторизованного пользователя и выводит их "
        context['my_author'] = Post.objects.filter(post_author__author_user=self.request.user)
        " Контекст вывода категорий подписки пользователя "
        context['my_subscribers'] = CategorySubscribers.objects.filter(subscriber_user=self.request.user)
        return context

# ================== Конец кода автора постов ==============================================================


# ========= КОД ДЛЯ СОЗДАНИЯ ПОДПИСКИ НА КАТЕГОРИЮ ОТПРАВКИ НА ПОЧТУ СООБЩЕНИЯ =============================
@login_required
def follow_user(request):
    """ Достаем текущего пользователя """
    user = request.user
    " Получаем ссылку из адресной строки и берем pk как id категории "
    id = request.META.get('HTTP_REFERER')[-2]
    " Получаем текущую категорию "
    category = Category.objects.get(id=id)
    " Создаем связь между пользователем и категорией "
    category.subscribers.add(user)
    " Сериалезируем переменные для передачи в селери "
    category = f'{category}'
    email = f'{user.email}'
    # success_url = f'/news/category/{category.join(id)}'
    # вызываем таск для асинхронной отправки письмо
    # send_mail_subscribe.delay(category, email)
    send_mail(
        subject=f'{category}',
        message=f'Вы {request.user.first_name} подписались на обновление категории {category}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[email, ],
    )
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unfollow_user(request):
    """ Достаем текущего пользователя """
    user = request.user
    " Получаем ссылку из адресной строки и берем pk как id категории "
    id = request.META.get('HTTP_REFERER')[-2]
    " Получаем текущую категорию "
    category = Category.objects.get(id=id)
    " Разрываем связь между пользователем и категорией "
    category.subscribers.remove(user)
    " Сериалезируем переменные для передачи в селери "
    category = f'{category}'
    email = f'{user.email}'
    # success_url = f'/news/category/{category.join(id)}'
    # вызываем таск для асинхронной отправки письмо
    # send_mail_unsubscribe.delay(category, email)
    send_mail(
        subject=f'{category}',
        message=f'Вы {request.user.first_name} отписались от обновлений {category}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[email, ]
    )
    return redirect(request.META.get('HTTP_REFERER'))
# =============================================================================================


# ============= Реализация повышения рейтинга =================================

# def add_like(request):
#     if request.POST:
#         pk = request.POST.get('pk')
#         post = Post.objects.get(id=pk)
#         post.like()
#         # post.postAuthor.update_rating()
#     return redirect(request.META.get('HTTP_REFERER'))


# @login_required
# def add_like(request):
#     if request.POST:
#         pk = request.POST.get('pk')
#         post = Post.objects.get(pk=pk)
#         post.like()
#         # post.postAuthor.update_rating()
#     return redirect(request.META.get('HTTP_REFERER'))
