from rest_framework import serializers
from user_app.models import User, Contact


# Serializer для пользователя
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'user', 'city', 'street', 'house',
                  'structure', 'building', 'apartment', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',
                  'company', 'position', 'contacts')
        read_only_fields = ('id',)


