# The classes here provide similar functionality to
# ProjectLocale.get_latest_activity in mangling latest activity data,
# although they use queryset `values` rather than objects
from pontoon.base.models import user_gravatar_url


class LatestActivityUser(object):
    def __init__(self, activity, activity_type):
        self.activity = activity
        self.type = activity_type

    @property
    def prefix(self):
        return "approved_" if self.type == "approved" else ""

    @property
    def email(self):
        return self.activity.get(self.prefix + "user__email")

    @property
    def first_name(self):
        return self.activity.get(self.prefix + "user__first_name")

    @property
    def name_or_email(self):
        return self.first_name or self.email

    @property
    def display_name(self):
        return self.first_name or self.email.split("@")[0]

    @property
    def username(self):
        return self.activity.get(self.prefix + "user__username")

    def gravatar_url(self, *args):
        if self.email:
            return user_gravatar_url(self, *args)


class LatestActivity(object):
    def __init__(self, activity):
        self.activity = activity

    @property
    def approved_date(self):
        return self.activity.get("approved_date")

    @property
    def date(self):
        if self.type == "approved":
            return self.approved_date
        return self.activity.get("date")

    @property
    def translation(self):
        return dict(string=self.activity.get("string", ""))

    @property
    def user(self):
        return (
            LatestActivityUser(self.activity, self.type)
            if "user__email" in self.activity or "approved_user__email" in self.activity
            else None
        )

    @property
    def type(self):
        if self.approved_date is not None and self.approved_date > self.activity.get(
            "date"
        ):
            return "approved"
        return "submitted"
