import math
import numpy as np
import random


def calculate_distance_3d(p1_3d, p2_3d):
        """Calculates the Euclidean distance between two 3D points."""
        dx = p1_3d[0] - p2_3d[0]
        dy = p1_3d[1] - p2_3d[1]
        dz = p1_3d[2] - p2_3d[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)


def calculate_pathloss(scenario, frequency, altitude, distance_ij, distance_tr=None, prev_distance=None,
                            average=True, state=None):
        """Helper for MCPlGen call."""
        return MCPlGen(
            scenario=scenario,
            f=frequency,
            h=altitude,
            d_ij=distance_ij,
            d_tr=distance_tr,
            prev_d=prev_distance,
            average=average,
            state=state
        )

# Predefinisco i parametri statici all’esterno per non ricrearli ad ogni chiamata
_freq700MHz = {
    'Suburban': {'a': 4.879, 'b': 0.4290, 'mu1': 0.0, 'mu2': 18, 'a1': 11.53, 'b1': 0.06, 'a2': 26.53, 'b2': 0.03},
    'Urban': {'a': 9.611, 'b': 0.1580, 'mu1': 0.6, 'mu2': 17, 'a1': 10.98, 'b1': 0.05, 'a2': 23.31, 'b2': 0.03},
    'DenseUrban': {'a': 12.081, 'b': 0.1139, 'mu1': 1.0, 'mu2': 20, 'a1': 9.64, 'b1': 0.04, 'a2': 30.83, 'b2': 0.04},
    'HighriseUrban': {'a': 27.230, 'b': 0.0797, 'mu1': 1.5, 'mu2': 29, 'a1': 9.16, 'b1': 0.03, 'a2': 32.13, 'b2': 0.03}
}

_freq2GHz = {
    'Suburban': {'a': 4.879, 'b': 0.4290, 'mu1': 0.1, 'mu2': 21, 'a1': 11.25, 'b1': 0.06, 'a2': 32.17, 'b2': 0.03},
    'Urban': {'a': 9.611, 'b': 0.1580, 'mu1': 1.0, 'mu2': 20, 'a1': 10.39, 'b1': 0.05, 'a2': 29.60, 'b2': 0.03},
    'DenseUrban': {'a': 12.081, 'b': 0.1139, 'mu1': 1.6, 'mu2': 23, 'a1': 8.96, 'b1': 0.04, 'a2': 35.97, 'b2': 0.04},
    'HighriseUrban': {'a': 27.230, 'b': 0.0797, 'mu1': 2.3, 'mu2': 34, 'a1': 7.37, 'b1': 0.03, 'a2': 37.08, 'b2': 0.03}
}

_freq5_8GHz = {
    'Suburban': {'a': 4.879, 'b': 0.4290, 'mu1': 0.2, 'mu2': 24, 'a1': 11.04, 'b1': 0.06, 'a2': 39.56, 'b2': 0.04},
    'Urban': {'a': 9.611, 'b': 0.1580, 'mu1': 1.2, 'mu2': 23, 'a1': 10.67, 'b1': 0.05, 'a2': 35.85, 'b2': 0.04},
    'DenseUrban': {'a': 12.081, 'b': 0.1139, 'mu1': 1.8, 'mu2': 26, 'a1': 9.21, 'b1': 0.04, 'a2': 40.86, 'b2': 0.04},
    'HighriseUrban': {'a': 27.230, 'b': 0.0797, 'mu1': 2.5, 'mu2': 41, 'a1': 7.15, 'b1': 0.03, 'a2': 40.96, 'b2': 0.03}
}

DEG = 180.0 / math.pi

def los_probability(theta_deg, a, b):
    # usa math.exp più veloce per singoli valori
    return 1.0 / (1 + a * math.exp(-b * (theta_deg - a)))


def MCPlGen(scenario, f, h, d_ij, d_tr, prev_d, state, average=False):
    # mappa scenario kappa0 fuori dal flusso if per velocità
    kappa0_map = {'Suburban': 74, 'DenseUrban': 28}
    kappa0 = kappa0_map.get(scenario, 50)

    # Seleziona parametri in base alla frequenza e scenario
    if f < 1000:
        pars = _freq700MHz[scenario]
    elif f <= 3000:
        pars = _freq2GHz[scenario]
    else:
        pars = _freq5_8GHz[scenario]

    # Calcoli angolo elevazione con math asin e degrees
    theta_rad = math.asin(h / d_ij)
    theta_deg = theta_rad * DEG

    # FSPL con math.log10 più veloce per singoli valori
    fspl = 20 * math.log10(d_ij) + 20 * math.log10(f) - 27.55

    # LoS probability
    p1 = los_probability(theta_deg, pars['a'], pars['b'])
    p2 = 1 - p1

    # Parametri media e deviazione standard (costanti già presenti)
    mu1, mu2 = pars['mu1'], pars['mu2']
    sigma1, sigma2 = 0.01, 0.1  # valori fissi da codice originale

    if average:
        eta_avg = p1 * mu1 + p2 * mu2
        totPL = fspl + eta_avg
        tot_gain = 10 ** (-totPL / 10)
        return tot_gain

    else:

        delta_d = abs(d_ij - prev_d) if prev_d is not None else 0

        kappa = kappa0 * math.tan(theta_rad)
        denom = kappa * (1 - p1)
        landa_signed = 1 / denom if denom > 1e-10 else 1e10

        if state == 1:
            p11 = p1 + (1 - p1) * math.exp(-landa_signed * delta_d)
            next_state = 1 if random.random() < p11 else 2
            sigma = sigma1
            mu = mu1
        else:
            p22 = p2 + (1 - p2) * math.exp(-landa_signed * delta_d)
            next_state = 2 if random.random() < p22 else 1
            sigma = sigma2
            mu = mu2

        eta = mu + sigma * random.gauss(0, 1)
        totPL = fspl + eta
        tot_gain = 10 ** (-totPL / 10)

        return tot_gain, next_state


if __name__ == "__main__":
    d_ij = math.sqrt(25000)
    prev_d = math.sqrt(25000)
    d_tr = 0

    avgPL = MCPlGen('Urban', 2e3, 50, d_ij, d_tr, prev_d, 1, average=True)
    print(f"GAIN from Averaged Path Loss: {avgPL:.12f}")

    stochPL, state = MCPlGen('Urban', 2e3, 50, d_ij, d_tr, prev_d, 2)
    print(f"GAIN (from Stochastic Path Loss): {stochPL:.12f}  | State: {state}")

    stochPL, state = MCPlGen('Urban', 2e3, 50, d_ij, d_tr, prev_d, 1)
    print(f"GAIN (from Stochastic Path Loss): {stochPL:.12f}  | State: {state}")




