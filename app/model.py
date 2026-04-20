from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


FEATURE_COLUMNS = ["ret_1", "ret_5", "vol_z", "ma_gap"]


class PriceDirectionModel:
    """Simple baseline model for up/down movement prediction."""

    def __init__(self) -> None:
        self.model = RandomForestClassifier(n_estimators=200, random_state=42)
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> None:
        X, y = self._build_xy(df)
        self.model.fit(X, y)
        self._fitted = True

    def predict_proba_latest(self, df: pd.DataFrame) -> float:
        if not self._fitted:
            self.fit(df)
        features = self.make_features(df).dropna().iloc[[-1]][FEATURE_COLUMNS]
        prob_up = float(self.model.predict_proba(features)[0, 1])
        return prob_up

    @staticmethod
    def make_features(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["ret_1"] = out["close"].pct_change(1)
        out["ret_5"] = out["close"].pct_change(5)
        out["vol_z"] = (out["volume"] - out["volume"].rolling(20).mean()) / (
            out["volume"].rolling(20).std() + 1e-9
        )
        ma_20 = out["close"].rolling(20).mean()
        out["ma_gap"] = (out["close"] - ma_20) / (ma_20 + 1e-9)
        out["target"] = (out["close"].shift(-1) > out["close"]).astype(int)
        return out

    def _build_xy(self, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        feat = self.make_features(df).dropna()
        X = feat[FEATURE_COLUMNS].to_numpy()
        y = feat["target"].to_numpy()
        return X, y
