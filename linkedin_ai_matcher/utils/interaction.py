from time import sleep

import numpy as np


def sleep_normal(mean: float = 0.5, std: float = 0.2) -> None:
    sleep(np.random.normal(loc=mean, scale=std))
