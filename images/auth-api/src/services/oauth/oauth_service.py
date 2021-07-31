from google_provider import GoogleProvider


class OAuthService:
    providers = {
        'google': GoogleProvider
    }

    @classmethod
    def get_provider(cls, provider_name):
        return cls.providers[provider_name]
