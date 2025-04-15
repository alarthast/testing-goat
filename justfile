export VIRTUAL_ENV  := env_var_or_default("VIRTUAL_ENV", ".venv")

export BIN := VIRTUAL_ENV + if os_family() == "unix" { "/bin" } else { "/Scripts" }
export PIP := BIN + if os_family() == "unix" { "/python -m pip" } else { "/python.exe -m pip" }

export DEFAULT_PYTHON := if os_family() == "unix" { `cat .python-version` } else { "python" }

set dotenv-load := true

# list available commands
default:
    @"{{ just_executable() }}" --list


# clean up temporary files
clean:
    rm -rf .venv


# ensure valid virtualenv
virtualenv *args:
    #!/usr/bin/env bash
    set -euo pipefail

    # Allow users to specify python version in .env
    PYTHON_VERSION=${PYTHON_VERSION:-$DEFAULT_PYTHON}

    # Create venv; installs `uv`-managed python if python interpreter not found
    test -d $VIRTUAL_ENV || uv venv --python $PYTHON_VERSION {{ args }}

    # Block accidentally usage of system pip by placing an executable at .venv/bin/pip
    echo 'echo "pip is not installed: use uv pip for a pip-like interface."' > .venv/bin/pip
    chmod +x .venv/bin/pip


_uv *args: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    UV_EXCLUDE_NEWER=${UV_EXCLUDE_NEWER:-}

    if [ -z "$UV_EXCLUDE_NEWER" ]; then
        # Set UV_EXCLUDE_NEWER to existing lockfile timestamp cutoff
        # If there is no timestamp, use 7 days ago
        TIMESTAMP=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2) || TIMESTAMP=$(date -d '-7 days' +"%Y-%m-%dT%H:%M:%SZ")
        export UV_EXCLUDE_NEWER=$TIMESTAMP
    fi

    uv {{ args }} || exit 1

# wrap `uv lock`: update `uv.lock` if dependencies in `pyproject.toml` have changed
lock *args: virtualenv (_uv "lock " + args)

# wrap `uv sync`
sync *args: virtualenv (_uv "sync " + args)

# wrap `uv add`
add args: virtualenv (_uv "add " + args)

# wrap `uv remove`
remove args: virtualenv (_uv "remove " + args)

# Install prod dependencies into environment
prodenv: lock
    #!/usr/bin/env bash
    set -euo pipefail

    uv sync --frozen --no-dev


# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#
# ensure dev requirements installed and up to date
devenv: lock && install-precommit
    #!/usr/bin/env bash
    set -euo pipefail

    uv sync --frozen


# ensure precommit is installed
install-precommit:
    #!/usr/bin/env bash
    set -euo pipefail

    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || $BIN/pre-commit install


# upgrade dependencies (specify package to upgrade single package, all by default)
# when resolving dependencies, exclude releases newer than `UV_EXCLUDE_NEWER` (default: 7 days ago)
upgrade package="": virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    UV_EXCLUDE_NEWER=${UV_EXCLUDE_NEWER:-$(date -d '-7 days' +"%Y-%m-%dT%H:%M:%SZ")}
    touch -d "$UV_EXCLUDE_NEWER" $VIRTUAL_ENV/.target

    LOCKFILE_TIMESTAMP=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2) || LOCKFILE_TIMESTAMP=""
    if [ -z $LOCKFILE_TIMESTAMP ]; then
        echo "Lockfile will be ignored due to no existing timestamp."
        echo "To respect the lockfile, do not run this recipe; directly run uv sync with UV_EXCLUDE_NEWER unset."
    else
        touch -d "$LOCKFILE_TIMESTAMP" $VIRTUAL_ENV/.existing

        if [ $VIRTUAL_ENV/.existing -nt $VIRTUAL_ENV/.target ]; then
            echo "The lockfile timestamp is newer than the target cutoff. Using the lockfile timestamp."
            UV_EXCLUDE_NEWER=$(grep -n exclude-newer uv.lock | cut -d'=' -f2 | cut -d'"' -f2)
        else
            # Write the new timestamp to the lockfile, or else `uv` will disregard it
            sed -i "s|^exclude-newer = .*|exclude-newer = \"$UV_EXCLUDE_NEWER\"|" uv.lock
        fi
    fi

    echo "UV_EXCLUDE_NEWER set to $UV_EXCLUDE_NEWER."

    opts="--upgrade"
    test -z "{{ package }}" || opts="--upgrade-package {{ package }}"
    uv sync --exclude-newer $UV_EXCLUDE_NEWER $opts

# update (upgrade) prod and dev dependencies
update-dependencies: upgrade


# *args is variadic, 0 or more. This allows us to do `just test -k match`, for example.
# Run the tests
test *args="src": devenv
    $BIN/python src/manage.py test {{ args }}

test-docker *args="src": devenv # Paired with run-docker
    TEST_SERVER=localhost:8888 python src/manage.py test {{ args }}

test-staging *args="src": devenv
    TEST_SERVER="goatstaging.${SERVER_URL}" python src/manage.py test {{ args }}

test-js : devenv
    firefox src/lists/static/tests/SpecRunner.html

format *args=".": devenv
    $BIN/ruff format --check {{ args }}

lint *args=".": devenv
    $BIN/ruff check {{ args }}

# run the various dev checks but does not change any files
check: (_uv "lock --check") format lint
    #!/usr/bin/env bash
    docker run --rm -i ghcr.io/hadolint/hadolint:v2.12.0-alpine < Dockerfile


# fix formatting and import sort ordering
fix: devenv
    $BIN/ruff check --fix .
    $BIN/ruff format .


# Run the dev project
run: devenv
    python src/manage.py runserver

run-docker: devenv
    docker build -t superlists . && docker run \
        -p 8888:8888 \
        --mount type=bind,source="$PWD/src/db.sqlite3",target=/src/db.sqlite3 \
        -e DJANGO_SECRET_KEY=sekrit \
        -e DJANGO_ALLOWED_HOST=localhost \
        -e FROM_EMAIL \
        -e EMAIL_USER \
        -e EMAIL_PASSWORD \
        -it superlists

# Remove built assets and collected static files
assets-clean:
    rm -rf assets/dist
    rm -rf staticfiles


# Install the Node.js dependencies
assets-install:
    #!/usr/bin/env bash
    set -euo pipefail

    # exit if lock file has not changed since we installed them. -nt == "newer than",
    # but we negate with || to avoid error exit code
    test package-lock.json -nt node_modules/.written || exit 0

    npm ci
    touch node_modules/.written


# Build the Node.js assets
assets-build:
    #!/usr/bin/env bash
    set -euo pipefail

    # find files which are newer than dist/.written in the src directory. grep
    # will exit with 1 if there are no files in the result.  We negate this
    # with || to avoid error exit code
    # we wrap the find in an if in case dist/.written is missing so we don't
    # trigger a failure prematurely
    if test -f assets/dist/.written; then
        find assets/src -type f -newer assets/dist/.written | grep -q . || exit 0
    fi

    npm run build
    touch assets/dist/.written


assets: assets-install assets-build


assets-rebuild: assets-clean assets
