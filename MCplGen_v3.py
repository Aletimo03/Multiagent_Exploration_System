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

  #  print (theta_deg)
  #  print("plos:" , 1.0 / (1 + a * np.exp(-b * (theta_deg - a)))) if  (1.0 / (1 + a * np.exp(-b * (theta_deg - a))))>0.5 else None
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

    landa_signed= 1 / kappa * (1 - p1)

    # Get LoS and NLoS mean losses
    mu1 = pars['mu1']
    mu2 = pars['mu2']
    sigma1 = 0.01 #  pars['a1'] * np.exp(-pars['b1'] * theta_rad)
    sigma2 = 0.1 #pars['a2'] * np.exp(-pars['b2'] * theta_rad)

    if average:
        # Use expected value
        eta_avg = p1 * mu1 + p2 * mu2
      #  print(eta_avg)
        totPL = fspl + eta_avg
        tot_gain = 10 ** (-totPL/10)
        return tot_gain

    else:
        delta_d = abs(d_ij - prev_d) if prev_d is not None else 0

        # Transition logic
        if state == "LoS":
            p11 = p1 + (1 - p1) * np.exp(-landa_signed * delta_d)
            # p11 is prob of staying in the state 1 ( LoS)


           # if p11<0.8:
            #    p11=0.8

                                                                  # in the Markov chain
            next_state = 1 if np.random.rand() < p11 else 2
         #   print("p1:",p1 , "p11: ", p11 , "next state:", next_state)
            sigma = sigma1
            mu = mu1
        else:
            p22 = p2 + (1 - p2) * np.exp(-landa_signed * delta_d)
                                                                  # p22 is prob of staying in the state 2 (nLoS)
                                                                  # in the Markov chain

          #  if p22>0.2:
          #      p22=0.2

            next_state = 2 if np.random.rand() < p22 else 1
           # print("p2:",p2 , "p22: ", p22 , "next state:", next_state)
            sigma = sigma2
            mu = mu2 # secondo me troppo cattivo

        eta = mu + sigma * np.random.randn()
        totPL = fspl + eta
        tot_gain = 10 ** (-totPL / 10)

        return tot_gain, next_state


if __name__ == "__main__":
    
 #usage example
 d_ij = 25000 ** (1/2)
 prev_d = 25000 ** (1/2)
 d_tr = 0

 # Averaged
 avgPL = MCPlGen('Urban', 2e3, 50, d_ij, d_tr, prev_d,1, average=True)
 print(f"GAIN from Averaged Path Loss: {avgPL:.12f} ")

 # Stochastic
 stochPL, state = MCPlGen('Urban', 2e3, 0.5, d_ij, d_tr, prev_d,2)
 print(f"GAIN (from Stochastic Path Loss): {stochPL:.12f}  | State: {state}")

 # Stochastic
 stochPL, state = MCPlGen('Urban', 2e3, 0.5, d_ij, d_tr, prev_d, 2)
 print(f"GAIN (from Stochastic Path Loss): {stochPL:.12f}  | State: {state}")

 # Stochastic
 stochPL, state = MCPlGen('Urban', 2e3, 0.5, d_ij, d_tr, prev_d, 2)
 print(f"GAIN (from Stochastic Path Loss): {stochPL:.12f}  | State: {state}")
