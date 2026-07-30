import pyotp
import qrcode
import io
import base64
from telecalling.models import UserSettings

def generate_2fa_secret(user):
    """
    Secret + QR code generate பண்ணும்
    Toggle ON பண்ணும்போது call ஆகும்
    """
    secret = pyotp.random_base32()

    # DB-ல் save பண்ணு
    security = UserSettings.objects.get(user=user)
    security.totp_secret = secret
    security.two_factor_authentication = False  # verify ஆனா மட்டும் true
    security.save()

    # QR code generate
    totp = pyotp.TOTP(secret)
    otp_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="YourCRMApp"
    )

    img = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "secret": secret,
        "qr_code": qr_base64
    }


def verify_2fa_otp(user, otp):
    """
    User enter பண்ண OTP சரியா இருக்கா check பண்ணும்
    """
    try:
        security = UserSettings.objects.get(user=user)
    except UserSettings.DoesNotExist:
        return False, "2FA setup இல்ல"

    totp = pyotp.TOTP(security.totp_secret)

    if totp.verify(otp):
        security.two_factor_authentication = True  # ✅ enable
        security.save()
        return True, "2FA enabled successfully!"
    else:
        return False, "Invalid OTP"


def disable_2fa(user):
    """
    Toggle OFF பண்ணும்போது call ஆகும்
    """
    try:
        security = UserSettings.objects.get(user=user)
        security.two_factor_authentication = False
        security.totp_secret = None
        security.save()
        return True, "2FA disabled"
    except UserSettings.DoesNotExist:
        return False, "Not found"


def verify_login_otp(user, otp):
    """
    Login பண்ணும்போது OTP check பண்ணும்
    """
    try:
        security = UserSettings.objects.get(
            user=user,
            two_factor_authentication=True
        )
    except UserSettings.DoesNotExist:
        return False, "2FA enabled இல்ல"

    totp = pyotp.TOTP(security.totp_secret)

    if totp.verify(otp):
        return True, "Login verified"
    else:
        return False, "Wrong OTP"