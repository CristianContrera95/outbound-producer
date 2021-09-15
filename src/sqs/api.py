import json
import time
import hashlib
import logging
from uuid import uuid4

import boto3
from boto.sqs.message import Message as SqsMessage

from sqs.exceptions import SQSEmptyQueue
from settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class SqsService:
    def __init__(self, queue_name, aws_access_key_id, aws_secret_access_key):
        _sqs = boto3.resource('sqs',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name='us-east-1')
        self.queue = _sqs.get_queue_by_name(QueueName=queue_name)

    @property
    def name(self) -> str:
        return self.queue.attributes['QueueArn'].split(':')[-1]

    @property
    def amount_msg(self) -> int:
        return int(self.queue.attributes['ApproximateNumberOfMessages'])

    def _send_msg(self, entries):
        """  # TODO: can send msg in parallel ?
        send messages to sqs in batch (10 msg at a time)
        :param entries: list of messages
        :return:
        """
        limit = 10
        offset = 0

        fail_msg = []  # to save failed messages

        logger.info("Let going to send messages")
        # Let going to iterate the list and send 10 messages
        n_iter = len(entries) // limit + 1
        for _ in range(n_iter):
            # send messages
            response = self.queue.send_messages(Entries=entries[offset:limit])
            # check failed msg
            if 'Failed' in response.keys():
                for fail in response['Failed']:
                    failed_msg = list(filter(lambda x: x['Id'] == fail['Id'], entries[offset:limit]))[0]
                    fail_msg.append(failed_msg)
                    # TODO: do something with this.. or not..

            # update slice
            offset = limit
            limit += 10
        logger.info(f"Messages failed:\n{fail_msg}")

    def send_msg(self, messages):
        entries = []
        for number, msg in messages.items():
            entries.append({
                'Id': str(uuid4()),
                'MessageBody': json.dumps({number: msg})
            })
        self._send_msg(entries)

    def get_msg(self, ) -> SqsMessage:
        try:
            message = self.queue.receive_messages(MaxNumberOfMessages=1)[0]
            return message
        except IndexError:
            raise SQSEmptyQueue

    @staticmethod
    def delete_msg(message: SqsMessage):
        message.delete()

    @staticmethod
    def _get_message_deduplication_id(body: str):
        timestamp = int(time.time())
        seed = "{body}{timestamp}".format(body=body, timestamp=str(timestamp)[:-1])
        ob = hashlib.sha256(seed.encode())
        return ob.hexdigest()
