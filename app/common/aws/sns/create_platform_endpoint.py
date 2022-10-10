import boto3
import botocore
import sys
import os
args = sys.argv
# from boto3.exceptions import InvalidParameterException, InternalErrorException, AuthorizationErrorException, NotFoundException
# TODO 定数ファイルへのパスを考慮
sys.path.append('../../../')
from const import const


def create_platform_endpoint(token, sns=None):

    if not sns:
        sns = boto3.resource('sns')
    platform_application = sns.PlatformApplication(
        os.environ["PLATFORM_APPLICATION_ARN"])

    try:
        platform_endpoint = platform_application.create_platform_endpoint(
            Token=token,
            # CustomUserData='string',
            # Attributes={
            #     'string': 'string'
            # }
        )
    except botocore.exceptions.ClientError as e:
        print(f'ClientError {e}')
        return
    # except InternalErrorException as e:
    #     print(f'InternalErrorException {e}')
    # except AuthorizationErrorException as e:
    #     print(f'AuthorizationErrorException {e}')
    # except NotFoundException as e:
    #     print(f'NotFoundException {e}')
    print(platform_endpoint)
    print(platform_endpoint.arn)
    return platform_endpoint.arn


if __name__ == "__main__":
    create_platform_endpoint(
        '3d9d89bae5f1b699d4ff0c9538e6b28b22748b27d1e5403fd923ded78d023a29')
