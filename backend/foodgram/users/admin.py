from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображение пользователей в админ-панели."""

    list_display = ('pk', 'username', 'first_name', 'last_name',
                    'email', 'password')
    list_editable = ('password',)
    search_fields = ('username', 'date_joined',)
    list_filter = ('is_active',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Отображение подписок в админ-панели."""

    list_display = ('pk', 'user', 'author',)
    list_editable = ('user', 'author',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'
