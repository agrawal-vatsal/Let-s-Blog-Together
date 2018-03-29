from django.core.urlresolvers import reverse
from django.test import TestCase


# Create your tests here.
class Tests(TestCase):
    def test_home_page_status_code(self):
        url = reverse('post_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
