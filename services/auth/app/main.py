# ... (rest of the imports) ...
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from pydantic import BaseModel
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

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

@app.get("/auth/amazon/login")
async def amazon_login():
    amazon_session = OAuth2Session(AMAZON_CLIENT_ID, redirect_uri=AMAZON_REDIRECT_URI)
    authorization_url, state = amazon_session.authorization_url(authorization_base_url)
    return RedirectResponse(authorization_url)

@app.get("/auth/amazon/callback")
async def amazon_callback(code: str, state: str):
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
