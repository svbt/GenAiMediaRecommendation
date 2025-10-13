How to run the service
```
Set up your environment: Fill out the .env file with your Amazon credentials and Kafka broker address.
Install dependencies: pip install -r auth/requirements.txt
Start the service: uvicorn app.main:app --reload --port 8000
```

Simulating the flow without a web UI
```
Initiate login: Open a web browser and go to http://localhost:8000/auth/amazon/login.
Amazon authentication: You will be redirected to the Amazon sign-in page.
Authentication complete: After you log in and grant access, Amazon will redirect you back to http://localhost:8000/auth/amazon/callback?code=...&state=....
Receive JWT: The FastAPI service will receive the redirect and return a JSON object containing the JWT.
Verify the token: You can test the token by making a manual API call using a tool like curl or Postman.
```

```
sh
# Replace <YOUR_JWT_TOKEN> with the token from the previous step
curl -X GET "http://localhost:8000/auth/verify?token=<YOUR_JWT_TOKEN>"
```

Test and RUN Without KAFKA
```
Update your code: Make sure your services/auth/app/main.py file is updated with the changes from Step 1.
Create .env file: Ensure you have the services/auth/.env file with your Amazon credentials.
Run Docker Compose: From your project root, execute docker compose up --build. This will start only the auth service.
Initiate login: Access http://localhost:8000/auth/amazon/login in your browser and complete the Amazon login flow. You will be redirected back to your service and get a JWT token.
Test the token: Use curl or a browser to test the /auth/verify endpoint with your new JWT. 
```