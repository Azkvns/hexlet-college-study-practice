from error_log import log_error


def test_log_error_appends_dated_line(tmp_path):
    log_file = tmp_path / "app.log"
    log_error("нет соединения", str(log_file))
    first = log_file.read_text(encoding="utf-8")
    assert "нет соединения" in first
    date_part = first[:10]
    time_part = first[11:19]
    assert len(date_part) == 10
    assert date_part[4] == "-"
    assert date_part[7] == "-"
    assert len(time_part) == 8
    assert time_part[2] == ":"
    assert time_part[5] == ":"
    log_error("повторная ошибка", str(log_file))
    second = log_file.read_text(encoding="utf-8")
    lines = second.strip().splitlines()
    assert len(lines) == 2
    assert "нет соединения" in lines[0]
    assert "повторная ошибка" in lines[1]
