import io
import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from core.constants import (MAX_LENGTH_ABOUT, MAX_LENGTH_PHONE,
                            MAX_LENGTH_USER_NAME, MAX_LENGTH_USER_SURNAME)

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=MAX_LENGTH_USER_NAME, verbose_name='Имя')
    surname = models.CharField(max_length=MAX_LENGTH_USER_SURNAME, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    phone = models.CharField(max_length=MAX_LENGTH_PHONE, blank=True, verbose_name='Телефон')
    github_url = models.URLField(blank=True, verbose_name='GitHub')
    about = models.TextField(max_length=MAX_LENGTH_ABOUT, blank=True, verbose_name='О себе')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    favorites = models.ManyToManyField('projects.Project', blank=True, related_name='favorited_by', verbose_name='Избранное')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            img = Image.new('RGB', (200, 200), color=self._get_random_color())
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 100)
            except:
                font = ImageFont.load_default()
            
            letter = self.name[0].upper()
            bbox = draw.textbbox((0, 0), letter, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (200 - text_width) / 2
            y = (200 - text_height) / 2 - 10
            
            draw.text((x, y), letter, font=font, fill='white')
            
            img_io = io.BytesIO()
            img.save(img_io, format='PNG')
            
            self.avatar.save(f'avatar_{self.email}.png', ContentFile(img_io.getvalue()), save=False)
        
        super().save(*args, **kwargs)
    
    def _get_random_color(self):
        colors = [
            (52, 152, 219),  
            (46, 204, 113),
            (231, 76, 60),
            (241, 196, 15),
            (155, 89, 182),
            (230, 126, 34),
            (26, 188, 156),
        ]
        return random.choice(colors)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname}'

    @property
    def full_name(self):
        return f'{self.name} {self.surname}'
