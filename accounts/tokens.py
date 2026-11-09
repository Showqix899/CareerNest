from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # is_active is part of the hash, so the link stops working once used
        return f"{user.pk}{user.is_active}{timestamp}"


account_activation_token = AccountActivationTokenGenerator()