import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")



#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################
def test_cancel_registered_when_waitlisted_empty_no_promotion():
    # Validates C2, C5, C7 (AC1)
    ev = EventRegistration(capacity=2)
    ev.register("A")
    ev.register("B")

    ev.cancel("A")

    assert ev.status("B") == UserStatus("registered", None)
    assert ev.status("A") == UserStatus("none", None)

    snap = ev.snapshot()
    assert snap["registered"] == ["B"]
    assert snap["waitlist"] == []
    
def test_register_until_capacity_then_waitlisted_fifo():
    # Validates C2, C3, C7 (AC2)
    ev = EventRegistration(capacity=2)

    s1 = ev.register("A")
    s2 = ev.register("B")
    s3 = ev.register("C")
    s4 = ev.register("D")

    assert s1 == UserStatus("registered", None)
    assert s2 == UserStatus("registered", None)
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = ev.snapshot()
    assert snap["registered"] == ["A", "B"]
    assert snap["waitlist"] == ["C", "D"]

def test_duplicate_registration_raises():
    # Validates C4, C7 (AC5)
    ev = EventRegistration(capacity=1)
    ev.register("A")

    with pytest.raises(DuplicateRequest):
        ev.register("A")

    ev.register("B")  # waitlisted
    with pytest.raises(DuplicateRequest):
        ev.register("B")

def test_cancel_registered_promotes_earliest_waitlisted():
    # Validates C3, C5, C7 (AC3)
    ev = EventRegistration(capacity=2)
    ev.register("A")
    ev.register("B")
    ev.register("C")  # waitlisted[0]
    ev.register("D")  # waitlisted[1]

    ev.cancel("A")  # should promote C

    snap = ev.snapshot()
    assert snap["registered"] == ["B", "C"]
    assert snap["waitlist"] == ["D"]

def test_cancel_waitlisted_removes_and_positions_update():
    # Validates C3, C6 (AC4)
    ev = EventRegistration(capacity=1)
    ev.register("A")      # registered
    ev.register("B")      # waitlisted pos1
    ev.register("C")      # waitlisted pos2
    ev.register("D")      # waitlisted pos3

    assert ev.status("D") == UserStatus("waitlisted", 3)

    ev.cancel("C")  # remove middle of waitlisted

    assert ev.status("B") == UserStatus("waitlisted", 1)
    assert ev.status("D") == UserStatus("waitlisted", 2)

    snap = ev.snapshot()
    assert snap["registered"] == ["A"]
    assert snap["waitlist"] == ["B", "D"]

def test_reregister_after_cancel_allowed():
    # Validates C2, C3, C5, C7 (AC8)
    ev = EventRegistration(capacity=1)
    ev.register("A")
    ev.register("B")  # waitlisted

    ev.cancel("A")  # promotes B
    assert ev.status("B") == UserStatus("registered", None)

    # A can re-register now (no longer in system)
    s = ev.register("A")
    assert s == UserStatus("waitlisted", 1)

    snap = ev.snapshot()
    assert snap["registered"] == ["B"]
    assert snap["waitlist"] == ["A"]

def test_capacity_zero_edge_case_all_waitlisted():
    # Validates C1, C2, C3 (AC6)
    ev = EventRegistration(capacity=0)

    s1 = ev.register("A")
    s2 = ev.register("B")

    assert s1 == UserStatus("waitlisted", 1)
    assert s2 == UserStatus("waitlisted", 2)

    snap = ev.snapshot()
    assert snap["registered"] == []
    assert snap["waitlist"] == ["A", "B"]

    ev.cancel("A")
    assert ev.status("A") == UserStatus("none", None)
    assert ev.status("B") == UserStatus("waitlisted", 1)

def test_cancel_unknown_user_raises_notfound():
    # Validates C8, C7 (AC7)
    ev = EventRegistration(capacity=1)
    ev.register("A")
    with pytest.raises(NotFound):
        ev.cancel("NOT_REAL")

    snap = ev.snapshot()
    assert snap["registered"] == ["A"]
    assert snap["waitlist"] == []
    