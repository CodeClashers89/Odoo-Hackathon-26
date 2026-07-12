from django import forms
from django.contrib.auth.models import User
from .models import Driver

class DriverForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Driver
        fields = ['name', 'license_number', 'license_category', 'license_expiry_date', 'contact_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_category': forms.Select(choices=[
                ('Heavy', 'Heavy'),
                ('Light', 'Light'),
                ('Commercial', 'Commercial'),
                ('Motorcycle', 'Motorcycle'),
                ('Other', 'Other')
            ], attrs={'class': 'form-control'}),
            'license_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].widget.attrs['readonly'] = True
            # Password not required when editing
            self.fields['password'].help_text = "Leave blank to keep current password."
        else:
            self.fields['username'].required = True
            self.fields['email'].required = True
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not self.instance.pk or (self.instance.pk and not self.instance.user):
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not self.instance.pk or (self.instance.pk and not self.instance.user):
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Email already exists.")
        return email

