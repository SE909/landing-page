from app.skills import edit_hero


def test_edit_hero_validate_and_apply():
    page_state = {
        "hero": {
            "title": "Ancien titre",
            "subtitle": "Une description",
            "cta_text": "S'inscrire",
        }
    }

    changes = {"title": "Nouveau titre"}
    assert edit_hero.validate(changes) is True

    updated = edit_hero.apply(page_state, changes)
    assert updated["hero"]["title"] == "Nouveau titre"
    assert updated["hero"]["subtitle"] == "Une description"

    # invalid change
    bad_changes = {"unknown_key": "x"}
    assert edit_hero.validate(bad_changes) is False
    updated2 = edit_hero.apply(page_state, bad_changes)
    # no change applied
    assert updated2["hero"]["title"] == "Ancien titre"
