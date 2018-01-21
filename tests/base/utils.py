
import pytest

from pontoon.base.models import Resource
from pontoon.base.utils import glob_to_regex


def test_util_glob_to_regex():
    assert glob_to_regex('*') == '^.*$'
    assert glob_to_regex('/foo*') == '^\\/foo.*$'
    assert glob_to_regex('*foo') == '^.*foo$'
    assert glob_to_regex('*foo*') == '^.*foo.*$'


@pytest.mark.django_db
def test_util_glob_to_regex_db(resource0, resource1):
    assert resource0 in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert resource1 in Resource.objects.filter(path__regex=glob_to_regex('*'))
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('*')))
        == list(Resource.objects.all()))
    assert (
        resource0
        in Resource.objects.filter(
            path__regex=glob_to_regex('*0*')))
    assert (
        resource1
        not in Resource.objects.filter(
            path__regex=glob_to_regex('*0*')))
    assert (
        list(Resource.objects.filter(path__regex=glob_to_regex('*0*')))
        == list(Resource.objects.filter(path__contains='0')))
