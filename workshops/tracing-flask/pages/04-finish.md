---
title: Finish
requires: [quiz:noted]
---

# Finish

The application never changed and the config never named it. One
entry, and every request the process served became one tree.

- A request event's result is its status line, its duration is time to
  last byte, and the method, path, query, route and endpoint sit in
  its data, so every filter and assertion that works on a call works
  on a request.

- The view sits beneath the request labelled by its endpoint, and the
  shop's own bindings nest beneath the view because they fire while
  the request is in flight.

- A view's exception is caught by Flask, so the request completes with
  a 500 and no exception; the instrumentation notes it against the
  request from the one place it can be seen.

- `ignore_paths` declines an ignored request and everything beneath
  it, so a health check leaves nothing on the trace, not even its
  view.

```{quiz}
:id: noted
:title: Two scopes, one failure
:shuffle: true
question: "The request line for /quote/missing read 500 INTERNAL SERVER ERROR !! KeyError. Where did the KeyError on the request line come from, given that the WSGI application returned normally?"
options:
  - { text: "A binding on Flask's handle_exception noted it against the enclosing request event with current_event(kind=\"request\").note_exception()", correct: true }
  - { text: "The middleware re-raised the exception after recording the 500, which is why the client saw an error page", explanation: "The client saw Flask's own 500 page, built by handle_exception. The middleware saw the application return a response and raised nothing." }
  - { text: "The view's event is the request's event, so its exception shows on both lines", explanation: "They are two events: the view's, which the exception escaped, and the request's, which completed with a status. Each carries the KeyError for its own reason." }
  - { text: "Flask propagates unhandled exceptions to the server when running under the runner", explanation: "The runner changes nothing about how Flask handles errors. It applied the config, and the instrumentation's binding on the error handler did the noting." }
explanation: Flask catches the view's exception and hands it to handle_exception, which builds the 500 and returns normally, so the request event closes with a status and no exception. The instrumentation binds that handler and notes the exception it receives against the nearest enclosing request event, so the request says both that it answered 500 and why.
```

The Finish button below says where to go next.
