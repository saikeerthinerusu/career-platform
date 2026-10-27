def calculate_reward(rating, completed_steps=0, total_steps=0):
    """
    Calculate a reward using student feedback
    and roadmap progress.

    rating: student feedback from 1 to 5
    completed_steps: number of completed roadmap steps
    total_steps: total roadmap steps
    """

    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5.")

    # Convert the 1–5 rating into a reward between -1 and 1.
    feedback_reward = (rating - 3) / 2

    # Calculate roadmap completion percentage.
    if total_steps > 0:
        progress = min(completed_steps / total_steps, 1.0)
    else:
        progress = 0.0

    # Combine feedback and progress.
    reward = (0.7 * feedback_reward) + (0.3 * progress)

    return round(reward, 3)
import json
import math
import os

STATE_FILE = "linucb_state.json"


def select_career_with_linucb(context, career_options, alpha=1.0):
    """
    Simple LinUCB-style career selection.

    context: list of numeric student features
    career_options: list of dictionaries containing career IDs
                    and titles
    """

    if not career_options:
        return None

    if not context:
        context = [1.0]

    state = {}

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                state = json.load(file)
        except (json.JSONDecodeError, OSError):
            state = {}

    best_career = None
    best_score = float("-inf")

    for career in career_options:
        career_key = str(career["id"])
        career_state = state.get(career_key, {"reward_sum": 0.0, "count": 0})

        average_reward = (
            career_state["reward_sum"] / career_state["count"]
            if career_state["count"] > 0
            else 0.0
        )

        exploration_bonus = alpha * math.sqrt(
            math.log(sum(item.get("count", 0) for item in state.values()) + 2)
            / (career_state["count"] + 1)
        )

        score = average_reward + exploration_bonus

        if score > best_score:
            best_score = score
            best_career = career

    return {
        "career": best_career,
        "selection_score": round(best_score, 3),
    }


def update_linucb_reward(career_id, reward):
    """
    Store reward observations for a career.
    """

    state = {}

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                state = json.load(file)
        except (json.JSONDecodeError, OSError):
            state = {}

    career_key = str(career_id)
    career_state = state.get(career_key, {"reward_sum": 0.0, "count": 0})

    career_state["reward_sum"] += float(reward)
    career_state["count"] += 1

    state[career_key] = career_state

    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)

    return career_state