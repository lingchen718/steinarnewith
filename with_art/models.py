# with_art/models.py
import os
import io
from django.db import models
from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image


# ================================================================
# Shared mixin: auto-slug from title
# ================================================================
class SlugFromTitleMixin:
    """Subclasses must define `slug_field` (name of slug attribute)
    and `slugify_from` (attribute name to slugify from)."""

    slug_field = 'slug'
    slugify_from = 'title'

    def save(self, *args, **kwargs):
        if not getattr(self, self.slug_field):
            base = slugify(getattr(self, self.slugify_from, '')) or f'{type(self).__name__.lower()}-{self.id}'
            slug = base
            counter = 1
            qs = type(self).objects.filter(**{self.slug_field: slug}).exclude(pk=self.pk)
            while qs.exists():
                counter += 1
                slug = f'{base}-{counter}'
                qs = type(self).objects.filter(**{self.slug_field: slug}).exclude(pk=self.pk)
            setattr(self, self.slug_field, slug)
        super().save(*args, **kwargs)


# ================================================================
# Shared mixin: auto-convert TIFF/PSD/GIF to JPEG on upload
# ================================================================
class WebImageConverterMixin:
    """Subclasses define `image_field` and `web_field`."""
    image_field = 'cover_image'
    web_field = 'cover_image_web'
    max_dimension = 2400
    jpeg_quality = 88

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._generate_web_image()

    def _generate_web_image(self):
        src = getattr(self, self.image_field, None)
        if not src:
            return

        base = os.path.splitext(os.path.basename(src.name))[0]
        web_name = f'{base}.jpg'

        # 已生成过同名 web 版就跳过（用文件名比较，兼容云端存储）
        dst = getattr(self, self.web_field, None)
        if dst and dst.name and dst.name.endswith(web_name):
            return

        try:
            src.open('rb')            # 兼容 Cloudinary 远程存储
            img = Image.open(src)
            img.load()
        except (FileNotFoundError, Image.UnidentifiedImageError, ValueError):
            return

        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        if max(img.size) > self.max_dimension:
            img.thumbnail((self.max_dimension, self.max_dimension), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=self.jpeg_quality, optimize=True, progressive=True)
        buf.seek(0)

        getattr(self, self.web_field).save(web_name, ContentFile(buf.read()), save=False)
        super().save(update_fields=[self.web_field])


class ArtProject(SlugFromTitleMixin, WebImageConverterMixin, models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='URL slug')
    description = models.TextField(blank=True)

    cover_image     = models.ImageField(upload_to='artworks/', blank=True, verbose_name='Cover image')
    cover_image_web = models.ImageField(upload_to='artworks/web/', blank=True)  # auto-generated
    cover_video     = models.FileField(upload_to='covers/video/', blank=True, null=True)
    cover_video_url = models.URLField('Video URL (Cloudinary)', blank=True, null=True)  # ← 新增


    is_current   = models.BooleanField(default=False, verbose_name='Currently on view',
                                        help_text='Show this project on the CURRENT page.')
    date_added   = models.DateTimeField(auto_now_add=True)
    order        = models.PositiveIntegerField(default=0,
                                               verbose_name='Order',
                                               help_text='Lower numbers appear first. Drag to reorder in admin.')

    image_field = 'cover_image'
    web_field   = 'cover_image_web'

    class Meta:
        ordering = ['order', '-date_added']
        verbose_name = 'art project'
        verbose_name_plural = 'art projects'

    def __str__(self):
        return self.title or f'ArtProject {self.id}'


class Entry(WebImageConverterMixin, models.Model):
    artproject = models.ForeignKey(ArtProject, on_delete=models.CASCADE, related_name='entries')
    title      = models.CharField(max_length=200, blank=True)
    image      = models.ImageField(upload_to='entries/')
    image_web  = models.ImageField(upload_to='entries/web/', blank=True)  # auto-generated
    video      = models.FileField(upload_to='covers/entries/video/', blank=True, null=True)
    video_url = models.URLField('Video URL (Cloudinary)', blank=True, null=True)

    description = models.TextField(blank=True)
    date_added  = models.DateTimeField(auto_now_add=True)
    order       = models.PositiveIntegerField(default=0)

    image_field = 'image'
    web_field   = 'image_web'

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f'Entry {self.id}'


class CurrentProject(SlugFromTitleMixin, WebImageConverterMixin, models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='URL slug')
    description = models.TextField(blank=True)

    cover_image     = models.ImageField(upload_to='current/', blank=True, verbose_name='Cover image')
    cover_image_web = models.ImageField(upload_to='current/web/', blank=True)  # auto-generated
    cover_video     = models.FileField(upload_to='covers/video/', blank=True, null=True)
    cover_video_url = models.URLField('Video URL (Cloudinary)', blank=True, null=True)

    date_added  = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True, verbose_name='Published',
                                       help_text='Uncheck to hide this project from the CURRENT page without deleting it.')
    order       = models.PositiveIntegerField(default=0)

    image_field = 'cover_image'
    web_field = 'cover_image_web'

    class Meta:
        ordering = ['order', '-date_added']
        verbose_name = 'current project'
        verbose_name_plural = 'current projects'

    def __str__(self):
        return self.title or f'CurrentProject {self.id}'


class CurrentEntry(WebImageConverterMixin, models.Model):
    current_project = models.ForeignKey(CurrentProject, on_delete=models.CASCADE,
                                        related_name='entries', verbose_name='Current project')
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='current/entries/')
    image_web = models.ImageField(upload_to='current/entries/web/', blank=True)  # auto-generated
    video = models.FileField(upload_to='covers/entries/video/', blank=True, null=True)
    video_url = models.URLField('Video URL (Cloudinary)', blank=True, null=True)

    description = models.TextField(blank=True)
    date_added  = models.DateTimeField(auto_now_add=True)
    order       = models.PositiveIntegerField(default=0)

    image_field = 'image'
    web_field = 'image_web'

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f'CurrentEntry {self.id}'


from django.db import models

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('commission', 'Commission a work'),
        ('exhibition', 'Exhibition proposal'),
        ('press', 'Press & media'),
        ('collaboration', 'Collaboration'),
        ('purchase', 'Purchase / pricing'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    budget = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"
