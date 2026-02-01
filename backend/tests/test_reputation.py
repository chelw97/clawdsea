"""Unit tests for reputation economy math (PRD). No DB required."""
import math
import sys
import os

# backend/app on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.reputation import (
    delta_rep_target,
    delta_rep_voter,
    clamp_rep,
)


def test_delta_rep_target_downvote():
    # sign=-1: ΔREP_target = -log(1 + REP_voter)
    assert delta_rep_target(-1, 0) == 0.0
    assert delta_rep_target(-1, 1.0) == -math.log(2)
    assert delta_rep_target(-1, 10.0) == -math.log(11)


def test_delta_rep_target_upvote():
    assert delta_rep_target(1, 1.0) == math.log(2)
    assert delta_rep_target(1, 0) == 0.0


def test_delta_rep_voter_downvote():
    # ΔREP_voter = -ε * (REP_target / (REP_target + k))
    eps, k = 0.01, 1.0
    assert delta_rep_voter(-1, 0, eps, k) == 0.0
    assert delta_rep_voter(-1, 2.0, eps, k) == -0.01 * (2.0 / 3.0)
    assert delta_rep_voter(-1, 1.0, eps, k) == -0.01 * 0.5


def test_clamp_rep():
    assert clamp_rep(1.5) == 1.5
    assert clamp_rep(0) == 0
    assert clamp_rep(-0.5) == 0.0


def run():
    test_delta_rep_target_downvote()
    test_delta_rep_target_upvote()
    test_delta_rep_voter_downvote()
    test_clamp_rep()
    print("OK: all reputation tests passed.")


if __name__ == "__main__":
    run()
