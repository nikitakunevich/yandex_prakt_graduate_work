from pydantic import BaseSettings


class Settings(BaseSettings):
    log_level: str = "INFO"
    cf_key_id = "K33LU8UGJYKH9R"
    cf_domain_name = "d3cyckes3v9dct.cloudfront.net"
    cf_private_key_file = "../cloudfront-keys/private_key.pem"
    url_path_prefix = "assets"
    url_expire_hours = 8


settings = Settings()
