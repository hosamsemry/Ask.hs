from django import forms
from .models import UserAccount, UserProfile

class RegisterForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ('email', 'password')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if not password or not confirm_password:
            raise forms.ValidationError("Password is required.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
        self.fields['password'].required = True
        self.fields['password'].widget = forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
        self.fields['confirm_password'] = forms.CharField(
            label='Confirm Password',
            widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
            required=True
        )


    def save(self, commit=True):
        user = super().save(commit=False)
        
        user.set_password(self.cleaned_data['password'])
        user.username = user.email.split("@")[0]

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
    class Meta:
        model = UserProfile
        fields = ['bio', 'picture', 'location', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['picture'].widget.attrs.update({'class': 'form-control'})