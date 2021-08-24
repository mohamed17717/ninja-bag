from django import forms
from .models import ToolIssueReport, SuggestedTool


class ToolIssueReportForm(forms.ModelForm):
  description = forms.CharField(label='', widget=forms.Textarea(attrs={
    'x-model':'issueDescription',
    'class':'w-full h-32 bg-primary-600 px-3 py-2',
    'placeholder':'Explain...',
    'x-ref':'reportIssueTextarea',
    'x-on:input':'textareaAutoGrow()',
    'style':'max-height: 60vh;',
  }))

  class Meta:
    model = ToolIssueReport
    fields = [ 'description' ]

  def clean_description(self):
    description = self.cleaned_data.get('description')
    length_required = 12

    if len(description.strip()) < length_required:
      raise forms.ValidationError(f'issue description must be more than {length_required} letter!!!')
    return description

  def get_error_meesage(self):
    return self.errors['description']


class SuggestToolForm(forms.ModelForm):
  description = forms.CharField(label='', widget=forms.Textarea(attrs={
    'x-model':'toolDescription',
    'class':'h-24 px-3 py-2 border-0 bg-primary-600',
    'placeholder':'Tool description',
    'name':'tool-suggestion',
    'x-ref':'suggestionTextarea',
    'x-on:input':'textareaAutoGrow()',
    'style':'max-height: 390px; height: 84px;',
  }))

  class Meta:
    model = SuggestedTool
    fields = [ 'description' ]

  def clean_description(self):
    description = self.cleaned_data.get('description')
    length_required = 12

    if len(description.strip()) < length_required:
      raise forms.ValidationError(f'suggested tool description must be more than {length_required} letter!!!')
    return description

  def get_error_meesage(self):
    return self.errors['description']

