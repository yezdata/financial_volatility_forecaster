from arch import arch_model
import numpy as np
from loguru import logger
from typing import Optional


def get_garch_pred(log_return, p: int, q: int, dist: str) -> Optional[float]:
    try:
        model = arch_model(log_return, vol='Garch', p=p, q=q, dist=dist, mean='Constant')
        
        res = model.fit(disp='off', show_warning=False)
        forecast = res.forecast(horizon=1)
        var = forecast.variance.iloc[-1]['h.1']
        
        logger.debug(res.summary())
        logger.info(f"GARCH prediction calculated: {np.sqrt(var):.4f}")
        return np.sqrt(var)

    except Exception:
        logger.exception("Error during GARCH training and prediction")
        return None
