from django.db import models
from django.contrib.auth.models import User

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    STRAND_CHOICES = [
        ('ABM', 'ABM'),
        ('GAS', 'GAS'),
        ('HUMMS', 'HUMMS'),
        ('HRM', 'HRM'),
        ('TM', 'TM'),
        ('ICT', 'ICT'),
    ]

    LEVEL_CHOICES = [
        ('HS11', 'High School Grade 11'),
        ('HS12', 'High School Grade 12'),
        ('COL', 'College'),
    ]

    first_name = models.CharField(max_length=255, default=" ")
    middle_name = models.CharField(max_length=255, default=" ")
    last_name = models.CharField(max_length=255, default=" ")
    suffix = models.CharField(max_length=255, default=" ")
    email = models.EmailField(default="")
    contact_number = models.CharField(max_length=15, default="")
    previous_school = models.CharField(max_length=255, default="")

    house_number = models.CharField(max_length=100, default=" ")
    street_name = models.CharField(max_length=255, default=" ")
    barangay = models.CharField(max_length=255, default=" ")
    city_municipality = models.CharField(max_length=255, default=" ")
    province = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, default="Philippines")
    guardian_name= models.CharField(max_length=255, default=" ")
  

    strand = models.CharField(
        max_length=10,
        choices=STRAND_CHOICES,
        default='GAS',
        help_text="Strand for which the student is applying"
    )

    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        default='HS11',
        help_text="Level of the student (HS11, HS12, COL)"
    )

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
    prerequisite = models.CharField(max_length=50, default="none")
    duration = models.IntegerField(default=60)  # fixed default type
    room = models.CharField(max_length=20, default="Room 1")

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Class(models.Model):
    subject_code = models.CharField(max_length=20, default="ex: SHSCO 01")
    subject_name = models.CharField(max_length=100, default="ex: Oral Communication")
    prerequisite = models.CharField(max_length=100, default="none")
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
    last_name = models.CharField(max_length=100, blank=True, default="")
    specialization = models.CharField(max_length=100, blank=True, default="")

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
    subject = models.ForeignKey(Class, on_delete=models.CASCADE)
    prelim = models.FloatField(null=True, blank=True)
    midterm = models.FloatField(null=True, blank=True)
    prefinals = models.FloatField(null=True, blank=True)
    finals = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject.subject_name}: " \
               f"Prelim {self.prelim}, Midterm {self.midterm}, " \
               f"Prefinals {self.prefinals}, Finals {self.finals}"


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
    strand = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_enrolled = models.BooleanField(default=False)

    # Checklist booleans
    psa_birth_certificate = models.BooleanField(default=False)
    psa_marriage_certificate = models.BooleanField(default=False)
    form_137 = models.BooleanField(default=False)
    form_138 = models.BooleanField(default=False)
    certificate_of_good_moral = models.BooleanField(default=False)
    id_pictures = models.BooleanField(default=False)
    long_envelopes = models.BooleanField(default=False)
    registration_form = models.BooleanField(default=False)
    cashier_payment = models.BooleanField(default=False)

    # Document uploads
    psa_birth_certificate_file = models.FileField(upload_to='documents/psa_birth/', null=True, blank=True)
    psa_marriage_certificate_file = models.FileField(upload_to='documents/psa_marriage/', null=True, blank=True)
    form_137_file = models.FileField(upload_to='documents/form_138/', null=True, blank=True)
    form_138_file = models.FileField(upload_to='documents/form_138/', null=True, blank=True)
    certificate_of_good_moral_file = models.FileField(upload_to='documents/good_moral/', null=True, blank=True)
    id_pictures_file = models.FileField(upload_to='documents/id_pictures/', null=True, blank=True)
    long_envelopes_file = models.FileField(upload_to='documents/long_envelopes/', null=True, blank=True)
    registration_form_file = models.FileField(upload_to='documents/registration_form/', null=True, blank=True)
    cashier_payment_file = models.FileField(upload_to='documents/payment/', null=True, blank=True)

    def __str__(self):
        return self.full_name



class ClassGroup(models.Model):
    STRAND_CHOICES = [
        ('ABM', 'ABM'),
        ('GAS', 'GAS'),
        ('HUMMS', 'HUMMS'),
        ('HRM', 'HRM'),
        ('TM', 'Tourism Management'),
        ('ICT', 'Information and Communication Technology'),
    ]

    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
    ]

    LEVEL_CHOICES = [
        ('HS11', 'Senior High School Grade 11'),
        ('HS12', 'Senior High School Grade 12'),
        ('COL', 'College'),
    ]

    name = models.CharField(max_length=100, unique=True)
    classes = models.ManyToManyField('Class', related_name='groups')
    strand = models.CharField(max_length=10, choices=STRAND_CHOICES, default='GAS')
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, default='1')
    level = models.CharField(max_length=4, choices=LEVEL_CHOICES, default='HS11')
    students = models.ManyToManyField('Student', related_name='class_groups', blank=True)

    def __str__(self):
        return f"{self.name} - {self.get_strand_display()} - {self.get_level_display()} - {self.get_semester_display()}"