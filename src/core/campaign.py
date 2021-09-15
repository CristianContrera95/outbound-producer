import logging

from db.hasura import campaign as campaign_db
from schema.campaign import Campaign
from settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


def launch_campaign(campaign_id, graphql, sqs, wpp_client):

    # get campaign
    logger.info(f"Get from hasura campaign: {campaign_id}")
    campaign_data = campaign_db.get_campaign(campaign_id, graphql)

    logger.info(f"Map campaign data to schema")
    campaign = Campaign(**campaign_data)

    logger.info(f"Validate contacts")
    campaign.validate_fields()

    logger.info(f"Validate and get wpp_id for each number")
    contacts_wpp = wpp_client.contact_ids([contact.number for contact in campaign.contacts])
    if contacts_wpp is not None:

        logger.info(f"Creating messages for sqs")
        messages = {}
        valid_numbers = []
        bad_numbers = []
        account_id = campaign.account.id
        campaign_len = len(campaign.contacts)

        for idx, contact in enumerate(campaign.contacts):
            if contacts_wpp[contact.number]['status'] == 'valid':
                messages[contact.number] = {
                    "to": contacts_wpp[contact.number]['wa_id'],
                    "type": "template",
                    "namespace": campaign.template.namespace,
                    "name": campaign.template.name,
                    "language": campaign.template.language,
                    "variables": contact.variables,
                    "campaign_uid": campaign_id,
                    "account_id": str(account_id),
                    "from": campaign.channel.value,
                    "last_campaign_msg": idx + 1 == campaign_len
                }
                valid_numbers.append(contact.number)
            else:
                bad_numbers.append(contact.number)

        if valid_numbers:
            campaign_db.update_campaign_contact(campaign_id,
                                                list(valid_numbers),
                                                campaign_db.eventStatus.pending,
                                                graphql,
                                                '')
        if bad_numbers:
            campaign_db.update_campaign_contact(campaign_id,
                                                list(bad_numbers),
                                                campaign_db.eventStatus.error,
                                                graphql,
                                                'invalid contact number')

        logger.info(f"{len(messages)} messages formatted")
        if len(messages) == 0:
            logger.info("Not messages to send")
            return

        sqs.send_msg(messages)
