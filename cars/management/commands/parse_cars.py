from django.core.management import BaseCommand

from auto_info.parsers.parser_cars import brands_parse


class Command(BaseCommand):
	def handle(self, *args, **options):
		brands_parse()
