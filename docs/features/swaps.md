# Swaps

## Overview

The swap system is the core transaction layer of SkillSwap. It manages the full lifecycle of a skill exchange from the initial request through to a completed session and mutual reviews. Every interaction is gated by strict participant-only access controls to protect user privacy and prevent abuse.

## How it Works

### Full Swap Lifecycle

```
1. DISCOVERY
   User A browses skills → finds User B's offered skill
       → clicks "Request Swap" on skill detail page

2. REQUEST
   User A selects which of their skills to offer in return
       → adds an optional message
           → submits → SwapRequest created (status: pending)
               → User B receives notification

3. RESPONSE
   User B sees request in inbox
       → accepts or denies
           → If denied: status = rejected, User A notified, flow ends
           → If accepted: status = accepted, User A notified

4. SESSION SCHEDULING
   Either participant visits swap detail page
       → fills in session form (date, duration, meeting link)
           → Session created (status: scheduled)
               → Both participants notified

5. COMPLETION
   Either participant marks session as completed
       → Session status = completed
           → "Leave a Review" button appears for both

6. REVIEWS
   Each participant can leave one review for the other
       → Rating (1-5) + optional comment
           → Reviewee's rating_average auto-updated
               → Reviewer notified
```

### Status State Machine

```
                ┌─────────┐
                │ PENDING │
                └────┬────┘
                     │
          ┌──────────┴──────────┐
          │                     │
     (receiver             (receiver
      accepts)               denies)
          ↓                     ↓
     ┌──────────┐          ┌──────────┐
     │ ACCEPTED │          │ REJECTED │
     └──────────┘          └──────────┘
     (sender cancels while pending)
          ↓
     ┌───────────┐
     │ CANCELLED │
     └───────────┘
```

## Technical Implementation

### Models (`swaps/models.py`)

**`SwapRequest`**

```python
class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    sender = models.ForeignKey(User, related_name='sent_requests', ...)
    receiver = models.ForeignKey(User, related_name='received_requests', ...)
    offered_skill = models.ForeignKey(UserSkill, related_name='offered_in_swaps', ...)
    requested_skill = models.ForeignKey(UserSkill, related_name='requested_in_swaps', ...)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Note: `offered_skill` and `requested_skill` reference `UserSkill` not `Skill`. This captures the specific user's proficiency and availability at the time of the request.

**`Session`**

```python
class Session(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    swap_request = models.OneToOneField(SwapRequest, related_name='session', ...)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    meeting_link = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
```

`OneToOneField` enforces that each swap can only have one session.

**`Review`**

```python
class Review(models.Model):
    session = models.ForeignKey(Session, related_name='reviews', ...)
    reviewer = models.ForeignKey(User, related_name='reviews_given', ...)
    reviewee = models.ForeignKey(User, related_name='reviews_received', ...)
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('session', 'reviewer')]  # one review per person per session
```

### Views (`swaps/views.py`)

| View | Auth Needed | Who can access | Purpose |
|---|---|---|---|
| `create_swap` | Yes | Any user | Send swap request |
| `inbox` | Yes | Any user | View received requests |
| `sent_requests` | Yes | Any user | View sent requests |
| `swap_detail` | Yes | Sender or receiver | View swap details |
| `accept_swap` | Yes | Receiver only | Accept pending swap |
| `deny_swap` | Yes | Receiver only | Deny pending swap |
| `cancel_swap` | Yes | Sender only | Cancel pending swap |
| `complete_session` | Yes | Either participant | Mark session complete |
| `leave_review` | Yes | Either participant | Submit review |

### Security Pattern

Every view that modifies a swap enforces ownership at the database level using `get_object_or_404` with ownership filters:

```python
# Only receiver can accept — 404 if wrong user tries
swap = get_object_or_404(SwapRequest, pk=pk, receiver=request.user)

# Only sender can cancel — 404 if wrong user tries
swap = get_object_or_404(SwapRequest, pk=pk, sender=request.user)

# Both can view — manual check with redirect
if request.user != swap.sender and request.user != swap.receiver:
    messages.error(request, "You do not have permission to view this swap.")
    return redirect('swaps:inbox')
```

### Business Rules Enforced in Views

```python
# 1. Cannot swap with yourself
if requested_skill.user == request.user:
    messages.error(request, "You can't swap with yourself!")
    return redirect('skills:list')

# 2. Cannot send duplicate pending requests
existing = SwapRequest.objects.filter(
    sender=request.user,
    requested_skill=requested_skill,
    status='pending'
).exists()

# 3. Can only accept/deny pending swaps
if swap.status != 'pending':
    messages.error(request, "This request is no longer pending.")

# 4. Can only review completed sessions
if session.status != 'completed':
    messages.error(request, "You can only review completed sessions.")

# 5. Can only review once per session
already_reviewed = Review.objects.filter(
    session=session, reviewer=request.user
).exists()
```

### Rating Calculation

`update_rating(user)` is called every time a new review is saved:

```python
def update_rating(user):
    from django.db.models import Avg
    reviews = Review.objects.filter(reviewee=user)
    avg = reviews.aggregate(Avg('rating'))['rating__avg']
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.rating_average = round(avg, 2) if avg else 0
    profile.save()
```

This recalculates from all reviews rather than incrementally updating, ensuring accuracy even if reviews are deleted.

### Forms (`swaps/forms.py`)

**`SwapRequestForm`**
Filters `offered_skill` dropdown to only show the current user's offered skills:

```python
def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')  # extract before calling super()
    super().__init__(*args, **kwargs)
    self.fields['offered_skill'].queryset = UserSkill.objects.filter(
        user=user,
        skill_type='offer'
    )
```

`kwargs.pop('user')` must happen before `super().__init__()` otherwise Django's base form receives an unexpected keyword argument.

**`SessionForm`**
Handles datetime-local input for scheduling.

**`ReviewForm`**
Rating dropdown (1-5 stars) and optional comment.

## URLs

| URL | Name | Description |
|---|---|---|
| `/swaps/create/<skill_id>/` | `swaps:create` | Send swap request |
| `/swaps/inbox/` | `swaps:inbox` | Received requests |
| `/swaps/sent/` | `swaps:sent` | Sent requests |
| `/swaps/<pk>/` | `swaps:detail` | Swap detail |
| `/swaps/<pk>/accept/` | `swaps:accept` | Accept swap |
| `/swaps/<pk>/deny/` | `swaps:deny` | Deny swap |
| `/swaps/<pk>/cancel/` | `swaps:cancel` | Cancel swap |
| `/swaps/session/<id>/complete/` | `swaps:complete_session` | Complete session |
| `/swaps/session/<id>/review/` | `swaps:leave_review` | Leave review |

## Key Design Decisions

### Why link SwapRequest to UserSkill not Skill?
When a swap request is created, it should capture the specific context: this particular user's proficiency level and availability. Linking to the generic `Skill` would lose that context. Linking to `UserSkill` preserves it.

### Why allow both participants to review?
A one-sided review system creates an imbalance; the reviewed party has no way to respond or share their experience. Mutual reviews build a more complete trust picture and incentivise both parties to show up and engage well.

### Why recalculate rating from all reviews rather than incrementally?
Incremental updates (`rating = (rating * count + new_rating) / (count + 1)`) can drift over time due to floating point errors. Recalculating from scratch with `Avg()` is always accurate regardless of how many reviews exist.

### Why use get_object_or_404 with ownership filter?
This pattern returns a 404 instead of a 403 when a user tries to access something they don't own. While 403 is technically more correct, 404 reveals less information about the system; an attacker can't confirm the resource exists.

## Known Limitations

- No way to reschedule a session once created
- No cancellation of an accepted swap (only pending swaps can be cancelled)
- Reviews cannot be edited or deleted once submitted
- No dispute resolution mechanism
- Session status must be manually marked as completed - no automatic completion

## Future Improvements

- [ ] Reschedule session request flow
- [ ] Cancel accepted swap with mutual agreement
- [ ] Dispute resolution system
- [ ] Session reminders via email (24h and 1h before)
- [ ] Automatic session completion after scheduled date passes
- [ ] Counter-offer on swap requests
- [ ] Group swaps (3+ participants)
- [ ] Swap history timeline on profile