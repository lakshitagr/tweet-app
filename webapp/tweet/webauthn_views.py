import base64
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    AuthenticatorSelectionCriteria,
    AttestationConveyancePreference,
    PublicKeyCredentialRequestOptions,
    UserVerificationRequirement,
)
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from .models import WebAuthnCredential

User = get_user_model()
RP_ID = "localhost"  # For local dev; use your domain in production
RP_NAME = "TweetNest"

# Temporary in-memory store (not suitable for production)
session_store = {}


@csrf_exempt
@login_required
def start_registration(request):
    user = request.user
    user_id = str(user.id).encode()

    options = generate_registration_options(
        rp=PublicKeyCredentialRpEntity(id=RP_ID, name=RP_NAME),
        user=PublicKeyCredentialUserEntity(
            id=user_id,
            name=user.username,
            display_name=user.username
        ),
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification="preferred"
        ),
        attestation=AttestationConveyancePreference.NONE
    )

    session_store[user.username] = options.challenge

    return JsonResponse(options.model_dump())


@csrf_protect
@login_required
def finish_registration(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        body = json.loads(request.body)
        user = request.user

        print("📩 Finish registration received:", json.dumps(body, indent=2))

        expected_challenge = request.session.get("webauthn_challenge")
        if not expected_challenge:
            return JsonResponse({"error": "No challenge found in session"}, status=400)

        verification = verify_registration_response(
            credential=body,
            expected_challenge=expected_challenge,
            expected_rp_id=RP_ID,
            expected_origin="http://localhost:8000",  # Update this for production
            require_user_verification=True
        )

        # Save credential to database
        WebAuthnCredential.objects.create(
            user=user,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count
        )

        print("✅ Fingerprint registration successful for:", user.username)
        return JsonResponse({"status": "ok"})

    except Exception as e:
        print("❌ Registration error:", str(e))
        return JsonResponse({"error": str(e)}, status=400)


@csrf_protect
def start_authentication(request):
    username = request.GET.get("username")
    try:
        user = User.objects.get(username=username)
        credential = WebAuthnCredential.objects.get(user=user)

        options = generate_authentication_options(
            rp_id=RP_ID,
            allow_credentials=[{
                "id": credential.credential_id,
                "transports": ["internal"],
                "type": "public-key"
            }],
            user_verification=UserVerificationRequirement.PREFERRED
        )

        session_store[username] = options.challenge

        return JsonResponse(options.model_dump())

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except WebAuthnCredential.DoesNotExist:
        return JsonResponse({"error": "Credential not found"}, status=404)


@csrf_protect
def finish_authentication(request):
    try:
        body = json.loads(request.body)
        username = body.get("username")
        user = User.objects.get(username=username)
        credential = WebAuthnCredential.objects.get(user=user)

        verification = verify_authentication_response(
            credential=body,
            expected_challenge=session_store[username],
            expected_rp_id=RP_ID,
            expected_origin="http://localhost:8000",
            credential_public_key=credential.public_key,
            credential_current_sign_count=credential.sign_count,
            require_user_verification=True
        )

        credential.sign_count = verification.new_sign_count
        credential.save()

        login(request, user)
        return JsonResponse({"status": "authenticated"})

    except Exception as e:
        print("Authentication error:", str(e))
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def fingerprint_register_view(request):
    return render(request, 'registration/fingerprint_register.html')
