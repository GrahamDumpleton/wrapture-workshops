---
title: Finish
requires: [quiz:where-the-500-is]
---

# Finish

The request became something a test can hold:

- `wrapture.instrumentation("flask")` applied the same
  instrumentation the config named, for the scope of a fixture, with
  the application built inside it.

- The request event carried the status as its `result`, the HTTP
  details and the matched route in `data`, the chunks and bytes of a
  streamed body, and the exception behind a 500 under `caught`.

- An ignored path left nothing on the tape, the view included.

- A binding with `mode="wsgi"` on the application's `wsgi_app`
  answered from the boundary, raised at it, and rewrote a status on
  the way out, with the event saying what the client really saw.

```{quiz}
:id: where-the-500-is
:title: Where the failure is
:shuffle: true
question: "A view raises KeyError and Flask answers 500. On the request event recorded by the instrumentation, where is the KeyError?"
options:
  - { text: "Under caught, as a note made from Flask's exception handler; exception is None because the application returned normally", correct: true }
  - { text: "On exception, because the middleware saw the view raise", explanation: "Flask catches the exception around the dispatch and returns the 500 response, so the middleware sees the application return normally." }
  - { text: "Nowhere on the request; only the view's own event records it", explanation: "The view's event does carry the KeyError as its escaping exception, and the instrumentation also notes it against the request from the handler, so both say it." }
  - { text: "In data under a status key", explanation: "The status line is the event's result, not a data key, and the exception is a note, not part of the status." }
explanation: The only code that can see the exception after Flask catches it is the handler, so the instrumentation binds the handler and notes the exception against the enclosing request event. raising() matches a noted exception as it matches an escaping one.
```

The Finish button below says where to go next.
