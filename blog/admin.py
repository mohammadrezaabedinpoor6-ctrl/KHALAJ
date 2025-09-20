from django.contrib import admin
from .models import Blog, Comment,Reply

# تعریف نمایش سفارشی برای وبلاگ‌ها
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title','author', 'description','cover', 'created_at', 'updated_at','views')  # مشخص کردن ستون‌های نمایش داده‌شده
    search_fields = ('title', 'description','likes')  # فعال کردن جستجو برای عنوان و محتوا
    list_filter = ('created_at','likes','views', 'author')  # فیلتر کردن بر اساس تاریخ و نویسنده

# تعریف نمایش سفارشی برای کامنت‌ها
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user','text', 'blog', 'datetime_created', 'is_active','parent')  # نمایش اطلاعات مربوط به کامنت‌ها
    search_fields = ('text','user','likes')  # جستجو بر اساس محتوای کامنت‌ها
    list_filter = ('is_active', 'datetime_created','likes')  # فیلتر کردن بر اساس تایید یا عدم تایید

# تعریف نمایش سفارشی برای کاربران
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'comment', 'datetime_created')  # نمایش اطلاعات پایه کاربران
    search_fields = ('user', 'text','likes')  # جستجو بر اساس نام کاربری و ایمیل
    list_filter = ('datetime_created','user')  # فیلتر کردن بر اساس تاریخ عضویت و ورود اخیر

# ثبت مدل‌ها در ادمین
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)
