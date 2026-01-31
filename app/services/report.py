import pandas as pd
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
from loguru import logger



def get_metrics_data(df) -> None:
    mape = df_res['error_rel'].mean()
    mae = df_res['error_abs'].mean()
    rmse = np.sqrt(mean_squared_error(results['Actual_Abs_Return'], results['Predicted_Volatility']))
    # -- 4. Bias (Podstřelujeme nebo přestřelujeme?)
    # -- Pokud je kladné -> Model systematicky nadhodnocuje riziko
    # -- Pokud je záporné -> Model systematicky podceňuje riziko (nebezpečné!)
    # AVG(predicted_vol - realized_vol) as global_bias
    worst_tickers = df_res.sort_values('error_abs', ascending=False).head(5)


def get_plots(df) -> None:
    # TODO -> vizualizace predikci v case - vzdy udelat i TS pro kazdou kombinace ticker model params v case pro vsechny jiz dostupne target_days
    pass
