# bluejayhost

Management functionality for an encrypted git repo

Two symmetric scripts will encrypt and decrypt a git repo containing sensitive
data (known as the vault). Unencrypted data should not be stored on disk so it
will be presented in `/tmp/bluejay/vlt`.

`/tmp/bluejay/vlt` should correspond to the path of the decrypted vault git repo.

During encryption the contents of `/tmp/bluejay/vlt` are compressed into a tar
file and encrypted. Consequently, for decryption a vault file is decrypted,
un-tar-ed and presented at `/tmp/bluejay/vlt`.

## bluejay_lock

This script takes the sensitive git repo vault as input. It then compresses and
encrypts the repo using a user provided AES key. The path to the vault can be provided as
input or the script will look in `/tmp/bluejay/vlt` by default. If the encryption is successful the
script should provide the name of the encrypted file in the current directory. The user can then
delete the input sensitive data. The format of the encrypted file is
`bluejay-$(date +%FT%T).enc` in the current working directory.


## bluejay_unlock

This script looks for an encrypted vault file. It can be provided as an input by the
user. If not provided the script looks for a file with the `.enc` extension. If multiple such files
exist, the most recently created is used. The script then decrypts and decompresses the data and
provides it for viewing in the `/tmp/bluejay/vlt` directory as a git repo. If the vault
directory already exists it exits with an error.
