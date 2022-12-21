import pytest
import os
import vcr
import mailerlite as MailerLite

from dotenv import load_dotenv
from pytest import fixture

@fixture
def subscriber_keys():
    return ['id', 'email', 'status', 'source', 'sent', 'opens_count', 'click_rate', 'ip_address', 'subscribed_at', 'unsubscribed_at', 'created_at', 'updated_at']

@fixture
def import_keys():
    return ['id', 'total', 'processed', 'imported', 'updated', 'errored', 'percent', 'done', 'invalid', 'invalid_count', 'mistyped', 'mistyped_count', 'changed', 'changed_count', 'unchanged', 'unchanged_count', 'unsubscribed', 'unsubscribed_count', 'role_based', 'role_based_count', 'banned_import_emails_count', 'updated_at', 'undone_at', 'stopped_at', 'undo_started_at', 'finished_at']

@fixture
def group_keys():
    return ['id', 'name', 'active_count', 'sent_count', 'opens_count', 'open_rate', 'clicks_count', 'click_rate', 'unsubscribed_count', 'unconfirmed_count', 'bounced_count', 'junk_count']

class TestSubscribers:
    @classmethod
    def setup_class(self):
        load_dotenv()

        self.client = MailerLite.Client({
            'api_key': os.getenv('API_KEY')
        })
    
    def test_api_url_is_properly_set(self):
        assert self.client.subscribers.base_api_url == "api/subscribers"

    @vcr.use_cassette('tests/vcr_cassettes/subscribers-list.yml', filter_headers=['Authorization'])
    def test_list_of_all_subscribers_should_be_returned(self, subscriber_keys):
        response = self.client.subscribers.list(limit=10, page=1)

        assert isinstance(response, dict)
        assert isinstance(response['data'], list)
        assert isinstance(response['data'][0], dict)
        assert set(subscriber_keys).issubset(response['data'][0].keys())

    def test_given_invalid_email_address_when_calling_create_then_create_subscriber_will_fail(self):
        with pytest.raises(ValueError):
            self.client.subscribers.create('wrong2mail.com')

    def test_given_invalid_param_when_caling_create_then_create_subscriber_will_fail(self):
        with pytest.raises(TypeError):
            self.client.subscribers.create('some@email.com', unknownparam=1)

    def test_given_invalid_fields_or_groups_params_when_calling_create_then_create_subscriber_will_fail(self):
        """Tests validation of additional parameters when creating a subscriber"""

        with pytest.raises(TypeError):
            self.client.subscribers.create('some@email.com', fields=[])

        with pytest.raises(TypeError):
            self.client.subscribers.create('some@email.com', groups={})
    
    @vcr.use_cassette('tests/vcr_cassettes/subscribers-create.yml', filter_headers=['Authorization'])
    def test_given_correct_params_when_calling_create_then_subscirber_is_created(self, subscriber_keys):
        response = self.client.subscribers.create('test5@email.com', fields={'name': 'Igor', 'last_name': 'Something'}, ip_address='1.1.1.1')

        pytest.entity_id = int(response['data']['id'])
        pytest.entity_email = response['data']['email']

        assert isinstance(response, dict)
        assert isinstance(response['data'], dict)
        assert set(subscriber_keys).issubset(response['data'].keys())

    @vcr.use_cassette('tests/vcr_cassettes/subscribers-update.yml', filter_headers=['Authorization'])
    def test_given_correct_params_when_calling_update_then_subscirber_is_updated(self, subscriber_keys):
        response = self.client.subscribers.update(pytest.entity_email, fields={'name': 'Someone', 'last_name': 'Something'}, ip_address='1.1.1.1')

        assert isinstance(response, dict)
        assert isinstance(response['data'], dict)
        assert set(subscriber_keys).issubset(response['data'].keys())
        assert response['data']['fields']['last_name'] == "Something"

    def test_given_invalid_subscriber_id_when_calling_get_then_returning_subscirber_will_fail(self):
        with pytest.raises(ValueError):
            self.client.subscribers.get('abcdefgh')

    @vcr.use_cassette('tests/vcr_cassettes/subscribers-get.yml', filter_headers=['Authorization'])
    def test_given_correct_params_when_calling_update_then_subscirber_is_returned(self, subscriber_keys):
        response = self.client.subscribers.get(pytest.entity_id)

        assert isinstance(response, dict)
        assert isinstance(response['data'], dict)
        assert set(subscriber_keys).issubset(response['data'].keys())

    def test_given_invalid_subscriber_id_when_calling_delete_then_returning_subscirber_will_fail(self):
        with pytest.raises(ValueError):
            self.client.subscribers.delete('abcdefgh')
    
    @vcr.use_cassette('tests/vcr_cassettes/subscribers-delete.yml', filter_headers=['Authorization'])
    def test_given_valid_subscriber_id_when_calling_delete_then_subscriber_is_deleted(self):
        response = self.client.subscribers.delete(pytest.entity_id)
        assert response == 204

        response = self.client.subscribers.delete(123123)
        assert response == 404
    
    @vcr.use_cassette('tests/vcr_cassettes/subscribers-get-import.yml', filter_headers=['Authorization'])
    def test_given_correct_import_id_when_calling_get_import_then_import_information_is_returned(self, import_keys):
        response = self.client.subscribers.get_import(75009793000998293)

        assert isinstance(response, dict)
        assert isinstance(response['data'], dict)
        assert set(import_keys).issubset(response['data'].keys())

    @vcr.use_cassette('tests/vcr_cassettes/subscribers-assign-subscriber-to-group.yml', filter_headers=['Authorization'])
    def test_given_correct_subscriber_id_and_grop_id_when_calling_assign_subscriber_to_group_then_subscriber_is_assigned(self, group_keys):
        """Tests an API call for retreiving members of a subscriber group"""

        group_id = 75011449370445335
        subscriber_id = 73931277474989872
        response = self.client.subscribers.assign_subscriber_to_group(subscriber_id, group_id)

        assert isinstance(response, dict)
        assert isinstance(response['data'], dict)
        assert set(group_keys).issubset(response['data'].keys())

    @vcr.use_cassette('tests/vcr_cassettes/subscribers-unassign-subscriber-from-group.yml', filter_headers=['Authorization'])
    def test_given_correct_subscriber_id_and_grop_id_when_calling_unassign_subscriber_from_group_then_subscriber_is_unassigned(self):
        """Tests an API call for retreiving members of a subscriber group"""

        group_id = 75011449370445335
        subscriber_id = 73931277474989872
        response = self.client.subscribers.unassign_subscriber_from_group(subscriber_id, group_id)

        assert response == True

        subscriber_id = 121212
        response = self.client.subscribers.unassign_subscriber_from_group(subscriber_id, group_id)

        assert response == False