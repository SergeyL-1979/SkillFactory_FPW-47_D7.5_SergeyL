from django.forms import ModelForm, Select, Textarea, TextInput, SelectMultiple, CharField
from .models import Post, Comment


class PostForm(ModelForm):
    # check_box = BooleanField(label='Ало, Галочка!')
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['post_author'].empty_label = 'Автор не выбран'

    class Meta:
        model = Post
        # fields = ['post_author', 'headline', 'position', 'post_category', 'post_text', ]
        fields = ['headline', 'position', 'post_category', 'post_text', ]

        widgets = {
            'headline': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок поста'
            }),
            'post_text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите текст...'
            }),
            # 'post_author__author_user': Select(attrs={
            #     'class': 'custom-select',
            #     'option selected': 'Выбрать автора'
            # }),
            'position': Select(attrs={
                'class': 'custom-select',
                'option selected': 'Выбрать тип'
            }),
            'post_category': SelectMultiple(attrs={
                'multiple class': 'form-control',
            }),
        }


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        # fields = '__all__'
        # fields = ['comment_user', 'comment_text', ]
        fields = ['comment_text', ]

        widgets = {
            # 'comment_user': Select(attrs={
            #     'class': 'custom-select',
            #     'option selected': 'Выбрать автора'
            # }),
            'comment_text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите текст...'
            }),
        }
