# ... (rest of the imports) ...
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from pydantic import BaseModel
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

import os

load_dotenv()

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

AMAZON_CLIENT_ID = os.getenv("AMAZON_CLIENT_ID")
AMAZON_CLIENT_SECRET = os.getenv("AMAZON_CLIENT_SECRET")
AMAZON_REDIRECT_URI = os.getenv("AMAZON_REDIRECT_URI")

# --- Dummy Database (In a real app, use a database) ---
db = {}

# --- FastAPI App Initialization ---
app = FastAPI()

# --- Utility functions ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Pydantic Models ---
class User(BaseModel):
    id: str
    providers: list[str]

# --- Amazon OAuth Flow ---
authorization_base_url = "https://www.amazon.com/ap/oa"
token_url = "https://api.amazon.com/auth/o2/token"
profile_url = "https://api.amazon.com/user/profile"

# Define the scopes your application needs
# 'profile' and 'profile:user_id' are common basic scopes
SCOPES = ["profile"]

@app.get("/auth/amazon/login")
async def amazon_login():
    # It's better to use WebApplicationClient to handle the OAuth flow
    # This automatically includes the required response_type and client_id
    client = WebApplicationClient(AMAZON_CLIENT_ID)

    # Use the client to prepare the authorization URL
    authorization_url = client.prepare_request_uri(
        authorization_base_url,
        redirect_uri=AMAZON_REDIRECT_URI,
        scope=SCOPES,
    )
    
    # Store the state in the user's session for security purposes (CSRF protection)
    # This step is critical but omitted in your original snippet
    # You will need to implement a session management system
    # e.g., using a library like `fastapi-sessions`.

    return RedirectResponse(authorization_url)

@app.get("/auth/amazon/callback")
async def amazon_callback(
    code: str = Query(None), # Make code optional
    state: str = Query(None), # Make state optional
    error: str = Query(None) # Add a parameter for the error response
):
    if error:
        # Handle the error reported by Amazon.
        # Example: print the error or raise an HTTPException.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amazon login failed with error: {error}"
        )

    if not code or not state:
        # This should not happen if the `error` check is working,
        # but is a good fallback.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code or state parameter."
        )
    amazon_session = OAuth2Session(AMAZON_CLIENT_ID, redirect_uri=AMAZON_REDIRECT_URI)
    
    token = amazon_session.fetch_token(
        token_url,
        client_secret=AMAZON_CLIENT_SECRET,
        code=code,
        include_client_id=True,
    )
    
    user_profile = amazon_session.get(profile_url).json()
    user_id = user_profile['user_id']
    
    if user_id not in db:
        db[user_id] = User(id=user_id, providers=["amazon"])
        # Temporarily comment out Kafka publishing
        print(f"[{datetime.now()}] (Kafka event skipped) Publishing user.login event for new user: {user_id}")
    else:
        if "amazon" not in db[user_id].providers:
            db[user_id].providers.append("amazon")
        # Temporarily comment out Kafka publishing
        print(f"[{datetime.now()}] (Kafka event skipped) Publishing user.login event for existing user: {user_id}")

    jwt_token = create_access_token({"sub": user_id, "providers": db[user_id].providers})
    
    return {"access_token": jwt_token, "token_type": "bearer"}

@app.get("/auth/verify")
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"message": "Token is valid", "payload": payload}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/")
async def root():
    return {"message": "Auth Service is running. Use /auth/amazon/login to start."}
