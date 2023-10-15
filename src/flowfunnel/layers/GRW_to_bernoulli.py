from typing import Optional, Union

import numpy as np
import pymc as pm

from .base import BaseLayer


class GRWToBernoulliLayer(BaseLayer):
    """
    Layer that models observed Bernoulli data based on a Gaussian Random Walk.

    Attributes:
        name (str): Name of the layer.
        observed_data (Optional[np.ndarray]): Observed data for this layer.
        shape (Optional[Tuple[int, ...]]): Shape of the Gaussian Random Walk.
        init_dist (Optional[pm.Distribution]): Initial distribution for the Gaussian Random Walk.
        prob (Optional[pm.Model]): Probabilistic model for this layer.
    """

    def add_to_model(
        self,
        model: pm.Model,
        prev_layer_output: Optional[Union[np.ndarray, pm.Model]] = None,
    ) -> None:
        """
        Add this layer to a given PyMC model.

        Args:
            model (pm.Model): The PyMC model to which this layer will be added.
            prev_layer_output (Optional[Union[np.ndarray, pm.Model]]): Output from the previous layer.

        Returns:
            None
        """
        with model:
            sigma = pm.HalfCauchy(f"sigma_{self.name}", beta=np.std(self.observed_data))
            self.zeta = pm.GaussianRandomWalk(
                self.name, sigma=sigma, shape=self.shape, init_dist=self.init_dist
            )
            self.prob = pm.math.invlogit(self.zeta)
            if self.prob is not None:
                pm.Bernoulli(
                    f"{self.name}_obs", p=self.prob.T, observed=self.observed_data
                )