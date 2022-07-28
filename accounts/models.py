from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import Group
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.urls import reverse

# =========================================================
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
# =========================================================


# =================== GROUP для входа через соцсети ===============================
@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    Group.objects.get(name='common').user_set.add(user)
    user.is_staff = True
    user.save()
# =================================================================================


class MyAccountManager(BaseUserManager):

    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(email=self.normalize_email(email), username=username, )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(email, password=password, )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_absolute_url(self):
        return reverse('edit', kwargs={"pk": self.pk})
    # def get_absolute_url(self):
    #     return f'/profile/{self.pk}'


class Account(AbstractBaseUser):
    """ AbstractBaseUser имеет только функцию аутентификации, у него нет фактических полей, вы предоставите поля для
    использования при создании подкласса. Вы также должны указать, какое поле будет представлять имя пользователя,
    обязательные поля и способы управления этими пользователями.
    Допустим, вы хотите использовать электронную почту для аутентификации, Django обычно использует имя пользователя
    для аутентификации, так как же изменить его для использования электронной почты? """

    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=50, verbose_name='first_name')
    last_name = models.CharField(max_length=50, verbose_name='last_name')
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    # birth_date = models.DateField(blank=True, null=True)

    objects = MyAccountManager()

    """USERNAME_FIELD - это строка, описывающая имя поля в пользовательской модели, 
    которое используется в качестве уникального идентификатора. """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    # Для проверки разрешений. Для простоты у всех администраторов есть ВСЕ разрешения
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_perms(self, perm_list, obj=None):
        """ Returns True if the user has each of the specified permissions. If object is passed, it checks if the user
        has all required perms for this object.
        Возвращает True, если у пользователя есть каждое из указанных разрешений. Если объект передан, он проверяет,
        есть ли у пользователя все необходимые разрешения для этого объекта. """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    # У этого пользователя есть разрешение на просмотр этого приложения? (ВСЕГДА ДА ДЛЯ ПРОСТОТЫ)
    def has_module_perms(self, app_label):
        return True
        # return self.is_admin
        # return self.is_superuser

    # class Meta:
    #     db_table = 'auth_user'

# ==============================================================
