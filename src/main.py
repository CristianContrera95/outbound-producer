import os
import logging
import datetime as dt

from settings import LOGGER_NAME # call to load env vars
from core.campaign import launch_campaign
from db.hasura import GraphQL
from wpp.api import WppClient
from sqs.api import SqsService
from schema.exceptions import InvalidData


logger = logging.getLogger(LOGGER_NAME)

# instance connections to be reused by lambda
def instance_conn(only: str = ''):
    sqs = None
    graphql = None
    wpp_client = None
    try:
        if only == 'gql' or only == '':
            logger.info("Instance graphql")
            graphql = GraphQL(os.getenv("HASURA_URL"), os.getenv("HASURA_TOKEN"))

        if only == 'wpp' or only == '':
            logger.info("Instance wpp client")
            wpp_client = WppClient()

        if only == 'sqs' or only == '':
            logger.info(f"Instance Sqs client")
            sqs = SqsService(os.getenv("SQS_QUEUE_NAME"),
                             os.getenv("AWS_ACCESS_KEY"),
                             os.getenv("AWS_SECERT_KEY"))

    except Exception as ex:
        logger.exception("Client cannot be created")

    return graphql, sqs, wpp_client

def check_clients():
    global graphql, sqs, wpp_client
    if graphql is None:
        graphql, _, _ = instance_conn('gql')
    if sqs is None:
        _, sqs, _ = instance_conn('sqs')
    if wpp_client is None or wpp_client.token_expires < dt.datetime.now():
        _, _, wpp_client = instance_conn('wpp')

graphql, sqs, wpp_client = instance_conn()


def handle_campaign(event, context=None):

    logger.info(f'Launch new campaign.\nContext:\n{context}')
    if context:
        context.callbackWaitsForEmptyEventLoop = False

    check_clients()

    campaign_uid = event.get('campaign_id')
    launch_campaign(campaign_uid, graphql, sqs, wpp_client)
    return {
        "statusCode": 200
    }


# if __name__ == "__main__":
#     print(handle_campaign({'campaign_id': "2bebbfd9-71c9-48e2-99db-e94ca1b0e713"}))
