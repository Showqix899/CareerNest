
from django import forms
from accounts.models import User


class SendPeerRequestForm(forms.Form):

    receiver = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["receiver"].queryset = User.objects.filter(
            is_active=True
        )


class AcceptPeerRequestForm(forms.Form):

    request_id = forms.UUIDField(
        widget=forms.HiddenInput()
    )


class RejectPeerRequestForm(forms.Form):

    request_id = forms.UUIDField(
        widget=forms.HiddenInput()
    )
