# Welcome to the wrapture workshops

These are guided, hands-on workshops for wrapture, the Python library
for attaching bindings to arbitrary call sites without modifying the
code being observed. Each one takes one thing you might want to do
with wrapture and walks you through doing it, in JupyterLab, with the
workshop checking your work as you go. The workshop browser lists them
in the order to take them; open the first, and the Finish dialog at the
end of each offers the next. A workshop installs wrapture for itself
when it opens, so the first page can take a moment to appear.

This session runs in a GitHub codespace, which opens in VS Code in the
browser. JupyterLab starts in the background, which takes a minute or
so the first time, and VS Code then shows a notification that the
application on port 8888 is available. Click its Open in Browser button
to open JupyterLab in a new tab. If the notification has gone, open the
Ports panel in VS Code and open the address of the port labelled
JupyterLab. Some workshops start small web services of their own on
other ports; you do not need to open those in the browser, since the
workshop's commands reach them from inside the codespace.

Leave the JupyterLab port's visibility as Private. JupyterLab here asks
for no password or token, because a private port can only be reached by
you, signed in to GitHub. Making the port public, or visible to an
organization, would let anyone who has its address run commands in
your codespace, including with the GitHub token the codespace holds for
your account.

The codespace belongs to your GitHub account and uses your monthly
Codespaces allowance while it runs. It is not temporary: your work is
kept when you close the tabs, and the codespace stops by itself after a
period of inactivity. You can resume it later from
[github.com/codespaces](https://github.com/codespaces), and JupyterLab
starts again with it. When you have finished with the workshops, delete
the codespace there too, so it no longer uses your storage allowance.
