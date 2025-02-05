from django.contrib import admin
from api import models as api_models

admin.site.register(api_models.CustomUser)
admin.site.register(api_models.Profile)
admin.site.register(api_models.Post)
admin.site.register(api_models.Category)
admin.site.register(api_models.Comment)
admin.site.register(api_models.Notification)
admin.site.register(api_models.Bookmark)
