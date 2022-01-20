from django.core.management.base import BaseCommand, CommandError

from shub.apps.users.models import User
from shub.logger import bot


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("--username", dest="username", default=None, type=str)

    help = "Generates a superuser."

    def handle(self, *args, **options):
        if options["username"] is None:
            raise CommandError("Please provide a username with --username")

        bot.debug("Username: %s" % options["username"])

        try:
            user = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            raise CommandError("This username does not exist.")

        if user.is_superuser is True:
            raise CommandError("This user is already a superuser.")
        else:
            user = User.objects.add_superuser(user)
            bot.debug("%s is now a superuser." % (user.username))
