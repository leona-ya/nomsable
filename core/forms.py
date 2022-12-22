from django import forms


class ParserInsertForm(forms.Form):
    url = forms.URLField(label="website url")
