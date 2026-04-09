"""
pytest configuration for ChurchOS backend.
Run: pytest --ds=churchos.settings.development -x -v
"""
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def superuser(db):
    User = get_user_model()
    return User.objects.create_superuser(
        email='admin@test.com',
        password='testpass123',
        first_name='Test',
        last_name='Admin',
    )


@pytest.fixture
def auth_client(api_client, superuser):
    api_client.force_authenticate(user=superuser)
    return api_client


@pytest.fixture
def church_settings(db):
    from apps.core.models import ChurchSettings
    settings, _ = ChurchSettings.objects.get_or_create(pk=1)
    settings.church_name = 'Test Church'
    settings.currency_code = 'GHS'
    settings.currency_symbol = '₵'
    settings.member_number_prefix = 'TST'
    settings.save()
    return settings


@pytest.fixture
def member(db, church_settings):
    from apps.members.models import Member
    return Member.objects.create(
        first_name='John',
        last_name='Doe',
        phone_primary='+233200000001',
        gender='male',
        membership_status='active',
    )
