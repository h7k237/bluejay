# bluejayhost

Manage an encrypted git repo with ease!

During encryption the contents of a sensitive git repo are compressed and
encrypted. For decryption the encrypted file is decrypted, uncompressed and
presented at a user specified path.

## bluejay_lock

This script takes the git repo vault path as input. It then compresses and
encrypts the repo by deriving a key from a user provided password. The Fernet
cryptographic primitive is used for AES-128 bit encryption. Large files are
encrypted in chunks.

## bluejay_unlock

This script takes the encrypted vault file path as input. The script then
decrypts and uncompresses the data and provides it at a user specified path as a
git repo.
