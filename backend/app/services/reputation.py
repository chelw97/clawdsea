"""Reputation economy math (PRD). Event-driven REP deltas."""
import math


def delta_rep_target(sign: int, rep_voter: float) -> float:
    """Single vote impact on target (content author).
    ΔREP_target = sign × log(1 + REP_voter). sign: +1 upvote, -1 downvote.
    """
    return sign * math.log1p(max(0.0, rep_voter))


def delta_rep_voter(sign: int, rep_target: float, epsilon: float, k: float) -> float:
    """Voter feedback: supporting valuable targets boosts voter REP.
    ΔREP_voter = sign × ε × (REP_target / (REP_target + k)).
    """
    if rep_target <= 0:
        return 0.0
    return sign * epsilon * (rep_target / (rep_target + k))


def clamp_rep(value: float) -> float:
    """REP must not go negative."""
    return max(0.0, value)
