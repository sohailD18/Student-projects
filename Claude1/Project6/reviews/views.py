from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from gamification.models import check_and_award_badges


@login_required
def create_review(request, task_id):
    """Create a review for a completed task"""
    from tasks.models import Task

    task = get_object_or_404(Task, id=task_id)

    # Validate permissions
    if request.user not in [task.created_by, task.assigned_to]:
        messages.error(request, 'You are not authorized to review this task.')
        return redirect('task_detail', task_id=task_id)

    if task.status != 'Completed':
        messages.error(request, 'You can only review completed tasks.')
        return redirect('task_detail', task_id=task_id)

    # Determine reviewee
    if request.user == task.created_by:
        reviewee = task.assigned_to
    else:
        reviewee = task.created_by

    # Check if already reviewed
    if Review.objects.filter(task=task, reviewer=request.user).exists():
        messages.error(request, 'You have already reviewed this task.')
        return redirect('task_detail', task_id=task_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.task = task
            review.reviewer = request.user
            review.reviewee = reviewee
            review.save()

            # Check and award badges
            check_and_award_badges(request.user)

            messages.success(request, 'Review submitted successfully!')
            return redirect('task_detail', task_id=task_id)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'task': task,
        'reviewee': reviewee,
    }
    return render(request, 'reviews/create_review.html', context)
