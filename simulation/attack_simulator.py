#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
from attack_classes import (
    PhishingAttack,
    MalwareAttack,
    DDoSAttack,
    DataLeakAttack,
    InsiderThreatAttack,
    RansomwareAttack,
    run_selected_attacks
)

class BaseAttackSimulator:
    def __init__(self, base_data: pd.DataFrame, anomaly_magnitude: float = 1.5, phase: str = "initial"):
        self.base_data = base_data.copy()
        self.anomaly_magnitude = anomaly_magnitude
        self.phase = phase

    def inject_anomaly(self, column: str, distribution: str = "normal", params: dict = {}):
        dist_map = {
            "normal": np.random.normal,
            "exponential": np.random.exponential,
            "poisson": np.random.poisson,
            "lognormal": np.random.lognormal
        }

        if distribution not in dist_map:
            raise ValueError(f"Unsupported distribution: {distribution}")

        noise_func = dist_map[distribution]
        noise = noise_func(**params, size=len(self.base_data))

        self.base_data[column] += self.anomaly_magnitude * noise
        return self.base_data

    def run_attack(self, attack_type: str):
        attack_map = {
            "phishing": PhishingAttack,
            "malware": MalwareAttack,
            "ddos": DDoSAttack,
            "data_leak": DataLeakAttack,
            "insider": InsiderThreatAttack,
            "ransomware": RansomwareAttack
        }

        if attack_type not in attack_map:
            raise ValueError(f"Unknown attack type: {attack_type}")

        attack_class = attack_map[attack_type]
        return attack_class(self.base_data).apply()

    def run_multiple_attacks(self, attack_list: list):
        return run_selected_attacks(self.base_data, attack_list)

