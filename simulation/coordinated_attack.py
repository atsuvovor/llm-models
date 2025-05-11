#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from attack_simulator import BaseAttackSimulator

def simulate_coordinated_attack(
    base_data: pd.DataFrame,
    phases: list = ["initial", "escalation", "critical"],
    attack_sequence: dict = None,
    anomaly_magnitude: float = 1.5
):
    if attack_sequence is None:
        attack_sequence = {
            "initial": ["phishing", "insider"],
            "escalation": ["malware", "data_leak"],
            "critical": ["ddos", "ransomware"]
        }

    attack_log = []
    combined_data = base_data.copy()

    for phase in phases:
        attacks = attack_sequence.get(phase, [])
        simulator = BaseAttackSimulator(combined_data, anomaly_magnitude=anomaly_magnitude, phase=phase)
        print(f"⏳ Running {phase} phase attacks: {attacks}")
        combined_data = simulator.run_multiple_attacks(attacks)
        attack_log.append((phase, attacks))

    return combined_data, attack_log

