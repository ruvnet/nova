"""
Cohen's Agentic Conjecture (CAC) Agent Implementation

A basic implementation of the dual-process cognitive architecture combining
neural networks (System 1) and symbolic reasoning (System 2) through a
dynamic gating mechanism.
"""

import warnings

# Suppress pydantic warning
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2")

from conjecture.agent import CACAgent
from conjecture.core.neural import NeuralSubsystem
from conjecture.core.symbolic import SymbolicSubsystem
from conjecture.core.gating import GatingController

__version__ = "1.0.0"
