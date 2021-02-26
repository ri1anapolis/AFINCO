from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ProjectUser


class ProjectUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = ProjectUser
        fields = UserCreationForm.Meta.fields


class ProjectUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = ProjectUser
        fields = UserChangeForm.Meta.fields
