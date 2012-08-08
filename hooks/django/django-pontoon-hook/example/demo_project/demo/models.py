from django.db import models
from django.utils.translation import gettext_lazy as _

class Demo(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=30,
            help_text=_("Help message for name field"))
