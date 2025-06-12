from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
import json

from .forms import (
    StudentSignupForm, EducatorSignupForm,
    StudentLoginForm, EducatorLoginForm
)
from .models import UserProfile

# -----------------------
# In-memory Data
# -----------------------
USERS = {}
QUIZZES = {
    "math101": {
        "title": "Basic Math Quiz",
        "questions": [
            {"id": 1, "question": "What is 2 + 2?", "options": ["3", "4", "5"], "answer": "4"},
            {"id": 2, "question": "What is 5 - 3?", "options": ["2", "3", "4"], "answer": "2"}
        ]
    }
}
LEADERBOARD = []
BADGES = {}
PROGRESS = {}

# -----------------------
# Utility Functions
# -----------------------
def assign_badge(username, score):
    if score >= 3:
        badge = "Expert"
    elif score >= 2:
        badge = "Intermediate"
    else:
        badge = "Beginner"
    BADGES[username] = badge
    return badge

# -----------------------
# API Views
# -----------------------
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({"success": True, "message": "User logged in!"})
                return JsonResponse({"success": False, "message": "Invalid credentials."})
            return JsonResponse({"success": False, "message": "Missing username or password."})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON."})
    return JsonResponse({"success": False, "message": "Invalid request method."})

@csrf_exempt
def get_badge(request):
    if request.user.is_authenticated:
        badge = BADGES.get(request.user.username, "No badge yet.")
        return JsonResponse({"username": request.user.username, "badge": badge})
    return JsonResponse({"success": False, "message": "Not authenticated."})

@csrf_exempt
def update_leaderboard(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            score = data.get('score')
            if score is None:
                return JsonResponse({"success": False, "message": "Missing score."})
            badge = assign_badge(request.user.username, score)
            existing = next((item for item in LEADERBOARD if item['username'] == request.user.username), None)
            if existing:
                existing['score'] = score
                existing['badge'] = badge
            else:
                LEADERBOARD.append({
                    "username": request.user.username,
                    "score": score,
                    "badge": badge
                })
            LEADERBOARD.sort(key=lambda x: x['score'], reverse=True)
            return JsonResponse({"success": True, "leaderboard": LEADERBOARD})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON."})
    return JsonResponse({"success": False, "message": "Invalid request."})

@csrf_exempt
def get_quiz(request):
    quiz_id = request.GET.get('quiz_id')
    quiz = QUIZZES.get(quiz_id)
    if quiz:
        return JsonResponse({"success": True, "quiz": quiz})
    return JsonResponse({"success": False, "message": "Quiz not found."})

@csrf_exempt
def submit_quiz(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            quiz_id = data.get('quiz_id')
            answers = data.get('answers')
            if not quiz_id or not answers:
                return JsonResponse({"success": False, "message": "Missing quiz_id or answers."})
            quiz = QUIZZES.get(quiz_id)
            if not quiz:
                return JsonResponse({"success": False, "message": "Quiz not found."})
            score = 0
            for question in quiz["questions"]:
                qid = str(question["id"])
                if answers.get(qid) == question["answer"]:
                    score += 1
            PROGRESS[request.user.username] = {
                "completed": PROGRESS.get(request.user.username, {}).get("completed", 0) + 1,
                "last_score": score
            }
            return JsonResponse({
                "success": True,
                "score": score,
                "total": len(quiz["questions"]),
                "badge": assign_badge(request.user.username, score)
            })
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON."})
    return JsonResponse({"success": False, "message": "Invalid request."})

@csrf_exempt
def assign_quiz(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            student = data.get('student')
            quiz_id = data.get('quiz_id')
            if student and quiz_id:
                assigned_quizzes = USERS.setdefault(student, {}).setdefault('quizzes', [])
                if quiz_id not in assigned_quizzes:
                    assigned_quizzes.append(quiz_id)
                return JsonResponse({
                    "success": True,
                    "message": f"Quiz {quiz_id} assigned to {student}."
                })
            return JsonResponse({"success": False, "message": "Missing student or quiz_id."})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON."})
    return JsonResponse({"success": False, "message": "Invalid request."})

@csrf_exempt
def get_progress(request):
    if request.user.is_authenticated:
        progress = PROGRESS.get(request.user.username, {"completed": 0})
        return JsonResponse({
            "username": request.user.username,
            "progress": progress
        })
    return JsonResponse({"success": False, "message": "Not authenticated."})

# -----------------------
# Page Views
# -----------------------
def home(request):
    return render(request, 'core_app/index.html')

def leaderboard(request):
    sorted_leaderboard = sorted(LEADERBOARD, key=lambda x: x['score'], reverse=True)
    return render(request, 'core_app/leaderboard.html', {'leaderboard': sorted_leaderboard})

def student_page(request):
    return render(request, 'core_app/student_page.html')

def educator_page(request):
    return render(request, 'core_app/educator_page.html')

def login_page(request):
    return render(request, 'core_app/login.html')

# -----------------------
# Authentication Views
# -----------------------
def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            profile = UserProfile.objects.get(user=user)
            if profile.user_type != 'student':
                messages.error(request, "Invalid user type for student login.")
                return redirect('student_login')
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('student_dashboard')
        messages.error(request, "Invalid username or password.")
    else:
        form = StudentLoginForm()
    return render(request, 'core_app/student_login.html', {'form': form})

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('student_login')
    else:
        form = StudentSignupForm()
    return render(request, 'core_app/student_signup.html', {'form': form})

@login_required
def student_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'student':
        logout(request)
        messages.error(request, "Access denied.")
        return redirect('student_login')
    return render(request, 'core_app/student_dashboard.html', {
        'user': request.user,
        'progress': PROGRESS.get(request.user.username, {})
    })

@login_required
def student_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def educator_login(request):
    if request.method == 'POST':
        form = EducatorLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                profile = user.userprofile
                if profile.user_type == 'educator':
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect('educator_dashboard')
                else:
                    messages.error(request, "This account is not registered as an educator.")
            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found. Please contact support.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = EducatorLoginForm()
    return render(request, 'core_app/educator_login.html', {'form': form})


def educator_signup(request):
    if request.method == 'POST':
        form = EducatorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('educator_login')
    else:
        form = EducatorSignupForm()
    return render(request, 'core_app/educator_signup.html', {'form': form})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
@login_required
def educator_dashboard(request):
    try:
        profile = request.user.userprofile
        if profile.user_type != 'educator':
            logout(request)
            return JsonResponse({
                "success": False,
                "message": "You don't have permission to access this page."
            }, status=403)
            
        # Send quizzes as JSON
        quizzes = [
            {
                "quiz_id": quiz_id,
                "title": quiz_data.get("title"),
                "num_questions": len(quiz_data.get("questions", []))
            }
            for quiz_id, quiz_data in QUIZZES.items()
        ]
        return JsonResponse({
            "success": True,
            "username": request.user.username,
            "quizzes": quizzes
        })
    except UserProfile.DoesNotExist:
        logout(request)
        return JsonResponse({
            "success": False,
            "message": "User profile not found. Please contact support."
        }, status=404)

    
@login_required
def educator_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

# -----------------------
# Custom LoginView
# -----------------------
class CustomLoginView(LoginView):
    template_name = 'core_app/login.html'

    def get_success_url(self):
        user = self.request.user
        try:
            if user.userprofile.user_type == 'student':
                return reverse_lazy('student_dashboard')
            elif user.userprofile.user_type == 'educator':
                return reverse_lazy('educator_dashboard')
        except AttributeError:
            pass
        return reverse_lazy('home')
