from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Item, Claim, Notification
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ClaimSerializer,
    ItemSerializer,
    NotificationSerializer,
    RegisterSerializer,
    UserSerializer,
)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    """Create a new account and return it together with JWT tokens."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Return the user profile alongside the access/refresh tokens."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Lightweight health-check endpoint for uptime/deploy probes."""
    return Response({'status': 'ok'})


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

class ItemViewSet(viewsets.ModelViewSet):
    """
    CRUD for items plus a ``claim`` action.

    List/retrieve are public; create requires auth; update/delete are
    restricted to the item's owner.
    """

    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Item.objects.select_related('owner', 'claimed_by')
        params = self.request.query_params
        user = self.request.user

        title = params.get('title')
        location = params.get('location')
        item_type = params.get('item_type')
        owner = params.get('owner')
        claimed_by = params.get('claimed_by')
        claimed = params.get('claimed')

        if title:
            qs = qs.filter(title__icontains=title)
        if location:
            qs = qs.filter(location__icontains=location)
        if item_type:
            qs = qs.filter(item_type__iexact=item_type)

        if owner == 'me' and user.is_authenticated:
            qs = qs.filter(owner=user)
        elif owner and owner.isdigit():
            qs = qs.filter(owner_id=int(owner))

        if claimed_by == 'me' and user.is_authenticated:
            qs = qs.filter(claimed_by=user)

        if claimed is not None:
            value = claimed.lower()
            if value in ('true', '1'):
                qs = qs.filter(claimed=True)
            elif value in ('false', '0'):
                qs = qs.filter(claimed=False)

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def claim(self, request, pk=None):
        item = self.get_object()

        if item.owner_id == request.user.id:
            return Response(
                {'detail': 'You cannot claim your own item.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if item.claimed:
            return Response(
                {'detail': 'This item has already been claimed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        already_pending = Claim.objects.filter(
            item=item,
            claimant=request.user,
            status='pending',
        ).exists()
        if already_pending:
            return Response(
                {'detail': 'You already have a pending claim for this item.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_claim = Claim.objects.create(item=item, claimant=request.user)
        Notification.objects.create(
            recipient=item.owner,
            claim=new_claim,
            message=(
                f'{request.user.username} wants to claim '
                f'your item "{item.title}".'
            ),
        )

        return Response(
            ClaimSerializer(
                new_claim,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Claims (approve / reject by the item owner, list "my claims")
# ---------------------------------------------------------------------------

class ClaimViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Claim.objects.select_related(
            'item',
            'item__owner',
            'claimant',
        )

        if self.action == 'list':
            # A user's own outgoing claims.
            qs = qs.filter(claimant=user)
            status_param = self.request.query_params.get('status')
            if status_param:
                qs = qs.filter(status=status_param)
            return qs

        # Detail routes (retrieve/approve/reject): the claimant or the
        # owner of the claimed item may access the claim.
        return qs.filter(Q(claimant=user) | Q(item__owner=user))

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        claim = self.get_object()

        if claim.item.owner_id != request.user.id:
            return Response(
                {'detail': 'You are not allowed to approve this claim.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if claim.status != 'pending':
            return Response(
                {'detail': 'This claim has already been reviewed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = claim.item

        if item.claimed:
            claim.status = 'rejected'
            claim.reviewed_at = timezone.now()
            claim.save(update_fields=['status', 'reviewed_at'])
            return Response(
                {'detail': 'This item has already been claimed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            claim.status = 'approved'
            claim.reviewed_at = timezone.now()
            claim.save(update_fields=['status', 'reviewed_at'])

            item.claimed = True
            item.claimed_by = claim.claimant
            item.save(update_fields=['claimed', 'claimed_by'])

            other_claims = Claim.objects.filter(
                item=item,
                status='pending',
            ).exclude(id=claim.id)

            for other in other_claims:
                other.status = 'rejected'
                other.reviewed_at = timezone.now()
                other.save(update_fields=['status', 'reviewed_at'])
                Notification.objects.create(
                    recipient=other.claimant,
                    claim=other,
                    message=(
                        f'Your claim for "{item.title}" was rejected '
                        f'because another claim was approved.'
                    ),
                )

            Notification.objects.create(
                recipient=claim.claimant,
                claim=claim,
                message=f'Your claim for "{item.title}" has been approved.',
            )

        return Response(
            ClaimSerializer(claim, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        claim = self.get_object()

        if claim.item.owner_id != request.user.id:
            return Response(
                {'detail': 'You are not allowed to reject this claim.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if claim.status != 'pending':
            return Response(
                {'detail': 'This claim has already been reviewed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        claim.status = 'rejected'
        claim.reviewed_at = timezone.now()
        claim.save(update_fields=['status', 'reviewed_at'])

        Notification.objects.create(
            recipient=claim.claimant,
            claim=claim,
            message=f'Your claim for "{claim.item.title}" has been rejected.',
        )

        return Response(
            ClaimSerializer(claim, context=self.get_serializer_context()).data
        )


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'claim',
            'claim__item',
            'claim__item__owner',
            'claim__claimant',
        )

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
        return Response(
            NotificationSerializer(
                notification,
                context=self.get_serializer_context(),
            ).data
        )

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)
        return Response({'detail': 'All notifications marked as read.'})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
        return Response({'unread': count})
