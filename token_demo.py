# token_demo.py - create a JWT, read it back, and watch it expire
import time
import jwt

SECRET = "dev-only-secret-please-change-me-32chars!"

# 1. Create a token that expires in 3 seconds
payload = {"sub": "mercy", "role": "coordinator", "exp": int(time.time()) + 3}
token = jwt.encode(payload, SECRET, algorithm="HS256")
print("The token:", token[:40] + "...")

# 2. Decode it while it is still fresh
print("Decoded:", jwt.decode(token, SECRET, algorithms=["HS256"]))

# 3. Wait for it to expire, then try again
time.sleep(4)
try:
    jwt.decode(token, SECRET, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    print("After 4 seconds: token expired, exactly as designed.")