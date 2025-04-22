from celery import shared_task
import logging
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.api import plaid_api
from plaid.model.liabilities_get_request import LiabilitiesGetRequest
from datetime import date
import json

# from .views import client
from .models import PlaidAccount
from .plaid_client import client

logger = logging.getLogger(__name__)

def convert_dates_to_strings(obj):
    """
    Recursively convert datetime.date objects to ISO format strings in a dictionary or list.
    """
    if isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_dates_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_to_strings(item) for item in obj]
    return obj

@shared_task
def fetch_plaid_account_data(plaid_account_id):
    """
    Celery task to fetch account data from Plaid for a single account.
    Only saves credit accounts with their corresponding balance information.
    """
    try:
        account = PlaidAccount.objects.get(id=plaid_account_id)

        # get liabilities
        liabilities_request = LiabilitiesGetRequest(access_token=account.access_token)
        liabilities_response = client.liabilities_get(liabilities_request)
        # logging.info(f"liabilities_response: {liabilities_response}")

        # Convert the response to a dictionary
        liabilities_dict = liabilities_response.to_dict()
        credit_accounts = liabilities_dict.get("liabilities", {}).get("credit", [])
        logger.info(f"credit_accounts: {credit_accounts}")

        # Create a mapping of account IDs to their data for efficient lookup
        account_map = {account.get("account_id"): account for account in liabilities_dict.get("accounts", [])}

        # Update credit accounts with their corresponding account data
        for credit_account in credit_accounts:
            account_id = credit_account.get("account_id")
            if account_id in account_map:
                # Create a new dictionary with the combined data
                logger.info(type(credit_account))
                credit_account.update(account_map[account_id])

        # Convert any date objects to strings
        credit_accounts = convert_dates_to_strings(credit_accounts)
        
        # logger.info(f"credit_accounts: {credit_accounts}")

        # Update the account
        account.connection_data = credit_accounts
        account.save()

        return
    
    except Exception as e:
        logger.error(f"Error fetching data for account {plaid_account_id}: {str(e)}")
        return 


@shared_task
def update_all_plaid_accounts():
    """
    Celery task to update all Plaid accounts.
    Uses a group of tasks to update accounts in parallel.
    """
    from celery import group

    plaid_accounts = PlaidAccount.objects.filter(connection_type="plaid")
    account_ids = list(plaid_accounts.values_list("id", flat=True))

    # Create a group of tasks to update all accounts in parallel
    task_group = group(
        fetch_plaid_account_data.s(account_id) for account_id in account_ids
    )

    # Execute the group of tasks
    result = task_group.apply_async()
    logger.info(f"task_id: {result.id}, total_accounts: {len(account_ids)}")
    return 
