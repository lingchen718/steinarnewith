import json
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ArtProjectForm
from .models import ArtProject, Entry, CurrentProject, CurrentEntry
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage

# Create your views here.

def index(request):
    """front page of with_art"""
    return render(request, 'with_art/index.html')


def artprojects(request):
    """show all the artprojects"""
    artprojects = ArtProject.objects.all()
    context = {'artprojects': artprojects}
    return render(request, 'with_art/artprojects.html', context)

def artproject(request, slug):
    artproject = get_object_or_404(ArtProject, slug=slug)
    entries = artproject.entries.order_by('-date_added')
    context = {'artproject': artproject, 'entries':entries}
    return render(request, 'with_art/artproject.html', context)

def currentproject(request, slug):    
    """Detail page for a CurrentProject."""    
    currentproject = get_object_or_404(CurrentProject, slug=slug)    
    return render(request, 'with_art/currentproject.html', {'currentproject': currentproject})

def home(request):
    return render(request, 'with_art/index.html')


def current_list(request):
    """The CURRENT page (alias for home, if you want a separate /current/ URL)."""
    current_projects = CurrentProject.objects.filter(is_published=True)
    return render(request, 'with_art/current.html', {'artprojects': current_projects})

def philo_view(request):
    return render(request, 'with_art/philo.html')
def contact_view(request):
    return render(request, 'with_art/contact.html')

def upload_artproject(request):
    if request.method == 'POST':
        form = ArtProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('artprojects')  # Replace with the view name you want to redirect to
    else:
        form = ArtProjectForm()

    return render(request, 'with_art/upload999899.html', {'form': form})



def contact_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            budget = request.POST.get('budget', '').strip()

            # 1. Validation
            if not all([name, email, subject, message]):
                return JsonResponse({'status': 'error', 'message': 'Please fill in all required fields.'}, status=400)

            # 2. Save to database (viewable in Admin)
            msg_obj = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                budget=budget or None
            )

            # 3. Send notification email to artist
            email_body = f"""New inquiry received from {name} ({email}):

Subject: {msg_obj.get_subject_display()}
Budget: {budget if budget else 'Not specified'}

Message:
{message}
"""
            send_mail(
                subject=f"New Website Inquiry: {msg_obj.get_subject_display()} from {name}",
                message=email_body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', 'studio@steinarnewith.no')],
                fail_silently=True,  # Keeps form working even if SMTP temporarily fails
            )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return render(request, 'with_art/contact.html')
