import json
from unittest.mock import call, patch

import components.InstrumentController as instrument_module
from components.InstrumentController import InstrumentController


class _RegistryKeyContext:
    def __init__(self, key_object):
        self._key_object = key_object

    def __enter__(self):
        return self._key_object

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_reg_set_writes_string_value_to_registry():
    key_object = object()

    with (
        patch("components.InstrumentController.winreg.CreateKey") as create_key,
        patch(
            "components.InstrumentController.winreg.OpenKey",
            return_value=_RegistryKeyContext(key_object),
        ) as open_key,
        patch("components.InstrumentController.winreg.SetValueEx") as set_value,
    ):
        InstrumentController._reg_set(InstrumentController.QUEUE_KEY, "Command", "PING")

    create_key.assert_called_once_with(
        instrument_module.winreg.HKEY_CURRENT_USER, InstrumentController.QUEUE_KEY
    )
    open_key.assert_called_once_with(
        instrument_module.winreg.HKEY_CURRENT_USER,
        InstrumentController.QUEUE_KEY,
        0,
        instrument_module.winreg.KEY_SET_VALUE,
    )
    set_value.assert_called_once_with(
        key_object,
        "Command",
        0,
        instrument_module.winreg.REG_SZ,
        "PING",
    )


def test_reg_get_returns_default_when_key_missing():
    with patch(
        "components.InstrumentController.winreg.OpenKey",
        side_effect=FileNotFoundError,
    ):
        value = InstrumentController._reg_get("missing", "missing", default="fallback")

    assert value == "fallback"


def test_send_command_commits_in_correct_order():
    with (
        patch("components.InstrumentController.uuid.uuid4", return_value="cmd-123"),
        patch.object(InstrumentController, "_reg_set") as reg_set,
    ):
        command_id = InstrumentController._send_command("READ", {"wavelength_nm": 260})

    assert command_id == "cmd-123"
    assert reg_set.call_args_list == [
        call(
            InstrumentController.PARAMS_KEY, "Json", json.dumps({"wavelength_nm": 260})
        ),
        call(InstrumentController.QUEUE_KEY, "CommandId", "cmd-123"),
        call(InstrumentController.QUEUE_KEY, "Command", "READ"),
    ]


def test_wait_for_reply_returns_reply_after_polling():
    reg_get_values = ["", "", "cmd-123", "OK", "C:/out/sample.csv", ""]

    def reg_get_side_effect(*_args, **_kwargs):
        return reg_get_values.pop(0)

    with (
        patch.object(InstrumentController, "_reg_get", side_effect=reg_get_side_effect),
        patch(
            "components.InstrumentController.time.time",
            side_effect=[0.0, 0.01, 0.02, 0.03],
        ),
        patch("components.InstrumentController.time.sleep"),
    ):
        reply = InstrumentController._wait_for_reply("cmd-123", timeout_s=1.0)

    assert reply == {
        "reply_id": "cmd-123",
        "status": "OK",
        "result_path": "C:/out/sample.csv",
        "error": "",
    }


def test_wait_for_reply_times_out_when_reply_never_arrives():
    with (
        patch.object(InstrumentController, "_reg_get", return_value=""),
        patch("components.InstrumentController.time.time", side_effect=[0.0, 0.5, 1.1]),
        patch("components.InstrumentController.time.sleep"),
    ):
        reply = InstrumentController._wait_for_reply("cmd-404", timeout_s=1.0)

    assert reply["status"] == "TIMEOUT"
    assert "Timed out" in reply["error"]


def test_change_params_creates_stored_params_file(tmp_path):
    fake_module_file = tmp_path / "InstrumentController.py"
    fake_module_file.write_text("# fake module path anchor", encoding="utf-8")

    controller = InstrumentController()
    with patch.object(instrument_module, "__file__", str(fake_module_file)):
        result = controller.changeParams({"integration_ms": "250", "mode": "uv-vis"})

    assert result is True
    stored_params = tmp_path / "storedParams.txt"
    assert stored_params.exists()
    contents = stored_params.read_text(encoding="utf-8")
    assert "integration_ms,250" in contents
    assert "mode,uv-vis" in contents


def test_change_params_merges_existing_and_overwrites_values(tmp_path):
    fake_module_file = tmp_path / "InstrumentController.py"
    fake_module_file.write_text("# fake module path anchor", encoding="utf-8")
    stored_params = tmp_path / "storedParams.txt"
    stored_params.write_text("integration_ms,100\ngain,2\n", encoding="utf-8")

    controller = InstrumentController()
    with patch.object(instrument_module, "__file__", str(fake_module_file)):
        result = controller.changeParams({"integration_ms": "500", "scan_count": "3"})

    assert result is True
    parsed = {}
    for line in stored_params.read_text(encoding="utf-8").splitlines():
        key, value = line.split(",", 1)
        parsed[key] = value

    assert parsed["integration_ms"] == "500"
    assert parsed["gain"] == "2"
    assert parsed["scan_count"] == "3"


def test_setup_returns_false_when_registry_operation_raises_oserror():
    controller = InstrumentController()
    with patch.object(controller, "_clear_mailbox", side_effect=OSError):
        assert controller.setup() is False


def test_take_blank_uses_result_path_when_scan_succeeds(tmp_path):
    controller = InstrumentController()
    target_file = tmp_path / "blank.csv"

    with patch.object(
        controller,
        "_send_and_wait",
        return_value={
            "status": "OK",
            "result_path": "C:/bridge/out/blank.csv",
            "error": "",
        },
    ) as send_wait:
        result = controller.take_blank(str(target_file))

    assert result is True
    assert controller.blank_file == "C:/bridge/out/blank.csv"
    send_wait.assert_called_once()


def test_shutdown_returns_false_on_timeout_reply():
    controller = InstrumentController()
    with patch.object(
        controller,
        "_send_and_wait",
        return_value={"status": "TIMEOUT", "result_path": "", "error": "Timed out"},
    ):
        assert controller.shutdown() is False
