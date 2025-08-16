from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from .models import AccessRefreshToken


@receiver(user_logged_in)
def save_spotify_tokens_on_login(sender, request, user, sociallogin=None, **kwargs):
    if sociallogin and sociallogin.account.provider == 'spotify':
        token = sociallogin.token

        AccessRefreshToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': token.token,
                'refresh_token': token.token_secret
            }
        )
