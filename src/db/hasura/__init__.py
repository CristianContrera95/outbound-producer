import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import log as requests_logger


requests_logger.setLevel(logging.ERROR)

class GraphQL:

    def __init__(self, hasura_url, hasura_token):
        headers = {
            "content-type": "application/json",
            "x-hasura-admin-secret": hasura_token
        }
        transport = AIOHTTPTransport(url=hasura_url, headers=headers)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def query(self, query: str, schema = None):
        result = self.client.execute(gql(query))
        if schema is not None:
            result = schema(result)
        return result


# # Example a GraphQL query
# graphql = GraphQL(os.getenv("HASURA_URL"), os.getenv("HASURA_TOKEN"))
#
# gql_client = GraphQL()
# result = gql_client.query("""
#   query getContinents {
#     continents {
#       code
#       name
#     }
#   }
# """)
# print(result)
