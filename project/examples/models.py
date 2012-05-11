from django.contrib.auth.models import User


# User class extensions
def user_unicode(self):
    """Use email address for string representation of user."""
    return self.email
User.add_to_class('__unicode__', user_unicode)
