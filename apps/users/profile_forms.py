# Імпорт базових форм Django
from django import forms

# Стандартна модель користувача Django
from django.contrib.auth.models import User

# Модель профілю користувача
from .models import Profile

# ФОРМА РЕДАГУВАННЯ ПРОФІЛЮ
class ProfileEditForm(forms.ModelForm):
    # Поля, які належать не Profile, а User
    email = forms.EmailField(
        required=True,
        label='Email'
    )

    first_name = forms.CharField(
        max_length=50,
        required=False,
        label="Ім'я"
    )

    last_name = forms.CharField(
        max_length=50,
        required=False,
        label='Прізвище'
    )

    class Meta:
        # Форма працює з моделлю Profile
        model = Profile

        # Поля, які редагуються в Profile
        fields = ['avatar', 'phone', 'address']

    # ІНІЦІАЛІЗАЦІЯ ФОРМИ
    def __init__(self, *args, **kwargs):

        # Витягуємо користувача з аргументів форми
        user = kwargs.pop('user', None)

        # Викликаємо стандартний __init__
        super().__init__(*args, **kwargs)

        # Додаємо CSS класи для стилізації інпутів
        self.fields['avatar'].widget.attrs['class'] = 'form-input'
        self.fields['phone'].widget.attrs['class'] = 'form-input'
        self.fields['address'].widget.attrs['class'] = 'form-input'

        self.fields['email'].widget.attrs['class'] = 'form-input'
        self.fields['first_name'].widget.attrs['class'] = 'form-input'
        self.fields['last_name'].widget.attrs['class'] = 'form-input'

        # Зберігаємо user для використання в save()
        self.user = user

        # Якщо користувач переданий - підставляємо його дані у форму
        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    # ЗБЕРЕЖЕННЯ ДАНИХ
    def save(self, commit=True):

        # Зберігаємо Profile, але поки без запису в БД
        profile = super().save(commit=False)

        # Отримуємо користувача
        user = self.user

        # Оновлюємо дані User (не Profile)
        if user:
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']

            # Зберігаємо User
            if commit:
                user.save()

        # Зберігаємо Profile
        if commit:
            profile.save()

        return profile