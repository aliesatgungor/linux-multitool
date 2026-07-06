
from unittest.mock import patch, MagicMock

from commands import execute


def _fake_result(returncode=0, stdout=b"", stderr=b""):
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


@patch("commands.subprocess.run")
def test_execute_success_returns_stdout(mock_run):
    mock_run.return_value = _fake_result(stdout=b"hello\n")
    assert execute(["echo", "hello"]) == "hello\n"


@patch("commands.subprocess.run")
def test_execute_empty_success_returns_placeholder(mock_run):
    mock_run.return_value = _fake_result(stdout=b"")
    assert execute(["true"]) == "(çıktı yok)"


@patch("commands.subprocess.run")
def test_execute_nonzero_returncode_shows_output(mock_run):
    mock_run.return_value = _fake_result(returncode=1, stderr=b"boom")
    assert execute(["false"]) == "boom"


@patch("commands.subprocess.run")
def test_execute_nonzero_returncode_no_output_shows_code(mock_run):
    mock_run.return_value = _fake_result(returncode=2)
    assert execute(["false"]) == "Hata: komut 2 koduyla sonlandı."


@patch("commands.subprocess.run", side_effect=FileNotFoundError())
def test_execute_missing_binary(mock_run):
    assert execute(["not-a-real-command"]) == "Hata: 'not-a-real-command' komutu bulunamadı."


@patch("commands.subprocess.run", side_effect=OSError("permission denied"))
def test_execute_oserror(mock_run):
    assert execute(["cmd"]) == "Hata: permission denied"
