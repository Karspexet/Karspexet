from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from django.urls import reverse

from factories import factories as f

# Remove CMS middleware, since they cause inconsistent query counts
NON_CMS_MIDDLEWARE = [m for m in settings.MIDDLEWARE if not m.startswith("cms.")]


@override_settings(MIDDLEWARE=NON_CMS_MIDDLEWARE)
class TestAdminsAreFast(TestCase):
    """
    Test that no admin does an unreasonable amount of queries in their changelist page
    """

    num_objects = 3

    @classmethod
    def setUpTestData(cls):
        cls.user = f.CreateStaffUser(is_superuser=True, username="dmon")

    def setUp(self):
        Site.objects.get_current()
        self.client.force_login(self.user)

    def test_account_admin(self):
        objs = f.CreateAccount.create_batch(self.num_objects)

        with self.assertNumQueries(5):
            response = self.client.get(admin_changelist_url(objs[0]))
        self.assertEqual(response.status_code, 200)

    def test_pricingmodel_admin(self):
        objs = f.CreatePricingModel.create_batch(self.num_objects)

        with self.assertNumQueries(5):
            response = self.client.get(admin_changelist_url(objs[0]))
        self.assertEqual(response.status_code, 200)

    def test_reservation_admin(self):
        objs = f.CreateReservationWithTicket.create_batch(self.num_objects)

        with self.assertNumQueries(9):
            response = self.client.get(admin_changelist_url(objs[0]))
        self.assertEqual(response.status_code, 200)

    def test_ticket_admin(self):
        objs = f.CreateTicket.create_batch(self.num_objects)

        with self.assertNumQueries(5):
            response = self.client.get(admin_changelist_url(objs[0]))
        self.assertEqual(response.status_code, 200)

    def test_voucher_admin(self):
        objs = f.CreateVoucher.create_batch(self.num_objects, created_by=self.user)

        with self.assertNumQueries(5):
            response = self.client.get(admin_changelist_url(objs[0]))
        self.assertEqual(response.status_code, 200)


def admin_changelist_url(model):
    return reverse("admin:ticket_%s_changelist" % type(model).__name__.lower())
