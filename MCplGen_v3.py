import math
import numpy as np


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


def los_probability(theta_deg, a, b):
    return 1.0 / (1 + a * np.exp(-b * (theta_deg - a)))

def MCPlGen(scenario, f, h, d_ij, d_tr, prev_d,state, average=False):
  #inputs
    # scenario: environment type
    # f: carrier frequency
    # h: UAV altitude
    # d_ij: UAV-GU distance
    # d_tr: UAV traveled distance
    # prev_d: UAV-GU previous distance
    
    # Parameter sets
    freq700MHz = {
        'SubUrban': {'a': 4.879, 'b': 0.4290, 'mu1': 0.0, 'mu2': 18, 'a1': 11.53, 'b1': 0.06, 'a2': 26.53, 'b2': 0.03},
        'Urban': {'a': 9.611, 'b': 0.1580, 'mu1': 0.6, 'mu2': 17, 'a1': 10.98, 'b1': 0.05, 'a2': 23.31, 'b2': 0.03},
        'DenseUrban': {'a': 12.081, 'b': 0.1139, 'mu1': 1.0, 'mu2': 20, 'a1': 9.64, 'b1': 0.04, 'a2': 30.83, 'b2': 0.04},
        'HighriseUrban': {'a': 27.230, 'b': 0.0797, 'mu1': 1.5, 'mu2': 29, 'a1': 9.16, 'b1': 0.03, 'a2': 32.13, 'b2': 0.03}
    }

    freq2GHz = {
        'SubUrban': {'a': 4.879, 'b': 0.4290, 'mu1': 0.1, 'mu2': 21, 'a1': 11.25, 'b1': 0.06, 'a2': 32.17, 'b2': 0.03},
        'Urban': {'a': 9.611, 'b': 0.1580, 'mu1': 1.0, 'mu2': 20, 'a1': 10.39, 'b1': 0.05, 'a2': 29.60, 'b2': 0.03},
        'DenseUrban': {'a': 12.081, 'b': 0.1139, 'mu1': 1.6, 'mu2': 23, 'a1': 8.96, 'b1': 0.04, 'a2': 35.97, 'b2': 0.04},
        'HighriseUrban': {'a': 27.230, 'b': 0.0797, 'mu1': 2.3, 'mu2': 34, 'a1': 7.37, 'b1': 0.03, 'a2': 37.08, 'b2': 0.03}
    }

    freq5_8GHz = {
        'SubUrban': {'a': 4.879, 'b': 0.4290, 'mu1': 0.2, 'mu2': 24, 'a1': 11.04, 'b1': 0.06, 'a2': 39.56, 'b2': 0.04},
        'Urban': {'a': 9.611, 'b': 0.1580, 'mu1': 1.2, 'mu2': 23, 'a1': 10.67, 'b1': 0.05, 'a2': 35.85, 'b2': 0.04},
        'DenseUrban': {'a': 12.081, 'b': 0.1139, 'mu1': 1.8, 'mu2': 26, 'a1': 9.21, 'b1': 0.04, 'a2': 40.86, 'b2': 0.04},
        'HighriseUrban': {'a': 27.230, 'b': 0.0797, 'mu1': 2.5, 'mu2': 41, 'a1': 7.15, 'b1': 0.03, 'a2': 40.96, 'b2': 0.03}
    }

    if scenario == "Suburban":
        kappa0 = 74
    elif scenario == "DenseUrban":
        kappa0 = 28
    else:
        kappa0 = 50

    # Select parameter set
    if f < 1000:
        pars = freq700MHz[scenario]
    elif f <= 3000:
        pars = freq2GHz[scenario]
    else:
        pars = freq5_8GHz[scenario]

    # Elevation angle
    theta_rad = np.arcsin(h / d_ij)
    theta_deg = np.degrees(theta_rad)


    # FSPL
    fspl = 20 * np.log10(d_ij) + 20 * np.log10(f) - 27.55

    # LoS probability
    p1 = los_probability(theta_deg, pars['a'], pars['b'])
    p2 = 1 - p1
    kappa = kappa0 * np.tan(theta_rad)

    # Get LoS and NLoS mean losses
    mu1 = pars['mu1']
    mu2 = pars['mu2']
    sigma1 = pars['a1'] * np.exp(-pars['b1'] * theta_rad)
    sigma2 = pars['a2'] * np.exp(-pars['b2'] * theta_rad)

    if average:
        # Use expected value
        eta_avg = p1 * mu1 + p2 * mu2
        totPL = fspl + eta_avg
        totPL_linear = 10 ** (-totPL/10)
        return totPL_linear
    else:
        # Rate matrix
        q11 = -1 / kappa
        q12 = 1 / kappa
        q21 = p1 / (p2 * kappa)
        q22 = -q21
        Q = np.array([[q11, q12], [q21, q22]])

        # Initial state

        if state == 1:
            lam = -Q[0, 0]
            next_state = 2
            sigma = sigma1
            mu = mu1
        else:
            lam = -Q[1, 1]
            next_state = 1
            sigma = sigma2
            mu = mu2

        eta = mu + sigma * np.random.randn()
        totPL = fspl + eta
        totPL_linear = 10 ** (-totPL / 10)

        # Holding distance
        if prev_d is not None and d_tr is not None:  # to just see the totPL_linear and not updating the LoS state
         d_hold = np.random.exponential(1 / lam)
         delta_d = abs(d_ij - prev_d)
         check_dist = max(d_tr, delta_d)


     #    print("DELTA D AND CHECK DIST:",delta_d,check_dist)
         if (delta_d == 0 and check_dist == 0) or (check_dist >= d_hold):
            state = 1  if np.random.rand() < p1 else 2

       #  if (delta_d== 0 and check_dist==0):
       #   print ("start of the simulation with LoS probabilit:",p1) #at the start of the simulations

       #  if check_dist >= d_hold:
        #    state = 1 # next_state

         return totPL_linear, state
        else:
            return totPL_linear


if __name__ == "__main__":
    
 #usage example
 d_ij = 25000 ** (1/2)
 prev_d = 25000 ** (1/2)
 d_tr = 0

 # Averaged
 avgPL = MCPlGen('Urban', 2e3, 50, d_ij, d_tr, prev_d,1, average=True)
 print(f"Averaged Path Loss: {avgPL:.12f} dB")

 # Stochastic
 stochPL, state = MCPlGen('Urban', 2e3, 0.5, d_ij, d_tr, prev_d,2)
 print(f"Stochastic Path Loss: {stochPL:.12f} dB | State: {state}")
