"""
API endpoints for skills management
"""
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Skill, CandidateSkill
from accounts.models import UserProfile


@require_http_methods(["GET"])
def api_skills_list(request):
    """
    GET /api/skills/ - List all available skills
    Returns JSON with list of skills
    """
    skills = Skill.objects.all().order_by('name')
    skills_data = [
        {
            'id': skill.id,
            'name': skill.name,
            'category': skill.category.name if skill.category else None,
            'description': skill.description
        }
        for skill in skills
    ]
    return JsonResponse({'skills': skills_data})


@require_http_methods(["POST"])
@login_required
def api_skill_add(request):
    """
    POST /api/skills/add/ - Add a skill to user's profile
    Expects JSON body: {skill: <skill_id>, level: <level>, years_of_experience: <years>}
    """
    try:
        # Parse request body
        data = json.loads(request.body)

        skill_id = data.get('skill')
        level = data.get('level', 'intermediate')
        years_of_experience = data.get('years_of_experience', 0)

        if not skill_id:
            return JsonResponse({'success': False, 'error': 'Skill ID is required'}, status=400)

        # Get skill object
        skill = get_object_or_404(Skill, id=skill_id)

        # Get user profile
        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)

        # Check if user already has this skill
        if CandidateSkill.objects.filter(user_profile=user_profile, skill=skill).exists():
            return JsonResponse({'success': False, 'error': 'You already have this skill'}, status=400)

        # Create candidate skill
        candidate_skill = CandidateSkill.objects.create(
            user_profile=user_profile,
            skill=skill,
            level=level,
            years_of_experience=years_of_experience,
            verified=False
        )

        return JsonResponse({
            'success': True,
            'message': 'Skill added successfully',
            'skill': {
                'id': candidate_skill.id,
                'name': skill.name,
                'level': level,
                'years_of_experience': years_of_experience
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def api_skill_remove(request, skill_id):
    """
    POST /api/skills/<id>/remove/ - Remove a skill from user's profile
    """
    try:
        # Get user profile
        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User profile not found'}, status=404)

        # Get the candidate skill
        candidate_skill = get_object_or_404(
            CandidateSkill,
            id=skill_id,
            user_profile=user_profile
        )

        skill_name = candidate_skill.skill.name
        candidate_skill.delete()

        return JsonResponse({
            'success': True,
            'message': f'Skill "{skill_name}" removed successfully'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def api_my_skills(request):
    """
    GET /api/skills/my/ - Get current user's skills
    """
    try:
        user_profile = request.user.profile
        skills = user_profile.candidate_skills.select_related('skill').all()

        skills_data = [
            {
                'id': skill.id,
                'skill_id': skill.skill.id,
                'name': skill.skill.name,
                'level': skill.level,
                'level_display': skill.get_level_display(),
                'years_of_experience': skill.years_of_experience,
                'verified': skill.verified
            }
            for skill in skills
        ]

        return JsonResponse({'skills': skills_data})

    except UserProfile.DoesNotExist:
        return JsonResponse({'skills': []})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
