import numpy as np
from arch import arch_model
from loguru import logger

from src.config import GarchParams


def get_garch_pred(log_return, params: GarchParams) -> float | None:
    try:
        model = arch_model(
            log_return,
            vol="GARCH",
            p=params.p,
            q=params.q,
            dist=params.dist,
            mean="Constant",
        )

        res = model.fit(disp="off", show_warning=False)
        forecast = res.forecast(horizon=1)
        var = forecast.variance.iloc[-1]["h.1"]

        logger.debug(res.summary())
        logger.info(f"GARCH prediction calculated: {np.sqrt(var):.4f}")
        return np.sqrt(var)

    except Exception:
        logger.exception("Error during GARCH training and prediction")
        return None
