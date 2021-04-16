from django.contrib.auth import get_user_model

import jwt
import datetime

User = get_user_model()




class JWT:
  __secret = 'mhmd'
  __algorithm ='HS512'

  @staticmethod
  def encode(payload):
    token = jwt.encode(payload, JWT.__secret, JWT.__algorithm)
    return token.decode('utf8')

  @staticmethod
  def decode(token):
    try:
      return jwt.decode(token, JWT.__secret, algorithms=[JWT.__algorithm])
    except jwt.exceptions.InvalidSignatureError:
      return False
    except Exception as e:
      print(e)
      return None

  @staticmethod
  def isValid(token):
    return bool(JWT.decode(token))


class JWTAuth:
  # token used in requests
  @staticmethod
  def generateUserToken(user):
    expired = datetime.datetime.now() + datetime.timedelta(days=7)
    payload = {
      'id': user.pk,
      'username': user.username,
      'email': user.email,
      'is_active': user.is_active,
      'expired': str(expired)
    }

    return JWT.encode(payload)

  @staticmethod
  def checkUserTokenValid(token):
    payload = JWT.decode(token)
    if not payload: return 

    expired = payload.get('expired')
    expiredTime = datetime.datetime.fromisoformat(expired)

    return datetime.datetime.now() < expiredTime

  @staticmethod
  def checkUserTokenIsActiveAccount(token):
    payload = JWT.decode(token) or {}
    return payload.get('is_active')

  @staticmethod
  def extractRequestToken(request):
    prefix = 'Token '
    httpAuthorization = request.META.get('HTTP_AUTHORIZATION', prefix)
    token = httpAuthorization[len(prefix):]

    return token

  @staticmethod
  def getUserFromToken(token):
    pk = JWTAuth.getUserIdFromToken(token)
    return User.objects.filter(pk=pk).first()


  # token used in account activation
  @staticmethod
  def getActivateToken(user):
    # get token that send in user mail
    payload = {'id': user.pk}
    return JWT.encode(payload)

  @staticmethod
  def getUserIdFromToken(token):
    # decode token and get user id to use in account activation
    payload = JWT.decode(token)
    return payload.get('id', None)

  # token used in forget password
  @staticmethod
  def checkForgetPasswordTokenValid(token):
    return JWT.isValid(token)

  @staticmethod
  def generateForgetPasswordToken(email):
    user = User.objects.filter(email=email).first()
    payload = JWTAuth.generateUserToken(user)
    payload.update({})
    return payload
