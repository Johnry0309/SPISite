# Standard Libraries
import random
import string
import os
import json

# Django Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.files.storage import default_storage, FileSystemStorage
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, Http404
from django.utils import timezone
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.utils.html import format_html

# Models
from .models import Application, ContactMessage, TeacherProfile, Grade, Class, Subject, Announcement, Student, ClassGroup 

# Forms
from .forms import ApplicationForm, ContactForm, SubjectForm, ClassForm, AssignClassTeacherForm, AssignClassStudentForm, AddClassForm, AnnouncementForm

# Django Auth Models
from django.contrib.auth.models import User




def announcement_page(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    return render(request, 'myapp/announcement_detail.html', {'announcement': announcement})

def manage_announcements(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_announcements')
    else:
        form = AnnouncementForm()

    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'manage_announcements.html', {
        'form': form,
        'announcements': announcements
    })

def announcement_detail(request, id):
    announcement = get_object_or_404(Announcement, id=id)
    return render(request, 'myapp/announcement_detail.html', {'announcement': announcement})

def public_announcement_detail(request, id):
    announcement = get_object_or_404(Announcement, id=id)
    return render(request, 'myapp/announcement_detail.html', {'announcement': announcement})

def delete_announcement(request, pk):
    # Ensure the user has the proper permissions (e.g., admin or staff).
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to delete this announcement.")
    
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Delete the announcement
    announcement.delete()
    
    # Redirect back to the manage announcements page
    return redirect('manage_announcements')




def add_class(request):
    if request.method == 'POST':
        form = AddClassForm(request.POST)
        if form.is_valid():
            # Create a new Class instance and save it to the database
            Class.objects.create(
                subject_code=form.cleaned_data['subject_code'],
                subject_name=form.cleaned_data['subject_name'],
                prerequisite=form.cleaned_data['prerequisite'],
                duration=form.cleaned_data['duration'],
                room=form.cleaned_data['room']
            )
            form = AddClassForm()  # Reset the form after successful submission
            success_message = "Class added successfully!"  # Success message
        else:
            success_message = None  # No success message if form is invalid
    else:
        form = AddClassForm()
        success_message = None

    # Fetch all classes to display
    classes = Class.objects.all()

    return render(request, 'myapp/manage_classes.html', {
        'form': form,
        'success_message': success_message,
        'classes': classes  # Pass the list of classes to the template
    })

def teacher_profile(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')  # Or redirect to some other page if not authenticated
    
    # Fetch the teacher profile associated with the logged-in user
    teacher_profile = TeacherProfile.objects.get(user=request.user)

    return render(request, 'myapp/teacher_profile.html', {'teacher_profile': teacher_profile})

def update_teacher_profile(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')  # Or redirect to some other page if not authenticated
    
    # Fetch the teacher profile associated with the logged-in user
    teacher_profile = TeacherProfile.objects.get(user=request.user)

    if request.method == 'POST':
        teacher_profile.first_name = request.POST.get('first_name')
        teacher_profile.middle_name = request.POST.get('middle_name')
        teacher_profile.address = request.POST.get('address')
        teacher_profile.save()
        return redirect('teacher_profile')  # Redirect to the teacher profile page after saving changes

    return redirect('teacher_profile')  # You can redirect or render a confirmation page if needed



# --- Basic Page Views ---

def home(request):
    # Get the latest 10 announcements
    announcements = Announcement.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'home.html', {'announcements': announcements})

def about(request):
    return render(request, 'myapp/about.html')

def mission(request):
    return render(request, 'myapp/mv.html')

def history(request):
    return render(request, 'myapp/hist.html')

def admissions(request):
    return render(request, 'admissions.html')

def requirements(request):
    return render(request, 'myapp/req.html')

def application_process(request):
    return render(request, 'myapp/appprocess.html')

def gallery(request):
    return render(request, 'myapp/gallery.html')

def academics(request):
    return render(request, 'myapp/academics.html')

def programs(request):
    return render(request, 'myapp/programs.html')

def faculty(request):
    return render(request, 'myapp/faculty.html')

def calendar(request):
    return render(request, 'myapp/acc_calendar.html')

def contact(request):
    return render(request, 'myapp/contact.html')

def quick_links(request):
    return render(request, 'myapp/quick_links.html')

def spiantipolo(request):
    return render(request, 'myapp/spiantipolo.html')

def spiqc(request):
    return render(request, 'myapp/spiqc.html')

def spicabanatuan(request):
    return render(request, 'myapp/cabanatuan.html')

def spiangeles(request):
    return render(request, 'myapp/angeles.html')

 #gallery options codes




def get_gallery_folders():
    gallery_folder_path = os.path.join(settings.MEDIA_ROOT,  'galleries')
    if not os.path.exists(gallery_folder_path):
        os.makedirs(gallery_folder_path)
    
    return [f for f in os.listdir(gallery_folder_path) if os.path.isdir(os.path.join(gallery_folder_path, f))]

def upload_folder(request):
    if request.method == 'POST' and 'images' in request.FILES:
        uploaded_images = request.FILES.getlist('images')  # Get all uploaded images
        gallery_name = request.POST.get('gallery_name')  # Get the selected gallery name
        gallery_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'images', 'galleries', gallery_name)
        
        if not os.path.exists(gallery_path):
            os.makedirs(gallery_path)

        fs = FileSystemStorage(location=gallery_path)

        for image in uploaded_images:
            unique_filename = get_random_string(8) + os.path.splitext(image.name)[1]
            fs.save(unique_filename, image)  # Save each image with a unique name

        messages.success(request, f"Images uploaded successfully to '{gallery_name}' gallery.")
        return redirect('upload_image')  # Redirect back after successful upload
    
    return render(request, 'upload_folder.html')



def upload_gallery_image(request):
    if request.method == 'POST' and request.FILES.get('gallery_image'):
        image = request.FILES['gallery_image']
        gallery_name = request.POST.get('gallery_name')  # Get the gallery name from the form
        gallery_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'images', 'galleries', gallery_name)
        
        if not os.path.exists(gallery_path):
            os.makedirs(gallery_path)
        
        fs = FileSystemStorage(location=gallery_path)
        unique_filename = get_random_string(8) + os.path.splitext(image.name)[1]
        fs.save(unique_filename, image)

        messages.success(request, f"Image uploaded successfully to '{gallery_name}' gallery.")
        return redirect('admin_home')  # Redirect back after successful upload

    return render(request, 'admin_base.html')

def gallery(request):
    galleries = {}
    
    # Path to the 'galleries' folder where images are stored
    gallery_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'images', 'galleries')

    if os.path.exists(gallery_path):  # Check if directory exists
        for folder in os.listdir(gallery_path):
            folder_path = os.path.join(gallery_path, folder)
            if os.path.isdir(folder_path):  # Ensure it's a folder
                images = [
                    f'images/galleries/{folder}/{img}' 
                    for img in os.listdir(folder_path) 
                    if img.endswith(('png', 'jpg', 'jpeg', 'gif'))
                ]
                
                if images:
                    galleries[folder] = images  # Store images by folder

    return render(request, 'myapp/gallery.html', {'galleries': galleries})

def custom_logout(request):
    user = request.user
    logout(request)  # Log out the user

    # Check if the user is an admin or a student
    if user.is_staff and user.is_superuser:  # Admin user
        messages.success(request, "Admin logged out successfully.")
        return redirect('admin_login')  # Redirect to the admin login page
    else:  # Regular student user
        messages.success(request, "Logged out successfully.")
        return redirect('login')  # Redirect to the student login page

# --- Apply Online View ---
def apply_online(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save() # Save the form
            messages.success(request, "Application submitted successfully!")
            return redirect('application_confirmation', application_id=application.id)
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ApplicationForm()

    return render(request, 'myapp/apply_online.html', {'form': form})

def application_confirmation(request, application_id):
    application = get_object_or_404(Application, pk=application_id) # get_object_or_404 if does not exist will display a 404 instead of displaying nothing
    return render(request, 'myapp/application_confirmation.html', {'application': application})

# --- Login Views ---

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Debugging: print the username and password entered
            print(f"Login attempt with username: {username}, password: {password}")

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if the user is active
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome, {username}!")  # Add success message on login
                    return redirect('student_dashboard')  # Ensure this matches the correct URL name
                else:
                    messages.error(request, 'Your account is deactivated.')
                    print("User account is deactivated.")
            else:
                messages.error(request, 'Invalid username or password.')
                print("Authentication failed.")
        else:
            messages.error(request, 'Invalid username or password.')
            print(f"Form errors: {form.errors}")  # Log the form errors for debugging

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required(login_url='/login/')
def teacher_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Ensure this redirects only if not logged in
    if not request.user.is_staff:
        return redirect('student_dashboard')  # Or a proper redirect if not a teacher
    return render(request, 'myapp/teacher_dashboard.html')

@login_required(login_url='/login/')
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_staff:
        return redirect('teacher_dashboard')  # Ensure this is working correctly
    return render(request, 'student_dashboard.html')

@login_required(login_url='/login/')
def teacher_profile(request):
    # Make sure the user is logged in and has a teacher profile
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')  # Or redirect to some other page if not authenticated
    
    # Fetch the teacher profile associated with the logged-in user
    teacher_profile = TeacherProfile.objects.get(user=request.user)
    
    return render(request, 'myapp/teacher_profile.html', {'teacher_profile': teacher_profile})


def custom_logout_view(request):
    logout(request)  # Logs out the user
    return redirect('login')  # Redirects to login page

# --- Admin Views ---
def is_admin(user):
    return user.is_staff and user.is_superuser # checks if the user is both of the condition

@login_required
@user_passes_test(is_admin) # checks user is an admin before accessing
def admin_dashboard(request):
    applications = Application.objects.all().order_by('-application_date')
    application_count = Application.objects.count()
    accepted_count = Application.objects.filter(status='accepted').count()
    rejected_count = Application.objects.filter(status='rejected').count()
    pending_count = Application.objects.filter(status='pending').count()

    context = {
        'applications': applications,
        'application_count': application_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'pending_count': pending_count,
    }
    return render(request, 'admin_dashboard.html', context)

def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                if is_admin(user):
                    messages.success(request, f"Admin {username} logged in successfully.") # message to the user
                    return redirect('admin_home')
                else:
                    logout(request)
                    messages.error(request, "You do not have admin privileges.")
                    return redirect('login')  # or redirect to some unauthorized page
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')

    else:
        form = AuthenticationForm() # if there is no data

    return render(request, 'admin_login.html', {'form': form}) # renders the form


def update_teacher_profile(request):
    user = request.user

    # Check if the profile exists, if not create a new one
    profile, created = TeacherProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.middle_name = request.POST.get('middle_name', '')
        user.address = request.POST.get('address', '')
        user.save()
        
        # Update teacher profile
        profile.middle_name = request.POST.get('middle_name', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        
        return redirect('teacher_dashboard')  # Redirect to teacher dashboard after update

    # Pass the profile data to the template to pre-fill form fields
    context = {
        'profile': profile
    }
    
    return render(request, 'teacher_dashboard.html', context)

def add_grade(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        grade_value = request.POST.get('grade')

        grade = Grade(student_id=student_id, subject_id=subject_id, grade_value=grade_value)
        grade.save()
        return redirect('teacher_dashboard')

    return render(request, 'teacher_dashboard.html')

@login_required(login_url='/admin/login/')  # Redirects logged-out users to login
@user_passes_test(is_admin, login_url='/admin/login/', redirect_field_name=None)
def upload_image(request):
    galleries_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'images', 'galleries')  # Correct path to static/images/galleries
    
    # Ensure that the folder exists
    if not os.path.exists(galleries_path):
        os.makedirs(galleries_path)

    # Get the list of galleries in the 'galleries' folder
    galleries = [f.name for f in os.scandir(galleries_path) if f.is_dir()]

    if request.method == 'POST':
        gallery_name = request.POST.get('gallery')  # Get the selected gallery from the form
        new_gallery_name = request.POST.get('new_gallery_name')  # Get the new gallery name from the form
        
        if 'image' not in request.FILES:
            messages.error(request, "No image selected.")
            return redirect('upload_image')

        uploaded_file = request.FILES['image']

        # If no gallery is selected and a new name is provided, create a custom folder with the new name
        if not gallery_name and new_gallery_name:
            gallery_name = new_gallery_name  # Use the new gallery name provided by the user
            custom_gallery_path = os.path.join(galleries_path, gallery_name)
            
            # Create the gallery folder if it doesn't exist
            if not os.path.exists(custom_gallery_path):
                os.makedirs(custom_gallery_path)
            gallery_path = custom_gallery_path
            messages.info(request, f"New gallery '{gallery_name}' created.")
        elif not gallery_name:
            # If no gallery name is provided, create a random gallery name
            gallery_name = get_random_string(8)  # Create a unique folder name
            custom_gallery_path = os.path.join(galleries_path, gallery_name)
            
            # Create the gallery folder if it doesn't exist
            if not os.path.exists(custom_gallery_path):
                os.makedirs(custom_gallery_path)
            gallery_path = custom_gallery_path
            messages.info(request, f"New gallery '{gallery_name}' created.")
        else:
            gallery_path = os.path.join(galleries_path, gallery_name)

            # Check if the directory exists, and if not, create it
            if not os.path.exists(gallery_path):
                os.makedirs(gallery_path)

        # Create a unique filename to prevent collisions
        unique_filename = get_random_string(8) + os.path.splitext(uploaded_file.name)[1]
        
        # Save the uploaded file to the correct location
        file_storage = FileSystemStorage(location=gallery_path)
        filename = file_storage.save(unique_filename, uploaded_file)

        # Show a success message
        messages.success(request, f"Image uploaded successfully to '{gallery_name}' gallery.")

        return redirect('upload_image')  # Redirect after successful upload

    return render(request, 'upload_image.html', {'galleries': galleries})

# Delete Image Functionality
@login_required(login_url='/admin/login/')
@user_passes_test(is_admin, login_url='/admin/login/', redirect_field_name=None)
def delete_image(request, gallery_name, image_name):
    gallery_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'images', 'galleries', gallery_name)
    image_path = os.path.join(gallery_path, image_name)

    # Check if the image exists and delete it
    if os.path.exists(image_path):
        os.remove(image_path)
        messages.success(request, f"Image '{image_name}' deleted successfully.")
    else:
        messages.error(request, f"Image '{image_name}' does not exist.")

    return redirect('gallery', gallery_name=gallery_name)


# Delete Gallery Functionality
@login_required(login_url='/admin/login/')
@user_passes_test(is_admin, login_url='/admin/login/', redirect_field_name=None)
def delete_gallery(request, gallery_name):
    gallery_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'images', 'galleries', gallery_name)

    # Check if the gallery exists and if it is empty
    if os.path.exists(gallery_path) and not os.listdir(gallery_path):
        os.rmdir(gallery_path)  # Remove the gallery folder
        messages.success(request, f"Gallery '{gallery_name}' deleted successfully.")
    else:
        messages.error(request, f"Gallery '{gallery_name}' is not empty or does not exist.")

    return redirect('gallery')





def delete_application(request, application_id):
    try:
        # Check if the application exists
        application = Application.objects.get(id=application_id)
        
        if request.method == 'POST':
            # Proceed with deletion
            application.delete()
            return redirect('admin_dashboard')  # Redirect to your application list or home page

    except Application.DoesNotExist:
        # Handle the case where the application does not exist
        raise Http404("Application not found.")
    
    # If not a POST request, render a confirmation page (optional)
    return render(request, 'admin_dashboard', {'application': application})



def generate_password(length=8):
    # Define a more secure set of characters (excluding punctuation)
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@login_required
@user_passes_test(is_admin)
def accept_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    # Check if the application is already accepted
    if application.status != 'accepted':
        application.status = 'accepted'
        application.save()

        password = generate_password()  # Generate a temporary password

        # Check if a student already exists for this application
        if hasattr(application, 'student'):
            # Student already exists, update their status
            student = application.student
            student.status = 'accepted'
            student.save()  # No need to update the password here

            # Set the password for the user
            user = student.user
            user.set_password(password)  # Hashes the password properly
            user.save()

            messages.success(request, f"{application.first_name}'s application has been accepted and student status updated.")
        else:
            # Create a new student if no student exists yet
            base_username = application.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Create the User and save the password (hashing is done by create_user)
            user = User.objects.create_user(
                username=username,
                email=application.email,
                password=password,  # Plain password, hashing is handled by `create_user()`
                first_name=application.first_name,
                last_name=application.last_name
            )
            user.is_active = True
            user.save()

            # Create the student object
            address = f"{application.house_number}, {application.street_name}, {application.barangay}, {application.city_municipality}, {application.province or ''}, {application.country}"
            student = Student.objects.create(
                application=application,
                user=user,  # Link the student to the user
                full_name=f"{application.first_name} {application.middle_name} {application.last_name}",
                email=application.email,
                contact_number=application.contact_number,
                previous_school=application.previous_school,
                address=address,
                status='accepted',
                generated_password=password,  # ✅ Save the generated password
            )
            messages.success(request, f"{application.first_name}'s application has been accepted. Student account created.")

    else:
        messages.warning(request, "This application has already been accepted.")

    return redirect('admin_dashboard')  # Redirect to the admin dashboard after accepting


def send_account_email(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    user = student.user
    application = student.application

    # Sync email from Application to Student and User
    if application.email and application.email != student.email:
        student.email = application.email
        user.email = application.email
        student.save()
        user.save()

    # Ensure the password is stored in plain text for email
    password = student.generated_password  # Ensure this is the plain text password
    if not password:
        messages.error(request, "Password not found for this student.")
        return redirect('admin_dashboard')

    # Debugging: Print the password to the terminal for troubleshooting
    print(f"Generated password for {student.full_name} ({user.username}): {password}")

    subject = "🎓 You're Accepted! Your Student Account is Ready"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [student.email]
    login_url = 'https://spi.com/login/'  # Replace with actual URL

    text_content = f"""
    Dear {application.first_name},

    Congratulations! Your application has been accepted.
    Student ID: {user.username}
    Temporary Password: {password}

    Please log in at: {login_url}

    Don't forget to visit the registrar's office to complete your enrollment.
    """

    html_content = f"""
    <p>Dear <strong>{application.first_name}</strong>,</p>
    <p>🎉 Congratulations! Your application has been <strong>accepted</strong>.</p>
    <p>Your temporary student account has been created:</p>
    <ul>
        <li><strong>Student ID (Username):</strong> {user.username}</li>
        <li><strong>Temporary Password:</strong> {password}</li>
    </ul>

    <p>👉 <a href="{login_url}" style="background-color: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Log in to your Student Portal</a></p>
    """

    send_mail(subject, text_content, from_email, to_email, html_message=html_content)
    messages.success(request, f"Login credentials sent to {student.full_name}.")
    student.email_sent = True
    student.save()

    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def reject_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)  # Get the application by ID

    if application.status != 'rejected':  # Only proceed if the application is not already rejected
        application.status = 'rejected'
        application.save()

        # Check if a student exists for this application
        if hasattr(application, 'student'):
            # Student already exists, update their status to 'rejected'
            student = application.student
            student.status = 'rejected'
            student.save()

            # Optionally, deactivate the student account or take any other necessary actions
            student.user.is_active = False  # Deactivate the student account
            student.user.save()

            messages.success(request, f"Application for {application.first_name} {application.last_name} has been rejected.")
        else:
            messages.success(request, f"Application for {application.first_name} {application.last_name} has been rejected, but no student was created yet.")

    else:
        messages.warning(request, "This application has already been rejected.")

    return redirect('admin_dashboard')  # Redirect to the admin dashboard after rejecting



@login_required
@user_passes_test(is_admin)
def admin_home(request):
    # Application Counts
    application_count = Application.objects.count()
    accepted_count = Application.objects.filter(status='accepted').count()
    rejected_count = Application.objects.filter(status='rejected').count()
    pending_count = Application.objects.filter(status='pending').count()
    message_count = ContactMessage.objects.count()

    # Recent Contact Messages
    recent_messages = ContactMessage.objects.order_by('-timestamp')[:5]  # Get the 5 most recent messages

    context = {
        'application_count': application_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'pending_count': pending_count,
        'recent_messages': recent_messages,
        'message_count': message_count,  # Add contact messages to the context
    }
    return render(request, 'admin_home.html', context)

def application_confirmation(request, application_id):
    application = Application.objects.get(pk=application_id)

    context = {'application': application}
    return render(request, 'myapp/application_confirmation.html', context)



def edit_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    student = application.student if application.student else None
    user = student.user if student else None

    generated_password = student.generated_password if student else None
    user_id = user.id if user else None

    if request.method == 'POST':
        # Update Application fields
        application.first_name = request.POST.get('first_name')
        application.middle_name = request.POST.get('middle_name')
        application.last_name = request.POST.get('last_name')
        application.email = request.POST.get('email')
        application.contact_number = request.POST.get('contact_number')
        application.previous_school = request.POST.get('previous_school')
        application.house_number = request.POST.get('house_number')
        application.street_name = request.POST.get('street_name')
        application.barangay = request.POST.get('barangay')
        application.city_municipality = request.POST.get('city_municipality')
        application.province = request.POST.get('province')
        application.country = request.POST.get('country')
        application.status = request.POST.get('status')
        application.save()

        # Update user and student fields
        if student and user:
            user.username = request.POST.get('username')
            user.email = application.email
            user.save()

            student.email = application.email  # Sync student email

            new_password = request.POST.get('password')
            if new_password:
                user.set_password(new_password)
                user.save()
                student.generated_password = new_password

            student.save()  # Save once after all updates

        messages.success(request, "Application updated successfully.")
        return redirect('admin_dashboard')

    return render(request, 'myapp/edit_application.html', {
        'application': application,
        'generated_password': generated_password,
        'user_id': user_id
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message to the database
            contact_message = ContactMessage(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            contact_message.save()

            # Optionally, send an email to the admin

            # Redirect to a success page or back to the contact form
            return redirect('contact_success')
    else:
        form = ContactForm()
    return render(request, 'myapp/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'myapp/contact_success.html')  # Create this template

def contact_messages(request):
    """Displays a list of contact form messages."""
    # Application Counts (same as in admin_home)
    application_count = Application.objects.count()
    accepted_count = Application.objects.filter(status='accepted').count()
    rejected_count = Application.objects.filter(status='rejected').count()
    pending_count = Application.objects.filter(status='pending').count()

    messages = ContactMessage.objects.order_by('-timestamp')  # Order by newest first

    # Fetch total message count
    message_count = ContactMessage.objects.count()

    context = {
        'messages': messages,
        'application_count': application_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'pending_count': pending_count,
        'message_count': message_count,  # Add message count to the context
    }
    return render(request, 'contact_messages.html', context)
def resolve_message(request, message_id):
    """Marks a contact message as resolved."""
    message = get_object_or_404(ContactMessage, pk=message_id)
    message.status = 'resolved' #Set the status resolve or delete in table
    message.save()
    return redirect('contact_messages')  # Redirect back to the messages list

def delete_message(request, message_id):
    """Deletes a contact message."""
    message = get_object_or_404(ContactMessage, pk=message_id)
    message.delete()
    return redirect('contact_messages')  # Redirect back to the messages list


# admin class management


def manage_classes(request):
    classes = Class.objects.all()
    class_groups = ClassGroup.objects.prefetch_related('classes').all()
    teachers = User.objects.filter(is_staff=True, is_superuser=False)
    students = User.objects.filter(is_staff=False)

    if request.method == 'POST':
        if 'add_class' in request.POST:
            subject_code = request.POST.get('subject_code')
            subject_name = request.POST.get('subject_name')
            prerequisite = request.POST.get('prerequisite')
            duration = request.POST.get('duration')
            room = request.POST.get('room')

            if all([subject_code, subject_name, prerequisite, duration, room]):
                Class.objects.create(
                    subject_code=subject_code,
                    subject_name=subject_name,
                    prerequisite=prerequisite,
                    duration=duration,
                    room=room
                )
                messages.success(request, 'Class added successfully.')
            else:
                messages.error(request, 'Please fill in all fields.')
            return redirect('manage_classes')

        elif 'assign_teacher' in request.POST:
            class_id = request.POST.get('class_id')
            teacher_id = request.POST.get('teacher_id')

            try:
                class_obj = Class.objects.get(id=class_id)
                teacher = User.objects.get(id=teacher_id)
                class_obj.teacher = teacher
                class_obj.save()
                messages.success(request, 'Class assigned to teacher.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
            return redirect('manage_classes')

        elif 'assign_student' in request.POST:
            class_id = request.POST.get('class_id')
            student_id = request.POST.get('student_id')

            try:
                class_obj = Class.objects.get(id=class_id)
                student = User.objects.get(id=student_id)
                class_obj.students.add(student)
                messages.success(request, 'Class assigned to student.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
            return redirect('manage_classes')

        elif 'add_group' in request.POST:
            group_name = request.POST.get('group_name')
            class_ids_json = request.POST.get('group_classes_json')
            strand = request.POST.get('strand')
            semester = request.POST.get('semester')
            level = request.POST.get('level')

            try:
                class_ids = json.loads(class_ids_json)
            except (TypeError, json.JSONDecodeError):
                class_ids = []

            if group_name and class_ids and strand and semester and level:
                try:
                    group = ClassGroup.objects.create(
                        name=group_name,
                        strand=strand,
                        semester=semester,
                        level=level
                    )
                    group.classes.set(Class.objects.filter(id__in=class_ids))
                    messages.success(request, 'Class group created successfully.')
                except Exception as e:
                    messages.error(request, f'Error: {e}')
            else:
                messages.error(request, 'Please fill in all group details.')
            return redirect('manage_classes')

        elif 'assign_group_to_student' in request.POST:
            student_id = request.POST.get('student_id')
            group_id = request.POST.get('group_id')

            try:
                student = User.objects.get(id=student_id)
                group = ClassGroup.objects.get(id=group_id)
                for class_obj in group.classes.all():
                    class_obj.students.add(student)
                messages.success(request, f'{group.name} assigned to student.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
            return redirect('manage_classes')

    return render(request, 'myapp/manage_classes.html', {
        'classes': classes,
        'class_groups': class_groups,
        'teachers': teachers,
        'students': students,
    })

def delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    class_obj.delete()
    messages.success(request, 'Class deleted successfully.')
    return redirect('manage_classes')

def add_delete_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        admin_type = request.POST.get('admin_type')

        if username and password and admin_type:
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists. Please choose a different one.')
            else:
                try:
                    user = User.objects.create_user(username=username, password=password)
                    # Assigning roles
                    if admin_type == 'teacher':
                        user.is_staff = True  # Only teachers should be 'staff'
                        user.save()
                        messages.success(request, f'{username} has been added as a teacher.')
                    else:
                        # Handle other types (e.g., students), no 'is_staff' for students
                        user.save()
                        messages.success(request, f'{username} has been added as a student.')
                except Exception as e:
                    messages.error(request, f'Error creating admin: {e}')
        else:
            messages.error(request, 'Please fill in all fields.')

    elif request.method == 'GET' and 'delete' in request.GET:
        user_id = request.GET['delete']
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, f'{user.username} has been deleted.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.') 

def assign_class_teacher(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        teacher_id = request.POST.get('teacher_id')

        try:
            subject_class = Class.objects.get(id=class_id)
            teacher = User.objects.get(id=teacher_id)

            subject_class.teacher = teacher
            subject_class.save()

            messages.success(request, f"Assigned {teacher.username} to {subject_class.class_name}")
        except Exception as e:
            messages.error(request, f"Error assigning teacher: {e}")

    return redirect('manage_classes')  # make sure this matches your tab view name

def assign_class_student(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        student_id = request.POST.get('student_id')

        try:
            subject_class = Class.objects.get(id=class_id)
            student = User.objects.get(id=student_id)

            # Add the student to the class (Many-to-Many relationship)
            subject_class.students.add(student)
            subject_class.save()

            messages.success(request, f"Assigned {student.username} to {subject_class.subject_name}")
        except Exception as e:
            messages.error(request, f"Error assigning student: {e}")

    return redirect('manage_classes')  # Redirecting to manage_classes view


def add_delete_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        admin_type = request.POST.get('admin_type')

        if username and password and admin_type:
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists. Please choose a different one.')
            else:
                try:
                    user = User.objects.create_user(username=username, password=password)
                    # Assigning roles
                    if admin_type == 'teacher':
                        user.is_staff = True  # Only teachers should be 'staff'
                        user.save()
                        messages.success(request, f'{username} has been added as a teacher.')
                    else:
                        # Handle other types (e.g., students), no 'is_staff' for students
                        user.save()
                        messages.success(request, f'{username} has been added as a student.')
                except Exception as e:
                    messages.error(request, f'Error creating admin: {e}')
        else:
            messages.error(request, 'Please fill in all fields.')

    elif request.method == 'GET' and 'delete' in request.GET:
        user_id = request.GET['delete']
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, f'{user.username} has been deleted.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    # Fetch only staff (teachers)
    users = User.objects.filter(is_staff=True)

    return render(request, 'add_delete_admin.html', {'users': users})

def class_detail(request, class_id):
    # Fetch the class and related teacher
    subject_class = get_object_or_404(Class, id=class_id)
    teacher = subject_class.teacher  # This assumes 'teacher' is a ForeignKey in the Class model
    students = subject_class.students.all()  # Assuming 'students' is a Many-to-Many relationship

    return render(request, 'myapp/class_detail.html', {
        'class': subject_class,
        'teacher': teacher,
        'students': students,
    })