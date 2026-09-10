"""Instrument urllib, entirely under the covers.

A stand-in for what a wrapture-instrumentation-urllib package would
ship: one Instrumentation subclass, triggered by the import of
urllib.request, that binds the opener's choke point so every outbound
request both records as a client-side call and carries the current
trace identity onward in its headers.

The whole public surface it needs is a binding with a transforms_args
stage and wrapture.trace_headers(), which returns the headers the
current tree's identity should travel as, whatever minted or parsed
it, and returns nothing when nothing is being recorded, so injection
is always safe to attempt.
"""

import wrapture


class UrllibInstrumentation(wrapture.Instrumentation):
    """Outbound request recording and trace propagation for urllib."""

    target = "urllib"
    removable = True

    @wrapture.instrumentation_hook("urllib.request")
    def request(self, name, module):
        def inject(args, kwargs):
            if not args:
                return args, kwargs

            # OpenerDirector.open takes a URL string or a Request; the
            # headers need a Request to land on.

            target = args[0]
            if isinstance(target, str):
                target = module.Request(target)

            if isinstance(target, module.Request):
                for header, value in wrapture.trace_headers().items():
                    target.add_unredirected_header(header.title(), value)

            return (target, *args[1:]), kwargs

        opener = wrapture.binding(module.OpenerDirector, "open", label="urllib.open")
        opener.on_call.transforms_args(inject)
        opener.apply()

        self.on_cleanup(opener.remove)
