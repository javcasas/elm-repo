"""
elm-repo: utility to manage libraries coming from
local or remote git repositories,
instead of from the original blessed repository.

Usage:
  * Modify your elm-package.json
    * Add your repository dependencies to dependencies.
      Usual format: "{user}/{package}": "min_version <= v < max_version"
    * Create a new key: "repo-dependencies".
      Fill it with your repository dependencies. The format for each one is:
        "{user}/{package}": "{url or path to git repo}@{git tag or branch}"
  * Run python elm-repo.py on your project dir.

Here is my example tweaked elm-package.json:

{
    "version": "1.0.0",
    "summary": "helpful summary of your project, less than 80 characters",
    "repository": "https://github.com/user/project.git",
    "license": "BSD3",
    "source-directories": [
        "."
    ],
    "exposed-modules": [],
    "dependencies": {
        "elm-lang/core": "3.0.0 <= v < 4.0.0",
        "evancz/elm-html": "3.0.0 <= v < 5.0.0",
        "javcasas/elm-decimal": "1.0.0 <= v < 2.0.0"
    },
    "repo-dependencies": {
        "javcasas/elm-decimal": "/home/javier/proyectos/elm/elm-decimal/.git@1.0.0"
    },
    "elm-version": "0.16.0 <= v < 0.17.0"
}
"""

import os
import subprocess
import json


def system(cmd, ignore_errors=False):
    res = os.system(cmd)
    if ignore_errors:
        return
    elif res != 0:
        raise Exception("Error happened when doing {}".format(cmd))


def chdir_to_root():
    while os.getcwd() != "/":
        try:
            with open("elm-package.json"):
                return
        except IOError:
            os.chdir("..")
    raise Exception("Can't find elm-package.json")


def read_config():
    with open("elm-package.json") as f:
        elm_package = f.read()
    config = json.loads(elm_package)
    return config


def make_directories():
    repos_dir = os.path.join("elm-repos")
    if not os.path.exists(repos_dir):
        os.makedirs(repos_dir)


def get_repo(repo_name, repo_url):
    creator, name = repo_name.split("/")
    full_dir = os.path.join("elm-repos", creator, name)
    try:
        repo_url, repo_version = repo_url.split("@")
    except:
        repo_version = "master"
    try:
        os.makedirs(full_dir)
    except OSError:
        pass
    if not os.path.exists(os.path.join(full_dir, ".git")):
        system("git clone {url} {dir}".format(url=repo_url, dir=full_dir))

    system("cd {dir} && git remote add origin {url}".format(dir=full_dir, url=repo_url), ignore_errors=True)
    system("cd {dir} && git fetch".format(dir=full_dir))
    system("cd {dir} && git checkout {version}".format(dir=full_dir, version=repo_version))


def get_repo_config(repo_name):
    creator, name = repo_name.split("/")
    full_dir = os.path.join("elm-repos", creator, name)
    with open(os.path.join(full_dir, "elm-package.json")) as f:
        elm_package = f.read()
    return json.loads(elm_package)


def get_repo_version(repo_name):
    config = get_repo_config(repo_name)
    return config['version']


def reset_packages_symlink(repo_name):
    creator, name = repo_name.split("/")
    full_dir = os.path.join("elm-stuff", "packages", creator, name)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)
    else:
        for fn in os.listdir(full_dir):
            os.remove(os.path.join(full_dir, fn))
    version = get_repo_version(repo_name)
    repo_dir = os.path.join(os.getcwd(), "elm-repos", creator, name)
    os.symlink(repo_dir, os.path.join(full_dir, version))


def build_package(repo_name):
    creator, name = repo_name.split("/")
    version = get_repo_version(repo_name)
    full_dir = os.path.join("elm-stuff", "packages", creator, name, version)
    system("cd {dir} && elm-make --yes".format(dir=full_dir))


def get_lang_version():
    out = subprocess.check_output("elm-make --help", shell=True)
    line = out.splitlines()[0]
    parts = line.split("(")[1].split(")")[0]
    elm, platform, version = parts.split()
    if elm == "Elm" and platform == "Platform":
        return version
    else:
        raise Exception("Unknown Elm version: {}".format(line))


def reset_build_artifacts_symlink(repo_name):
    creator, name = repo_name.split("/")
    full_dir = os.path.join("elm-stuff", "build-artifacts", get_lang_version(), creator)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)
    else:
        for fn in os.listdir(full_dir):
            os.remove(os.path.join(full_dir, fn))
    repo_dir = os.path.join(os.getcwd(), "elm-repos", creator, name, "elm-stuff", "build-artifacts", get_lang_version(), creator, name)
    os.symlink(repo_dir, os.path.join(full_dir, name))


def update_exact_dependencies(repo_name):
    creator, name = repo_name.split("/")
    version = get_repo_version(repo_name)
    with open(os.path.join("elm-stuff", "exact-dependencies.json")) as f:
        current_exact_dependencies = json.loads(f.read())

    current_exact_dependencies[repo_name] = version
    with open(os.path.join("elm-stuff", "exact-dependencies.json"), "w") as f:
        f.write(json.dumps(current_exact_dependencies, indent=4))


def remove_repo_dependencies():
    system("cp elm-package.json elm-package.json.bak")
    config = read_config()
    for k in config['repo-dependencies'].keys():
        del config['dependencies'][k]
    with open("elm-package.json", "w") as f:
        f.write(json.dumps(config))


def reset_repo_dependencies():
    system("mv elm-package.json.bak elm-package.json")


def main():
    chdir_to_root()
    config = read_config()
    make_directories()
    for k, v in config['repo-dependencies'].iteritems():
        get_repo(k, v)
        reset_packages_symlink(k)
        build_package(k)
        reset_build_artifacts_symlink(k)
    try:
        remove_repo_dependencies()
        system("elm-make --yes")
    finally:
        reset_repo_dependencies()

    for k, v in config['repo-dependencies'].iteritems():
        update_exact_dependencies(k)

if __name__ == "__main__":
    print "elm-make version 0.0.1"
    main()
