from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from orders.celery import send_email
from .serializers import UserSerializer, ContactSerializer
from .models import ConfirmEmailToken, Contact


# Create your views here.
class RegisterUser(APIView):
    """Регистрация покупателя"""
    throttle_scope = 'register'


    def post(self, request, *args, **kwargs):
        """
        Метод проверяет наличие обязательных полей, сложность пароля,
        уникальность имени пользователя, после чего сохраняет пользователя в системе.
        """
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return Response({'status': False, 'error': {'password': password_error}},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()

                    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user.id)
                    return Response({'status': True, 'токен для подтверждения электронной почты': token.key},
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response({'status': False, 'error': user_serializer.errors},
                                    status=status.HTTP_403_FORBIDDEN)
        return Response({'status': False, 'error': 'Не указаны необходимые поля'},
                        status=status.HTTP_400_BAD_REQUEST)


class ConfirmAccount(APIView):
    """Подтверждение регистрации"""
    throttle_scope = 'anon'
    # Регистрация методом POST

    def post(self, request, *args, **kwargs):
        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True})
            else:
                return Response({'Status': False, 'Errors': 'Неправильно указан токен или email'})
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class LoginUser(APIView):
    """Класс для авторизации"""
    throttle_scope = 'anon'

    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'status': True, 'token': token.key})
            return Response({'status': False, 'error': 'Не удалось войти'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'status': False, 'error': 'Не указаны необходимые поля'},
                        status=status.HTTP_400_BAD_REQUEST)


class UserDetails(APIView):
    """Класс для работы с данными пользователя"""
    throttle_scope = 'user'

    def get(self, request, *args, **kwargs):
        """возвращает все данные пользователя"""
        if not request.user.is_authenticated:
            return Response({'Status': False,
                             'Error': 'Требуется авторизация'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """изменения данных пользователя """
        if {'password'}.issubset(request.data):
            if 'password' in request.data:
                try:
                    validate_password(request.data['password'])
                except Exception as password_error:
                    return Response({'status': False, 'error': {'password': password_error}},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    request.user.set_password(request.data['password'])
            user_serializer = UserSerializer(request.user, data=request.data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
                return Response({'status': True}, status=status.HTTP_200_OK)
            else:
                return Response({'status': False, 'error': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы(Password)'})


class ContactView(APIView):
    """Класс для работы с контактами пользователя"""
    throttle_scope = 'user'

    def get(self, request, *args, **kwargs):
        """получение контактов"""
        if not request.user.is_authenticated:
            return Response({'Status': False,
                             'error': 'Требуется авторизация'}, status=status.HTTP_403_FORBIDDEN)
        contact = Contact.objects.filter(user__id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """добавление контакта"""
        if not request.user.is_authenticated:
            return Response({'Status': False,
                             'error': 'Требуется авторизация'}, status=status.HTTP_403_FORBIDDEN)
        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': True}, status=status.HTTP_201_CREATED)
            else:
                Response({'status': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': False, 'error': 'Не указаны необходимые поля'},
                        status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, *args, **kwargs):
        """изменение контакта"""
        if not request.user.is_authenticated:
            return Response({'status': False,
                             'error': 'Требуется авторизация'}, status=status.HTTP_403_FORBIDDEN)
        if {'id'}.issubset(request.data):
            try:
                contact = Contact.objects.get(pk=int(request.data["id"]))
            except ValueError:
                return Response(
                    {'status': False, 'error': 'Неверный тип поля ID.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ContactSerializer(contact, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': True}, status=status.HTTP_200_OK)

            return Response({'status': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': False, 'error': 'Не указаны необходимые поля'},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """удаляет информацию о контактных дынных покупателя"""
        if not request.user.is_authenticated:
            return Response({'status': False,'error': 'Требуется авторизация'},status=status.HTTP_403_FORBIDDEN)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return Response({'status': True,
                                 'Удалено объектов': deleted_count},
                                status=status.HTTP_200_OK)
        return Response({'status': False,
                         'error': 'Не указаны все необходимые аргументы'},
                        status=status.HTTP_400_BAD_REQUEST)
