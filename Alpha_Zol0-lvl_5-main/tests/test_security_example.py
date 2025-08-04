def test_no_eval_in_code():
    with open("main.py") as f:
        code = f.read()
    assert "eval(" not in code
