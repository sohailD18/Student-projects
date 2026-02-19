from django.urls import path
from . import views
from . import api

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/post/', views.post_job, name='post_job'),
    path('jobs/<int:job_id>/apply/', views.submit_application, name='submit_application'),
    path('applications/', views.my_applications, name='my_applications'),
    path('my-jobs/', views.my_posted_jobs, name='my_posted_jobs'),
    path('jobs/<int:job_id>/save/', views.save_job, name='save_job'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('applications/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('jobs/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('applications/<int:application_id>/resume/', views.download_resume, name='download_resume'),
    path('recommendations/', views.job_recommendations, name='job_recommendations'),
    path('jobs/<int:job_id>/candidates/', views.job_candidates_matches, name='job_candidates'),

    # Interview Bot URLs
    path('jobs/<int:job_id>/interview/start/', views.start_interview, name='start_interview'),
    path('interview/<int:session_id>/', views.interview_take, name='interview_take'),
    path('interview/<int:session_id>/submit/<int:question_id>/', views.interview_submit_response, name='interview_submit'),
    path('interview/<int:session_id>/complete/', views.interview_complete, name='interview_complete'),
    path('interview/results/<int:session_id>/', views.interview_results, name='interview_results'),
    path('interviews/', views.interview_list, name='interview_list'),

    # Notifications URLs
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.unread_notification_count, name='unread_notification_count'),

    # Analytics Dashboard URL
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    # Skills API URLs
    path('api/skills/', api.api_skills_list, name='api_skills_list'),
    path('api/skills/add/', api.api_skill_add, name='api_skill_add'),
    path('api/skills/my/', api.api_my_skills, name='api_my_skills'),
    path('api/skills/<int:skill_id>/remove/', api.api_skill_remove, name='api_skill_remove'),
]
