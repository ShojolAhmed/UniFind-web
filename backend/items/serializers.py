from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Item, Claim, Notification


class PublicUserSerializer(serializers.ModelSerializer):
    """Minimal, non-sensitive user info safe to expose publicly."""

    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Full profile of the authenticated user (includes email)."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'A user with this email already exists.'
            )
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password2': 'The two password fields did not match.'}
            )

        # Run Django's configured password validators.
        candidate = User(
            username=attrs.get('username'),
            email=attrs.get('email')
        )
        try:
            validate_password(attrs['password'], candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ItemSerializer(serializers.ModelSerializer):
    owner = PublicUserSerializer(read_only=True)
    claimed_by = PublicUserSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()
    user_has_pending_claim = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id',
            'title',
            'item_type',
            'description',
            'location',
            'image',
            'contact',
            'claimed',
            'created_at',
            'owner',
            'claimed_by',
            'is_owner',
            'user_has_pending_claim',
        ]
        read_only_fields = [
            'id',
            'claimed',
            'created_at',
            'owner',
            'claimed_by',
        ]

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and obj.owner_id == request.user.id
        )

    def get_user_has_pending_claim(self, obj):
        request = self.context.get('request')
        if not (request and request.user.is_authenticated):
            return False
        return obj.claims.filter(
            claimant=request.user,
            status='pending'
        ).exists()


class ClaimItemSerializer(serializers.ModelSerializer):
    """Lightweight item representation nested inside a claim/notification."""

    owner = PublicUserSerializer(read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'title',
            'item_type',
            'description',
            'location',
            'image',
            'claimed',
            'owner',
        ]
        read_only_fields = fields


class ClaimSerializer(serializers.ModelSerializer):
    item = ClaimItemSerializer(read_only=True)
    claimant = PublicUserSerializer(read_only=True)

    class Meta:
        model = Claim
        fields = [
            'id',
            'item',
            'claimant',
            'status',
            'created_at',
            'reviewed_at',
        ]
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    claim = ClaimSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'message',
            'is_read',
            'created_at',
            'claim',
        ]
        read_only_fields = fields
