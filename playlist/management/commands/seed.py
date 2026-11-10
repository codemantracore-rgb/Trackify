from django.core.management.base import  BaseCommand
from playlist.seed_data import seed_data
class Command(BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument(
            '--total',type=int,default=100
        )
    def handle(self,*args,**options):
        total=options['total']
        seed_data(total)
        self.stdout.write(
            self.style.SUCCESS(
                "Data Generated Sucess!"
            )
        )

