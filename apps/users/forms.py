# Імпортуємо базові форми Django
from django import forms

# Вбудована форма реєстрації користувача (включає парольні перевірки)
from django.contrib.auth.forms import UserCreationForm

# Стандартна модель користувача Django
from django.contrib.auth.models import User

# ФОРМА РЕЄСТРАЦІЇ КОРИСТУВАЧА
class RegisterForm(UserCreationForm):
    # Додаємо поле email (воно не входить стандартно в UserCreationForm)
    email = forms.EmailField(
        required=True,
        label='Email'
    )

    # Додаємо ім'я користувача (не обов'язкове поле)
    first_name = forms.CharField(
        max_length=50,
        required=False,
        label='Ім\'я'
    )

    class Meta:
        # Вказуємо, що форма працює з моделлю User
        model = User

        # Поля, які будуть відображатися у формі
        fields = [
            'username',
            'first_name',
            'email',
            'password1',
            'password2'
        ]

    # Перевизначення ініціалізації форми
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Додаємо CSS клас до всіх полів форми
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'