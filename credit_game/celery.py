import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_game.settings')

app = Celery('credit_game')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# # Configure Celery to use SQS
# if settings.USE_LOCAL_SQS == 'True':
#     app.conf.update(
#         broker_url='sqs://localhost:9324',
#         broker_transport_options={
#             'region': settings.AWS_REGION,
#             'is_secure': False,
#             'endpoint_url': 'http://localhost:9324',
#         },
#         task_serializer='json',
#         accept_content=['json'],
#         result_serializer='json',
#         timezone='UTC',
#         enable_utc=True,
#         task_default_queue='default',
#     )
# else:
# app.conf.update(
# #         broker_url=settings.CELERY_BROKER_URL,
#         broker_transport_options={
#             'region': settings.AWS_REGION,
#             'visibility_timeout': 3600,  # 1 hour
#             'polling_interval': 1,  # 1 second
#         },
# #         task_serializer='json',
# #         accept_content=['json'],
# #         result_serializer='json',
# #         timezone='UTC',
# #         enable_utc=True,
#         task_default_queue='default',
#     )

# Add beat schedule
app.conf.beat_schedule = {
    'update-plaid-accounts': {
        'task': 'plaidstuff.tasks.update_all_plaid_accounts',
        'schedule': 28800.0,  # Run every 8 hours
    },
} 