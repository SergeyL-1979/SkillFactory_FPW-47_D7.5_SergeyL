from django.contrib.sites.shortcuts import get_current_site
from django.db.models.signals import m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст

from .models import Post, PostCategory, CategorySubscribers
from NewsPaper.settings import DEFAULT_FROM_EMAIL  # для почтового ящика по умолчанию


@receiver(m2m_changed, sender=PostCategory)
def notify_post_create(sender, instance, action, **kwargs):
    """  С помощью данного метода мы создаем "post_add" который отправляется после добавления одного или нескольких
    объектов. Далее с помощью instance - экземпляр, чье отношение «многие-ко-многим» обновляется, мы можем получить
    все посты всех категорий. С помощью фильтрации получаем категорию на которую подписан пользователь. Формируем
    тему и сообщение с помощью EmailMultiAlternatives, так же получаем список e-mail пользователей для рассылки.
    """
    if action == 'post_add':
        for cat in instance.post_category.all():
            for subscribe in CategorySubscribers.objects.filter(category=cat):

                msg = EmailMultiAlternatives(
                    subject=instance.headline,
                    body=instance.post_text,
                    from_email=DEFAULT_FROM_EMAIL,
                    to=[subscribe.subscriber_user.email],
                )

                " Получения ссылки поста в теле письма "
                full_url = ''.join(['http://', get_current_site(None).domain, ':8000'])

                html_content = render_to_string(
                    'post_create.html',
                    {
                        'posts': instance.post_text,
                        'recipient': subscribe.subscriber_user.email,
                        'category_name': subscribe.category,
                        'subscriber_user': subscribe.subscriber_user,
                        'pk_id': instance.pk,
                        'date': instance.create_date,
                        'current_site': full_url,
                    },
                )

                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # print(f'{instance.headline} {instance.post_text}')
                # print('Уведомление отослано подписчику ',
                #       subscribe.subscriber_user, 'на почту',
                #       subscribe.subscriber_user.email, ' на тему ', subscribe.category)
