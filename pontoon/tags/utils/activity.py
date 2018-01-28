
from pontoon.base.templatetags.helpers import (
    as_simple_translation, naturaltime)
from pontoon.base.models import user_gravatar_url


class LatestActivityUser(object):

    def __init__(self, user):
        self.user = user

    @property
    def email(self):
        return self.user.get('user__email')

    @property
    def first_name(self):
        return self.user.get('user__first_name')

    @property
    def name_or_email(self):
        return self.first_name or self.email

    def gravatar_url(self, *args):
        if self.email:
            return user_gravatar_url(self, *args)

    def as_dict(self):
        return dict(
            avatar=self.gravatar_url(44),
            name=self.name_or_email)


class LatestActivity(object):

    def __init__(self, activity):
        self.activity = activity

    @property
    def approved_date(self):
        return self.activity.get('approved_date')

    @property
    def date(self):
        return self.activity.get('date')

    @property
    def translation(self):
        return self.activity.get('string')

    @property
    def user(self):
        return (
            LatestActivityUser(self.activity)
            if 'user__email' in self.activity
            else None)

    @property
    def type(self):
        if self.approved_date is not None and self.approved_date > self.date:
            return 'approved'
        return 'submitted'

    def as_dict(self):
        return dict(
            date=self.date.isoformat(),
            ago=naturaltime(self.date),
            translation=(
                self.translation
                and dict(string=as_simple_translation(self.translation))),
            action=self.type,
            user=self.user and self.user.as_dict())
