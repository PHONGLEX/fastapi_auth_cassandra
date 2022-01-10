import jwt
import secrets

from fastapi import APIRouter, status, HTTPException, Depends, Request, Response
from fastapi_jwt_auth import AuthJWT
import redis

from helpers.config import *
from helpers.authentication import *
from models.auth import *
from workers.worker import send_email_task

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, request: Request):
    user_info = data.dict(exclude_unset=True)
    user = User.create_user(**user_info)
    d = {'id': user.id.hex}
    site = request.get('server')
    token = jwt.encode(d, config['SECRET_KEY'], algorithm="HS256").decode()
    link = f"http://{site[0]}:{site[1]}/auth/email-verify/?token={token}"
    body = f"""
        Hi {user.name},
        Please use the link below to verify your account {link}
    """
    data = {
        "subject": "Verify your account",
        "body": body,
        "to": [user.email]
    }
    send_email_task.delay(data)
    return {"message": "We've sent you an email to verify your account"}


@auth_router.get('/email-verify', status_code=status.HTTP_200_OK)
async def email_verify(token: str):
    try:
        payload = jwt.decode(token, config['SECRET_KEY'], algorithms=["HS256"])
        user = User.objects.get(id=payload['id'])
        if user and not user.is_verified:
            user.is_verified = True
            user.save()
            return {"message": "Successfully verified your account"}
    except jwt.exceptions.DecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is invalid, please request a new one", headers={"WWW-Authenticate": "Bearer"})
    except jwt.exceptions.ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is expired, please request a new one", headers={"WWW-Authenticate": "Bearer"})


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(data: UserLogin, Authorize: AuthJWT=Depends()):
    user_info = data.dict()
    user_qs = User.objects.filter(email=user_info['email']).allow_filtering()
    if user_qs.count() > 0:
        user = user_qs[0]
        if user and user.verify_password(user_info['password']):
            access_token = Authorize.create_access_token(subject=user.email, user_claims={"is_staff": user.is_staff})
            refresh_token = Authorize.create_refresh_token(subject=user.email)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
    raise AUTH_EXCEPTION        


@auth_router.post('/reset-password', status_code=status.HTTP_201_CREATED)
async def reset_password(data: UserResetPassword, request: Request):
    user_qs = User.objects.filter(email=data.dict()['email']).allow_filtering()
    if user_qs.count() > 0:
        user = user_qs[0]
        d = {"id": user.id.hex}
        site = request.get('server')
        token = secrets.token_hex()
        uidb64 = create_signed_token(token.encode('utf-8'), d)
        link = f"http://{site[0]}:{site[1]}/auth/reset-password-confirm/{uidb64}/{token}/"
        body = f"""
            Hi {user.name}
            Please use the link below to reset password {link}
        """
        data = {
            "subject": "Reset your password",
            "body": body,
            "to": [user.email]
        }
        send_email_task.delay(data)
        return {"message": "We've sent you an email to reset your password"}  
    raise AUTH_EXCEPTION    
        

@auth_router.post('/reset-password-confirm/{uidb64}/{token}/', status_code=status.HTTP_200_OK)
async def reset_password_confirm(uidb64: str, token: str):
    verified, payload = verify_signed_token(token.encode('utf-8'), uidb64)
    if verified:
        return {"success": True, "uidb64": uidb64, "token": token}
    raise TOKEN_EXCEPTION


@auth_router.patch('/set-new-password', status_code=status.HTTP_202_ACCEPTED)
async def set_new_password(data: ResetPasswordModel):
    req = data.dict()
    verified, payload = verify_signed_token(req['token'].encode('utf-8'), req['uidb64'])
    if verified:
        user = User.objects.get(id=payload['id'])
        if user:
            user.set_password(req['password'])
            user.save()
            return {"message": "Changed password successfully"}
    raise TOKEN_EXCEPTION


@auth_router.post('/logout')
@validate_token
async def logout(Authorize: AuthJWT=Depends()):
    jti = Authorize.get_raw_jwt()['jti']
    redis_conn.setex(jti, settings.access_expires, "true")
    return Response(status_code=status.HTTP_204_NO_CONTENT)