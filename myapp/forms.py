from django import forms
from .models import Application, Subject, Class, TeacherProfile, ClassAssignment,  Announcement


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'first_name','middle_name','last_name', 'email', 'contact_number', 'previous_school',
            'house_number', 'street_name', 'barangay',
            'city_municipality', 'province', 'country'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control'}),
            'street_name': forms.TextInput(attrs={'class': 'form-control'}),
            'barangay': forms.TextInput(attrs={'class': 'form-control'}),
            'city_municipality': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_first_name(self):
        return self.validate_not_empty(self.cleaned_data.get("first_name"), "First Name")
    
    def clean_middle_name(self):
        return self.validate_not_empty(self.cleaned_data.get("middle_name"), "Middle Name")
    
    def clean_last_name(self):
        return self.validate_not_empty(self.cleaned_data.get("last_name"), "Last_Name")

    def clean_previous_school(self):
        return self.validate_not_empty(self.cleaned_data.get("previous_school"), "Previous School")

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get("contact_number", "").strip()
        if not contact_number:
            raise forms.ValidationError("Contact number cannot be empty or contain only spaces.")
        if not contact_number.isdigit():
            raise forms.ValidationError("Contact number must contain only numbers.")
        return contact_number

    def clean_email(self):
        return self.validate_not_empty(self.cleaned_data.get("email"), "Email")

    def clean_house_number(self):
        return self.validate_not_empty(self.cleaned_data.get("house_number"), "House Number")

    def clean_street_name(self):
        return self.validate_not_empty(self.cleaned_data.get("street_name"), "Street Name")

    def clean_barangay(self):
        return self.validate_not_empty(self.cleaned_data.get("barangay"), "Barangay")

    def clean_city_municipality(self):
        return self.validate_not_empty(self.cleaned_data.get("city_municipality"), "City/Municipality")

    def clean_country(self):
        return self.validate_not_empty(self.cleaned_data.get("country"), "Country")

    @staticmethod
    def validate_not_empty(value, field_name):
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

class AddClassForm(forms.Form):
    subject_code = forms.CharField(max_length=10, label='Subject Code', required=True)
    subject_name = forms.CharField(max_length=100, label='Subject Description', required=True)
    prerequisite = forms.CharField(max_length=50, label='prerequisite', required=True, help_text='e.g. MWF 10:00-11:00')
    duration = forms.IntegerField(label='Duration (in hrs)', required=True)
    room = forms.CharField(max_length=10, label='Room', required=True)

class AddClassGroupForm(forms.Form):
    name = forms.CharField(max_length=100, label='Group Name', required=True)
    classes = forms.ModelMultipleChoiceField(
        queryset=Class.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'image']  