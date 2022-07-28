from django.contrib import admin
from .models import Author, Post, PostCategory, Category, CategorySubscribers, Comment


# Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('author_user', 'author_rating', 'id')
    list_filter = ('author_user', )
    list_editable = ('author_rating', )
    ordering = ('-author_rating', )


class CommentPostAdmin(admin.StackedInline):
    model = Comment
    list_display = ('comment_user',)
    readonly_fields = ('comment_post', 'comment_create', 'comment_rating')
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('headline', 'position', 'post_author', 'slug', 'create_date', 'post_rating', 'id')
    list_filter = ('position', 'create_date', 'post_author')
    raw_id_fields = ('post_author',)
    search_fields = ('headline', 'post_text')
    prepopulated_fields = {'slug': ('headline',), }
    ordering = ['-create_date']
    list_editable = ('post_rating', )
    list_per_page = 10
    list_max_show_all = 100
    # Поле для комментария
    inlines = [CommentPostAdmin, ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_user', 'comment_text', 'comment_create', 'comment_rating', 'id')
    # readonly_fields = ('comment_user', 'comment_post', 'comment_create', 'comment_rating')
    search_fields = ('comment_user', 'comment_post', )
    list_filter = ('comment_user', 'comment_create', )
    list_editable = ('comment_rating', )
    ordering = ('-comment_create', )
    list_per_page = 10
    list_max_show_all = 100


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('post', 'category')
    list_filter = ('category', )


@admin.register(CategorySubscribers)
class CategorySubscribersAdmin(admin.ModelAdmin):
    list_display = ('category', 'subscriber_user', )


# admin.site.register(Author)
# admin.site.register(Post)
# admin.site.register(PostCategory)
admin.site.register(Category)
# admin.site.register(Comment)
# admin.site.register(CategorySubscribers)
