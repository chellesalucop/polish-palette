from django.urls import path, include



from . import views







urlpatterns = [



# General & Landing



    path('', views.landing, name='landing'),



    path('dashboard/', views.dashboard_view, name='dashboard'),







# Client Authentication (Merged from Finished Code)



    path('login/', views.login_view, name='login'),

    path('accounts/login/', views.login_view, name='account_login'), # Override Allauth



    path('signup/', views.signup_view, name='signup'),

    path('accounts/signup/', views.signup_view, name='account_signup'), # Override Allauth



    path('logout/', views.logout_view, name='logout'),

    path('accounts/logout/', views.logout_view, name='account_logout'), # Override Allauth



    path('two-factor-verify/', views.two_factor_verify, name='two_factor_verify'),



    path('two-factor-resend/', views.two_factor_resend, name='two_factor_resend'),







# Client Profile Management (Merged from Finished Code)



    path('profile/', views.profile_view, name='profile'),



    path('profile/picture/', views.profile_picture_view, name='profile_picture'),



    path('profile/password/', views.change_password_view, name='change_password'),



    path('profile/delete/', views.delete_account, name='delete_account'),



    path('history/', views.client_history_view, name='client_history'),

    # Client Reviews
    path('reviews/', views.client_review_list_view, name='client_review_list'),
    path('reviews/create/<int:appointment_id>/', views.client_review_create_view, name='client_review_create'),
    path('reviews/<int:review_id>/edit/', views.client_review_edit_view, name='client_review_edit'),
    path('reviews/<int:review_id>/delete/', views.client_review_delete_view, name='client_review_delete'),







 # Salon Features



    path('services/', views.services_view, name='services'),



    path('booking/', views.booking_create_view, name='booking_create'),



    path('appointments/', views.appointments_list_view, name='appointments_list'),



    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),



    path('appointment/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),

    path('appointment/<int:appointment_id>/reschedule/initiate/', views.reschedule_initiate, name='reschedule_initiate'),

    path('appointment/<int:appointment_id>/reschedule/propose/', views.reschedule_propose, name='reschedule_propose'),

    path('appointment/<int:appointment_id>/reschedule/confirm/', views.reschedule_confirm, name='reschedule_confirm'),

    path('appointment/<int:appointment_id>/reschedule/abort/', views.reschedule_abort, name='reschedule_abort'),







    path('services/', views.services_view, name='services'),



# Password Reset Flow (Merged from Finished Code)



    path('forgot-password/', views.forgot_password_email, name='forgot_password_email'),



    path('forgot-password/otp/', views.forgot_password_otp, name='forgot_password_otp'),



    path('forgot-password/reset/', views.forgot_password_reset, name='forgot_password_reset'),





# Client Forgot Password Flow (New Templates)

    path('client/forgot-password/', views.forgot_password_email, name='client_forgot_password_email'),

    path('client/forgot-password/otp/', views.forgot_password_otp, name='client_forgot_password_otp'),

    path('client/forgot-password/reset/', views.forgot_password_reset, name='client_forgot_password_reset'),



    



# Artist Forgot Password

    path('artist/forgot-password/', views.artist_forgot_password_email, name='artist_forgot_password_email'),

    path('artist/forgot-password/otp/', views.artist_forgot_password_otp, name='artist_forgot_password_otp'),

    path('artist/forgot-password/reset/', views.artist_forgot_password_reset, name='artist_forgot_password_reset'),



# Artist URLs



    path('artist/login/', views.artist_login_view, name='artist_login'),



    path('clear-session/', views.clear_session_view, name='clear_session'),



    path('artist/dashboard/', views.artist_dashboard_view, name='artist_dashboard'),



    path('artist/approve-reject/', views.artist_approve_reject_view, name='artist_approve_reject'),

    

    path('artist/appointment/<int:appointment_id>/override/', views.manual_status_override, name='manual_status_override'),



    path('artist/history/', views.artist_history_view, name='artist_history'),

    path('artist/schedule/', views.artist_schedule_view, name='artist_schedule'),

    path('artist/reviews/', views.artist_reviews_view, name='artist_reviews'),

    path('artist/reviews/<int:review_id>/reply/', views.artist_review_reply_view, name='artist_review_reply'),



    path('artist/logout/', views.artist_logout_view, name='artist_logout'),



# Session Control Endpoints

    path('artist/start-session/', views.start_session_view, name='artist_start_session'),

    path('artist/finish-session/', views.finish_session_view, name='finish_session'),

    path('artist/reschedule/<int:appointment_id>/', views.artist_reschedule_view, name='artist_reschedule'),





# Social Auth



    path('accounts/', include('allauth.urls')),

    path('set-social-password/', views.set_social_password, name='set_social_password'),



# AI-Powered Features

    path('dashboard/ai-portfolio/', views.ai_portfolio_manager, name='ai_portfolio_manager'),



    path('api/recommend-designs/', views.get_design_recommendations, name='get_design_recommendations'),



    path('artist/upload-receipt/', views.upload_payment_receipt, name='upload_payment_receipt'),



    path('client/upload-file/', views.client_file_upload, name='client_file_upload'),

    path('artists/<int:artist_id>/reviews/', views.artist_public_reviews_view, name='artist_public_reviews'),



# Notification Bell API

    path('api/notifications/', views.notifications_list, name='notifications_list'),

    path('api/notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),

    path('api/notifications/clear/', views.notifications_clear, name='notifications_clear'),



]