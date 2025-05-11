#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd

class BaseAttack:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def apply(self):
        raise NotImplementedError("Subclasses must implement the apply method.")

class PhishingAttack(BaseAttack):
    def apply(self):
        idx = self.data.sample(frac=0.1).index
        self.data.loc[idx, "Login Attempts"] += np.random.poisson(3, size=len(idx))
        self.data.loc[idx, "Threat Score"] += 1
        self.data.loc[idx, "Threat Level"] = "Medium"
        return self.data

class MalwareAttack(BaseAttack):
    def apply(self):
        idx = self.data.sample(frac=0.1).index
        self.data.loc[idx, "Data Transfer MB"] *= 2
        self.data.loc[idx, "Threat Score"] += 2
        self.data.loc[idx, "Threat Level"] = "High"
        return self.data

class DDoSAttack(BaseAttack):
    def apply(self):
        idx = self.data.sample(frac=0.1).index
        self.data.loc[idx, "Session Duration in Second"] *= 3
        self.data.loc[idx, "Threat Score"] += 3
        self.data.loc[idx, "Threat Level"] = "Critical"
        return self.data

class DataLeakAttack(BaseAttack):
    def apply(self):
        idx = self.data.sample(frac=0.05).index
        self.data.loc[idx, "Num Files Accessed"] += 20
        self.data.loc[idx, "Threat Score"] += 2
        self.data.loc[idx, "Threat Level"] = "High"
        return self.data

class InsiderThreatAttack(BaseAttack):
    def apply(self):
        idx = self.data.sample(frac=0.05).index
        self.data.loc[idx, "Access Control Violation"] = 1
        self.data.loc[idx, "Threat Score"] += 1.5
        self.data.loc[idx, "Threat Level"] = "Medium"
        return self.data

class RansomwareAttack(BaseAttack):
    def apply(self):
        idx = self.data.sample(frac=0.03).index
        self.data.loc[idx, "Cost"] += 50000
        self.data.loc[idx, "Threat Score"] += 4
        self.data.loc[idx, "Threat Level"] = "Critical"
        return self.data

def run_selected_attacks(data: pd.DataFrame, attack_list: list):
    for attack_name in attack_list:
        attack_map = {
            "phishing": PhishingAttack,
            "malware": MalwareAttack,
            "ddos": DDoSAttack,
            "data_leak": DataLeakAttack,
            "insider": InsiderThreatAttack,
            "ransomware": RansomwareAttack
        }

        if attack_name not in attack_map:
            raise ValueError(f"Unknown attack type: {attack_name}")

        attack_instance = attack_map[attack_name](data)
        data = attack_instance.apply()

    return data

