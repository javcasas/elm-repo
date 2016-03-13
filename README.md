# elm-repo
Tool for managing libraries that doesn't come from the blessed elm sources.

## Usage

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
