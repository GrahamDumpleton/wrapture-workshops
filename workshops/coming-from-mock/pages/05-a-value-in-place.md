---
title: A value in place
requires: [verify:value-binding]
---

# A value in place

Not every patch is a call. `patch.dict(os.environ, {...})` and
`monkeypatch.setenv()` put a value somewhere for the duration of a
test, and the two currency tests do the same thing with each. wrapture
spells both as a value binding: name the owner, name the slot with
`item=` or `attr=`, and say what it holds. The with-block form
replaces the first test; the decorator form, the direct counterpart
of `@patch.dict`, replaces the second, and injects the slot under its
own name.

```{editor-replace}
:id: convert-patch-dict
:path: test_shop.py
:regex: true
:match: ^def test_currency_with_patch_dict\(.*\n(?:    .*\n)+
def test_currency_with_value_binding():
    with wrapture.binding(os.environ, item="SHOP_CURRENCY").overrides("EUR"):
        assert Gateway().charge(500, CARD)["currency"] == "EUR"

```

```{editor-replace}
:id: convert-setenv
:path: test_shop.py
:regex: true
:match: ^def test_currency_with_monkeypatch\(.*\n(?:    .*\n)+
@wrapture.bound(os.environ, item="SHOP_CURRENCY").overrides("EUR")
def test_currency_with_decorator(SHOP_CURRENCY):
    assert Gateway().charge(500, CARD)["currency"] == "EUR"

```

```{execute}
:id: run-value-binding
:session: shell
:wait: prompt
pytest -q test_shop.py
```

The mechanics are the same as `patch.dict`: the owner is changed in
place and restored on exit. What a value binding adds is the binding
lifecycle. It is a context manager, it can be suspended and resumed,
it goes in a group with everything else the test patches, and the
pytest plugin's leak sweep reports one left applied. `hides()` is
`delenv`, and a whole settings dict is a mapping binding, with
`updates()` merging entries and `overrides()` replacing them, the one
dict changed in place so every holder sees it.

```{verify}
:id: value-binding
:label: The two currency tests are converted and the suite is green
:substrate: shell
:trigger: after:run-value-binding; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && ! grep -q -E '^def (test_currency_with_patch_dict|test_currency_with_monkeypatch)\(' test_shop.py && [ "$(grep -c -E '^def (test_currency_with_value_binding|test_currency_with_decorator)\(' test_shop.py)" = "2" ] && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def (test_currency_with_patch_dict|test_currency_with_monkeypatch|test_currency_with_value_binding|test_currency_with_decorator)\(' test_shop.py | sed 's/^/still in the file: /'; exit 1
```
