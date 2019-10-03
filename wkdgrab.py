#!/usr/bin/env python3

import functools
import hashlib
import itertools
import requests
import sys
import os
import subprocess
import re


class text_colors:
    SUCCESS = '\033[1;92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    NORMAL = '\033[0m'


def which(program):
    def is_executable_file(filepath):
        return os.path.isfile(filepath) and os.access(filepath, os.X_OK)

    filepath, filename = os.path.split(program)
    if filepath:
        if is_executable_file(program):
            return program
    else:
        for path in os.environ["PATH"].strip(os.pathsep).split(os.pathsep):
            potential = os.path.join(path, program)
            if is_executable_file(potential):
                return potential
    return None


def find_email(arglist):
    posix_option = re.compile('^-[a-zA-Z0-9]*$')
    gnu_option = re.compile('^-{2}[a-zA-Z0-9][-a-zA-Z0-9]*$')
    email, unexpected = None, []
    options = {
        'verbose': False,
        'autoimport': False,
        'gpg-executable': 'gpg'
    }
    i = 0
    while i < len(arglist):
        arg = arglist[i]
        if '@' in arg:
            email = arglist.pop(i)
        elif posix_option.fullmatch(arg):
            option = list(arg[1:])
            if 'x' in option:
                if len(arglist) > i+1 and option[-1] == 'x':
                    execpath = arglist.pop(i + 1)
                    absoluteloc = which(execpath)
                    if absoluteloc is None:
                        print('{color}error:{endcolor}'.format(color = text_colors.FAIL,
                                                            endcolor = text_colors.NORMAL), end=' ')
                        print('provided gpg executable {path} could not be found'.format(path = execpath))
                        exit(1)
                    else:
                        options['gpg-executable'] = absoluteloc
                        option.remove('x')
                else:
                    print('{color}error:{endcolor}'.format(color = text_colors.FAIL,
                                                           endcolor = text_colors.NORMAL), end=' ')
                    print('-{argument} must be followed by the name and/or path of your gpg executable'.format(
                        argument = 'x'))
                    exit(1)

            if 'v' in option:
                options['verbose'] = True
                option.remove('v')

            if 'i' in option:
                options['autoimport'] = True
                option.remove('v')

            if len(option) > 0:
                unexpected.append('-{}'.format(''.join(option)))
            i += 1
        elif gnu_option.fullmatch(arg):
            option = arg[1:]
            if option == '-verbose':
                options['verbose'] = True
            elif option == '-import':
                options['autoimport'] = True
            elif option == '-gpg-executable':
                if len(arglist) > i+1:
                    execpath = arglist.pop(i + 1)
                    absoluteloc = which(execpath)
                    if absoluteloc is None:
                        print('{color}error:{endcolor}'.format(color = text_colors.FAIL,
                                                            endcolor = text_colors.NORMAL), end=' ')
                        print('provided gpg executable {path} could not be found'.format(path = execpath))
                        exit(1)
                    else:
                        options['gpg-executable'] = absoluteloc
                else:
                    print('{color}error:{endcolor}'.format(color = text_colors.FAIL,
                                                           endcolor = text_colors.NORMAL), end=' ')
                    print('-{argument} must be followed by the name and/or path of your gpg executable'.format(
                        argument = arg))
                    exit(1)
            else:
                unexpected.append(arg)
            i += 1
        else:
            unexpected.append(arglist.pop(i))

    """
    display options set on cmd line & exit:
    options_set = [opt for opt, val in options.items()
                    if val == True or (type(val) is str and val != 'gpg')]
    print('email: {email}\n'
          'options: {options}'.format(
              email = email,
              options = ', '.join(options_set) if len(options_set) > 0 else 'none'))
    if options['gpg-executable'] != 'gpg':
        print('executable: {exc}'.format(exc = options['gpg-executable']))
    exit()
    """
    return (email, options, unexpected)


def attempt_download(url, key_filename, **kwargs):
    verbose = kwargs.get('verbose')
    if verbose:
        print('{target}\ntrying server...'.format(target = url), end=' ', flush=True)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(key_filename, 'wb') as out:
                out.write(r.content)
                if verbose: print('{style}success!{endstyle}\n'.format(
                    style=text_colors.SUCCESS,
                    endstyle=text_colors.NORMAL
                ), end='')
            on_success(url, key_filename, **kwargs)
        elif verbose:
            print('got response {status} {reason}'.format(
                target = url, status = r.status_code, reason = r.reason
            ))
    except requests.exceptions.Timeout as ex:
        if verbose:
            print('connection timed out'.format(target = url))
    except requests.exceptions.ConnectionError as ex:
        if verbose:
            moreinfo = ''
            match = re.match('^([A-Za-z]+://)?(([^/]+\.){2}[^/]+)(/.*)', url)
            if match is not None:
                server = match.groups()[1]
                if server is not None and server.strip() != '':
                    moreinfo = ' {}'.format(server)
            print('can\'t find dns records for server{}'.format(moreinfo))
    except requests.exceptions.RequestException as ex:
        if verbose:
            print('connection problem ({details})'.format(url = target, details = ex.msg))


def on_success(url, key_file, **kwargs):
    verbose = kwargs.get('verbose')
    autoimport = kwargs.get('autoimport')
    gpg = kwargs.get('gpg-executable')
    if gpg is None:
        gpg = 'gpg'
    if verbose:
        print('successfully retrieved public key from {source}'.format(source = url))
    print('saved public key to {filename}'.format(filename = key_file))
    if autoimport:
        import_key = True
    else:
        while True:
            user_response = input('import key in gpg? (yes/no) ').lower()
            if user_response in ['yes', 'no']:
                import_key = user_response == 'yes'
                break
            else:
                print('please respond `yes\' or `no\'')
    if import_key:
        command = [gpg, '--import', key_file]
        result = subprocess.call(command,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        if result == 0:
            print('successfully added key to your keychain')
            exit()
        else:
            print('error adding key to keychain (code {code}). try adding the\n'
                  'key manually by running:\n'
                  '    gpg --import {file}'.format(code = result, file = filename))
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

help_text = ['usage: {program} [-iv] [-x <gpg-path>] user@domain.com',
             '',
             'options:',
             '    -i --import            automatically import new keys without prompting',
             '    -v --verbose           print more information about progress and results',
             '    -x --gpg-executable    use the provided path or executable instead of the',
             '                           standard `gpg` (useful if gpg is named differently',
             '                           or is not in your $PATH)']

email, options, unexpected_args = find_email(sys.argv[1:])
if email is None:
    for line in help_text:
        print(line.format(program = os.path.basename(sys.argv[0])))
    exit()

if options.get('verbose') and len(unexpected_args) > 0:
    print('unrecognized {arguments}: {arglist}'.format(
        arguments = 'options' if len(unexpected_args) > 1 else 'option',
        arglist = ', '.join(unexpected_args)
    ))

local_part, domain_part = email.split('@')
hashed_fingerprint = local_zbase32(local_part)

first_potential = 'https://openpgpkey.{domain}/.well-known/openpgpkey/{domain}/hu/{hash32}?l={local}'.format(
    domain = domain_part, local = local_part, hash32 = hashed_fingerprint
)
second_potential = 'https://{domain}/.well-known/openpgpkey/hu/{hash32}?l={local}'.format(
    domain = domain_part, local = local_part, hash32 = hashed_fingerprint
)

dest_file = '{}.asc'.format(email)
attempt_download(first_potential, dest_file, **options)
attempt_download(second_potential, dest_file, **options)

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

if options.get('verbose'):
    print(failure_msg)
exit(1)
