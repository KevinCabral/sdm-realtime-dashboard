from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from services.audit import log_data_access
from services.config import CSV_DATA_PATH


class TurnoutService:
    def __init__(self) -> None:
        self._rng = random.Random()
        self._data = self._load_seed_data()
        self._last_updated = datetime.utcnow()

    def _load_seed_data(self) -> pd.DataFrame:
        data_path = Path(CSV_DATA_PATH)
        if data_path.exists():
            df = pd.read_csv(data_path)
        else:
            df = pd.DataFrame(
                [
                    {
                        "voter_id": f"V{idx:04d}",
                        "full_name": f"Voter {idx}",
                        "polling_station": f"Station {(idx % 5) + 1}",
                        "region": ["North", "South", "East", "West"][idx % 4],
                        "has_voted": False,
                        "voted_at": None,
                        "validation_status": "not_voted",
                    }
                    for idx in range(1, 151)
                ]
            )

        df["has_voted"] = df["has_voted"].astype(bool)
        df["voted_at"] = pd.to_datetime(df["voted_at"], errors="coerce")
        df["validation_status"] = df["validation_status"].fillna("not_voted")
        return df

    def _simulate_updates(self) -> None:
        not_voted_idx = self._data.index[~self._data["has_voted"]]
        if len(not_voted_idx) == 0:
            self._last_updated = datetime.utcnow()
            return

        updates = min(self._rng.randint(0, 4), len(not_voted_idx))
        if updates == 0:
            self._last_updated = datetime.utcnow()
            return

        chosen = self._rng.sample(list(not_voted_idx), updates)
        now = datetime.utcnow()

        for idx in chosen:
            self._data.at[idx, "has_voted"] = True
            self._data.at[idx, "voted_at"] = now - timedelta(minutes=self._rng.randint(0, 180))
            self._data.at[idx, "validation_status"] = self._rng.choice(["validated", "pending_validation"])

        self._last_updated = datetime.utcnow()

    def get_turnout_data(self, actor: str) -> tuple[pd.DataFrame, datetime]:
        log_data_access(actor=actor, action="read_turnout_data")
        self._simulate_updates()
        return self._data.copy(), self._last_updated


def get_display_status(df: pd.DataFrame) -> pd.Series:
    return df.apply(
        lambda row: "pending validation"
        if row["has_voted"] and row["validation_status"] == "pending_validation"
        else ("voted" if row["has_voted"] else "not voted"),
        axis=1,
    )
