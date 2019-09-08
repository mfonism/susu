# from django.urls import reverse
# from rest_framework.test import APITestCase, APIRequestFactory
# from rest_framework import status

# from ..models import User
# from ..serializers import UserSerializer


# class UserListAPITest(APITestCase):

#     def setUp(self):
#         User.objects.create_user(
#             email='mfon@etimfon.com', password='4g8menut!',
#             first_name='Mfon', last_name='Eti-mfon'
#         )
#         User.objects.create_user(
#             email='ambrose@igibo.com', password='nopassword',
#             first_name='Ambrose', last_name='Igibo'
#         )
#         User.objects.create_user(
#             email='ediomo@udofia.com', password='iamfabulous',
#             first_name='Ediomo', last_name='Udofia'
#         )
#         User.objects.create_user(
#             email='kim@essien.com', password='chubbybaby',
#             first_name='Kim', last_name='Essien'
#         )

#     def test_list_user(self):
#         # authenticated user can list users
#         self.client.force_authenticate(User.objects.get(pk=1))

#         url = reverse('user-detail')
#         response = self.client.get(url)

#         print()
#         print(response.data)
#         print()

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, {})
