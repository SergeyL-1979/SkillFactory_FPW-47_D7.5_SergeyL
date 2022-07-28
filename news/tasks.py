from celery import shared_task
from datetime import timedelta, date

from django.core.mail import EmailMultiAlternatives  # импортируем класс для создания объекта письма HTML-шаблон
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш HTML-шаблон в текст

# получаем domain имя. передаем ссылку типа http://127.0.0.1:8001
from django.contrib.sites.shortcuts import get_current_site
from .models import Post

# из settings импортируем email по-умолчанию
from NewsPaper.settings import DEFAULT_FROM_EMAIL


def collect_subscribers(category):
    """ Перебрать всех подписчиков в таблице категорий, извлечь их электронную почту
     и сформировать список получателей электронной почты """
    email_recipients = []
    for user in category.subscribers.all():
        email_recipients.append(user.email)

    return email_recipients


def send_emails(post_object, *args, **kwargs):
    """ Функция подготовки всех постов для передачи любых переменных в шаблон HTML который будет сформирован
    render_to_string и отправлен на почту подписчикам """
    html = render_to_string(
        kwargs['template'],
        {
            # передаем в шаблон любые переменные
            'category_object': kwargs['category_object'],
            # передаем в шаблон любые переменные
            'post_object': post_object,
            # передаем в шаблон domain
            'current_url': ''.join(['http://', get_current_site(None).domain, ':8000'])
        },
    )

    msg = EmailMultiAlternatives(
        # Тема сообщения
        subject=kwargs['email_subject'],
        # Вставляем от кого рассылка
        from_email=DEFAULT_FROM_EMAIL,
        # отправляем всем подписчикам из списка рассылку
        to=kwargs['email_recipients']
    )

    msg.attach_alternative(html, 'text/html')
    msg.send(fail_silently=False)


@shared_task
def week_email_sending():
    """ Функция отправки рассылки подписчикам собранных постов за неделю. С помощью timedelta(days=7) определяем период
    Post.objects.all() - берем все посты и создаем пустой список past_week_posts = [], в который добавим посты созданные
    за timedelta(days=7). """
    week = timedelta(days=7)
    posts = Post.objects.all()
    past_week_posts = []
    template = 'weekly_digest.html'
    email_subject = 'Your News Portal Weekly Digest'

    """ Сортируем посты от сегодняшней даты минусую по дате создания поста и если она меньше timedelta(days=7) то 
    добавляем в список past_week_posts = [] """
    for post in posts:
        time_delta = date.today() - post.create_date.date()
        if time_delta < week:
            past_week_posts.append(post)

    """ Из past_week_categories = set() делаем множество в которое будем 
    добавлять категории формируя их по постам в категориях """
    past_week_categories = set()
    for post in past_week_posts:
        for category in post.post_category.all():
            past_week_categories.add(category)

    """ Из email_recipients_set = set() делаем множество в которое будем 
        добавлять email подписчиков на категорию """
    email_recipients_set = set()
    for category in past_week_categories:
        " Запрос почтового ящика пользователя "
        get_user_emails = set(collect_subscribers(category))
        email_recipients_set.update(get_user_emails)

    """ Из раннего созданного множества email_recipients_set = set() преобразовываем его в список. Сортируем по 
    категория на которые подписаны пользователи. Формируем списки для рассылки. Создаем HTML шаблон для email и 
    делаем рассылку """
    email_recipients = list(email_recipients_set)
    for email in email_recipients:
        post_object = []
        categories = set()

        for post in past_week_posts:
            subscription = post.post_category.all().values('subscribers').filter(subscribers__email=email)
            if subscription.exists():
                post_object.append(post)
                categories.update(post.post_category.filter(subscribers__email=email))

        category_object = list(categories)

        send_emails(
            post_object,
            category_object=category_object,
            email_subject=email_subject,
            template=template,
            email_recipients=[email, ]
        )
