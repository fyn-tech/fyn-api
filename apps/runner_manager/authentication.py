from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import RunnerInfo


class RunnerTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            runner = RunnerInfo.objects.select_related("owner").get(token=key)
        except RunnerInfo.DoesNotExist:
            raise AuthenticationFailed("Invalid runner token.")

        if not runner.owner.is_active:
            raise AuthenticationFailed("User account is disabled.")

        user = runner.owner
        user._runner_info = runner

        return (user, runner)
