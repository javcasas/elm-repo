import os
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

def reset_symlinks(repo_name):
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
    

def main():
    chdir_to_root()
    config = read_config()
    make_directories()
    for k, v in config['repo-dependencies'].iteritems():
        get_repo(k, v)
        reset_symlinks(k)

if __name__ == "__main__":
    main()
