# Beyond callables

A guided workshop for JupyterLab, built with jupyterlab-workshop.

## Try it

Install the extension alongside JupyterLab in a virtual environment,
start JupyterLab from the directory holding this one, and open it as a
workshop:

```
uv add jupyterlab jupyterlab-workshop
uv run jupyter lab
```

(or `pip install jupyterlab jupyterlab-workshop` and `jupyter lab`).

Then use "Open Workshop…" in the Workshop panel, or right-click this
directory in the file browser and choose "Open as Workshop".

## Layout

`workshop.yaml` and `pages/` are the workshop. Starter files for the
learner go in `files/`; they are copied into `work/`, the workspace,
when the workshop opens, and that is where the learner's files land.
`work/` is generated, so it is not committed.

## Check it

```
jupyter workshop lint .
jupyter workshop test .
```

`lint` needs Node.js on the path. `test` needs the `test` extra, which
installs Playwright, and a browser for it: `uv add
"jupyterlab-workshop[test]"` (or `pip install` the same) and then
`playwright install chromium`.

Workshop name: `beyond-callables`.
