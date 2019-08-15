# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.forms import ModelForm
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from collections import OrderedDict


class AddPaymentCard(forms.Form):
    card_number = forms.CharField(max_length=16, widget=forms.TextInput(),
        error_messages = {
            'invalid': 'Такой карты не существует',
        }
    )
    cvv_card = forms.CharField(max_length=3, widget=forms.TextInput(),
        error_messages = {
            'invalid': 'CVV код должен содержать 3 цыфры',
            'verify_error': 'Вы неверно ввели CVV пароль от вашей карты'
        }
    )
    month_card = forms.CharField(max_length=2, widget=forms.TextInput(),
        error_messages = {
            'invalid': 'Вы неверно ввели месяц вашей карты',
        }
    )
    year_card = forms.CharField(max_length=2, widget=forms.TextInput(),
        error_messages = {
            'invalid': 'Вы неверно ввели год вашей карты',
        }
    )

class UserCreateForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'custom_email', 'password1', 'password2', 'first_name', 'last_name']
    error_messages = {
        'password_mismatch': ('Паролі не співпадають'),
        'invalid': ('Введіть пароль не менше 8 символів використовуючи цифри, латиницю і принаймні одну велику літеру'),
        'required': ('Це поле обов\'язкове'),
    }
    first_name = forms.CharField(label='Введіть ім\'я', widget=forms.TextInput(attrs={
        'placeholder': 'Введіть ім\'я, наприклад Іван',
        'class': 'form-control'
    }),
   error_messages={
        'required': ('Це поле обов\'язкове'),
   })
    last_name = forms.CharField(label='Введіть прізвище', widget=forms.TextInput(attrs={
        'placeholder': 'Введіть прізвище, наприклад Іванов',
        'class': 'form-control'
    }),
    error_messages={
        'required': ('Це поле обов\'язкове'),
    })

    custom_email = forms.EmailField(label='Введіть ваш адрес електронної пошти', widget=forms.EmailInput(
        attrs = {
            'class': 'form-control',
            'placeholder': 'Введіть ваш адрес електронної пошти',
            }), error_messages = {
                    'invalid': ('Введений вами адрес електронної пошти не відповідає формату example@postal.com'),
                    'required': ('Це поле обов\'язкове'),
            })

    username = forms.CharField(label='Введіть Логін',help_text='', max_length=255,  validators=[
            RegexValidator(r'^[a-zA-Z][a-zA-Z0-9-_\.]{2,20}$')
        ],
        error_messages={
            'unique': ('Користувач з таким логіном існує'),
            'invalid': ('Введіть логін використовуючи латиницю і цифри наприклад Ivanov123'),
            'required': ('Це поле обов\'язкове'),
        },
        widget=forms.TextInput(
                attrs={

                    'class': 'form-control',
                    'placeholder': 'Придумайте логін',
                }
            )
        )

    password1 = forms.CharField(label='Придумайте пароль', help_text='', validators=[
        RegexValidator(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}')
    ],
    widget=forms.PasswordInput(
    attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте пароль',
        }
    ),
    error_messages = {
            'password_mismatch': ('Паролі не співпадають'),
            'invalid': ('Введіть пароль не менше 8 символів використовуючи цифри, латиницю і принаймні одну велику літеру'),
            'required': ('Це поле обов\'язкове'),
        }
    )
    password2 = forms.CharField(label='Повторіть пароль', help_text='', validators=[
        RegexValidator(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}')
    ],
    widget=forms.PasswordInput(
    attrs={
            'class': 'form-control',
            'placeholder': 'Введіть пароль',
        }
    ),
    error_messages = {
            'password_mismatch': ('Паролі не співпадають'),
            'invalid': ('Введіть пароль не менше 8 символів використовуючи цифри, латиницю і принаймні одну велику літеру'),
            'required': ('Це поле обов\'язкове'),
        }
    )



    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        if len(password2) < 8:
            raise forms.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
            )
        return password2

    def save(self):
        print(self.cleaned_data.get('first_name'),
            self.cleaned_data.get('last_name'),
            self.cleaned_data.get('custom_email'),
            self.cleaned_data.get('username'),
            self.cleaned_data.get('password1'))
        return CustomUser.objects.create(first_name=self.cleaned_data.get('first_name'),
                                  last_name=self.cleaned_data.get('last_name'),
                                  custom_email=self.cleaned_data.get('custom_email'),
                                  username=self.cleaned_data.get('username'),
                                  password=self.cleaned_data.get('password1'))



class ChangeImageForm(forms.Form):
    image = forms.ImageField(allow_empty_file=False)
