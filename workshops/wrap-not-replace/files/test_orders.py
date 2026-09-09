"""Tests for the order service, written with unittest.mock.

The workshop adds the wrapture version of each test below it.
"""

from unittest.mock import MagicMock, patch

import pytest

from orders import Gateway, OrderService


def test_stub_with_mock():
    with patch.object(Gateway, "charge", return_value={"id": "stub", "amount": 0}):
        assert OrderService().place(500)["id"] == "stub"


def test_drifted_call_with_mock():
    with patch.object(Gateway, "charge", return_value={"id": "stub"}):
        assert Gateway().charge(500, bogus=True) == {"id": "stub"}


def test_self_call_with_mock():
    gateway = MagicMock()
    service = OrderService(gateway=gateway)
    service.place(500)
    gateway.charge.assert_called_once_with(500)


def test_error_path_with_mock():
    gateway = MagicMock()
    ledger = MagicMock()
    ledger.record.side_effect = OSError("disk full")
    notifier = MagicMock()

    service = OrderService(gateway, ledger, notifier)

    with pytest.raises(OSError):
        service.place(500)

    gateway.refund.assert_called_once_with(gateway.charge.return_value["id"])
    notifier.send.assert_not_called()
