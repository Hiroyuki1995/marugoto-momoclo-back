import boto3
import sys
import os
args = sys.argv
# TODO 定数ファイルへのパスを考慮
sys.path.append('../../../')
from const import const


# 指定されたデバイストークンがプラットフォームアプリケーション"marugoto-momoclo"の中で
# エンドポイントとして登録されているかどうかをBooleanで返す
def get_endpoint(device_token):
    sns = boto3.client('sns')
    list_endpoints = sns.list_endpoints_by_platform_application(
        PlatformApplicationArn=os.environ["PLATFORM_APPLICATION_ARN"])
    endpoint_tokens = []
    for endpoint in list_endpoints['Endpoints']:
        token = endpoint['Attributes']['Token']
        endpoint_tokens.append(token)
    print(f'endpoint_tokens {endpoint_tokens}')
    is_registered = device_token in endpoint_tokens
    if is_registered:
        index = endpoint_tokens.index(device_token)
        endpoint_arn = list_endpoints['Endpoints'][index]['EndpointArn']
        print(f'endpoint_arn {endpoint_arn}')
    return {'is_registered': is_registered, 'endpoint_arn': endpoint_arn if is_registered else None}


if __name__ == "__main__":
    get_endpoint(
        device_token='3d9d89bae5f1b699d4ff0c9538e6b28b22748b27d1e5403fd923ded78d023a29')
