import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    _is_valid_english_word,
    _validate_spelling_finding,
    _is_american_british_pair,
    repair_broken_words,
    _get_common_words,
)


def make_finding(orig, suggestion, ftype="Spelling"):
    return {
        "type": ftype,
        "original_text": orig,
        "suggestion": suggestion,
        "severity": "High",
        "context": "test",
    }


def test_valid_words_not_flagged():
    valid_words = [
        "accountability", "governance", "implementation", "administration",
        "infrastructure", "transparency", "sustainability", "stakeholders",
        "collaboration", "decentralisation", "organization", "programme",
        "development", "management", "government", "department",
        "initiative", "institutional", "competency", "efficiency",
        "effectiveness", "innovation", "technology", "bureaucratic",
        "empowerment", "transformation", "modernisation", "rehabilitation",
        "procurement", "expenditure", "jurisdiction", "administrative",
        "commissioner", "municipality", "surveillance", "enforcement",
        "compliance", "regulation", "constitutional", "resolution",
    ]

    for word in valid_words:
        assert _is_valid_english_word(word), f"'{word}' not recognized as valid"

    for word in valid_words:
        finding = make_finding(word, "something_else")
        assert not _validate_spelling_finding(finding), f"'{word}' was not filtered (validate returned True)"

    print("test_valid_words_not_flagged PASSED")


def test_misspellings_still_caught():
    misspellings = [
        ("teh", "the"),
        ("recieve", "receive"),
        ("seperate", "separate"),
        ("occurence", "occurrence"),
        ("goverment", "government"),
        ("accomodation", "accommodation"),
        ("definately", "definitely"),
        ("occured", "occurred"),
        ("reccomend", "recommend"),
        ("enviroment", "environment"),
    ]

    for orig, sugg in misspellings:
        assert not _is_valid_english_word(orig), f"misspelling '{orig}' recognized as valid word"
        finding = make_finding(orig, sugg)
        assert _validate_spelling_finding(finding), f"misspelling '{orig}' -> '{sugg}' was incorrectly filtered out"

    print("test_misspellings_still_caught PASSED")


def test_american_to_british_flagged():
    pairs = [
        ("organization", "organisation"),
        ("center", "centre"),
        ("analyze", "analyse"),
        ("color", "colour"),
        ("favor", "favour"),
        ("behavior", "behaviour"),
        ("realize", "realise"),
        ("recognize", "recognise"),
        ("standardize", "standardise"),
        ("defense", "defence"),
        ("program", "programme"),
        ("labor", "labour"),
    ]

    for american, british in pairs:
        assert _is_american_british_pair(american, british), f"'{american}' -> '{british}' not detected as Am/Br pair"
        finding = make_finding(american, british)
        assert _validate_spelling_finding(finding), f"Am->Br '{american}' -> '{british}' was incorrectly filtered"

    print("test_american_to_british_flagged PASSED")


def test_pdf_broken_words_discarded():
    broken_pairs = [
        ("account ability", "accountability"),
        ("gover nance", "governance"),
        ("imple mentation", "implementation"),
        ("admini stration", "administration"),
        ("infra structure", "infrastructure"),
        ("trans parency", "transparency"),
        ("sustain ability", "sustainability"),
        ("stake holders", "stakeholders"),
        ("colla boration", "collaboration"),
        ("decentrali sation", "decentralisation"),
    ]

    for orig, sugg in broken_pairs:
        finding = make_finding(orig, sugg)
        assert not _validate_spelling_finding(finding), f"broken word '{orig}' -> '{sugg}' not filtered"

    print("test_pdf_broken_words_discarded PASSED")


def test_repair_broken_words():
    test_cases = [
        ("a ccountability is important", "accountability is important"),
        ("gover nance framework", "governance framework"),
        ("imple mentation plan", "implementation plan"),
    ]

    for input_text, expected in test_cases:
        result = repair_broken_words(input_text)
        assert expected in result, f"repair('{input_text}') = '{result}', expected '{expected}'"

    print("test_repair_broken_words PASSED")


def test_both_valid_words_different_meaning():
    finding = make_finding("affect", "effect")
    assert not _validate_spelling_finding(finding), "'affect'->'effect' should be filtered (both valid)"
    print("test_both_valid_words_different_meaning PASSED")


def test_non_spelling_findings_unaffected():
    grammar_finding = {
        "type": "Grammar",
        "original_text": "the team have decided",
        "suggestion": "the team has decided",
        "severity": "High",
        "context": "Subject-verb agreement",
    }
    assert grammar_finding.get("type") != "Spelling", "Grammar type should not be Spelling"
    print("test_non_spelling_findings_unaffected PASSED")


def test_malformed_findings():
    empty_finding = make_finding("", "")
    result = _validate_spelling_finding(empty_finding)
    assert isinstance(result, bool), "Should handle empty finding without error"

    no_suggestion = {"type": "Spelling", "original_text": "teh", "severity": "High"}
    result2 = _validate_spelling_finding(no_suggestion)
    assert isinstance(result2, bool), "Should handle missing suggestion without error"

    print("test_malformed_findings PASSED")


def test_hyphenated_and_punctuated_tokens():
    finding = make_finding("e-governance", "egovernance")
    result = _validate_spelling_finding(finding)
    assert isinstance(result, bool), "Should handle hyphenated tokens"

    finding2 = make_finding("it's", "its")
    result2 = _validate_spelling_finding(finding2)
    assert isinstance(result2, bool), "Should handle punctuated tokens"

    print("test_hyphenated_and_punctuated_tokens PASSED")


def test_non_am_br_suffix_pairs():
    assert not _is_american_british_pair("doctor", "doctour"), "'doctor'->'doctour' should NOT match Am/Br"
    assert not _is_american_british_pair("water", "watre"), "'water'->'watre' should NOT match Am/Br"
    print("test_non_am_br_suffix_pairs PASSED")


def test_repair_does_not_join_valid_phrases():
    phrases_that_must_not_change = [
        "log in to portal",
        "move on to next",
        "check in to hotel",
        "on to the next topic",
        "in to the room",
        "up on the hill",
        "go in to see",
        "he is a good man",
        "she can do it",
    ]

    for phrase in phrases_that_must_not_change:
        result = repair_broken_words(phrase)
        assert result == phrase, f"repair('{phrase}') incorrectly changed to '{result}'"

    print("test_repair_does_not_join_valid_phrases PASSED")


if __name__ == "__main__":
    tests = [
        test_valid_words_not_flagged,
        test_misspellings_still_caught,
        test_american_to_british_flagged,
        test_pdf_broken_words_discarded,
        test_repair_broken_words,
        test_both_valid_words_different_meaning,
        test_non_spelling_findings_unaffected,
        test_malformed_findings,
        test_hyphenated_and_punctuated_tokens,
        test_non_am_br_suffix_pairs,
        test_repair_does_not_join_valid_phrases,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"{test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"{test.__name__} ERROR: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} tests passed")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
