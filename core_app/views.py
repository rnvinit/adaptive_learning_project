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

# -----------------------------
# In-Memory Data Storage
# -----------------------------
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

# -----------------------------
# Utility Functions
# -----------------------------
def assign_badge(username, score):
    if score >= 3:
        badge = "Expert"
    elif score >= 2:
        badge = "Intermediate"
    else:
        badge = "Beginner"
    BADGES[username] = badge
    return badge

# -----------------------------
# HTML VIEWS (Student / Educator)
# -----------------------------
def home(request):
    return render(request, 'core_app/index.html')

def login_page(request):
    return render(request, 'core_app/login.html')

def student_page(request):
    return render(request, 'core_app/student_page.html')

def educator_page(request):
    return render(request, 'core_app/educator_page.html')

def leaderboard(request):
    sorted_board = sorted(LEADERBOARD, key=lambda x: x['score'], reverse=True)
    return render(request, 'core_app/leaderboard.html', {'leaderboard': sorted_board})

def terms_view(request):
    return render(request, 'core_app/terms.html')

def privacy_view(request):
    return render(request, 'core_app/privacy.html')

def cookies_view(request):
    return render(request, 'core_app/cookies.html')


# -----------------------------
# Student Authentication Views
# -----------------------------
def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                if user.userprofile.user_type != 'student':
                    messages.error(request, "Access denied for non-students.")
                    return redirect('student_login')
            except UserProfile.DoesNotExist:
                messages.error(request, "Profile not found.")
                return redirect('student_login')
            login(request, user)
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = StudentLoginForm()
    return render(request, 'core_app/student_login.html', {'form': form})

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('student_login')
    else:
        form = StudentSignupForm()
    return render(request, 'core_app/student_signup.html', {'form': form})

@login_required
def student_dashboard(request):
    try:
        if request.user.userprofile.user_type != 'student':
            logout(request)
            return redirect('student_login')
    except UserProfile.DoesNotExist:
        logout(request)
        return redirect('student_login')

    return render(request, 'core_app/student_dashboard.html', {
        'user': request.user,
        'progress': PROGRESS.get(request.user.username, {})
    })

@login_required
def student_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

# -----------------------------
# Educator Authentication Views
# -----------------------------
def educator_login(request):
    if request.method == 'POST':
        form = EducatorLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                if user.userprofile.user_type != 'educator':
                    messages.error(request, "Not registered as educator.")
                    return redirect('educator_login')
            except UserProfile.DoesNotExist:
                messages.error(request, "Profile error.")
                return redirect('educator_login')
            login(request, user)
            return redirect('educator_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = EducatorLoginForm()
    return render(request, 'core_app/educator_login.html', {'form': form})

def educator_signup(request):
    if request.method == 'POST':
        form = EducatorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # Don't create UserProfile again here
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('educator_login')
    else:
        form = EducatorSignupForm()
    return render(request, 'core_app/educator_signup.html', {'form': form})


@login_required
def educator_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

@csrf_exempt
@login_required
def educator_dashboard(request):
    try:
        if request.user.userprofile.user_type != 'educator':
            logout(request)
            return redirect('educator_login')
    except UserProfile.DoesNotExist:
        logout(request)
        return redirect('educator_login')

    # Sample static in-memory content (replace with dynamic data later)
    courses = [
        {"name": "Math 101", "students": 25, "status": "Active"},
        {"name": "Science Basics", "students": 30, "status": "Active"},
    ]

    quizzes = {
        "math101": {
            "title": "Basic Math Quiz",
            "questions_count": len(QUIZZES["math101"]["questions"])
        }
    }

    recent_submissions = [
        {"quiz": "Basic Math Quiz", "student": "student1", "score": "3/5"},
        {"quiz": "Science Quiz", "student": "student2", "score": "4/5"},
    ]
    courses = [
        {'title': 'Mathematics', 'students': 30},
        {'title': 'Science', 'students': 25}
    ]

    context = {
        'user': request.user,
        'quizzes': quizzes,
        'recent_submissions': recent_submissions,
        'courses': courses,  # ← add this
    }

    return render(request, 'core_app/educator_dashboard.html', context)

    return render(request, 'core_app/educator_dashboard.html', {
        'user': request.user,
        'courses': courses,
        'quizzes': quizzes,
        'recent_submissions': recent_submissions,
    })

# -----------------------------
# LoginView Customization
# -----------------------------
class CustomLoginView(LoginView):
    template_name = 'core_app/login.html'

    def get_success_url(self):
        try:
            utype = self.request.user.userprofile.user_type
            if utype == 'student':
                return reverse_lazy('student_dashboard')
            elif utype == 'educator':
                return reverse_lazy('educator_dashboard')
        except:
            return reverse_lazy('home')

# -----------------------------
# API / JSON VIEWS
# -----------------------------
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = authenticate(username=data.get('username'), password=data.get('password'))
            if user:
                login(request, user)
                return JsonResponse({"success": True, "message": "Login successful."})
            return JsonResponse({"success": False, "message": "Invalid credentials."})
        except:
            return JsonResponse({"success": False, "message": "Invalid request."})
    return JsonResponse({"success": False, "message": "POST method required."})

@csrf_exempt
@login_required
def get_badge(request):
    return JsonResponse({
        "username": request.user.username,
        "badge": BADGES.get(request.user.username, "No badge yet.")
    })

@csrf_exempt
@login_required
def update_leaderboard(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = data.get("score")
            if score is None:
                return JsonResponse({"success": False, "message": "Score is required."})
            badge = assign_badge(request.user.username, score)
            existing = next((entry for entry in LEADERBOARD if entry["username"] == request.user.username), None)
            if existing:
                existing.update(score=score, badge=badge)
            else:
                LEADERBOARD.append({"username": request.user.username, "score": score, "badge": badge})
            return JsonResponse({"success": True, "leaderboard": sorted(LEADERBOARD, key=lambda x: x['score'], reverse=True)})
        except:
            return JsonResponse({"success": False, "message": "Invalid data."})
    return JsonResponse({"success": False, "message": "POST method required."})

@csrf_exempt
def get_quiz(request):
    quiz_id = request.GET.get('quiz_id')
    quiz = QUIZZES.get(quiz_id)
    if quiz:
        return JsonResponse({"success": True, "quiz": quiz}, safe=False)
    return JsonResponse({"success": False, "message": "Quiz not found."})

@csrf_exempt
@login_required
def submit_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz = QUIZZES.get(data.get('quiz_id'))
            if not quiz:
                return JsonResponse({"success": False, "message": "Quiz not found."})
            answers = data.get('answers', {})
            score = sum(1 for q in quiz["questions"] if answers.get(str(q["id"])) == q["answer"])
            PROGRESS[request.user.username] = {
                "completed": PROGRESS.get(request.user.username, {}).get("completed", 0) + 1,
                "last_score": score
            }
            badge = assign_badge(request.user.username, score)
            return JsonResponse({"success": True, "score": score, "total": len(quiz["questions"]), "badge": badge})
        except:
            return JsonResponse({"success": False, "message": "Invalid data."})
    return JsonResponse({"success": False, "message": "POST method required."})

@csrf_exempt
@login_required
def assign_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student = data.get('student')
            quiz_id = data.get('quiz_id')
            if student and quiz_id:
                USERS.setdefault(student, {}).setdefault('quizzes', []).append(quiz_id)
                return JsonResponse({"success": True, "message": f"Assigned quiz '{quiz_id}' to {student}."})
            return JsonResponse({"success": False, "message": "Missing data."})
        except:
            return JsonResponse({"success": False, "message": "Invalid JSON."})
    return JsonResponse({"success": False, "message": "POST method required."})

@csrf_exempt
@login_required
def get_progress(request):
    return JsonResponse({
        "username": request.user.username,
        "progress": PROGRESS.get(request.user.username, {"completed": 0, "last_score": 0})
    })

from .ai.engines.adaptive import AdaptiveEngine
from .ai.services.gpt_integration import AIContentGenerator

def check_answer(user_answer, correct_answer):
    """
    Helper function to validate quiz answers
    Args:
        user_answer (str): Answer submitted by user
        correct_answer (str): Correct answer from question
    Returns:
        bool: True if answer is correct
    """
    return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

@login_required
def adaptive_quiz(request):
    engine = AdaptiveEngine()
    difficulty = engine.calculate_difficulty(request.user.id)
    
    if request.method == 'GET':
        # Sample question - replace with your actual question generation
        question = {
            'text': "What is the capital of France?",
            'options': ["London", "Paris", "Berlin", "Madrid"],
            'correct': "Paris",
            'explanation': "Paris is the capital and most populous city of France"
        }
        return render(request, 'quiz_page.html', {'question': question})
    
    elif request.method == 'POST':
        try:
            is_correct = check_answer(
                request.POST.get('answer', ''),
                request.POST.get('correct_answer', '')
            )
            
            engine.update_user_state(
                user_id=request.user.id,
                correct=is_correct,
                response_time=float(request.POST.get('time_spent', 30))
            )
            
            return JsonResponse({
                'status': 'success',
                'is_correct': is_correct,
                'explanation': request.POST.get('explanation', '')
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)