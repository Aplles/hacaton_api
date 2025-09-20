from conf.settings.django import env


DATABASES = {"default": env.db()}
