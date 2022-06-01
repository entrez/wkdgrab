# wkdgrab

Check for (& import!) Web Key Directory-hosted GPG keys associated with a given email
address. For more information, see [this memo](https://tools.ietf.org/html/draft-koch-openpgp-webkey-service).

### Usage
`wkdgrab.py [-iv] [-x <gpg-path>] user@domain.com`

### Options

|                                         Argument | Description                                                       |
| -----------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------- |
|                                 `-i`, `--import` | Automatically import new keys into gpg without prompting the user |
|                                `-v`, `--verbose` | Print more detailed information about progress and results |
|   `-x <gpg-path>`, `--gpg-executable <gpg-path>` | Make calls to `<gpg-path>`, in lieu of `gpg` (potentially useful if your installation of gpg is not in your `$PATH`, for example) |

### Example

```
$ wkdgrab -v me@entrez.cc
https://openpgpkey.entrez.cc/.well-known/openpgpkey/entrez.cc/hu/s8y7oh5xrdpu9psba3i5ntk64ohouhga?l=me
trying server... can't find dns records for server openpgpkey.entrez.cc
https://entrez.cc/.well-known/openpgpkey/hu/s8y7oh5xrdpu9psba3i5ntk64ohouhga?l=me
trying server... success!
successfully retrieved public key from https://entrez.cc/.well-known/openpgpkey/hu/s8y7oh5xrdpu9psba3i5ntk64ohouhga?l=me
saved public key to me@entrez.cc.key
import key in gpg? (yes/no) yes
successfully added key to your keychain
```
