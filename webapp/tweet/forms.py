from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class TweetForm(forms.Form):
    text = forms.CharField(
        max_length=280,
        widget=forms.Textarea(attrs={'rows': 7, 'placeholder': 'What’s happening?'}),
        label='Tweet Text'      
    )
    photo = forms.ImageField(required=False, label='Attach Image')


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # ✅ Properly indented
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border rounded-md dark:bg-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 input-transition'
            })

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user





class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 rounded-md bg-black text-white focus:outline-none focus:ring-2 focus:ring-cyan-400 transition',
            'placeholder': 'you@example.com'
        })

        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-2 rounded-md bg-black text-white focus:outline-none focus:ring-2 focus:ring-cyan-400 transition',
            'placeholder': '••••••••'
        })

    
    


      


