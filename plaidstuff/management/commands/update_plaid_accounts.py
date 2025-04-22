from django.core.management.base import BaseCommand
from plaidstuff.tasks import update_all_plaid_accounts
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update all Plaid accounts with their latest data using Celery'

    def handle(self, *args, **options):
        self.stdout.write('Starting Plaid account update...')
        
        try:
            result = update_all_plaid_accounts.delay()
            
            self.stdout.write(self.style.SUCCESS(
                f"Update task started. Task ID: {result.id}"
            ))
            
        except Exception as e:
            logger.error(f"Error in update_plaid_accounts command: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error starting Plaid accounts update: {str(e)}')
            ) 