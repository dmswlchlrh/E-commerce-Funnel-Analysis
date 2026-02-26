from src.preprocess import load_data, prepare_funnel
from src.funnel_analysis import calculate_funnel_behaviour, calculate_funnel_strict

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from utils.utility import Utility
from utils.color_utility import color_by_adherence

# =========================
# 1. Data load and preprocess
# =========================
df = load_data("data/sample_ecommerce.csv")
funnel_df = prepare_funnel(df)

behaviour_summary = calculate_funnel_behaviour(funnel_df)
strict_summary = calculate_funnel_strict(funnel_df)
strict_summary["drop_off"] = strict_summary["users"].shift(1) - strict_summary["users"]

top_categories = (
    funnel_df["category_code"]
    .value_counts()
    .head(5)
    .index
)

# =========================
# Configure dashboard
# =========================
fig = plt.figure(figsize=(14, 8))
gs = fig.add_gridspec(2, 4)

# =========================
# (0) Strict Behaviour Users
# =========================
ax0 = fig.add_subplot(gs[0, 0])
ax0.bar(
    behaviour_summary.index,
    behaviour_summary["users"],
    width=0.4,
    color="skyblue")

ax0.set_title("Overall E-commerce Behaviour Funnel")
ax0.set_yscale("log")
ax0.set_ylabel("Unique Users (log)")

for i, rate in enumerate(behaviour_summary["conversion_rate"]):
    if pd.notna(rate):
        ax0.text(i, behaviour_summary["users"][i], f"{rate:.1%}", ha="center", va="bottom")

# =========================
# (1) Strict Funnel Users
# =========================

ax1 = fig.add_subplot(gs[1, 0])
ax1.bar(
    strict_summary.index,
    strict_summary["users"],
    width=0.4)

ax1.set_title("Overall E-commerce Strict Funnel")
ax1.set_yscale("log")
ax1.set_ylabel("Unique Users (log)")

for i, rate in enumerate(strict_summary["conversion_rate"]):
    if pd.notna(rate) and rate < 1:
        ax1.text(i, strict_summary["users"][i], f"{rate:.1%}", ha="center", va="bottom")

# =========================
# (2) Purchase rate
# =========================

categories = list(top_categories)

behaviour_rate = []
strict_rate = []

for category in categories:
    cat_df = funnel_df[funnel_df["category_code"] == category]

    # Behaviour
    b = calculate_funnel_behaviour(cat_df)
    behaviour_rate.append(
        b.loc["View", "users"] and b.loc["Purchase", "users"] / b.loc["View", "users"]
    )

    # Strict
    s = calculate_funnel_strict(cat_df)
    strict_rate.append(
        s.loc["View", "users"] and s.loc["Purchase", "users"] / s.loc["View", "users"]
    )

x = np.arange(len(categories))
width = 0.35

ax2 = fig.add_subplot(gs[:, 1:3])
ax2.bar(
    x - width/2,
    behaviour_rate,
    width,
    label="Behavior Funnel"
)

ax2.bar(
    x + width/2,
    strict_rate,
    width,
    label="Strict Funnel"
)

labels = [Utility.get_last_text(cat) for cat in categories]

ax2.set_xticks(x)
ax2.set_xticklabels(labels, ha="center")

ax2.set_ylabel("Purchase / View")
ax2.set_title("Purchase Rate by Category: Behavior vs Strict Funnel")
ax2.legend()

# =========================
# (3) Adherence ratio
# =========================

adherence = {}

category_counts = (
    funnel_df[funnel_df["funnel_stage"] == "View"]
    .groupby("category_code")["user_id"]
    .nunique()
)

# Filter categories which have small amount of users
categories = category_counts[category_counts >= 100].index

for category in categories:
    cat_df = funnel_df[funnel_df["category_code"] == category]

    # Behavior
    b = calculate_funnel_behaviour(cat_df)
    b_view = b.loc["View", "users"]
    b_purchase = b.loc["Purchase", "users"]
    behavior_rate = b_purchase / b_view if b_view > 0 else 0

    # Strict
    s = calculate_funnel_strict(cat_df)
    s_view = s.loc["View", "users"]
    s_purchase = s.loc["Purchase", "users"]
    strict_rate = s_purchase / s_view if s_view > 0 else 0

    # Adherence Ratio
    adherence[category] = (
        strict_rate / behavior_rate if behavior_rate > 0 else 0
    )

adherence_df = (
    pd.DataFrame.from_dict(adherence, orient="index", columns=["adherence_ratio"])
      .sort_values("adherence_ratio") 
)

ax3 = fig.add_subplot(gs[:, 3])  # 예: 왼쪽 전체 영역

labels = [
    Utility.get_last_text(cat)
    for cat in adherence_df.index
]

colors = adherence_df["adherence_ratio"].apply(color_by_adherence)

ax3.barh(
    labels,
    adherence_df["adherence_ratio"],
    color=colors
)

ax3.axvline(
    x=1,
    color="red",
    linestyle="--",
    linewidth=1,
    label="Perfect Funnel Adherence"
)

ax3.set_xlabel("Funnel Adherence Ratio (Strict / Behavior)")
ax3.set_title("Funnel Adherence Ratio of Categories")
ax3.legend()

# =========================
# Show
# =========================
plt.suptitle("UK Online Retail Funnel Analysis Dashboard", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()