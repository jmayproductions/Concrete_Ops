from modules.pour_logic.psi_predictor import predict_psi

def test_psi_prediction_range():
    result = predict_psi(slag_pct=20, cement_pct=50, w_c_ratio=0.42)
    assert 2000 <= result <= 10000
