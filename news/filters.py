import django
from django_filters import FilterSet, DateFilter
from .models import Post, Author


# class PostFilter(FilterSet):
#     # post_author = Filter(field_name='post_author__author_user__first_name')
#     # headline = CharFilter(field_name='headline', )
#
#     class Meta:
#         model = Post
#         fields = {'post_author__author_user__first_name': ['contains'],
#                   'headline': ['icontains'],
#                   'create_date': ['lte'],
#                   }
class PostFilter(FilterSet):
    create_date = DateFilter(
        lookup_expr='gt',
        widget=django.forms.DateInput(
            attrs={
                'type': 'date'
            }
        )
    )

    class Meta:
        model = Post
        fields = {
            'headline': ['icontains'],
            'post_author__author_user__first_name': ['contains'],
            # 'post_author__author_user__first_name': ['exact'],
        }

# class PostFilter(FilterSet):
#
#     class Meta:
#         model = Post
#         fields = {'post_author__author_user__first_name': ['contains'], 'headline': ['icontains'], 'create_date': ['lte']}
