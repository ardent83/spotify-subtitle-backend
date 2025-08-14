from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from .models import AccessRefreshToken


@receiver(pre_social_login)
def save_spotify_tokens(sender, request, sociallogin, **kwargs):
    if sociallogin.account.provider == 'spotify':
        user = sociallogin.user
        token = sociallogin.token

        AccessRefreshToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': token.token,
                'refresh_token': token.token_secret
            }
        )
