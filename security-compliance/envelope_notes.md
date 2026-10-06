# Envelope encryption: a CMK wraps a DEK

Flow (recognise, not a homemade cipher lab):

1. The customer master key (CMK) lives in KMS, Key Vault, or an HSM.
2. The CMK wraps, meaning encrypts, a short-lived data encryption key (DEK).
3. The DEK encrypts the blob: a volume, a backup, an object.
4. Store the ciphertext and the wrapped DEK together. The CMK never leaves the HSM.
5. To read: unwrap the DEK with the CMK, then decrypt the blob with the DEK.

Evidence this week: name the CMK in kms_twin.json and secret_refs.yaml.
Do not invent AES inside a FastAPI route.