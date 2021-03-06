#
# Copyright (C) Foundry 2020
#

import base64
import binascii
import hashlib
import hmac
import json
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Tuple

import requests


class flix:
    """Flix will handle the login and expose functions to get,
    create shows etc.
    """

    def __init__(self):
        self.reset()

    def authenticate(self, hostname: str, login: str, password: str) -> Dict:
        """authenticate will authenticate a user

        Arguments:
            hostname {str} -- Hostname of the server

            login {str} -- Login of the user

            password {str} -- Password of the user

        Returns:
            Dict -- Authenticate
        """
        authdata = base64.b64encode((login + ':' + password).encode('UTF-8'))
        response = None
        header = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + authdata.decode('UTF-8'),
        }
        try:
            r = requests.post(hostname + '/authenticate', headers=header,
                              verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
            self.hostname = hostname
            self.login = login
            self.password = password
        except requests.exceptions.RequestException as err:
            print('Authentification failed', err)
            return None

        self.key = response['id']
        self.secret = response['secret_access_key']
        self.expiry = datetime.strptime(
            response['expiry_date'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
        return response

    def get_shows(self) -> Dict:
        """get_shows retrieve the list of shows

        Returns:
            Dict -- Shows
        """
        headers = self.__get_headers(None, '/shows', 'GET')
        response = None
        try:
            r = requests.get(self.hostname + '/shows', headers=headers,
                             verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
            response = response.get('shows')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve shows', err)
            return None
        return response

    def get_asset(self, asset_id: int) -> Dict:
        """get_asset retrieve an asset

        Arguments:
            asset_id {int} -- Asset ID

        Returns:
            Dict -- Asset
        """
        url = '/asset/{0}'.format(asset_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None

        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve asset', err)
            return None
        return response

    def get_episodes(self, show_id: int) -> Dict:
        """get_episodes retrieve the list of episodes from a show

        Arguments:
            show_id {int} -- Show ID

        Returns:
            Dict -- Episodes
        """
        url = '/show/{0}/episodes'.format(show_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            r.raise_for_status()
            response = json.loads(r.content)
            response = response.get('episodes')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve episodes', err)
            return None
        return response

    def get_sequences(self, show_id: int, episode_id: int = None) -> Dict:
        """get_sequences retrieve the list of sequence from a show

        Arguments:
            show_id {int} -- Show ID

            episode_id {int} -- Episode ID (default: {None})

        Returns:
            Dict -- Sequences
        """
        url = '/show/{0}/sequences'.format(show_id)
        if episode_id is not None:
            url = '/show/{0}/episode/{1}/sequences'.format(
                show_id, episode_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
            response = response.get('sequences')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve sequences', err)
            return None
        return response

    def get_panels(
            self, show_id: int, sequence_id: int, rev_number: int) -> Dict:
        """get_panels retrieve the list of panels from a sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            rev_number {int} -- Sequence revision number

        Returns:
            Dict -- Panels
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/panels'.format(
            show_id, sequence_id, rev_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
            response = response.get('panels')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve panels', err)
            return None
        return response

    def get_dialogues(
            self, show_id: int, sequence_id: int, rev_number: int) -> Dict:
        """get_dialogues get the list of dialogues from a sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            rev_number {int} -- Sequence revision number

        Returns:
            Dict -- Dialogues
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/dialogues'.format(
            show_id, sequence_id, rev_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
            response = response.get('dialogues')
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve dialogues', err)
            return None
        return response

    def get_sequence_rev(self, show_id: int, sequence_id: int,
                         revision_number: int) -> Dict:
        """get_sequence_rev retrieve a sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            revision_number {int} -- Sequence Revision Number

        Returns:
            Dict -- Sequence Revision
        """
        url = '/show/{0}/sequence/{1}/revision/{2}'.format(
            show_id, sequence_id, revision_number)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve sequence revision', err)
            return None
        return response

    def download_media_object(
            self, temp_filepath: str, media_object_id: int) -> str:
        """download_media_object download a media object

        Arguments:
            temp_filepath {str} -- Temp filepath to store the downloaded file

            media_object_id {int} -- Media Object ID

        Returns:
            str -- Temp filepath of the downloaded file
        """
        url = '/file/{0}/data'.format(media_object_id)
        headers = self.__get_headers(None, url, 'GET')
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            file = open(temp_filepath, 'wb')
            file.write(r.content)
            file.close()
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve media object', err)
            return None
        return temp_filepath

    def start_quicktime_export(self,
                               show_id: int,
                               sequence_id: int,
                               seq_rev_number: int,
                               panel_revisions: List,
                               episode_id: int = None,
                               include_dialogue: bool = False) -> Dict:
        """start_quicktime_export will create a quicktime export

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            seq_rev_number {int} -- Sequence Revision Number

            panel_revisions {List} -- List of panel revisions

            episode_id {int} -- Episode ID (default: {None})

            include_dialogue {bool} -- Include Dialogue (default: {False})

        Returns:
            Dict -- Export response
        """
        url = '/show/{0}/sequence/{1}/revision/{2}/export/quicktime'.format(
            show_id, sequence_id, seq_rev_number)
        if episode_id is not None:
            url = ('/show/{0}/episode/{1}/sequence/{2}/revision/{3}/' +
                   'export/quicktime').format(
                       show_id, episode_id, sequence_id, seq_rev_number)
        content = {
            'include_dialogue': include_dialogue,
            'panel_revisions': panel_revisions
        }
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers,
                              data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not export quicktime', err)
            return None
        return response

    def get_chain(self, chain_id: int) -> Dict:
        """get_sequence_rev retrieve a chain

        Arguments:
            chain_id {int} -- Chain ID

        Returns:
            Dict -- Chain
        """
        url = '/chain/{0}'.format(chain_id)
        headers = self.__get_headers(None, url, 'GET')
        response = None
        try:
            r = requests.get(self.hostname + url, headers=headers,
                             verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not retrieve chain', err)
            return None
        return response

    def new_sequence_revision(self,
                              show_id: int,
                              sequence_id: int,
                              revisioned_panels: List,
                              markers: List,
                              comment: str = 'From Shotgun') -> Dict:
        """new_sequence_revision will create a new sequence revision

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            revisioned_panels {List} -- List of revisionned panels

            markers {List} -- List of Markers

            comment {str} -- Comment (default: {'From Shotgun'})

        Returns:
            Dict -- Sequence Revision
        """
        url = '/show/{0}/sequence/{1}/revision'.format(show_id, sequence_id)
        content = {
            'comment': comment,
            'imported': False,
            'meta_data': {
                'annotations': [],
                'audio_timings': [],
                'highlights': [],
                'markers': markers
            },
            'revisioned_panels': revisioned_panels
        }
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers,
                              data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not create sequence revision', err)
            return None
        return response

    def new_panel(
            self, show_id: int, sequence_id: int, asset_id: int = None,
            duration: int = 12) -> Dict:
        """new_panel will create a blank panel

        Arguments:
            show_id {int} -- Show ID

            sequence_id {int} -- Sequence ID

            asset_id {int} -- Asset ID (default: {None})

            duration {int} -- Duration (default: {12})

        Returns:
            Dict -- Panel
        """
        url = '/show/{0}/sequence/{1}/panel'.format(show_id, sequence_id)
        content = {
            'duration': duration,
        }
        if asset_id is not None:
            content['asset'] = {'asset_id': asset_id}
        headers = self.__get_headers(content, url, 'POST')
        response = None
        try:
            r = requests.post(self.hostname + url, headers=headers,
                              data=json.dumps(content), verify=False)
            response = json.loads(r.content)
        except requests.exceptions.RequestException as err:
            if r is not None and r.status_code == 401:
                print('Your token has been revoked')
            else:
                print('Could not create blank panel', err)
            return None
        return response

    def reset(self):
        """reset will reset the user info
        """
        self.hostname = None
        self.secret = None
        self.expiry = None
        self.login = None
        self.password = None
        self.key = None

    def mo_per_shots(self,
                     panels_per_markers: Dict,
                     show_id: int,
                     seq_id: int,
                     seq_rev_number: int,
                     episode_id: int = None) -> Dict:
        """mo_per_shots will make a mapping of all media objects per shots and
        will start the quicktime export per shot

        Arguments:
            panels_per_markers {Dict} -- Panels per markers

            show_id {int} -- Show ID

            seq_id {int} -- Sequence ID

            seq_rev_number {int} -- Sequence Revision ID

            episode_id {int} -- Episode ID (default: {None})

        Returns:
            Dict -- Media objects per shots
        """
        mo_per_shots = {}
        for shot_name in panels_per_markers:
            mo_per_shots[shot_name] = {'artwork': [], 'thumbnails': []}
            panels = panels_per_markers[shot_name]
            for p in panels:
                asset = self.get_asset(
                    p.get('asset').get('asset_id'))
                if asset is None:
                    return None, False
                artwork = asset.get('media_objects', {}).get('artwork')[0]
                mo_per_shots[shot_name]['artwork'].append({
                    'name': artwork.get('name'),
                    'id': p.get('id'),
                    'revision_number': p.get('revision_number'),
                    'pos': p.get('pos'),
                    'mo': artwork.get('id')
                })
                mo_per_shots[shot_name]['thumbnails'].append(
                    {'name': asset.get('media_objects', {}).get('thumbnail')
                     [0].get('name'),
                     'id': p.get('id'),
                     'revision_number': p.get('revision_number'),
                     'pos': p.get('pos'),
                     'mo': asset.get('media_objects', {}).get('thumbnail')
                     [0].get('id')})
        return mo_per_shots, True

    def get_mo_quicktime_export(
            self, shot_name: str, panels: List, show_id: int, seq_id: int,
            seq_rev_number: int, episode_id: int,
            on_retry: Callable[[int],
                               None]):
        """get_mo_quicktime_export will start the quicktime export and wait until it
        is completed and retrieve the asset from it to return his media object ID

        Arguments:
            shot_name {str} -- Shot name

            panels {List} -- List of panels to export

            show_id {int} -- Show ID

            seq_id {int} -- Sequence ID

            seq_rev_number {int} -- Sequence Revision Number

            episode_id {int} -- Episode ID

            on_retry {Callable[[int], None]} -- Callback for the on retry

        Returns:
            int -- Media Object ID of the quicktime
        """

        chain_id = self.start_quicktime_export(
            show_id, seq_id, seq_rev_number, panels, episode_id, False)
        retry = 0
        while True:
            res = self.get_chain(chain_id)
            if res is None or res.get('status') == 'errored' or res.get(
                    'status') == 'timed out':
                return None
            if res.get('status') == 'in progress':
                on_retry(retry)
                retry = retry + 1
                time.sleep(1)
                continue
            if res.get('status') == 'completed':
                asset = self.get_asset(
                    res.get('results', {}).get('assetID'))
                if asset is None:
                    return None
                return asset.get(
                    'media_objects', {}).get('artwork', [])[0].get('id')

    def get_markers(self, sequence_revision: object) -> Dict:
        """get_markers will format the sequence_revision to have a
        mapping of markers: start -> marker_name

        Arguments:
            sequence_revision {object} -- Sequence revision

        Returns:
            Dict -- Markers by start time
        """
        markers_mapping = {}
        markers = sequence_revision.get('meta_data', {}).get('markers', [])
        for m in markers:
            markers_mapping[m.get('start')] = m.get('name')
        return OrderedDict(sorted(markers_mapping.items()))

    def format_panel_for_revision(self, panel: object, pos: int) -> object:
        """format_panel_for_revision will format the panel as
        revisionned panel

        Arguments:
            panel {object} -- Panel from Flix

            pos {int} -- Position in the Flix timeline

        Returns:
            object -- Formatted panel
        """
        return {
            'dialogue': panel.get('dialogue'),
            'duration': panel.get('duration'),
            'id': panel.get('panel_id'),
            'revision_number': panel.get('revision_number'),
            'asset': panel.get('asset'),
            'pos': pos
        }

    def get_markers_per_panels(self, markers: List, panels: List) -> Dict:
        """get_markers_per_panels will return a mapping of markers per panels

        Arguments:
            markers {List} -- List of markers

            panels {List} -- List of panels

        Returns:
            Dict -- Panels per markers
        """
        panels_per_markers = {}
        panel_in = 0
        markers_keys = list(markers.keys())
        marker_i = 0
        for i, p in enumerate(panels):
            if markers_keys[marker_i] == panel_in:
                panels_per_markers[markers[markers_keys[marker_i]]] = []
                panels_per_markers[markers[markers_keys[marker_i]]].append(
                    self.format_panel_for_revision(p, i))
                if len(markers_keys) > marker_i + 1:
                    marker_i = marker_i + 1
            elif markers_keys[marker_i] > panel_in:
                panels_per_markers[markers[markers_keys[marker_i - 1]]].append(
                    self.format_panel_for_revision(p, i))
            elif len(markers_keys) - 1 == marker_i:
                if markers[markers_keys[marker_i]] not in panels_per_markers:
                    panels_per_markers[markers[markers_keys[marker_i]]] = []
                panels_per_markers[markers[markers_keys[marker_i]]].append(
                    self.format_panel_for_revision(p, i))
            panel_in = panel_in + p.get('duration')
        return panels_per_markers

    def __get_token(self) -> Tuple[str, str]:
        """__get_token will request a token and will reset it
        if it is too close to the expiry date

        Returns:
            Tuple[str, str] -- Key and Secret
        """
        if (self.key is None or self.secret is None or self.expiry is None or
                datetime.now() + timedelta(hours=2) > self.expiry):
            authentificationToken = self.authenticate(
                self.hostname, self.login, self.password)
            auth_id = authentificationToken['id']
            auth_secret_token = authentificationToken['secret_access_key']
            auth_expiry_date = authentificationToken['expiry_date']
            auth_expiry_date = auth_expiry_date.split('.')[0]
            self.key = auth_id
            self.secret = auth_secret_token
            self.expiry = datetime.strptime(auth_expiry_date,
                                            '%Y-%m-%dT%H:%M:%S')
        return self.key, self.secret

    def __fn_sign(self,
                  access_key_id: str,
                  secret_access_key: str,
                  url: str,
                  content: object,
                  http_method: str,
                  content_type: str,
                  dt: str) -> str:
        """After being logged in, you will have a token.

        Arguments:
            access_key_id {str} -- Access key ID from your token

            secret_access_key {str} -- Secret access key from your token

            url {str} -- Url of the request

            content {object} -- Content of your request

            http_method {str} -- Http Method of your request

            content_type {str} -- Content Type of your request

            dt {str} -- Datetime

        Raises:
            ValueError: 'You must specify a secret_access_key'

        Returns:
            str -- Signed header
        """
        raw_string = http_method.upper() + '\n'
        content_md5 = ''
        if content:
            if isinstance(content, str):
                content_md5 = hashlib.md5(content).hexdigest()
            elif isinstance(content, bytes):
                hx = binascii.hexlify(content)
                content_md5 = hashlib.md5(hx).hexdigest()
            elif isinstance(content, dict):
                jsoned = json.dumps(content)
                content_md5 = hashlib.md5(jsoned.encode('utf-8')).hexdigest()
        if content_md5 != '':
            raw_string += content_md5 + '\n'
            raw_string += content_type + '\n'
        else:
            raw_string += '\n\n'
        raw_string += dt.isoformat().split('.')[0] + 'Z' + '\n'
        url_bits = url.split('?')
        url_without_query_params = url_bits[0]
        raw_string += url_without_query_params
        if len(secret_access_key) == 0:
            raise ValueError('You must specify a secret_access_key')
        digest_created = base64.b64encode(
            hmac.new(secret_access_key.encode('utf-8'),
                     raw_string.encode('utf-8'),
                     digestmod=hashlib.sha256).digest()
        )
        return 'FNAUTH ' + access_key_id + ':' + digest_created.decode('utf-8')

    def __get_headers(
            self, content: object, url: str, method: str = 'POST') -> object:
        """__get_headers will generate the header to make any request
        containing the authorization with signature

        Arguments:
            content {object} -- Content of the request

            url {str} -- Url to make the request

            method {str} -- Request method (default: {'POST'})

        Returns:
            object -- Headers
        """
        dt = datetime.utcnow()
        key, secret = self.__get_token()
        return {
            'Authorization': self.__fn_sign(
                key,
                secret,
                url,
                content,
                method,
                'application/json',
                dt),
            'Content-Type': 'application/json',
            'Date': dt.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        }
