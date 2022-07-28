from django import forms
from django.contrib.auth.models import Group, User
from allauth.account.forms import LoginForm, SignupForm, ChangePasswordForm
from .models import Account


# ====================  Мой код формы регистрации  ==============================================
class MyCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=20, label='Имя',
                                 widget=forms.TextInput(attrs={'class': 'form-label',
                                                               'placeholder': 'Имя', }))
    last_name = forms.CharField(max_length=20, label='Фамилия',
                                widget=forms.TextInput(attrs={'class': 'form-label',
                                                              'placeholder': 'Фамилия', }))

    # birth_date = forms.DateField(label="Дата рождения", initial=datetime.date.today,
    #                              widget=forms.DateInput(attrs={'class': 'form-control',
    #                                                            'id': "example-date-input",
    #                                                            'type': 'date'}))

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.is_active = self.cleaned_data['is_active']
        # user.birth_date = self.cleaned_data['birth_date']
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        user.is_staff = True
        user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', )

# ==== ТЕСТ СМЕНЫ ПАРОЛЯ =========================

