from django.db import models
from django.contrib.auth.models import User

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    first_name = models.CharField(max_length=255, default=" ")
    middle_name = models.CharField(max_length=255, default=" ")
    last_name = models.CharField(max_length=255, default=" ")
    email = models.EmailField(default="not_provided@example.com")
    contact_number = models.CharField(max_length=15, default="0000000000")
    previous_school = models.CharField(max_length=255, default="Unknown School")

    house_number = models.CharField(max_length=100, default=" ")
    street_name = models.CharField(max_length=255, default=" ")
    barangay = models.CharField(max_length=255, default=" ")
    city_municipality = models.CharField(max_length=255, default=" ")
    province = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, default="Philippines")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status of the application (Pending, Accepted, Rejected)"
    )

    applicant = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='applications')
    notes = models.TextField(blank=True, default="")

    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}) - {self.get_status_display()}"

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        ordering = ['application_date']


class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    )

    name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField(default="not_provided@example.com")
    message = models.TextField(default="No message provided.")
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class Subject(models.Model):
    subject_code = models.CharField(max_length=20, default="N/A")
    subject_name = models.CharField(max_length=100, default="Unnamed Subject")
    schedule = models.CharField(max_length=50, default="TBA")
    duration = models.IntegerField(default=60)  # fixed default type
    room = models.CharField(max_length=20, default="Room 1")

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Class(models.Model):
    subject_code = models.CharField(max_length=20, default="N/A")
    subject_name = models.CharField(max_length=100, default="Unnamed Class")
    schedule = models.CharField(max_length=100, default="TBA")
    duration = models.IntegerField(default=60)
    room = models.CharField(max_length=50, default="Room 1")
    teacher = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='teaching_classes')
    students = models.ManyToManyField(User, related_name='enrolled_classes', blank=True)

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default="No First Name")
    middle_name = models.CharField(max_length=100, blank=True, default="")
    address = models.TextField(default="Not Provided")

    def __str__(self):
        return self.user.username


class ClassAssignment(models.Model):
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='student_classes')

    def __str__(self):
        return f"{self.assigned_class} - {self.teacher}"


class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255, default="Untitled Course")
    grade = models.CharField(max_length=10, default="N/A")

    def __str__(self):
        return f"{self.student.username} - {self.course_name}: {self.grade}"


class Announcement(models.Model):
    title = models.CharField(max_length=200, default="Untitled Announcement")
    content = models.TextField(default="No content.")
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, default="Unnamed Student")
    email = models.EmailField(default="student@example.com")
    contact_number = models.CharField(max_length=15, default="0000000000")
    previous_school = models.CharField(max_length=255, default="Unknown School")
    address = models.TextField(default="No Address Provided")
    status = models.CharField(max_length=50, default='pending')
    generated_password = models.CharField(max_length=128, blank=True, null=True, default="samplepassword")
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
