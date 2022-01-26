from django.core.management.base import BaseCommand, CommandError

from ddash.apps.users.models import User
from spackon.logger import bot

from getpass import getpass


class Command(BaseCommand):
    """add a user (typically to use the API) without any special permissions."""

    def add_arguments(self, parser):
        parser.add_argument("--username", dest="username", default=None, type=str)

    help = "Generates a user (e.g., for the API) for ddash."

    def handle(self, *args, **options):
        if options["username"] is None:
            raise CommandError("Please provide a username with --username")

        bot.debug("Username: %s" % options["username"])

        # The username cannot exist
        usercount = User.objects.filter(username=options["username"]).count()
        if usercount > 0:
            raise CommandError("This username already exists.")

        # Create the user and ask for password
        password = getpass("Enter Password:")
        user = User.objects.create_user(options["username"], password=password)
        # user by default is not staff or superuser, but will have api token
        user.save()
        print("User %s successfully created." % user.username)
