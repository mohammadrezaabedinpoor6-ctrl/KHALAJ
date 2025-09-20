from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
import jdatetime


class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    cover = models.ImageField(upload_to="covers/", verbose_name='عکس جلد', blank=True, default='covers/default.png')
    audio = models.FileField(upload_to="audio/", verbose_name="فایل صوتی", blank=True, null=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="blogs", verbose_name="نویسنده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="زمان ویرایش")
    likes = models.ManyToManyField(get_user_model(), related_name='liked_blogs', blank=True,  verbose_name="لایک‌ها")
    views = models.IntegerField(default=0, verbose_name="بازدید")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.id])

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def jalali_created(self):
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d')

    @property
    def jalali_updated(self):
        return jdatetime.datetime.fromgregorian(datetime=self.updated_at).strftime('%Y/%m/%d')


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments', verbose_name="کاربر")
    text = models.TextField(verbose_name="متن پیام")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments', verbose_name="وبلاگ")
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='child_comments',
        verbose_name="کامنت والد"
    )
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    likes = models.ManyToManyField(get_user_model(), related_name='liked_comments', blank=True, verbose_name="لایک‌ها")

    def __str__(self):
        return f"{self.user}: {self.text}"

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def jalali_created(self):
        return jdatetime.datetime.fromgregorian(datetime=self.datetime_created).strftime('%Y/%m/%d %H:%M')


class Reply(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='replies', verbose_name="کاربر")
    text = models.TextField(verbose_name="متن پاسخ")
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='reply_set',
        verbose_name="کامنت"
    )
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    likes = models.ManyToManyField(get_user_model(), related_name='liked_replies', blank=True, verbose_name="لایک ها")

    def __str__(self):
        return f"{self.user}: {self.text}"

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def jalali_created(self):
        return jdatetime.datetime.fromgregorian(datetime=self.datetime_created).strftime('%Y/%m/%d %H:%M')

