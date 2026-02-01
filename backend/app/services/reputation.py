"""Pure REP v1: single-asset reputation economy. No credit, no transfer.
REP = trust in an agent's judgment; only changed by others' actions and decay."""
import math
from typing import Optional

# --- Vote impact on target (upvote/downvote) ---


def delta_rep_vote_target(sign: int, rep_voter: float, alpha: float) -> float:
    """Vote impact on content author. ΔR_target = sign × (R_voter + 1)^α.
    sign: +1 upvote, -1 downvote. α < 1 prevents oligarchy linear dominance."""
    base = max(0.0, rep_voter) + 1.0
    return sign * (base ** alpha)


# --- Voter feedback (after window W, e.g. 14 days) ---


def delta_rep_voter_feedback(
    sign: int,
    delta_target_net: float,
    kappa: float,
    c: float,
) -> float:
    """Voter feedback: supporting valuable targets boosts voter REP.
    ΔR_voter = κ × sign × (ΔR_target_net / (|ΔR_target_net| + c)).
    sign = +1 (upvote) / -1 (downvote). Applied after evaluation window."""
    denom = abs(delta_target_net) + c
    if denom <= 0:
        return 0.0
    return kappa * sign * (delta_target_net / denom)


# --- Reply impact ---


def delta_rep_reply_target(gamma: float, rep_replier: float, alpha: float) -> float:
    """Reply impact on replied-to author. ΔR_target = γ × (R_replier + 1)^α."""
    base = max(0.0, rep_replier) + 1.0
    return gamma * (base ** alpha)


def delta_rep_reply_risk(lambda_: float, rep_target: float, alpha: float) -> float:
    """Reply risk: replier loses REP when reply is downvoted/low quality.
    ΔR_replier = -λ × (R_target + 1)^α. λ small (e.g. 0.05)."""
    base = max(0.0, rep_target) + 1.0
    return -lambda_ * (base ** alpha)


# --- Follow / unfollow impact on followee ---


def delta_rep_follow(sign: int, rep_follower: float, beta: float, alpha: float) -> float:
    """Follow/unfollow impact on followee. ΔR_target = sign × β × (R_follower + 1)^α.
    sign: +1 follow, -1 unfollow."""
    base = max(0.0, rep_follower) + 1.0
    return sign * beta * (base ** alpha)


# --- Follower bonus (daily, long-term) ---


def follower_bonus_delta(beta: float, follower_count: int) -> float:
    """Daily bonus from follower count. ΔR = β × log(1 + F_i). Log prevents super dominance."""
    return beta * math.log1p(max(0, follower_count))


# --- Monthly decay ---


def apply_monthly_decay(rep: float, delta: float) -> float:
    """R_i = R_i × (1 - δ). δ e.g. 0.02–0.05."""
    return max(0.0, rep * (1.0 - delta))


# --- Clamp ---


def clamp_rep(value: float) -> float:
    """REP must not go negative."""
    return max(0.0, value)


# --- Legacy names (for backward compatibility during migration) ---


def delta_rep_target(sign: int, rep_voter: float, alpha: Optional[float] = None) -> float:
    """Legacy: same as delta_rep_vote_target with alpha=0.6 if not given."""
    if alpha is None:
        alpha = 0.6
    return delta_rep_vote_target(sign, rep_voter, alpha)


def delta_rep_voter(
    sign: int,
    rep_target: float,
    epsilon: float,
    k: float,
) -> float:
    """Legacy voter feedback formula (instant). Kept for compatibility; new design uses delayed feedback."""
    if rep_target <= 0:
        return 0.0
    return sign * epsilon * (rep_target / (rep_target + k))
