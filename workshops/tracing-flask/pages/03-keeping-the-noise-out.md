---
title: Keeping the noise out
requires: [verify:server-up-again, verify:health-ignored]
---

# Keeping the noise out

Health checks and static assets make up most of the traffic on a lot
of services and none of the interest. On the previous page the probe
the panel sent to `/health` printed its own tree, and after a day of a
load balancer polling it that is most of the file. The instrumentation
takes a list of paths not to record.

```{editor-replace}
:id: add-ignore
:path: wrapture.toml
:match: name = "flask"
name = "flask"
ignore_paths = ["/health"]
```

Start the server again, with a fresh trace file so the check on this
page sees only what this page sends.

```{execute}
:id: restart-server
:session: shell
:title: Start the server again under the new config
:wait: 3s
rm -f trace.jsonl && python -m wrapture -m flask --app webshop run --port {{ server_port }}
```

```{verify}
:id: server-up-again
:label: The server answers on port {{ server_port }} again
:substrate: shell
:trigger: after:restart-server
curl -sf -o /dev/null http://127.0.0.1:{{ server_port }}/health && echo "The server answers on port {{ server_port }}"
```

This time the probe left only Flask's access log line behind. Send a
health check of your own from the terminal on the right, then a
quote, to see the difference side by side.

```{execute}
:id: curl-health
:session: client
:wait: prompt
curl http://127.0.0.1:{{ server_port }}/health
```

```{execute}
:id: curl-gadget
:session: client
:wait: prompt
curl http://127.0.0.1:{{ server_port }}/quote/gadget
```

```
127.0.0.1 - - [10/Sep/2026 14:51:43] "GET /health HTTP/1.1" 200 -
GET /quote/gadget (webshop.wsgi_app)
  quote(item='gadget')
    flask:render_template(template_name_or_list='quote.html', context='<context>')
    flask:render_template -> '<18 chars>' [1.5ms]
  quote -> '<p>gadget: 120</p>' [1.7ms]
webshop.wsgi_app -> '200 OK' [2.3ms, body 5us over 1 chunk]
```

A matching request runs and answers as normal but records nothing at
all, and the "at all" matters. Declining the request event alone would
leave the view, any lifecycle callbacks and any template render it
made on the trace as anonymous roots with no request above them, the
same problem `tree=True` solved on a plain binding two workshops ago.
The setting silences everything beneath an ignored request for its
whole extent.

The other switch worth knowing about is `lifecycle = false`. Flask
extensions register `before_request` and `after_request` callbacks
liberally, for loading users, cleaning up sessions and stamping
headers, and the instrumentation observes every one of them by default
in the order Flask runs them. For an application with several
extensions that is faithful but noisy, and switching it off leaves the
callbacks running unobserved.

There is no magic in the `[[instrument]]` entry. It names an
`Instrumentation` class whose hooks run when Flask is imported, and
those hooks apply bindings to three choke points in Flask, using the
same bindings as everywhere else. Constructing a `Flask` instance
installs the recording WSGI middleware on its `wsgi_app` attribute, so
every application the process creates is covered however it was made,
application factories included. Registering a route substitutes an
observed version of the view function, since Flask captures views into
its dispatch table the moment `@app.route` runs, before any binding on
the module could have seen them. And `handle_exception` gets the
binding that notes the failure against the request.

```{verify}
:id: health-ignored
:label: The health checks left nothing on the trace, and the quote did
:substrate: shell
:trigger: after:curl-gadget
out=$(.venv/bin/python -c "import wrapture; r = wrapture.load_events('trace.jsonl'); paths = [x['data']['path'] for x in r if x['kind'] == 'request']; assert '/quote/gadget' in paths, 'no request event for /quote/gadget yet: send it from the client terminal'; assert '/health' not in paths, f'a /health request was recorded: ignore_paths is missing from the instrument entry, or the server was not restarted (recorded: {paths})'; assert not any(x['path'] == 'webshop:health' for x in r), 'the health view was recorded as an orphan root, so the request was declined without its subtree'; print('Only the quote on the trace: the health checks recorded nothing, not even the view')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads the fresh `trace.jsonl` and expects a request event
for `/quote/gadget`, none for `/health`, and no `health` view event
either. A recorded `/health` means the server is still running the
old config, or the `ignore_paths` line did not land under
`name = "flask"`; stop the server with Ctrl-C and start it again.
```

Stop the server before finishing.

```{interrupt}
:id: stop-server-again
:session: shell
:title: Stop the server
```
