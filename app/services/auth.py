from app.services.security import OAuth2JWTBearer, OAuth2JWTBearerRefresh

oauth2_scheme = OAuth2JWTBearer(tokenUrl="token")
oauth2_refresh_scheme = OAuth2JWTBearerRefresh(tokenUrl="token")
