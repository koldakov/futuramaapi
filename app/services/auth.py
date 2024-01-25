from app.services.security import OAuth2JWTBearer

oauth2_scheme = OAuth2JWTBearer(tokenUrl="token")
