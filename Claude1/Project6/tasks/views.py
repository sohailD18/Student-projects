from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Task
from .forms import TaskForm, TaskSearchForm
from credits.models import Transaction
from gamification.models import check_and_award_badges


@login_required
def task_list(request):
    tasks = Task.objects.filter(status='Open')
    search_form = TaskSearchForm(request.GET)

    user_skills = []
    if request.user.is_authenticated:
        user_skills = request.user.profile.skills.split(',')

    # Filter by skills
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        status_filter = search_form.cleaned_data.get('status')

        if search_query:
            tasks = tasks.filter(required_skills__icontains=search_query)

        if status_filter:
            tasks = tasks.filter(status=status_filter)

    # Match user skills
    matched_tasks = []
    for task in tasks:
        task.is_matched = task.matches_user_skills(request.user.profile.skills)
        if task.is_matched:
            matched_tasks.append(task)

    context = {
        'tasks': tasks,
        'search_form': search_form,
        'matched_tasks': matched_tasks,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Check if task matches user's skills
    is_matched = False
    if request.user.is_authenticated:
        is_matched = task.matches_user_skills(request.user.profile.skills)

    # Check if user can apply
    can_apply = (
        task.status == 'Open' and
        task.created_by != request.user and
        not task.assigned_to
    )

    # Check if user can complete
    can_complete = (
        task.status == 'In Progress' and
        task.created_by == request.user and
        task.assigned_to
    )

    context = {
        'task': task,
        'is_matched': is_matched,
        'can_apply': can_apply,
        'can_complete': can_complete,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm()

    context = {'form': form}
    return render(request, 'tasks/create_task.html', context)


@login_required
def apply_for_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if task.status != 'Open' or task.created_by == request.user:
        messages.error(request, 'You cannot apply for this task.')
        return redirect('task_detail', task_id=task_id)

    if task.assigned_to:
        messages.error(request, 'This task is already assigned.')
        return redirect('task_detail', task_id=task_id)

    # Assign task to user
    task.assigned_to = request.user
    task.status = 'In Progress'
    task.save()

    messages.success(request, 'You have been assigned to this task!')
    return redirect('task_detail', task_id=task_id)


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Only creator can complete the task
    if task.created_by != request.user:
        messages.error(request, 'Only the task creator can mark it as complete.')
        return redirect('task_detail', task_id=task_id)

    if task.status != 'In Progress' or not task.assigned_to:
        messages.error(request, 'Task cannot be completed.')
        return redirect('task_detail', task_id=task_id)

    # Create transaction for payment
    try:
        from django.utils import timezone
        transaction = Transaction(
            sender=task.created_by,
            receiver=task.assigned_to,
            amount=task.estimated_duration,
            task=task
        )
        transaction.save()

        # Mark task as completed
        task.status = 'Completed'
        task.completed_at = timezone.now()
        task.save()

        # Check and award badges
        check_and_award_badges(task.assigned_to)
        check_and_award_badges(task.created_by)

        messages.success(request, f'Task completed! {task.estimated_duration} credits transferred.')
    except ValidationError as e:
        # Extract the error message from the validation error
        error_message = str(e)
        if hasattr(e, 'message_dict'):
            # If it's a dictionary of errors, get the first error message
            errors = list(e.message_dict.values())
            if errors and len(errors) > 0:
                error_message = errors[0][0] if isinstance(errors[0], list) else str(errors[0])
        messages.error(request, error_message)
    except Exception as e:
        messages.error(request, f'Error completing task: {str(e)}')

    return redirect('task_detail', task_id=task_id)


@login_required
def my_tasks(request):
    created_tasks = Task.objects.filter(created_by=request.user)
    assigned_tasks = Task.objects.filter(assigned_to=request.user)

    context = {
        'created_tasks': created_tasks,
        'assigned_tasks': assigned_tasks,
    }
    return render(request, 'tasks/my_tasks.html', context)
