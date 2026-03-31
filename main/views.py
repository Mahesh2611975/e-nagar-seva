from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import TruncMonth
from django.db.models.functions import TruncMonth
import json
import math

from .models import Complaint, Officer, Update, Profile, Notification


# -------------------------------
# 📏 Distance Function
# -------------------------------
def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


# -------------------------------
# 🏠 HOME
# -------------------------------
def home(request):
    return render(request, 'home.html')


# -------------------------------
# 📌 Department Mapping
# -------------------------------
def get_department(category):
    mapping = {
        'road': 'Road Department',
        'water': 'Water Department',
        'garbage': 'Sanitation',
        'electricity': 'Electrical Department'
    }
    return mapping.get(category, 'General')


# -------------------------------
# 🤖 AI CATEGORY DETECTION
# -------------------------------
def detect_category(text):
    text = text.lower()

    if any(w in text for w in ["road", "pothole", "street"]):
        return "road"
    elif any(w in text for w in ["water", "leak", "pipe"]):
        return "water"
    elif any(w in text for w in ["electric", "light", "power"]):
        return "electricity"
    elif any(w in text for w in ["garbage", "waste", "dust"]):
        return "garbage"

    return "other"


# -------------------------------
# 🔐 AUTH
# -------------------------------
def citizen_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            profile = Profile.objects.get(user=user)

            if profile.role == 'citizen':
                login(request, user)
                return redirect('citizen_dashboard')
    
    return render(request, 'citizen_login.html')


def officer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                profile = Profile.objects.get(user=user)

                if profile.role == 'officer':
                    login(request, user)
                    return redirect('staff_dashboard')
                else:
                    return render(request, 'officer_login.html', {
                        'error': 'You are not an officer'
                    })

            except Profile.DoesNotExist:
                return render(request, 'officer_login.html', {
                    'error': 'Profile not found'
                })

        else:
            return render(request, 'officer_login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'officer_login.html')


def custom_logout(request):
    logout(request)
    return redirect('home')


def citizen_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')

        if User.objects.filter(username=username).exists():
            return render(request, 'citizen_signup.html', {'error': 'Username exists'})

        user = User.objects.create_user(username=username, password=password)

        profile = Profile.objects.get(user=user)
        profile.role = 'citizen'
        profile.save()

        return redirect('citizen_login')

    return render(request, 'citizen_signup.html')


from .models import Profile
def officer_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # ✅ CHECK EMPTY
        if not username or not password:
            return render(request, 'officer_signup.html', {
                'error': 'All fields are required'
            })

        # ✅ CHECK DUPLICATE USERNAME
        if User.objects.filter(username=username).exists():
            return render(request, 'officer_signup.html', {
                'error': 'Username already exists'
            })

        # ✅ CREATE USER
        user = User.objects.create_user(username=username, password=password)

        # ✅ CREATE PROFILE
        Profile.objects.create(user=user, role='officer')

        return redirect('officer_login')

    return render(request, 'officer_signup.html')


# -------------------------------
# 🔁 DASHBOARD REDIRECT
# -------------------------------
@login_required
def dashboard_redirect(request):
    user = request.user

    if user.is_staff or user.profile.role == 'officer':
        return redirect('staff_dashboard')

    return redirect('citizen_dashboard')


# -------------------------------
# 👤 CITIZEN DASHBOARD
# -------------------------------
@login_required


@login_required
def citizen_dashboard(request):
    complaints = Complaint.objects.filter(user=request.user)

    total = complaints.count()
    pending = complaints.filter(status='pending').count()
    completed = complaints.filter(status='resolved').count()

    # 📊 CATEGORY DATA
    category_data = complaints.values('category').annotate(count=Count('id'))

    # 📊 STATUS DATA
    status_data = complaints.values('status').annotate(count=Count('id'))

    # 📊 MONTHLY DATA
    monthly_data = complaints.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id'))

    # Convert to JSON
    category_data = json.dumps(list(category_data))
    status_data = json.dumps(list(status_data))
    monthly_data = json.dumps([
        {"month": str(item["month"].strftime("%b")), "count": item["count"]}
        for item in monthly_data if item["month"]
    ])

    return render(request, 'citizen/dashboard.html', {
        'complaints': complaints,
        'total': total,
        'pending': pending,
        'completed': completed,
        'category_data': category_data,
        'status_data': status_data,
        'monthly_data': monthly_data
    })


# -------------------------------
# 👮 + 🛠 STAFF DASHBOARD
# -------------------------------
@login_required


@login_required
def staff_dashboard(request):
    complaints = Complaint.objects.all()

    # 🔥 FILTER LOGIC
    status = request.GET.get('status')

    if status == "pending":
        complaints = complaints.filter(status='pending')

    elif status == "in_progress":
        complaints = complaints.filter(status='in_progress')

    elif status == "resolved":
        complaints = complaints.filter(status='resolved')

    # 🔢 COUNTS (ALWAYS FROM ALL DATA)
    total = Complaint.objects.count()
    pending_count = Complaint.objects.filter(status='pending').count()
    completed_count = Complaint.objects.filter(status='resolved').count()

    return render(request, 'office/dashboard.html', {
        'complaints': complaints,
        'total': total,
        'pending_count': pending_count,
        'completed_count': completed_count
    })
# 📸 ADD COMPLAINT
# -------------------------------
@login_required
def add_complaint(request):
    if request.method == 'POST':

        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        latitude = float(request.POST.get('latitude') or 0)
        longitude = float(request.POST.get('longitude') or 0)
        address = request.POST.get('address', '')

        category = detect_category(description)
        dept = get_department(category)

        # Assign officer based on department
        officer = Officer.objects.filter(department=dept).first()
        assigned = officer.user if officer else None

        Complaint.objects.create(
            user=request.user,
            image=image,
            category=category,
            description=description,
            latitude=latitude,
            longitude=longitude,
            status="pending",
            assigned_officer=assigned,
            address=address
        )

        return redirect('dashboard')

    return render(request, 'citizen/complaint.html')


# -------------------------------
# 🔄 UPDATE STATUS
# -------------------------------
@login_required


def update_status(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.method == 'POST':
        status = request.POST.get('status')
        remark = request.POST.get('remark')

        # ✅ update status + remark
        complaint.status = status
        complaint.remark = remark

        # 📸 SAVE PROGRESS IMAGE (optional)
        if 'progress_image' in request.FILES:
            complaint.progress_image = request.FILES['progress_image']

        # 📸 SAVE COMPLETED IMAGE (IMPORTANT)
        if 'completed_image' in request.FILES:
            complaint.completed_image = request.FILES['completed_image']

        # ✅ SAVE FIRST (VERY IMPORTANT)
        complaint.save()

        # 🔔 CREATE NOTIFICATION AFTER SAVE
        if status == "resolved":
            Notification.objects.create(
                user=complaint.user,
                message="✅ Your complaint is now resolved",
                image=complaint.completed_image  # 🔥 THIS WILL WORK NOW
            )

        elif status == "in_progress":
            Notification.objects.create(
                user=complaint.user,
                message="🔧 Your complaint is now in progress"
            )

    return redirect('staff_dashboard')


# -------------------------------
# 🔔 NOTIFICATIONS
# -------------------------------
@login_required
def notifications(request):
    data = Notification.objects.filter(user=request.user).order_by('-id')
    complaints = Complaint.objects.filter(user=request.user)

    return render(request, 'citizen/notifications.html', {
        'data': data,
        'complaints': complaints
    })

