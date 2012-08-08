from django.forms import ModelForm
from demo.models import Demo
from django.utils.translation import ugettext_lazy as _

class DemoForm(ModelForm):
    class Meta:
        model = Demo

    def __init__(self, *args, **kwargs):
        super(DemoForm, self).__init__(*args, **kwargs)
        self.fields['name'].help_text = _('form help text')
