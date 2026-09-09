# Guided JupyterLab workshops for wrapture. Run `just` to list targets.

collection_title := "wrapture workshops"
collection_description := "Guided JupyterLab workshops that teach wrapture: wrapping call sites without changing the code being observed, for monkey patching, testing and tracing."
collection_repo := "https://github.com/GrahamDumpleton/wrapture-workshops"

# List available targets.
default:
    @just --list

# Set up the environment: sync uv, fetch the reference checkouts, download the self-test browser, link the authoring skill.
install:
    uv sync
    git submodule update --init
    uv run playwright install chromium
    just skill

# The skill ships inside the jupyterlab-workshop package. Linking it into
# .claude/skills lets Claude Code load it without a copy in this repository,
# and it tracks the pinned release; rerun after bumping the version.
# Link the authoring skill from the installed package into .claude/skills.
skill:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(uv run python -c 'import jupyterlab_workshop, pathlib; print(pathlib.Path(jupyterlab_workshop.__file__).parent / "skills" / "jupyterlab-workshop-authoring")')
    mkdir -p .claude/skills
    ln -sfn "$target" .claude/skills/jupyterlab-workshop-authoring
    echo "Linked .claude/skills/jupyterlab-workshop-authoring -> $target"

# JupyterLab must run from this directory: the extension lists workshops/
# as installed, and the MCP live tools open workshops by paths relative
# to this root, such as workshops/<name>.
# Start JupyterLab from the checkout with the workshops listed as installed.
lab *ARGS:
    uv run jupyter lab {{ARGS}}

# Scaffold a new workshop under workshops/; extra args go to `jupyter workshop init`.
new NAME *ARGS:
    uv run jupyter workshop init workshops/{{NAME}} {{ARGS}}

# Lint collection.json and every workshop, or only the workshops named.
lint *NAMES:
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    names=({{NAMES}})
    if [ ${#names[@]} -eq 0 ]; then
        if [ -f collection.json ]; then
            uv run jupyter workshop lint collection.json
        fi
        dirs=(workshops/*/)
    else
        dirs=("${names[@]/#/workshops/}")
    fi
    if [ ${#dirs[@]} -eq 0 ]; then
        echo "No workshops under workshops/ yet"
        exit 0
    fi
    for dir in "${dirs[@]}"; do
        echo "== $dir"
        uv run jupyter workshop lint "$dir"
    done

# Render one workshop as HTML to check what a page looks like; extra args go to `jupyter workshop render`.
render NAME *ARGS:
    uv run jupyter workshop render workshops/{{NAME}} {{ARGS}}

# The self-test runs the workshop's commands and checks for real, as you,
# on this machine; only the workshop directory is protected, by a
# temporary copy. Read the workshop first.
# JUPYTERLAB_WORKSPACES_DIR keeps the test server out of the user's
# shared JupyterLab workspace, whose restored tabs from other sessions
# can block a run (jupyterlab-workshop 0.1.16 does not isolate it yet).
# Self-test one workshop in a JupyterLab of its own; extra args go to `jupyter workshop test`.
test NAME *ARGS:
    JUPYTERLAB_WORKSPACES_DIR="$(mktemp -d)" uv run jupyter workshop test workshops/{{NAME}} {{ARGS}}

# Self-test every workshop, writing a JUnit report for each.
test-all:
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    for dir in workshops/*/; do
        name=$(basename "$dir")
        echo "== $dir"
        JUPYTERLAB_WORKSPACES_DIR="$(mktemp -d)" uv run jupyter workshop test "$dir" --junit "results-$name.xml"
    done

# The repository URL is given explicitly so the index does not depend on
# a git remote being configured in the checkout.
# Write or refresh collection.json, the index the workshop browser reads.
index:
    uv run jupyter workshop index workshops --title "{{collection_title}}" --description "{{collection_description}}" --repo "{{collection_repo}}" --ordered

# Binder installs from binder/requirements.txt, so it is the locked
# runtime set (no dev group) exported from uv.lock, and is regenerated
# whenever the lock changes.
# Relock and export the runtime dependencies to binder/requirements.txt.
requirements:
    uv lock
    uv export --no-dev --no-hashes --no-annotate -o binder/requirements.txt

# The extension's reference checkout is what agents read for the workshop
# format beyond the skill (docs/, examples/ and the source), so it is
# kept at the tag of the pinned release and moves with the pin.
# Pin a new jupyterlab-workshop release, relock, export, relink the skill and move the reference checkout.
bump VERSION:
    uv add "jupyterlab-workshop=={{VERSION}}"
    just requirements
    just skill
    git -C reference/jupyterlab-workshop fetch --tags
    git -C reference/jupyterlab-workshop checkout "{{VERSION}}"
    git add reference/jupyterlab-workshop

# The reference checkout is what agents read for wrapture's API and
# documentation, so it is kept at the tag of the release the workshops
# teach; the workshops' own requirements name that version too.
# Move the wrapture reference checkout to a release tag, e.g. `just bump-wrapture 1.0.0a22`.
bump-wrapture VERSION:
    git -C reference/wrapture fetch --tags
    git -C reference/wrapture checkout "{{VERSION}}"
    git add reference/wrapture
    @echo "reference/wrapture is at {{VERSION}}; update the wrapture version in each workshop's requirements to match"

# Remove what opening, running and publishing the workshops leaves behind.
clean:
    rm -rf workshops/*/_workshop workshops/*/work workshops/*/dist workshops/*/scratch
    rm -f results-*.xml
    find . -type d -name .ipynb_checkpoints -not -path "./.venv/*" -exec rm -rf {} +
    find . -type d -name __pycache__ -not -path "./.venv/*" -not -path "./scratch/*" -exec rm -rf {} +

# Also remove the environment and the skill link; run `just install` afterwards.
distclean: clean
    rm -rf .venv .claude/skills/jupyterlab-workshop-authoring
    git submodule deinit -f reference/wrapture reference/jupyterlab-workshop
