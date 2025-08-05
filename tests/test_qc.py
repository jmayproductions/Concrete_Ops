from modules.qc.slump_checker import SlumpChecker

def test_slump_check():
    checker = SlumpChecker(min_slump=75, max_slump=125)
    assert checker.check_slump(100) == "within_spec"
    assert checker.check_slump(60) == "too_low"
    assert checker.check_slump(140) == "too_high"
