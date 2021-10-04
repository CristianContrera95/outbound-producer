import datetime as dt
import json
from enum import Enum
from typing import List, Optional

from gql.transport.exceptions import TransportQueryError

from schema.exceptions import InvalidData


def get_campaign(campaign_uid: str, graphql, raw=False):
    """
    Query and return a campaign data from db
    :param raw: bool if is True returns the campaign as it comes from the db
    """
    try:
        campaign = graphql.query(f"""
            query getCampaigns {{
              campaign(where: {{id: {{_eq: "{campaign_uid}"}}}}) {{
                name
                status
                account {{
                  id
                  name
                }}
                channel {{
                  name
                  type_id
                  value
                }}
                template {{
                  name
                  namespace
                  language
                  content
                }}
                contacts {{
                  id
                  variables
                  contact {{
                    number
                  }}
                }}
              }}
            }}
        """)
    except TransportQueryError as err:
        raise InvalidData(f"Invalid campaign_uid: {campaign_uid}")

    if not raw:
        if not campaign['campaign']:
            raise InvalidData(f"campaign {campaign_uid} don\'t exists")
        campaign = campaign['campaign'][0]
        # Hasura return contacts with a schema such as:
        # 'contacts': [
        # {'variables': {'1': 'Cristian'},
        #   'contact': {'name': 'Cristian celu', 'number': '+5493546476307'}}, {...]
        # Let transform that to this schema:
        # 'contacts': [
        # {'name': 'Cristian celu', 'number': '+5493546476307', 'variables': {'1': 'Cristian'}},
        # {'name': ..}]
        campaign['contacts'] = list(map(lambda x: {'id': x['id'], **x['contact'], 'variables': json.dumps(x['variables'])
                                        if isinstance(x['variables'], dict) else x['variables']},
                                        campaign['contacts']))

    return campaign


class eventStatus(Enum):
    error = 'error'
    done = 'done'
    pending = 'pending'


def update_campaign_contact(campaign_uid: str, contacts_uid: List[str], status: eventStatus,
                            graphql, error_desc: Optional[str] = None):
    affected_rows = graphql.query(f"""
      mutation UpdateStates {{
        update_campaign_contact(
        where: {{ 
          campaing_id: {{_eq: "{campaign_uid}"}}
          _and: {{contact: {{number: {{_in: {contacts_uid}}}}}}}
        }}
        _set: {{
          event_status_id: {status.value}
          error_description: "{error_desc}"
          msg_cost: 0
          last_update: "{dt.datetime.now()}"
        }}
        )
        {{
        affected_rows
        }}
      }}
    """.replace("'", '"'))

    return affected_rows


def update_campaign(campaign_uid: str, status: eventStatus, graphql):
    try:
        graphql.query(f"""
          mutation UpdateStatus {{
            update_campaign(
            where: {{ 
              id: {{_eq: "{campaign_uid}"}}
            }},
            _set: {{
              status: {status.value}
              updated_at: "{dt.datetime.now()}"
            }}
            )
            {{
            affected_rows
            }}
          }}
        """)
    except TransportQueryError as err:
        raise InvalidData(f"Invalid campaign_uid: {campaign_uid}")
