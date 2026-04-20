from app.model import PriceDirectionModel
from app.sample_data import generate_ohlcv


def test_model_predicts_probability_range() -> None:
    df = generate_ohlcv(240)
    model = PriceDirectionModel()
    p = model.predict_proba_latest(df)
    assert 0.0 <= p <= 1.0
