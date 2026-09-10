# Configuration for JupyterLab started from this checkout. Jupyter does
# not look in the current directory for config files, so this one is
# named explicitly: `just lab` passes `--config=jupyter_lab_config.py`,
# and `uv run jupyter lab --config=jupyter_lab_config.py` does the same.
#
# Open the workshop browser with the checkout's own collection added for
# the session, so the workshops are listed in the order to take them,
# numbered, rather than the order the workshops directory gives. The
# collection is added for the session only; the browser offers Subscribe
# to keep it.
c.LabApp.default_url = "/lab?collection=collection.json"
