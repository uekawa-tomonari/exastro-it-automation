# Copyright 2022 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
共通関数 module
"""
import secrets
import string
import base64
import codecs
from pathlib import Path
import pytz
import datetime
from datetime import timezone
import re
import os
from flask import g
import requests
import json
import shutil
from common_libs.common.exception import AppException
from common_libs.common.encrypt import *


def ky_encrypt(lcstr):
    """
    Encode a string

    Arguments:
        lcstr: Encoding target value
    Returns:
        Encoded string
    """
    if lcstr is None:
        return ""

    if len(lcstr) == 0:
        return ""

    return encrypt_str(lcstr)


def ky_decrypt(lcstr):
    """
    Decode a string

    Arguments:
        lcstr: Decoding target value
    Returns:
        Decoded string
    """
    if lcstr is None:
        return ""

    if len(lcstr) == 0:
        return ""

    return decrypt_str(lcstr)


def ky_file_encrypt(src_file, dest_file):
    """
    Encode a file

    Arguments:
        src_file: Encoding target file
        dest_file: Encoded file
    Returns:
        is success:(bool)
    """
    try:
        # ファイルオープン
        fsrc = open(src_file)

        # ファイル読み込み
        lcstr = Path(src_file).read_text(encoding="utf-8")

        # エンコード関数呼び出し
        enc_data = ky_encrypt(lcstr)

        # ファイル書き込み
        Path(dest_file).write_text(enc_data, encoding="utf-8")
    except Exception:
        return False
    finally:
        # ファイルクローズ
        fsrc.close()

    return True


def ky_file_decrypt(src_file, dest_file):
    """
    Decode a file

    Arguments:
        src_file: Decoding target file
        dest_file: Decoded file
    Returns:
        is success:(bool)
    """
    try:
        # ファイルオープン
        fsrc = open(src_file)

        # ファイル読み込み
        lcstr = Path(src_file).read_text(encoding="utf-8")

        # デコード関数呼び出し
        enc_data = ky_decrypt(lcstr)

        # ファイル書き込み
        Path(dest_file).write_text(enc_data, encoding="utf-8")
    except Exception:
        return False
    finally:
        # ファイルクローズ
        fsrc.close()

    return True


def generate_secrets(length=16, punctuation=''):
    """
    generate secrets

    Arguments:
        length: secrets length
        punctuation: symbol used
    Returns:
        (str)secrets value
    """
    # string.ascii_letters - alfabet lower and upper
    # string.digits - number
    # string.punctuation - symbol  !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    pass_chars = string.ascii_letters + string.digits + punctuation
    secrets_val = ''.join(secrets.choice(pass_chars) for x in range(length))

    return secrets_val


def get_timestamp(is_utc=True):
    """
    get timestamp

    Returns:
        2022-07-01 07:36:24.551751
    """
    return datetime.datetime.now()


def get_iso_datetime(is_utc=True):
    """
    get timestamp for api response format

    Args:
        is_utc (bool):

    Returns:
        2022-08-02T10:26:18.809Z
    """
    return datetime_to_str(datetime.datetime.now())


def datetime_to_str(p_datetime):
    """datetime to string (ISO format)
    Args:
        p_datetime (datetime): datetime
    Returns:
        str: datetime formated string (UTC)
    """
    if p_datetime is None:
        return None

    if p_datetime.tzinfo is None:
        aware_datetime = pytz.timezone(os.environ.get('TZ', 'UTC')).localize(p_datetime)
    else:
        aware_datetime = p_datetime

    utc_datetime = aware_datetime.astimezone(timezone.utc)
    return utc_datetime.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def arrange_stacktrace_format(t):
    """
    stacktrace

    Arguments:
        t: return traceback.format_exc()
    Returns:
        (str)
    """
    retStr = ""

    exception_block_arr = t.split('Traceback (most recent call last):\n')
    # exception_block = exception_block_arr[1]  # most deep exception called
    exception_block_index = 0
    for exception_block in exception_block_arr:
        exception_block = re.sub(r'\n\nDuring handling of the above exception, another exception occurred:\n\n', '', exception_block.strip())
        if exception_block[0:4] != 'File':
            continue

        retStr = retStr + "\n{} : exception block".format(exception_block_index)
        exception_block_index = exception_block_index + 1

        trace_block_arr = re.split('File ', exception_block)
        for trace_block in trace_block_arr:
            row_arr = re.split('\n', str(trace_block.strip()))
            row_index = 0
            row_str = ""
            length = len(row_arr) - 1
            if length == 0:
                continue

            for row in row_arr:

                if row_index == 0:
                    row_str = "\n -> " + row
                elif row_index == 1:
                    row_str = row_str + ", " + row.strip()
                    retStr = retStr + row_str
                elif row_index == 2:
                    retStr = retStr + "\n " + row.strip()

                row_index = row_index + 1

    return retStr


def file_encode(file_path):
    """
    Encode a file to base64

    Arguments:
        file_path: Encoding target filepath
    Returns:
        Encoded string
    """
    try:
        is_file = os.path.isfile(file_path)
        if not is_file:
            return ""

        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return False


def file_decode(file_path):
    """
    Encode a file to base64

    Arguments:
        file_path: Encoding target filepath
    Returns:
        Encoded string
    """
    try:
        is_file = os.path.isfile(file_path)
        if not is_file:
            return ""

        with open(file_path, "rb") as f:
            text = f.read().decode()
        text_decrypt = ky_decrypt(text)
        return base64.b64encode(text_decrypt.encode()).decode()
    except Exception:
        return False


def get_upload_file_path(workspace_id, menu_id, uuid, column_name_rest, file_name, uuid_jnl):
    """
    Get filepath

    Arguments:
        workspace_id: workspace_id
        menu_id: menu_id
        uuid: uuid
        column_name_rest: column_name_rest
        file_name: Target file name
        uuid_jnl: uuid_jnl
    Returns:
        filepath
    """
    organization_id = g.get("ORGANIZATION_ID")
    file_path = "/storage/{}/{}/uploadfiles/{}/{}/{}/{}".format(organization_id, workspace_id, menu_id, column_name_rest, uuid, file_name)
    old_file_path = ""
    if uuid_jnl is not None:
        if len(uuid_jnl) > 0:
            old_file_path = "/storage/{}/{}/uploadfiles/{}/{}/{}/old/{}/{}".format(organization_id, workspace_id, menu_id, column_name_rest, uuid, uuid_jnl, file_name)  # noqa: E501

    return {"file_path": file_path, "old_file_path": old_file_path}


def get_upload_file_path_specify(workspace_id, place, uuid, file_name, uuid_jnl):
    """
    Get filepath

    Arguments:
        workspace_id: workspace_id
        place: Target file place
        uuid: uuid
        file_name: Target file name
        uuid_jnl: uuid_jnl
    Returns:
        filepath
    """
    organization_id = g.get("ORGANIZATION_ID")
    file_path = "/storage/{}/{}{}/{}/{}".format(organization_id, workspace_id, place, uuid, file_name)
    old_file_path = ""
    if uuid_jnl is not None:
        if len(uuid_jnl) > 0:
            old_file_path = "/storage/{}/{}{}/{}/old/{}/{}".format(organization_id, workspace_id, place, uuid, uuid_jnl, file_name)  # noqa: E501

    return {"file_path": file_path, "old_file_path": old_file_path}


def upload_file(file_path, text):
    """
    Upload a file

    Arguments:
        file_path: Target filepath
        text: file text
    Returns:
        is success:(bool)
    """
    path = os.path.dirname(file_path)

    if type(text) is bytes:
        text = base64.b64decode(text.encode()).decode()

    if isinstance(text, str):
        text = base64.b64decode(text.encode())

    if not os.path.isdir(path):
        os.makedirs(path)

    try:
        with open(file_path, "bx") as f:
            f.write(text)
    except Exception:
        return False

    f.close

    return True


def encrypt_upload_file(file_path, text):
    """
    Encode and upload file

    Arguments:
        file_path: Target filepath
        text: file text
    Returns:
        is success:(bool)
    """
    try:
        text = base64.b64decode(text.encode()).decode()
        text = ky_encrypt(text)
    except Exception:
        return False

    path = os.path.dirname(file_path)

    if not os.path.isdir(path):
        os.makedirs(path)

    try:
        with open(file_path, "w") as f:
            f.write(text)
    except Exception:
        return False

    return True


def get_exastro_platform_workspaces():
    """
    ユーザが所属するworkspaceの一覧と、操作中のworkspaceに所属する環境をExastroPlatformに問い合わせて取得する

    Arguments:
        None
    Returns:
        workspaces:(list)
        environments:(list)
    """
    organization_id = g.get('ORGANIZATION_ID')
    workspace_id = g.get('WORKSPACE_ID')
    host_name = os.environ.get('PLATFORM_API_HOST')
    port = os.environ.get('PLATFORM_API_PORT')
    user_id = g.get('USER_ID')
    language = g.get('LANGUAGE')
    workspaces = {}
    environments_list = []
    environments = []

    header_para = {
        "Content-Type": "application/json",
        "User-Id": user_id,
        "Roles": json.dumps(g.ROLES),
        "Language": language
    }

    # 2回目以降の検索はgの値を使用する
    if organization_id == g.get("PLATFORM_WORKSPACES_ORG") and workspace_id == g.get("PLATFORM_WORKSPACES_WS") and user_id == g.get("PLATFORM_WORKSPACES_USER"):  # noqa: E501
        workspaces = g.get('PLATFORM_WORKSPACES')
        environments = g.get('PLATFORM_ENVIRONMENTS')

    else:
        # API呼出
        api_url = "http://{}:{}/internal-api/{}/platform/users/{}/workspaces".format(host_name, port, organization_id, user_id)
        request_response = requests.get(api_url, headers=header_para)

        response_data = json.loads(request_response.text)

        if request_response.status_code != 200:
            raise AppException('999-00005', [api_url, response_data])

        # workspaceの一覧を取得
        for record in response_data['data']:
            workspaces[record['id']] = record['name']
            if workspace_id == record['id']:
                if 'informations' in record and 'environments' in record['informations']:
                    environments_list = record['informations']['environments']

        for value in environments_list:
            environments.append(value['name'])

        # gに値を設定しておく
        g.PLATFORM_WORKSPACES = workspaces
        g.PLATFORM_ENVIRONMENTS = environments

        g.PLATFORM_WORKSPACES_ORG = organization_id
        g.PLATFORM_WORKSPACES_WS = workspace_id
        g.PLATFORM_WORKSPACES_USER = user_id

    return workspaces, environments


def get_workspace_roles():
    """
    workspaceに所属するロールの一覧をExastroPlatformに問い合わせて取得する

    Arguments:
        None
    Returns:
        roles:(list)
    """
    organization_id = g.get('ORGANIZATION_ID')
    workspace_id = g.get('WORKSPACE_ID')
    host_name = os.environ.get('PLATFORM_API_HOST')
    port = os.environ.get('PLATFORM_API_PORT')
    user_id = g.get('USER_ID')
    language = g.get('LANGUAGE')
    roles = []

    header_para = {
        "Content-Type": "application/json",
        "User-Id": user_id,
        "Roles": json.dumps(g.ROLES),
        "Language": language
    }

    # 2回目以降の検索はgの値を使用する
    if organization_id == g.get("WORKSPACE_ROLES_ORG") and workspace_id == g.get("WORKSPACE_ROLES_WS"):
        roles = g.get('WORKSPACE_ROLES')

    else:
        # API呼出
        api_url = "http://{}:{}/internal-api/{}/platform/workspaces/{}/roles".format(host_name, port, organization_id, workspace_id)
        request_response = requests.get(api_url, headers=header_para)

        response_data = json.loads(request_response.text)

        if request_response.status_code != 200:
            raise AppException('999-00005', [api_url, response_data])

        # workspaceの一覧を取得
        for record in response_data['data']:
            roles.append(record['name'])

        # gに値を設定しておく
        g.WORKSPACE_ROLES = roles

        g.WORKSPACE_ROLES_ORG = organization_id
        g.WORKSPACE_ROLES_WS = workspace_id

    return roles


def get_exastro_platform_users():
    """
    workspaceに所属するユーザの一覧をExastroPlatformに問い合わせて取得する

    Arguments:
        None
    Returns:
        users:(list)
    """
    organization_id = g.get('ORGANIZATION_ID')
    workspace_id = g.get('WORKSPACE_ID')
    host_name = os.environ.get('PLATFORM_API_HOST')
    port = os.environ.get('PLATFORM_API_PORT')
    user_id = g.get('USER_ID')
    language = g.get('LANGUAGE')
    users = {}

    if "ROLES" in g:
        roles = g.ROLES
    else:
        roles = ""

    header_para = {
        "Content-Type": "application/json",
        "User-Id": user_id,
        "Roles": json.dumps(roles),
        "Language": language
    }

    # 2回目以降の検索はgの値を使用する
    if organization_id == g.get("PLATFORM_USERS_ORG") and workspace_id == g.get("PLATFORM_USERS_WS"):
        users = g.get('PLATFORM_USERS')

    else:
        # API呼出
        api_url = "http://{}:{}/internal-api/{}/platform/workspaces/{}/users".format(host_name, port, organization_id, workspace_id)
        request_response = requests.get(api_url, headers=header_para)

        response_data = json.loads(request_response.text)

        if request_response.status_code != 200:
            raise AppException('999-00005', [api_url, response_data])

        # workspaceの一覧を取得
        for record in response_data['data']:
            users[record['id']] = record['name']

        # gに値を設定しておく
        g.PLATFORM_USERS = users
        g.PLATFORM_USERS_ORG = organization_id
        g.PLATFORM_USERS_WS = workspace_id

    return users


def get_user_name(user_id):
    """
    ユーザIDを元にユーザ名を取得する

    Arguments:
        user_id: ユーザID
    Returns:
        user_name: (string)
    """
    user_name = ""
    users = get_exastro_platform_users()

    if user_id in users:
        user_name = users[user_id]
    else:
        status_code = 'MSG-00001'
        user_name = g.appmsg.get_api_message(status_code, [user_id])

    return user_name


def get_all_execution_limit(limit_key):
    """
    システム全体の同時実行数最大値取得

    Returns:
        limit値
    """
    host_name = os.environ.get('PLATFORM_API_HOST')
    port = os.environ.get('PLATFORM_API_PORT')

    header_para = {
        "Content-Type": "application/json",
        "User-Id": "dummy",
    }

    # API呼出
    api_url = "http://{}:{}/internal-api/platform/settings/common".format(host_name, port)
    request_response = requests.get(api_url, headers=header_para)

    response_data = json.loads(request_response.text)

    if request_response.status_code != 200:
        raise AppException('999-00005', [api_url, response_data])

    # システム全体の同時実行数最大値取得
    limit = 0
    for record in response_data['data']:
        if record["key"] == limit_key:
            limit = record["value"]

    return limit


def get_org_execution_limit(limit_key):
    """
    Organization毎の同時実行数最大値取得

    Returns:
        limit値
    """
    host_name = os.environ.get('PLATFORM_API_HOST')
    port = os.environ.get('PLATFORM_API_PORT')

    header_para = {
        "Content-Type": "application/json",
        "User-Id": "dummy",
        "Roles": "dummy",
        "Language": g.get('LANGUAGE')
    }

    # API呼出
    api_url = "http://{}:{}/internal-api/platform/limits".format(host_name, port)
    request_response = requests.get(api_url, headers=header_para)

    response_data = json.loads(request_response.text)

    if request_response.status_code != 200:
        raise AppException('999-00005', [api_url, response_data])

    # システム全体の同時実行数最大値取得
    limit_list = {}
    for record in response_data['data']:
        if limit_key in record["limits"]:
            limit_list[record["organization_id"]] = record["limits"][limit_key]
        else:
            limit_list[record["organization_id"]] = 0

    return limit_list


def create_dirs(config_file_path, dest_dir):
    """
    config_file_pathのファイルに記載されているディレクトリをdest_dir配下に作成する

    Arguments:
        config_file_path: 設定ファイル
        dest_dir: 作成するディレクトリ
    Returns:
        is success:(bool)
    """
    with open(config_file_path) as f:
        lines = f.readlines()

    for target_path in lines:
        target_path = target_path.replace("\n", "")
        try:
            os.makedirs(dest_dir + target_path)
        except FileExistsError:
            pass
    return True


def put_uploadfiles(config_file_path, src_dir, dest_dir):
    """
    config_file_pathのファイルに記載されているファイルをdest_dir配下に作成する

    Arguments:
        config_file_path: 設定ファイル
        src_dir: コピー元のファイル格納ディレクトリ
        dest_dir: 作成するディレクトリ
    Returns:
        is success:(bool)
    """
    with open(config_file_path, 'r') as material_conf_json:
        material_conf = json.load(material_conf_json)
        for menu_id, file_info_list in material_conf.items():
            for file_info in file_info_list:
                for file, copy_cfg in file_info.items():
                    # org_file = src_dir + "/".join([menu_id, file])
                    org_file = os.path.join(os.path.join(src_dir, menu_id), file)
                    old_file_path = os.path.join(dest_dir, menu_id) + copy_cfg[0]
                    file_path = os.path.join(dest_dir, menu_id) + copy_cfg[1]

                    if not os.path.isdir(old_file_path):
                        os.makedirs(old_file_path)

                    shutil.copy(org_file, old_file_path + file)
                    try:
                        os.symlink(old_file_path + file, file_path + file)
                    except FileExistsError:
                        pass

    return True


if __name__ == '__main__':
    # print(generate_secrets())
    pass


def get_maintenance_mode_setting():
    """
    メンテナンスモードの状態を取得する

    Returns:
        maintenance_mode
    """
    host_name = os.environ.get('PLATFORM_API_HOST')
    port = os.environ.get('PLATFORM_API_PORT')

    header_para = {
        "Content-Type": "application/json",
        "User-Id": "dummy",
    }

    # API呼出
    api_url = "http://{}:{}/internal-api/platform/maintenance-mode-setting".format(host_name, port)
    request_response = requests.get(api_url, headers=header_para)

    response_data = json.loads(request_response.text)

    if request_response.status_code != 200:
        raise AppException('999-00005', [api_url, response_data])

    # メンテナンスモードの設定値を取得
    maintenance_mode = response_data.get('data')

    return maintenance_mode
