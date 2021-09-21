from django import forms
from Common.models import Corporate_Login

from Common.models import Corporate_Agent
from Common.models import Corporate


class Corporate_Login_Form(forms.ModelForm):
    class Meta:
        model = Corporate_Login
        fields = "__all__"


class Corporate_Agent_Login_Form(forms.ModelForm):
    class Meta:
        model = Corporate_Agent
        fields = ['email','password','status','user_name']


class Corporate_Form(forms.ModelForm):
    class Meta:
        model = Corporate
        fields = "__all__"