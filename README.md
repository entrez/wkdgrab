## wkdgrab

### usage
`wkdgrab.py [-iv] [-x <gpg-path>] user@domain.com`

### options

|                                         argument | description                                                       |
| -----------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------- |
|                                 `-i`, `--import` | automatically import new keys into gpg without prompting the user |
|                                `-v`, `--verbose` | print more detailed information about progress and results |
|   `-x <gpg-path>`, `--gpg-executable <gpg-path>` | make calls to,in lieu of `gpg` (potentially useful if your installation of gpg is not in your `$PATH`, for example) |