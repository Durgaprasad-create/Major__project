from django.shortcuts import render,redirect
from django.http import HttpResponseForbidden
from job_app.models import Job,Profile,JobApplication
from django.contrib.auth import login,authenticate,logout
from .forms import EmployerRegistrationForm, EmployeeRegistrationForm,LoginForm,JobForm,JobApplicationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm,Profile
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib import messages


def home(request):
    latest_jobs = Job.objects.order_by('-posted_on')[:3]
    return render(request, 'job_app/home.html', {'Jobs': latest_jobs})

def job_list(request):
    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location', '')

    Jobs = Job.objects.all().order_by('-posted_on')

    if keyword:
        Jobs = Jobs.filter(Q(JobRole__icontains=keyword) | Q(description__icontains=keyword))

    if location:
        Jobs = Jobs.filter(location__icontains=location)

    return render(request, 'job_app/joblist.html', {
        'Jobs': Jobs,
        'keyword': keyword,
        'location': location
    })


def job_category(request, category):
    # Convert URL-friendly slug to readable category
    category_name = category.replace('-', ' ').title()

    # Filter jobs from DB that match this category (case-insensitive)
    Jobs = Job.objects.filter(category__iexact=category_name).order_by('-posted_on')

    return render(request, 'job_app/joblist.html', {"category": category_name, "Jobs": Jobs})


def register(request):
    return render(request, "job_app/register.html")

#user registration

def employer_register(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            profile_picture = form.cleaned_data.get('profile_picture')
            Profile.objects.create(user=user, profile_picture=profile_picture,user_type='employer')
            login(request, user)  # Auto-login after registration
            return redirect('home')  # Redirect to homepage
    else:
        form = EmployerRegistrationForm()
    return render(request, 'job_app/employer_register.html', {'form': form})

def employee_register(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()  
            profile_picture = form.cleaned_data.get('profile_picture')
            Profile.objects.create(user=user, profile_picture=profile_picture,user_type='employee')
            login(request, user)
            return redirect('home')
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'job_app/employee_register.html', {'form': form})

#login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("home")  # Redirect to home after login
    else:
        form = LoginForm()
    return render(request, "job_app/login.html", {"form": form})

#logout
def logout_view(request):
    logout(request)
    return redirect("home")

#post_job
@login_required
def post_job(request):
    if request.user.user_type != 'employer':
        return redirect('home')
    
    if request.method =='POST':
        form = JobForm(request.POST)
        if form.is_valid():
            Job = form.save(commit=False)
            Job.posted_by = request.user
            Job.save()
            return redirect('job_list')
    else:
        form = JobForm()

    return render(request, 'job_app/post_job.html', {'form': form})
         

def profile(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profile.html', {'profile_form': profile_form})




@login_required
def dashboard(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    # Handle profile picture upload
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Profile picture updated successfully!')
        return redirect('dashboard')

    # Profile completeness
    filled_fields = sum(bool(getattr(profile, field)) for field in ['profile_picture'])
    total_fields = 1
    completeness_percentage = int((filled_fields / total_fields) * 100)

    # Common context
    context = {
        'user': user,  # Ensure 'user' is passed for template conditionals
        'profile': profile,
        'completeness_percentage': completeness_percentage,
    }

    if request.user.user_type == 'employee':
        applied_jobs = JobApplication.objects.filter(applicant=user).select_related('job')
        context['applied_jobs'] = applied_jobs
        context['job_count'] = applied_jobs.count()
    
    elif request.user.user_type == 'employer':
        posted_jobs = Job.objects.filter(posted_by=user)
        context['posted_jobs'] = posted_jobs
        context['job_count'] = posted_jobs.count()

    return render(request, 'job_app/dashboard.html', context)



@login_required
def edit_profile(request):
    user = request.user

    # handle profile-picture upload
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        profile = user.profile
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, "Profile picture updated.")
        return redirect('edit_profile')

    # handle name/email update
    if request.method == 'POST' and 'user_name' in request.POST:
        new_username = request.POST.get('user_name')
        new_email    = request.POST.get('email')
        if new_username and new_email:
            user.username = new_username
            user.email    = new_email
            user.save()
            messages.success(request, "Your name and email have been updated.")
        else:
            messages.error(request, "Both fields are required.")
        return redirect('edit_profile')

    return render(request, 'job_app/edit_profile.html')


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    has_applied = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()

    context = {
        'job': job,
        'has_applied': has_applied,
    }
    return render(request, 'job_app/job_detail.html', context)



@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter', '')

        JobApplication.objects.create(
            job=job,
            applicant=request.user,
            resume=resume,
            cover_letter=cover_letter
        )

        return redirect('job_detail', job_id=job.id)

    return render(request, 'job_app/apply_job.html', {'job': job})
   
def view_applicants(request, job_id):
    # Fetch the job that the employer posted
    job = get_object_or_404(Job, id=job_id)
    
    # Check if the logged-in user is the employer who posted the job
    if job.posted_by != request.user:
        return HttpResponseForbidden("You are not authorized to view applicants for this job.")
    
    # Fetch all applicants for the job
    applicants = JobApplication.objects.filter(job=job).select_related('applicant')

    context = {
        'job': job,
        'applicants': applicants
    }
    return render(request, 'job_app/view_applicants.html', context)



@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Ensure only the job poster can delete the job
    if request.user == job.posted_by:
        job.delete()
        messages.success(request, "Job deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this job.")

    return redirect('dashboard')
















