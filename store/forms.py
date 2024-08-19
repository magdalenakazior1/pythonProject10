from django import forms
from django.contrib.auth.models import User
from .models import Product, Profile, Category, Review, CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'image_url', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'city', 'state', 'zipcode', 'country', 'phone_number']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent_category']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class CustomUserCreationForm(UserCreationForm):
    ACCOUNT_TYPE_CHOICES = [
        ('regular', 'Regular User'),
        ('staff', 'Staff'),
        ('admin', 'Administrator'),
    ]

    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, label="Account Type")
    account_password = forms.CharField(required=False, label="Account Type Password", widget=forms.PasswordInput)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'account_type', 'account_password')

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        account_password = cleaned_data.get('account_password')

        if account_type in ['staff', 'admin'] and account_password != '12345':
            raise forms.ValidationError("Invalid password for selected account type.")

        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')
