from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Delete db.sqlite3, run migrations, and recreate default admin."

    def handle(self, *args, **options):
        db_path = settings.BASE_DIR / "db.sqlite3"

        # Close active DB connections before removing SQLite file on Windows.
        connections.close_all()

        if db_path.exists():
            db_path.unlink()
            self.stdout.write(self.style.WARNING(f"Removed database: {db_path}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"Database not found, skipping removal: {db_path}")
            )

        self.stdout.write("Applying migrations...")
        call_command("migrate", interactive=False)

        self.stdout.write("Creating default admin user...")
        call_command("addmin")

        self.stdout.write(self.style.SUCCESS("Database wiped, migrated, and admin created."))
