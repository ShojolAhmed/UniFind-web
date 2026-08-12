from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import timezone

from .models import Item, Claim, Notification
from .forms import ItemForm
from .auth_forms import StudentSignUpForm

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages

class UserLoginView(LoginView):
    template_name='items/login.html'

def home(request):

    items = Item.objects.all()

    title = request.GET.get('title', '')
    location = request.GET.get('location', '')

    if title:
        items = items.filter(
            title__icontains=title
        )

    if location:
        items = items.filter(
            location__icontains=location
        )

    return render(
        request,
        'items/home.html',
        {
            'items': items,
            'title': title,
            'location': location
        }
    )


@login_required
def student_dashboard(request):

    my_posts = Item.objects.filter(
        owner=request.user
    ).order_by('-id')

    claimed_items = Item.objects.filter(
        claimed_by=request.user
    ).order_by('-id')

    pending_claims = Claim.objects.filter(
        claimant=request.user,
        status='pending'
    ).select_related(
        'item'
    ).order_by('-created_at')

    return render(
        request,
        'items/student_dashboard.html',
        {
            'my_posts': my_posts,
            'claimed_items': claimed_items,
            'pending_claims': pending_claims
        }
    )


@login_required
def add_item(request):

    if request.method=='POST':

        form=ItemForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            item=form.save(
                commit=False
            )

            item.owner=request.user

            item.save()

            return redirect('/')

    else:
        form=ItemForm()

    return render(
        request,
        'items/add.html',
        {'form':form}
    )

@login_required
def edit_item(request, id):
    item = get_object_or_404(Item, id=id)

    if item.owner != request.user:
        raise PermissionDenied("You are not allowed to edit this item.")

    if request.method == 'POST':
        form = ItemForm(
            request.POST,
            request.FILES,
            instance=item
        )
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ItemForm(instance=item)

    return render(
        request,
        'items/edit.html',
        {'form': form, 'item': item}
    )


@login_required
def delete_item(request, id):
    item = get_object_or_404(Item, id=id)

    if item.owner != request.user:
        raise PermissionDenied("You are not allowed to delete this item.")

    if request.method == 'POST':
        item.delete()
        return redirect('/')

    return render(
        request,
        'items/delete_confirm.html',
        {'item': item}
    )

@login_required
def claim(request, id):

    item = get_object_or_404(
        Item,
        id=id
    )

    # User cannot claim their own item
    if item.owner == request.user:
        messages.error(
            request,
            'You cannot claim your own item.'
        )
        return redirect('/')

    # Item has already been claimed
    if item.claimed:
        messages.warning(
            request,
            'This item has already been claimed.'
        )
        return redirect('/')

    # Check if this user already has a pending claim
    existing_claim = Claim.objects.filter(
        item=item,
        claimant=request.user,
        status='pending'
    ).first()

    if existing_claim:
        messages.warning(
            request,
            'You already have a pending claim for this item.'
        )
        return redirect('/')

    # Create the claim request
    claim_request = Claim.objects.create(
        item=item,
        claimant=request.user
    )

    # Notify the owner
    Notification.objects.create(
        recipient=item.owner,
        claim=claim_request,
        message=(
            f'{request.user.username} wants to claim '
            f'your item "{item.title}".'
        )
    )

    messages.success(
        request,
        'Claim request sent successfully. The owner has been notified.'
    )

    return redirect('/')

@login_required
def notifications(request):

    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        'claim',
        'claim__item',
        'claim__claimant'
    ).order_by('-created_at')

    return render(
        request,
        'items/notifications.html',
        {
            'notifications': user_notifications
        }
    )

@login_required
def mark_notification_read(request, id):

    notification = get_object_or_404(
        Notification,
        id=id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save()

    return redirect('/notifications/')

@login_required
def approve_claim(request, id):

    if request.method != 'POST':
        return redirect('/notifications/')

    claim = get_object_or_404(
        Claim,
        id=id
    )

    # Only the item owner can approve the claim
    if claim.item.owner != request.user:
        raise PermissionDenied(
            "You are not allowed to approve this claim."
        )

    # Claim already reviewed
    if claim.status != 'pending':
        messages.warning(
            request,
            'This claim has already been reviewed.'
        )
        return redirect('/notifications/')

    # Item was already claimed by someone else
    if claim.item.claimed:
        claim.status = 'rejected'
        claim.reviewed_at = timezone.now()
        claim.save()

        messages.warning(
            request,
            'This item has already been claimed.'
        )

        return redirect('/notifications/')

    # Approve the claim
    claim.status = 'approved'
    claim.reviewed_at = timezone.now()
    claim.save()

    # Mark the item as claimed
    item = claim.item
    item.claimed = True
    item.claimed_by = claim.claimant
    item.save()

    other_claims = Claim.objects.filter(
        item=item,
        status='pending'
    ).exclude(
        id=claim.id
    )

    for other_claim in other_claims:

        other_claim.status = 'rejected'
        other_claim.reviewed_at = timezone.now()
        other_claim.save()

        Notification.objects.create(
            recipient=other_claim.claimant,
            claim=other_claim,
            message=(
                f'Your claim for "{item.title}" was rejected '
                f'because another claim was approved.'
            )
        )

    # Notify the claimant
    Notification.objects.create(
        recipient=claim.claimant,
        claim=claim,
        message=(
            f'Your claim for "{item.title}" has been approved.'
        )
    )

    messages.success(
        request,
        'Claim approved successfully.'
    )

    return redirect('/notifications/')

@login_required
def reject_claim(request, id):

    if request.method != 'POST':
        return redirect('/notifications/')

    claim = get_object_or_404(
        Claim,
        id=id
    )

    # Only the item owner can reject the claim
    if claim.item.owner != request.user:
        raise PermissionDenied(
            "You are not allowed to reject this claim."
        )

    # Claim already reviewed
    if claim.status != 'pending':
        messages.warning(
            request,
            'This claim has already been reviewed.'
        )
        return redirect('/notifications/')

    # Reject claim
    claim.status = 'rejected'
    claim.reviewed_at = timezone.now()
    claim.save()

    # Notify claimant
    Notification.objects.create(
        recipient=claim.claimant,
        claim=claim,
        message=(
            f'Your claim for "{claim.item.title}" has been rejected.'
        )
    )

    messages.success(
        request,
        'Claim rejected.'
    )

    return redirect('/notifications/')

def signup(request):

    if request.method=='POST':

        form=StudentSignUpForm(
            request.POST
        )

        if form.is_valid():

            user=form.save()

            login(
                request,
                user
            )

            return redirect('/')

    else:

        form=StudentSignUpForm()

    return render(
        request,
        'items/signup.html',
        {'form':form}
    )
