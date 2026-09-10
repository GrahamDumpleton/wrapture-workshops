---
title: What to leave as mock
requires: [verify:one-left]
---

# What to leave as mock

One test is left, and it stays as it is. The notifier delivers through
a transport it is handed, and the test hands it a bare `Mock()`: an
object with no class behind it, whose `deliver` method exists because
the test touched it. Everything on the earlier pages followed one rule
with one opt-out. The rule: wrap the real code, strictly, and record
what actually flowed. The opt-out: when the test itself must supply
the thing being called, `stub()` supplies one callable and
`mock(Spec)` one collaborator, still strict and still recorded.

What wrapture deliberately does not provide is the spec-less form: a
`Mock` or `MagicMock` whose attributes exist on first touch and whose
call chains all answer. A fabricated object that answers everything
verifies nothing; the misspelled method, the drifted signature and the
unconfigured chain all pass silently. A test that cannot name the
class it is substituting has a question to answer before it has a
double to build, and until this shop has a transport class to name,
`unittest.mock` is the right tool for that test.

That leaves `unittest.mock` two genuine holds: it is in the standard
library, and it is the tool for fabrication without a spec. The two
libraries coexist happily in one suite. Tidy the imports to what the
file still uses and run it one last time.

```{editor-replace}
:id: trim-imports
:path: test_shop.py
:regex: true
:match: ^import logging\nimport os\nfrom unittest\.mock import DEFAULT, Mock, call, patch\n
import os
from unittest.mock import Mock

```

```{execute}
:id: run-one-left
:session: shell
:wait: prompt
pytest -q test_shop.py
```

Ten pass, nine with wrapture and one with mock, and the file imports
only `Mock`.

```{verify}
:id: one-left
:label: One mock test remains, the imports are trimmed, and the suite is green
:substrate: shell
:trigger: after:run-one-left; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && [ "$(grep -c -E '^def test_.*_with_(mock|caplog|patch_dict|monkeypatch)\(' test_shop.py)" = "1" ] && grep -q '^from unittest.mock import Mock$' test_shop.py && ! grep -q '^import logging$' test_shop.py && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def test_.*_with_(mock|caplog|patch_dict|monkeypatch)\(|^import logging|^from unittest' test_shop.py | sed 's/^/in the file: /'; exit 1
```

```{hint}
:title: If the check fails
The check expects ten passes, exactly one test still named `_with_mock`
(the transport test), the import line `from unittest.mock import Mock`
and no `logging` import. A page whose replace found nothing leaves
its mock test in place; go back to it and check the test's name in
the file.
```
