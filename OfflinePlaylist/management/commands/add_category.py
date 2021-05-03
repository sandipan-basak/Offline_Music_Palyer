from django.core.management.base import BaseCommand
from OfflinePlaylist.models import Category

class Command(BaseCommand):

    # help = "Whatever you want to print here"

    
    def handle(self, **options):
        Category.objects.all().delete()
        Category.objects.create(name='Artist')
        Category.objects.create(name='Album')
        Category.objects.create(name='Track')
        print(Category.objects.all())