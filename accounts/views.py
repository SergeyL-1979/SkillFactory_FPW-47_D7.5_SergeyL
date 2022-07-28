from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import UpdateView

from .models import Account
from news.models import Author, Category

from django.shortcuts import redirect
from .forms import LoginForm, UserEditForm


class UserEdit(UpdateView):
    model = Account
    template_name = 'accounts/edit.html'
    form_class = UserEditForm
    success_url = '/news/'

    # def get_object(self, **kwargs):
    #     id = self.kwargs.get('pk')
    #     return User.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        " Контекст отображение категорий в выпадающем статус баре "
        context['category_name'] = Category.objects.all()
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        context['time_now'] = datetime.now()
        return context

    def get_object(self, **kwargs):
        return self.request.user

    def get_success_url(self):
        return self.request.path


@login_required
def upgrade_me(request='user'):
    user = request.user
    premium_group = Group.objects.get(name='authors')

    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
        Author.objects.create(author_user=user)
    return redirect('/news/')

