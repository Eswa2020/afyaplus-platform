# hash_demo.py - see password hashing with your own eyes
import bcrypt

password = b"logistics2026"
stored_hash = bcrypt.hashpw(password, bcrypt.gensalt())

print("What we store:", stored_hash.decode())
print("Right password matches:", bcrypt.checkpw(b"logistics2026", stored_hash))
print("Wrong password matches:", bcrypt.checkpw(b"letmein", stored_hash))