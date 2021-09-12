from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy
from django_rest_passwordreset.tokens import get_token_generator

# Create your models here.

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Создание и сохрание пользователя с указанными username, email, and password."""
        if not email:
            raise ValueError('Не указан адрес email')
        if not password:
            raise ValueError('Не указан пароль')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    # username = None
    email = models.EmailField(gettext_lazy('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(gettext_lazy('username'),
                                max_length=150,
                                help_text=gettext_lazy(
                                    'Необходимый. 150 символов или меньше. Только буквы, цифры и @ /. / + / - / _.'),
                                validators=[username_validator],
                                error_messages={'unique': gettext_lazy('Пользователь с таким именем уже существует.')},
                                )
    is_active = models.BooleanField(gettext_lazy('active'),
                                    default=False,
                                    help_text=gettext_lazy('Определяет, следует ли считать этого пользователя активным.'
                                                           'Снимите этот флажок вместо удаления учетных записей.'),
                                    )

    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)


class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city}, ул.{self.street}, дом {self.house} ({self.phone})'


class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE,
                             verbose_name=gettext_lazy("Пользователь, связанный с этим токеном сброса пароля"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=gettext_lazy("Когда был создан этот токен"))
    key = models.CharField(gettext_lazy("Key"), max_length=64, db_index=True, unique=True)

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return f"Токен подтверждения Email для пользователя {self.user}"
