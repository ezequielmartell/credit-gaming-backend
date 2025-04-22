from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import base64
import os
import datetime as dt
import json
import time
from datetime import date, timedelta
import uuid
import logging
from dotenv import load_dotenv
import plaid
from plaid.model.payment_amount import PaymentAmount
from plaid.model.payment_amount_currency import PaymentAmountCurrency
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.recipient_bacs_nullable import RecipientBACSNullable
from plaid.model.payment_initiation_address import PaymentInitiationAddress
from plaid.model.payment_initiation_recipient_create_request import (
    PaymentInitiationRecipientCreateRequest,
)
from plaid.model.payment_initiation_payment_create_request import (
    PaymentInitiationPaymentCreateRequest,
)
from plaid.model.payment_initiation_payment_get_request import (
    PaymentInitiationPaymentGetRequest,
)
from plaid.model.link_token_create_request_payment_initiation import (
    LinkTokenCreateRequestPaymentInitiation,
)
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.user_create_request import UserCreateRequest
from plaid.model.consumer_report_user_identity import ConsumerReportUserIdentity
from plaid.model.asset_report_create_request import AssetReportCreateRequest
from plaid.model.asset_report_create_request_options import (
    AssetReportCreateRequestOptions,
)
from plaid.model.asset_report_user import AssetReportUser
from plaid.model.asset_report_get_request import AssetReportGetRequest
from plaid.model.asset_report_pdf_get_request import AssetReportPDFGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.investments_transactions_get_request_options import (
    InvestmentsTransactionsGetRequestOptions,
)
from plaid.model.investments_transactions_get_request import (
    InvestmentsTransactionsGetRequest,
)
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.transfer_authorization_create_request import (
    TransferAuthorizationCreateRequest,
)
from plaid.model.transfer_create_request import TransferCreateRequest
from plaid.model.transfer_get_request import TransferGetRequest
from plaid.model.transfer_network import TransferNetwork
from plaid.model.transfer_type import TransferType
from plaid.model.transfer_authorization_user_in_request import (
    TransferAuthorizationUserInRequest,
)
from plaid.model.ach_class import ACHClass
from plaid.model.transfer_create_idempotency_key import TransferCreateIdempotencyKey
from plaid.model.transfer_user_address_in_request import TransferUserAddressInRequest
from plaid.model.signal_evaluate_request import SignalEvaluateRequest
from plaid.model.statements_list_request import StatementsListRequest
from plaid.model.link_token_create_request_statements import (
    LinkTokenCreateRequestStatements,
)
from plaid.model.link_token_create_request_cra_options import (
    LinkTokenCreateRequestCraOptions,
)
from plaid.model.statements_download_request import StatementsDownloadRequest
from plaid.model.consumer_report_permissible_purpose import (
    ConsumerReportPermissiblePurpose,
)
from plaid.model.cra_check_report_base_report_get_request import (
    CraCheckReportBaseReportGetRequest,
)
from plaid.model.cra_check_report_pdf_get_request import CraCheckReportPDFGetRequest
from plaid.model.cra_check_report_income_insights_get_request import (
    CraCheckReportIncomeInsightsGetRequest,
)
from plaid.model.cra_check_report_partner_insights_get_request import (
    CraCheckReportPartnerInsightsGetRequest,
)
from plaid.model.cra_pdf_add_ons import CraPDFAddOns
from plaid.api import plaid_api
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PlaidAccount
from .serializers import PlaidAccountSerializer
from .tasks import fetch_plaid_account_data
from .plaid_client import client
from rest_framework import status

load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")
PLAID_PRODUCTS = os.getenv("PLAID_PRODUCTS", "transactions").split(",")
PLAID_COUNTRY_CODES = os.getenv("PLAID_COUNTRY_CODES", "US").split(",")
PLAID_CLIENT_NAME = os.getenv("PLAID_CLIENT_NAME", "No App Name Found")

host = plaid.Environment.Sandbox

if PLAID_ENV == "sandbox":
    host = plaid.Environment.Sandbox

if PLAID_ENV == "production":
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = os.getenv("PLAID_REDIRECT_URI")

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))


class PlaidAccountViewSet(viewsets.ModelViewSet):
    serializer_class = PlaidAccountSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access
    queryset = PlaidAccount.objects.none()

    def get_queryset(self):
        # Filter objects to only those belonging to the logged-in user
        return PlaidAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        logging.info(f"request: {self.request}")
        # Save the instance with the current user
        if isinstance(self.request.data.get('connection_data'), list):
            serializer.save(user=self.request.user)
        else:
            serializer.save(user=self.request.user, connection_data=[self.request.data.get('connection_data')])

        # instance = serializer.save(user=self.request.user, )


# generate a plaid link token
# Create a user token which can be used for Plaid Check, Income, or Multi-Item link flows
# https://plaid.com/docs/api/users/#usercreate


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_link_token(request):
    logging.info("Creating link token")
    user_token = request.user.id
    # logging.info(f"user_token: {user_token}")
    # if not user_token:
    # # if user_token is None or len(user_token) == 0:
    #     logging.error(f"user: {request.user.id} - user_token is required")
    #     return Response({"error": "user_token is required"})

    try:
        link_request = LinkTokenCreateRequest(
            products=products,
            client_name=PLAID_CLIENT_NAME,
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=str(time.time())),
        )
        if PLAID_REDIRECT_URI is not None:
            link_request["redirect_uri"] = PLAID_REDIRECT_URI
        if Products("statements") in products:
            statements = LinkTokenCreateRequestStatements(
                end_date=date.today(), start_date=date.today() - timedelta(days=30)
            )
            link_request["statements"] = statements

        cra_products = [
            "cra_base_report",
            "cra_income_insights",
            "cra_partner_insights",
        ]
        if any(product in cra_products for product in PLAID_PRODUCTS):
            link_request["user_token"] = user_token
            link_request["consumer_report_permissible_purpose"] = (
                ConsumerReportPermissiblePurpose("ACCOUNT_REVIEW_CREDIT")
            )
            link_request["cra_options"] = LinkTokenCreateRequestCraOptions(
                days_requested=60
            )
        # create link token
        response = client.link_token_create(link_request)
        return Response(response.to_dict())
    except plaid.ApiException as e:
        logging.error(e)
        return Response(e.body)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def exchange_public_token(request):
    public_token = request.data.get("public_token")
    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        plaid_access_token = exchange_response["access_token"]
        plaid_item_id = exchange_response["item_id"]

        item_response = client.item_get({"access_token": plaid_access_token})
        plaid_institution = item_response["item"]["institution_name"]

        new_item = PlaidAccount.objects.create(
            user=request.user,
            institution=plaid_institution,
            access_token=plaid_access_token,
            item_id=plaid_item_id,
            connection_type="plaid",
        )

        # Trigger the fetch task for the new account
        fetch_plaid_account_data.delay(new_item.id)

        return Response(exchange_response.to_dict())
    except plaid.ApiException as e:
        return Response(e.body)
    

