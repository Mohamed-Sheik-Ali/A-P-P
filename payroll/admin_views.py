from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.utils.html import format_html
from .models import UserProfile
from django.contrib.auth.models import User


@method_decorator(staff_member_required, name='dispatch')
class PendingUsersView(ListView):
    model = UserProfile
    template_name = 'admin/pending_users.html'
    context_object_name = 'pending_users'
    
    def get_queryset(self):
        return UserProfile.objects.filter(approval_status='pending').select_related('user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Pending User Approvals'
        context['pending_count'] = self.get_queryset().count()
        context['total_users'] = UserProfile.objects.count()
        context['approved_users'] = UserProfile.objects.filter(approval_status='approved').count()
        context['rejected_users'] = UserProfile.objects.filter(approval_status='rejected').count()
        return context


@staff_member_required
def quick_approve_user(request, user_id):
    """Quick approve a user from the dashboard"""
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfile, user_id=user_id)
        if user_profile.approval_status == 'pending':
            user_profile.approve(request.user)
            user_profile.save()
            messages.success(request, f'User {user_profile.user.username} has been approved successfully.')
        else:
            messages.warning(request, f'User {user_profile.user.username} is not in pending status.')
    
    return redirect('payroll:admin-pending-users')


@staff_member_required 
def quick_reject_user(request, user_id):
    """Quick reject a user from the dashboard"""
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfile, user_id=user_id)
        reason = request.POST.get('reason', 'Rejected by admin')
        if user_profile.approval_status == 'pending':
            user_profile.reject(request.user, reason)
            user_profile.save()
            messages.warning(request, f'User {user_profile.user.username} has been rejected.')
        else:
            messages.warning(request, f'User {user_profile.user.username} is not in pending status.')
    
    return redirect('payroll:admin-pending-users')
