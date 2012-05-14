class RequestForm(forms.ModelForm):
    company_url = forms.URLField(max_length=60, required=False, label="Company URL", widget=TextInput(attrs={'style': "width: %s;" % text_input_width}),)
    usage = forms.CharField(max_length=500, required=True, label="How are you planning to use this API? * \n(e.g. mobile app, local directory, etc)", widget=forms.Textarea(attrs={'class': 'forminput', 'style': "height: 100px"}),)
    category = models.ForeignKey('foo.bar', blank=False, null=True, help_text='You must select a category. If none is appropriate, select Other.')
