# Your first binding

A guided JupyterLab workshop, the first in the
[wrapture workshops](https://github.com/GrahamDumpleton/wrapture-workshops)
collection. In about ten minutes you create a
[wrapture](https://github.com/GrahamDumpleton/wrapture) binding on a
method, see that nothing is patched until you say so, apply it, suspend
and resume it, remove it, scope it to a block, and change one thing
about a call while the real method keeps running.

wrapture is installed into a virtual environment of the workshop's own,
under `_workshop/venv` inside this directory, when the workshop opens.
Nothing is installed anywhere else.

## Run it

Start JupyterLab from the directory holding the `workshops` directory,
with the jupyterlab-workshop extension installed, and open this
workshop from the workshop browser, or go straight to it:

```
http://localhost:8888/lab?workshop=workshops/first-binding
```

## Check it

From the repository root:

```
just lint first-binding
just test first-binding
```
