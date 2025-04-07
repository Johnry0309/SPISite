from django import forms
from .models import Application, Subject, Class, TeacherProfile, ClassAssignment

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'address', 'email', 'contact_number', 'previous_school']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        return self.validate_not_empty(self.cleaned_data.get("name"), "Name")

    def clean_address(self):
        return self.validate_not_empty(self.cleaned_data.get("address"), "Address")

    def clean_previous_school(self):
        return self.validate_not_empty(self.cleaned_data.get("previous_school"), "Previous school")

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get("contact_number", "").strip()
        if not contact_number:
            raise forms.ValidationError("Contact number cannot be empty or contain only spaces.")
        if not contact_number.isdigit():
            raise forms.ValidationError("Contact number must contain only numbers.")
        return contact_number

    @staticmethod
    def validate_not_empty(value, field_name):
        """Helper function to check if a field is empty or contains only spaces."""
        if not value or not value.strip():
            raise forms.ValidationError(f"{field_name} cannot be empty or contain only spaces.")
        return value.strip()


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email', 'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 4, 'class': 'form-control'})
    )

    def clean_name(self):
        return self.validate_not_empty(self.cleaned_data.get("name"), "Name")

    def clean_message(self):
        return self.validate_not_empty(self.cleaned_data.get("message"), "Message")

    @staticmethod
    def validate_not_empty(value, field_name):
        """Helper function to check if a field is empty or contains only spaces."""
        if not value or not value.strip():
            raise forms.ValidationError(f"{field_name} cannot be empty or contain only spaces.")
        return value.strip()

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = '__all__'

class AssignClassTeacherForm(forms.ModelForm):
    class Meta:
        model = ClassAssignment
        fields = ['assigned_class', 'teacher']

class AssignClassStudentForm(forms.ModelForm):
    class Meta:
        model = ClassAssignment
        fields = ['assigned_class', 'students']
        widgets = {
            'students': forms.CheckboxSelectMultiple
        }

from django import forms

class AddClassForm(forms.Form):
    subject_code = forms.CharField(max_length=10, label='Subject Code', required=True)
    subject_name = forms.CharField(max_length=100, label='Subject Description', required=True)
    schedule = forms.CharField(max_length=50, label='Schedule', required=True, help_text='e.g. MWF 10:00-11:00')
    duration = forms.IntegerField(label='Duration (in hrs)', required=True)
    room = forms.CharField(max_length=10, label='Room', required=True)