from django.contrib import admin
from .models import State, Lga, CustomUser, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import SignUpForm, UserChangeForm, UserCreationForm
from django.conf import settings
import datetime
from .models import CustomUser as User


# Register your models here.
@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Lga)
class LgaAdmin(admin.ModelAdmin):
    list_display = ('state', 'name')


def assign_id(modeladmin, request, queryset):
    date = datetime.datetime.now()
    year = date.strftime("%Y")[1:]
    id_count = User.objects.filter(membership_id__isnull=False).count()
    i = 1
    for user in queryset:
        user.membership_id = f'GRTP/KN/{year}/{str(id_count + i).zfill(5)}'
        user.save()
        i += 1


assign_id.short_description = 'Assign id to selected user(s)'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ('email', 'first_name', 'middle_name', 'last_name', 'membership_id', 'phone', 'reg_approved',
                    'is_active', 'is_admin', 'is_staff', )
    list_filter = ('reg_approved', 'is_active', 'is_staff', )

    fieldsets = (
        (None, {'fields': ('email', 'is_active', 'is_staff', 'is_admin', 'reg_approved', 'password')}),
        ('Personal info', {'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone',
                                      'membership_id')}),
        ('Groups', {'fields': ()}),
        ('Permissions', {'fields': ()}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'is_active', 'is_staff', 'is_admin', 'reg_approved', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'phone',
                                      'membership_id')}),
        ('Groups', {'fields': ()}),
        ('Permissions', {'fields': ()}),
    )

    search_fields = ('email', 'first_name', 'last_name', 'phone', 'membership_id')
    ordering = ('email',)
    filter_horizontal = ()
    readonly_fields = ('membership_id', )
    actions = [assign_id, ]
    inlines = (ProfileInline, )


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'membership_id', 'address',  'state', 'lg', 'hometown', 'job_name', )
    # list_filter = ('lg', )

    def user_name(self, obj):
        return f'{obj.user.first_name} {obj.user.middle_name} {obj.user.last_name}'

    def membership_id(self, obj):
        return obj.user.membership_id
