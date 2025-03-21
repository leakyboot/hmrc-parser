from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate hash for 'testpass'
password = "testpass"
hashed = pwd_context.hash(password)
print(f"Generated hash for '{password}': {hashed}")

# Verify the hash
is_valid = pwd_context.verify(password, hashed)
print(f"Hash verification: {is_valid}")
