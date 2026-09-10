import logging
import os
from unittest.mock import DEFAULT, Mock, call, patch

import pytest

from shop import CardDeclined, Gateway, Ledger, Notifier, OrderService, place_with_retry

CARD = "4111-1111-1111-1111"
DECLINED = "4000-0000-0000-0000"


def test_stub_with_mock():
    with patch.object(Gateway, "charge", return_value={"id": "stub", "amount": 0}):
        assert OrderService().place(500, CARD, tenant="acme")["id"] == "stub"


def test_gateway_down_with_mock():
    with patch.object(Gateway, "charge", side_effect=TimeoutError("down")):
        with pytest.raises(TimeoutError):
            OrderService().place(500, CARD, tenant="acme")


def test_retry_with_mock():
    outcomes = [TimeoutError("down"), TimeoutError("down"), {"id": "ch_500", "amount": 500}]
    with patch.object(Gateway, "charge", side_effect=outcomes) as charge:
        assert place_with_retry(OrderService(), 500, CARD, tenant="acme")["id"] == "ch_500"
        assert charge.call_count == 3


def test_ledger_failure_with_mock():
    with patch.multiple(Gateway, charge=DEFAULT, refund=DEFAULT) as gateway:
        gateway["charge"].return_value = {"id": "ch_500", "amount": 500}
        with patch.object(Ledger, "record", side_effect=OSError("disk full")):
            with pytest.raises(OSError):
                OrderService().place(500, CARD, tenant="acme")
        gateway["refund"].assert_called_once_with("ch_500")


def test_currency_with_patch_dict():
    with patch.dict(os.environ, {"SHOP_CURRENCY": "EUR"}):
        assert Gateway().charge(500, CARD)["currency"] == "EUR"


def test_currency_with_monkeypatch(monkeypatch):
    monkeypatch.setenv("SHOP_CURRENCY", "EUR")
    assert Gateway().charge(500, CARD)["currency"] == "EUR"


def test_real_charge_with_mock():
    gateway = Gateway()
    with patch.object(gateway, "charge", wraps=gateway.charge) as charge:
        result = OrderService(gateway=gateway).place(500, CARD, tenant="acme")
        charge.assert_called_once_with(500, CARD)
        assert result["id"] == "ch_500"


def test_order_of_calls_with_mock():
    with patch.object(Gateway, "charge", return_value={"id": "ch", "amount": 0}) as charge:
        service = OrderService()
        service.place(500, CARD, tenant="acme")
        service.place(250, CARD, tenant="globex")
        charge.assert_has_calls([call(500, CARD), call(250, CARD)])


def test_declined_is_logged_with_caplog(caplog):
    caplog.set_level(logging.WARNING, logger="shop")
    with pytest.raises(CardDeclined):
        OrderService().place(250, DECLINED, tenant="globex")
    assert "card ending 0000 declined" in caplog.text


def test_transport_with_mock():
    transport = Mock()
    Notifier(transport).send("hello")
    transport.deliver.assert_called_once_with("hello", priority="normal")
