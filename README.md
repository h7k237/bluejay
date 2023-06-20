# bluejayhost

Management functionality for an encrypted git repo.

Two scripts encrypt and decrypt a git repo containing sensitive data (known as
the vault). Unencrypted data should not be stored on disk so it is presented at
`/tmp/bluejay/vlt`.

During encryption the contents of `/tmp/bluejay/vlt` are compressed and
encrypted. For decryption the vault file is decrypted, uncompressed and
presented at `/tmp/bluejay/vlt`.

## bluejay_lock

This script takes the sensitive git repo vault as input. It then compresses and
encrypts the repo using a user provided AES key. The path to the vault can be
provided on the CLI or the script will look in `/tmp/bluejay/vlt` by default. If
the encryption is successful the script provides the name of the encrypted file.
The user can then delete the input sensitive data. The format of the encrypted
file is `bluejay-$(date +%FT%T).enc`.

## bluejay_unlock

This script looks for an encrypted vault file. It can be provided on the CLI by
the user. If not provided the script looks for a file with the `.enc` extension
in the current directory. If multiple such files exist, the most recently
created is used. The script then decrypts and decompresses the data and provides
it in the `/tmp/bluejay/vlt` directory as a git repo. If the vault directory
already exists it exits with an error.
