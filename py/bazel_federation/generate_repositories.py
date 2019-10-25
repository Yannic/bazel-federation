from bazel_federation.dependencies import dependencies

_header = '''
# Generated by `@bazel_federation//py/bazel_federation:generate_repositories`.
# DO NOT EDIT.

"""Defines load functions for all repositories that are part of the federation.

WARNING: The following definitions are placeholders since none of the projects
have been tested at the versions listed in this file.
Please do not use them (yet). Future commits to this file will set the proper
versions and ensure that all dependencies are correct.
"""

load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")
'''

print(_header)

deps = {}

n = len(dependencies)

# TODO(yannic): This should emit code that `buildifier` is happy with.

for key in sorted(dependencies):
    dependency = dependencies[key]
    if dependency["type"] == "load":
        load = dependency["load"]
        print("load('{}', _declare_{} = '{}')".format(load["label"], key,
                                                      load["symbol"]))
    else:
        print('def _declare_{}():'.format(key))
        print('    """Loads `@{}` if it does not exist.'.format(key))
        print('')
        print('    Unlike `{}()`, this function does not load'.format(key) +
              ' any (transitive) dependencies."""')
        if dependency["type"] == "bind":
            # TODO(yannic): Should binds be declared with `maybe`?
            print('    native.bind(name = "{}", actual = "{}")'.format(
                key, dependency["bind"]))
        elif dependency["type"] == "forward":
            # TODO(yannic): Don't emit calls to `_declare_foo()` if `foo` is of type "forward".
            print(
                '    # `{}` is of type "forward" and does not declare a repository.'
                .format(key))
            print('    pass')
        elif dependency["type"] == "http_archive":
            http_archive = dependency["http_archive"]
            print('    maybe(http_archive,')
            print("        name = '{}',".format(key))
            print("        sha256 = '{}',".format(http_archive['sha256']))
            print('        urls = [')
            for url in http_archive["urls"]:
                print('            "{}",'.format(url))
            print('        ],')
            if 'strip_prefix' in http_archive:
                print("        strip_prefix = '{}',".format(
                    http_archive['strip_prefix']))
            print('    )')
        elif dependency["type"] == "git_repository":
            git_repository = dependency["git_repository"]
            print('    maybe(git_repository,')
            print("        name = '{}',".format(key))
            print("        remote = '{}',".format(git_repository['remote']))
            print("        commit = '{}',".format(git_repository['commit']))
            print('    )')

    d = {}
    queue = [key]
    while len(queue):
        repo = queue.pop()
        d[repo] = True

        for dep in dependencies[repo]["dependencies"]:
            if not dep in d:
                queue.append(dep)

    deps[key] = [repo for repo in d if repo != key]

for key in sorted(deps):
    print("def {}():".format(key))
    print('    """Loads `@{}` and all of its dependencies."""'.format(key))
    print("    _declare_{}()".format(key))
    print("    {}_deps()".format(key))

    print("def {}_deps():".format(key))
    print('    """Loads all dependencies of `@{}`.'.format(key))
    print('')
    print('    Note: This function loads only the dependencies of ' +
          '`@{}`, the repository itself is not loaded.'.format(key))
    print('    Most users should use `{}()` instead of calling '.format(key) +
          'this directly."""')
    rules_deps = sorted(deps[key])
    if len(rules_deps):
        for dep in sorted(deps[key]):
            print("    _declare_{name}()".format(name=dep))
    else:
        print("    pass # No dependencies")
