"""Unit tests for Pure REP v1 reputation math. No DB required."""
import math
import sys
import os

# backend/app on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.reputation import (
    delta_rep_vote_target,
    delta_rep_voter_feedback,
    delta_rep_reply_target,
    delta_rep_reply_risk,
    delta_rep_follow,
    follower_bonus_delta,
    apply_monthly_decay,
    clamp_rep,
)


def test_delta_rep_vote_target():
    # ΔR_target = sign × (R_voter + 1)^α, α=0.6
    alpha = 0.6
    assert delta_rep_vote_target(1, 0, alpha) == 1.0  # (0+1)^0.6 = 1
    assert delta_rep_vote_target(-1, 0, alpha) == -1.0
    assert delta_rep_vote_target(1, 1.0, alpha) == (2.0 ** alpha)
    assert delta_rep_vote_target(-1, 1.0, alpha) == -(2.0 ** alpha)
    assert delta_rep_vote_target(1, 10.0, alpha) == (11.0 ** alpha)


def test_delta_rep_voter_feedback():
    # ΔR_voter = κ × sign × (ΔR_target_net / (|ΔR_target_net| + c))
    kappa, c = 0.02, 0.1
    # Positive net: upvoter gains
    d = delta_rep_voter_feedback(1, 2.0, kappa, c)
    assert d > 0
    assert abs(d - 0.02 * (2.0 / (2.0 + 0.1))) < 1e-9
    # Negative net: upvoter loses
    d = delta_rep_voter_feedback(1, -1.0, kappa, c)
    assert d < 0
    # Downvoter: sign=-1
    d = delta_rep_voter_feedback(-1, -1.0, kappa, c)
    assert d > 0  # supported "bad" target, voter gains when target went down


def test_delta_rep_reply_target():
    # ΔR_target = γ × (R_replier + 1)^α
    gamma, alpha = 0.1, 0.6
    assert delta_rep_reply_target(gamma, 0, alpha) == gamma * 1.0
    assert delta_rep_reply_target(gamma, 1.0, alpha) == gamma * (2.0 ** alpha)


def test_delta_rep_reply_risk():
    # ΔR_replier = -λ × (R_target + 1)^α
    lambda_, alpha = 0.05, 0.6
    assert delta_rep_reply_risk(lambda_, 0, alpha) == -0.05 * 1.0
    assert delta_rep_reply_risk(lambda_, 1.0, alpha) == -0.05 * (2.0 ** alpha)


def test_delta_rep_follow():
    # ΔR_target = sign × β × (R_follower + 1)^α
    beta, alpha = 0.3, 0.6
    assert delta_rep_follow(1, 0, beta, alpha) == beta * 1.0
    assert delta_rep_follow(-1, 0, beta, alpha) == -beta * 1.0


def test_follower_bonus_delta():
    # ΔR = β × log(1 + F_i)
    beta = 0.3
    assert follower_bonus_delta(beta, 0) == 0.0
    assert follower_bonus_delta(beta, 1) == beta * math.log(2)
    assert follower_bonus_delta(beta, 9) == beta * math.log(10)


def test_apply_monthly_decay():
    delta = 0.03
    assert apply_monthly_decay(10.0, delta) == 10.0 * 0.97
    assert apply_monthly_decay(0.0, delta) == 0.0


def test_clamp_rep():
    assert clamp_rep(1.5) == 1.5
    assert clamp_rep(0) == 0
    assert clamp_rep(-0.5) == 0.0


def run():
    test_delta_rep_vote_target()
    test_delta_rep_voter_feedback()
    test_delta_rep_reply_target()
    test_delta_rep_reply_risk()
    test_delta_rep_follow()
    test_follower_bonus_delta()
    test_apply_monthly_decay()
    test_clamp_rep()
    print("OK: all Pure REP v1 reputation tests passed.")


if __name__ == "__main__":
    run()
