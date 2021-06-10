""" Add fake data to our Quote model using the Faker python package """

from .models import Quote
from faker import Faker

fake = Faker()

def add_fake_data():
    for x in range(10000):
        Quote.objects.create(name=fake.name(), quote=fake.text())

    print('Completed!!! Check your database.')

