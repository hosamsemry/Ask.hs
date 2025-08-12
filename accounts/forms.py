from django import forms
from .models import UserAccount, UserProfile

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        required=True
    )

    class Meta:
        model = UserAccount
        fields = ('email', 'password')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserAccount.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email.split("@")[0]
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user



class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email or not password:
            raise forms.ValidationError("Both fields are required.")
        
        return cleaned_data
    
class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username"
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'bio', 'location', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['picture'].widget.attrs.update({'class': 'form-control'})

        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserAccount.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        username = self.cleaned_data.get('username')
        if username and profile.user.username != username:
            profile.user.username = username
            profile.user.save()
        if commit:
            profile.save()
        return profile
