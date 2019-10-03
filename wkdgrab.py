#!/usr/bin/env python3

import functools
import hashlib
import itertools
import requests
import sys
import os


def find_email(arglist):
    email = None
    i = 0
    while i < len(arglist):
        arg = arglist[i]
        if '@' in arg:
            email = arglist.pop(i)
        else:
            i += 1
    return (email, arglist)


def attempt_download(url, local_filename, verbose):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_filename, 'wb') as out:
                out.write(r.content)
            indicate_success(url, local_filename)
        elif verbose:
            print('request to {target} returned {status} {reason}'.format(
                target = url, status = r.status_code, reason = r.reason
            ))
    except requests.exceptions.Timeout as ex:
        if verbose:
            print('connection to {target} timed out'.format(target = url))
    except requests.exceptions.ConnectionError as ex:
        if verbose:
            print('unable to connect to {target}'.format(target = url))
    except requests.exceptions.RequestException as ex:
        if verbose:
            print('error contacting {target} ({details})'.format(url = target, details = ex.msg))


def indicate_success(url, filename):
    if verbose:
        print('successfully retrieved public key from {source}'.format(source = url))
    print('saved public key to {file}'.format(file = filename))
    exit()


def encode_zbase32(bs):
    ALPHABET = b'ybndrfg8ejkmcpqxot1uwisza345h769'
    result = bytearray()
    for word in itertools.zip_longest(*([iter(bs)] * 5)):
        padding_count = word.count(None)
        n = functools.reduce(lambda x, y: (x << 8) + (y or 0), word, 0)
        for i in range(0, (40 - 8 * padding_count), 5):
            result.append(ALPHABET[(n >> (35 - i)) & 0x1F])
    return result


def local_zbase32(s):
    '''
    used to locate public key filename on server

    e.g. for me@entrez.cc:

    >>> local_zbase32('me')
    's8y7oh5xrdpu9psba3i5ntk64ohouhga'

    https://entrez.cc/.well-known/openpgpkey/hu/s8y7oh5xrdpu9psba3i5ntk64ohouhga?l=me
    '''
    sb = s.lower().encode('utf8')
    zb = encode_zbase32(
        hashlib.sha1(sb).digest()
    )
    return zb.decode('utf8')

help_text = "usage: {program} [-v|--verbose] user@domain.com".format(
    program = os.path.basename(sys.argv[0])
)

args = sys.argv[1:]
email, arguments = find_email(args)
if email is None:
    print(help_text)
    exit()

verbose = '-v' in arguments or '--verbose' in arguments

local_part, domain_part = email.split('@')
hashed_fingerprint = local_zbase32(local_part)

first_potential = 'https://openpgpkey.{domain}/.well-known/openpgpkey/{domain}/hu/{hash32}?l={local}'.format(
    domain = domain_part, local = local_part, hash32 = hashed_fingerprint
)
second_potential = 'https://{domain}/.well-known/openpgpkey/hu/{hash32}?l={local}'.format(
    domain = domain_part, local = local_part, hash32 = hashed_fingerprint
)

dest_file = '{}.asc'.format(email)
attempt_download(first_potential, dest_file, verbose)
attempt_download(second_potential, dest_file, verbose)

failure_msg = 'unable to locate public key for {target}'.format(target = email)

# failure_msg = '''
# unable to locate public key for {target}
# urls:
#   1. {url1}
#   2. {url2}
# '''.format(
#       target = email,
#       url1 = first_potential,
#       url2 = second_potential
# )

if verbose:
    print(failure_msg)
exit(1)
