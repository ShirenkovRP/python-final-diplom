from django.contrib import admin

# Register your models here.
from user_app.models import User, Contact, ConfirmEmailToken

admin.site.register(User)
admin.site.register(Contact)
admin.site.register(ConfirmEmailToken)


