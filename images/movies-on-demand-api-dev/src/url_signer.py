from datetime import datetime, timedelta
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner
from config import settings

KEY_ID = settings.cf_key_id
BASE_URL = 'https://' + settings.cf_domain_name
PATH_PREFIX = settings.url_path_prefix
PRIVATE_KEY_PATH = settings.cf_private_key_file


def rsa_signer(message):
    with open(PRIVATE_KEY_PATH, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


cloudfront_signer = CloudFrontSigner(KEY_ID, rsa_signer)


def get_signed_url(movie_file_name: str) -> str:

    url = BASE_URL + '/' + PATH_PREFIX + '/' + movie_file_name
    expire_date = datetime.now() + timedelta(hours=settings.url_expire_hours)

    signed_url = cloudfront_signer.generate_presigned_url(
        url, date_less_than=expire_date)
    return signed_url
