from datetime import datetime
import numpy as np
import pandas as pd
import random
import socket
import struct

# -------------------- Utility Classes --------------------

class IPAddressGenerator:
    def generate_random_ip(self):
        return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

    def generate_ip_pair(self):
        return self.generate_random_ip(), self.generate_random_ip()

# -------------------- Base Attack Class --------------------

class BaseAttack:
    def __init__(self, df, anomaly_magnitude=1.5):
        self.df = df.copy()
        self.anomaly_magnitude = anomaly_magnitude

    def apply(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def _safe_mean(self, series, default=1.0):
        val = series.mean()
        return val if pd.notna(val) and val >= 0 else default

    def _safe_std(self, series, default=0.5):
        val = series.std()
        return val if pd.notna(val) and val > 0 else default

# -------------------- Attack Implementations --------------------

class PhishingAttack(BaseAttack):
    def apply(self):
        targets = self.df[self.df["Category"] == "Access Control"].sample(frac=0.1, random_state=42)
        
        self.df.loc[targets.index, "Login Attempts"] += self.anomaly_magnitude * np.random.poisson(
            lam=self._safe_mean(self.df["Login Attempts"]), size=len(targets))
        self.df.loc[targets.index, "Impact Score"] += self.anomaly_magnitude * np.random.normal(
            loc=self._safe_mean(self.df["Impact Score"]), scale=self._safe_std(self.df["Impact Score"]), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Threat Score"] += self.anomaly_magnitude * np.random.normal(
            loc=self._safe_mean(self.df["Threat Score"]), scale=self._safe_std(self.df["Threat Score"]), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Attack Type"] = "Phishing"
        return self.df.loc[targets.index]

class MalwareAttack(BaseAttack):
    def apply(self):
        targets = self.df[self.df["Category"] == "System Vulnerability"].sample(frac=0.1, random_state=42)

        self.df.loc[targets.index, "Num Files Accessed"] += self.anomaly_magnitude * np.random.poisson(
            lam=self._safe_mean(self.df["Num Files Accessed"]), size=len(targets))
        self.df.loc[targets.index, "Impact Score"] += self.anomaly_magnitude * np.random.normal(
            loc=self._safe_mean(self.df["Impact Score"]), scale=self._safe_std(self.df["Impact Score"]), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Threat Score"] += self.anomaly_magnitude * np.random.normal(
            loc=self._safe_mean(self.df["Threat Score"]), scale=self._safe_std(self.df["Threat Score"]), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Attack Type"] = "Malware"
        return self.df.loc[targets.index]

class DDoSAttack(BaseAttack):
    def apply(self):
        targets = self.df[self.df["Category"] == "Network Security"].sample(frac=0.2, random_state=42)
        ip_gen = IPAddressGenerator()
        ip_pairs = [ip_gen.generate_ip_pair() for _ in range(len(targets))]

        self.df.loc[targets.index, "Session Duration in Second"] += self.anomaly_magnitude * np.random.exponential(
            scale=self._safe_mean(self.df["Session Duration in Second"]), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Impact Score"] += self.anomaly_magnitude * np.random.exponential(
            scale=self._safe_mean(self.df["Impact Score"]), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Threat Score"] += self.anomaly_magnitude * np.random.exponential(
            scale=self._safe_mean(self.df["Threat Score"]), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Login Attempts"] += self.anomaly_magnitude * np.random.poisson(
            lam=self._safe_mean(self.df["Login Attempts"]), size=len(targets))

        self.df.loc[targets.index, "Source IP Address"] = [pair[0] for pair in ip_pairs]
        self.df.loc[targets.index, "Destination IP Address"] = [pair[1] for pair in ip_pairs]
        self.df.loc[targets.index, "Attack Type"] = "DDoS"
        return self.df.loc[targets.index]

class DataLeakAttack(BaseAttack):
    def apply(self):
        targets = self.df[self.df["Category"] == "Data Breach"].sample(frac=0.1, random_state=42)

        transfer_log_mean = np.log(self._safe_mean(self.df["Data Transfer MB"]))
        transfer_log_std = np.log(self._safe_std(self.df["Data Transfer MB"]))

        self.df.loc[targets.index, "Data Transfer MB"] += self.anomaly_magnitude * np.random.lognormal(
            mean=transfer_log_mean, sigma=transfer_log_std, size=len(targets))
        self.df.loc[targets.index, "Impact Score"] += self.anomaly_magnitude * np.random.lognormal(
            mean=np.log(self._safe_mean(self.df["Impact Score"])), sigma=np.log(self._safe_std(self.df["Impact Score"])), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Threat Score"] += self.anomaly_magnitude * np.random.lognormal(
            mean=np.log(self._safe_mean(self.df["Threat Score"])), sigma=np.log(self._safe_std(self.df["Threat Score"])), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Attack Type"] = "Data Leak"
        return self.df.loc[targets.index]

class InsiderThreatAttack(BaseAttack):
    def apply(self):
        self.df['hour'] = pd.to_datetime(self.df['Timestamps'], errors='coerce').dt.hour
        late_hours = self.df[(self.df['hour'] < 6) | (self.df['hour'] > 23)]
        targets = late_hours.sample(frac=0.1, random_state=42)

        transfer_log_mean = np.log(self._safe_mean(self.df["Data Transfer MB"]))
        transfer_log_std = np.log(self._safe_std(self.df["Data Transfer MB"]))

        self.df.loc[targets.index, "Access Restricted Files"] = True
        self.df.loc[targets.index, "Data Transfer MB"] += self.anomaly_magnitude * np.random.lognormal(
            mean=transfer_log_mean, sigma=transfer_log_std, size=len(targets))
        self.df.loc[targets.index, "Impact Score"] += self.anomaly_magnitude * np.random.lognormal(
            mean=np.log(self._safe_mean(self.df["Impact Score"])), sigma=np.log(self._safe_std(self.df["Impact Score"])), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Threat Score"] += self.anomaly_magnitude * np.random.lognormal(
            mean=np.log(self._safe_mean(self.df["Threat Score"])), sigma=np.log(self._safe_std(self.df["Threat Score"])), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Attack Type"] = "Insider Threat"
        return self.df.loc[targets.index]

class RansomwareAttack(BaseAttack):
    def apply(self):
        targets = self.df[self.df["Category"] == "System Vulnerability"].sample(frac=0.02, random_state=42)

        self.df.loc[targets.index, "CPU Usage %"] += self.anomaly_magnitude * np.random.normal(
            loc=self._safe_mean(self.df["CPU Usage %"]), scale=self._safe_std(self.df["CPU Usage %"]), size=len(targets))
        self.df.loc[targets.index, "Memory Usage MB"] += self.anomaly_magnitude * np.random.lognormal(
            mean=np.log(self._safe_mean(self.df["Memory Usage MB"])), sigma=np.log(self._safe_std(self.df["Memory Usage MB"])), size=len(targets))
        self.df.loc[targets.index, "Num Files Accessed"] += self.anomaly_magnitude * np.random.poisson(
            lam=self._safe_mean(self.df["Num Files Accessed"]), size=len(targets))
        self.df.loc[targets.index, "Impact Score"] += self.anomaly_magnitude * np.random.lognormal(
            mean=np.log(self._safe_mean(self.df["Impact Score"])), sigma=np.log(self._safe_std(self.df["Impact Score"])), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Threat Score"] += self.anomaly_magnitude * np.random.lognormal(
            mean=np.log(self._safe_mean(self.df["Threat Score"])), sigma=np.log(self._safe_std(self.df["Threat Score"])), size=len(targets)).astype(int)
        self.df.loc[targets.index, "Attack Type"] = "Ransomware"
        return self.df.loc[targets.index]


class EarlyAnomalyDetectorClass:
    #def __init__(self):
    #    pass
    def __init__(self, df):
        self.df = df.copy()

    def detect_early_anomalies(self, column='Threat Score'):
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        self.df['Actual Anomaly'] = ((self.df[column] < Q1 - 1.5 * IQR) | (self.df[column] > Q3 + 1.5 * IQR)).astype(int)
        #get anomlous dataframe
        df_anomalies = self.df[self.df['Actual Anomaly'] == 1]
        #get normal dataframe
        df_normal = self.df[self.df['Actual Anomaly'] == 0]

        return df_anomalies, df_normal



# -------------------- Attack Runner --------------------

def run_selected_attacks(df, anomaly_magnitude, selected_attacks, verbose=True):
    attack_map = {
        "phishing": PhishingAttack,
        "malware": MalwareAttack,
        "ddos": DDoSAttack,
        "data_leak": DataLeakAttack,
        "insider": InsiderThreatAttack,
        "ransomware": RansomwareAttack
    }

    if not selected_attacks:
        raise ValueError("No attacks selected for simulation.")

    if df is None:
        raise ValueError("Input DataFrame is None. Please check the file path.")

    full_df_with_anomalies = df.copy()
    full_df_with_anomalies["AnomalyInjected"] = False  # Initialize new column

    anomaly_records = []

    for attack in selected_attacks:
        if verbose:
            print(f"[+] Applying {attack.capitalize()} Attack")

        attack_class = attack_map.get(attack)
        if not attack_class:
            raise ValueError(f"Unknown attack type: {attack}")

        attack_instance = attack_class(full_df_with_anomalies, anomaly_magnitude)
        modified_rows_df = attack_instance.apply()

        if modified_rows_df is None or modified_rows_df.empty:
            if verbose:
                print(f"[-] No rows affected by {attack.capitalize()} Attack.")
            continue

        # Mark modified rows in full_df_with_anomalies
        modified_indices = modified_rows_df.index
        full_df_with_anomalies.loc[modified_indices, "AnomalyInjected"] = True
        full_df_with_anomalies.loc[modified_indices, "Attack Type"] = attack.capitalize()

        anomaly_records.append(modified_rows_df)

    # Combine all modified rows
    if anomaly_records:
        anomalies_only_df = pd.concat(anomaly_records, ignore_index=True)
    else:
        anomalies_only_df = pd.DataFrame(columns=full_df_with_anomalies.columns)

    return anomalies_only_df

    