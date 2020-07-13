<div align="center">
    <img alt="wkdgrab" src="https://camo.githubusercontent.com/27f85956a324b06bee1199faf4d4679959d38534/68747470733a2f2f3078302e73742f697455302e706e67" />
</div>

***

check for web key directory-hosted gpg keys associated with a given email
address. for more information, see [this memo](https://tools.ietf.org/html/draft-koch-openpgp-webkey-service).

### usage
`wkdgrab.py [-iv] [-x <gpg-path>] user@domain.com`

### options

|                                         argument | description                                                       |
| -----------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------- |
|                                 `-i`, `--import` | automatically import new keys into gpg without prompting the user |
|                                `-v`, `--verbose` | print more detailed information about progress and results |
|   `-x <gpg-path>`, `--gpg-executable <gpg-path>` | make calls to,in lieu of `gpg` (potentially useful if your installation of gpg is not in your `$PATH`, for example) |

### example

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
