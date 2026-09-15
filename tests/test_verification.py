from app.harness.verification import find_candidate, match_record, norm_dob, norm_phone

MARGARET = {"full_name": "Margaret Chen", "dob": "1985-03-15", "id_last4": "4472", "policy_number": "POL-9921"}


def test_normalisers():
    assert norm_dob("March 15, 1985") == "1985-03-15"
    assert norm_dob("03/15/1985") == "1985-03-15"
    assert norm_phone("(650) 521-2836") == "6505212836"
    assert norm_phone("+1 650 521 2836") == "6505212836"


def test_policy_number_is_lookup_only(fx):
    rec, via = find_candidate({"policy_number": "pol 9921"}, fx)
    assert rec["party_id"] == "P9" and via == "policy_number"
    res = match_record({"policy_number": "POL-9921"}, rec)
    assert res.matched == [] and res.provided == []


def test_three_matches(fx):
    rec, _ = find_candidate(MARGARET, fx)
    res = match_record(MARGARET, rec)
    assert sorted(res.matched) == ["dob", "full_name", "id_last4"]
    assert res.mismatched == []


def test_mismatch_detected(fx):
    rec, _ = find_candidate(MARGARET, fx)
    res = match_record({**MARGARET, "dob": "1985-03-16"}, rec)
    assert res.mismatched == ["dob"]


def test_aliases_and_alternate_fields(fx):
    rec, via = find_candidate({"full_name": "Yaven Li"}, fx)
    assert rec["party_id"] == "P13" and via == "full_name"
    res = match_record({"full_name": "Li Ya Wen", "email": "YAWEN.LI@example.com", "phone": "650-521-2830"}, rec)
    assert sorted(res.matched) == ["email", "full_name", "phone"]


def test_lookup_by_phone_or_email(fx):
    assert find_candidate({"phone": "6503882920"}, fx)[0]["party_id"] == "P7"
    assert find_candidate({"email": "matian@example.com"}, fx)[0]["party_id"] == "P12"
    assert find_candidate({"full_name": "Nobody Here"}, fx)[0] is None


def test_representative_lookup(fx):
    assert fx.find_representative("david chen", "Margaret Chen", "son")["buyer_party_id"] == "P9"
    assert fx.find_representative("David Chen", "Margaret Chen", "daughter") is None
    assert fx.find_representative("Someone Else", "Margaret Chen", None) is None
