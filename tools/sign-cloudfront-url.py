from datetime import datetime, timedelta

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner

# pip install cryptography
# https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-creating-signed-url-canned-policy.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#examples


def rsa_signer(message):
    with open('../images/movies-on-demand-api-dev/cloudfront-keys/private_key.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


key_id = 'K1V7VQCAGHUSXP'
base_url = 'https://d28ajo2rmubsoy.cloudfront.net'
path_prefix = 'assets'
movie_file_name = 'girl-showing-rainbow.mp4'
url = base_url + '/' + path_prefix + '/' + movie_file_name
expire_date = datetime.now() + timedelta(hours=8)

cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

# Create a signed url that will be valid until the specific expiry date
# provided using a canned policy.
signed_url = cloudfront_signer.generate_presigned_url(
    url, date_less_than=expire_date)
print(signed_url)

