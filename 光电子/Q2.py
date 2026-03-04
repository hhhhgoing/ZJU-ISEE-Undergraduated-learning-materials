import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Key Parameters
# 1. Material and Structure
d = 10e-4  # cm (active layer width)
h = 50e-7  # cm (active layer thickness)
L = 800e-4 # cm (cavity length)

# 2. Optical and Cavity Properties
n_eff = 3.5
lambda_0 = 1550e-7 # cm (central wavelength in free space)
Gamma = 0.07 # Optical confinement factor
R1 = 0.35 # Facet reflectivity R1
R2 = 0.35 # Facet reflectivity R2
v_g = 8.82e9 # cm/s (Group velocity)
alpha_i = 13 # cm^-1 (Internal loss)

# 3. Gain Characteristics
delta_nu_N = 0.5e12 # Hz (Lorentz linewidth)
g0 = 7e-6 # cm^3/s (Differential gain coefficient)
n0 = 1.75e18 # cm^-3 (Transparent carrier concentration)

# 4. Other Parameters
n_i = 5.5e8 # cm^-3 (Intrinsic carrier concentration)
beta_s = 1e-5 # Spontaneous emission coupling factor
tau_r = 1e-9 # s (Carrier lifetime)
tau_n = 1e-9 # s (Radiative recombination lifetime due to spontaneous emission)
T = 300 # K (Operating Temperature)

# Constants
q = 1.602176634e-19 # C (Elementary charge)
c = 3e10 # cm/s (Speed of light in vacuum)
h_planck = 6.62607015e-34 # J*s (Planck's constant)

# Part a: Calculate mirror loss alpha_m and threshold gain g_th

# Calculate mirror loss alpha_m
alpha_m = (1 / (2 * L)) * np.log(1 / (R1 * R2))
print(f"Calculated Mirror Loss (α_m): {alpha_m:.2f} cm^-1")

# Calculate threshold gain g_th
g_th = (alpha_i + alpha_m) / Gamma
print(f"Calculated Threshold Gain (g_th): {g_th:.2f} cm^-1")

# Part b: Simulate I-V and I-P curves, obtain threshold current and output power at I=1.2Ith

# Volume of the active layer
V = L * d * h
print(f"Active layer volume (V): {V:.2e} cm^3")

# Photon lifetime
tau_p = 1 / (v_g * (alpha_i + alpha_m))
print(f"Photon lifetime (τ_p): {tau_p:.2e} s")

# Threshold carrier density (n_th)
# At threshold, g_th = g0 * (n_th - n0)
n_th = n0 + (g_th / g0)
print(f"Threshold Carrier Density (n_th): {n_th:.2e} cm^-3")

# Threshold current (I_th)
# I_th = q * V * (n_th / tau_r)
I_th = q * V * (n_th / tau_r)
print(f"Threshold Current (I_th): {I_th:.4f} A")
print(f"Threshold Current (I_th): {I_th*1000:.4f} mA")


# Rate Equations
# dn/dt = (I / (qV)) - (n / tau_r) - (g * S / V)
# dS/dt = (Gamma * g * S / V) - (S / tau_p) + (beta_s * n / tau_r)

# To ensure the rate equation calculation is robust, we need to correct the gain term
# The gain term g*S/V is usually written as Gamma * g * S.
# Let's use the more common forms of rate equations
# dn/dt = J / (q*h) - n/tau_n - Gamma * g0 * (n - n0) * S / (1 + epsilon * S)  (simplified, no gain saturation here)
# dS/dt = Gamma * g0 * (n - n0) * S - S/tau_p + beta_s * n / tau_n

# Let's define the rate equations for carrier density (n) and photon density (S)
# The current density J = I / (d*L)
# The current I_inj = I_forward_bias
# dn/dt = (I_inj / (q * V)) - (n / tau_r) - (v_g * Gamma * g * S)  # This g should be g0(n-n0)
# dS/dt = (Gamma * v_g * g * S) - (S / tau_p) + (beta_s * n / tau_r)

# Let's adjust the rate equations to match the common forms and ensure consistent units.
# dn/dt = J/q - n/tau_r - Gamma * g0 * (n-n0) * S * v_g # This form seems more consistent for photon density in cm^-3
# dS/dt = Gamma * g0 * (n-n0) * S * v_g - S/tau_p + beta_s * n / tau_r

# Let's verify the units and common forms for rate equations.
# A common form for carrier density (n in cm^-3) and photon density (S in cm^-3) is:
# dn/dt = I / (q * V) - n / tau_r - v_g * g0 * (n - n0) * S
# dS/dt = Gamma * v_g * g0 * (n - n0) * S - S / tau_p + beta_s * n / tau_r

# Let's stick with the most common and robust form:
# N: total number of carriers in the active region (N = n * V)
# P: total number of photons in the cavity (P = S * V_cavity where V_cavity = L*d*h_effective)
# Here, S is photon density, so S needs to be in cm^-3, and the gain is g = g0(n-n0).
# The terms v_g * g * S are transitions per unit volume per second.
# So, for carrier density:
# dN/dt = I/q - N/tau_n - v_g * g0 * (N/V - n0) * P * V_active
# dP/dt = Gamma * v_g * g0 * (N/V - n0) * P - P/tau_p + beta_s * N / tau_n

# Let's define the state variables as n (carrier density) and S (photon density)
def rate_equations(t, y, I_inj):
    n, S = y[0], y[1]

    # Gain calculation (g = g0(n - n0))
    # Ensure gain is non-negative
    g = g0 * (n - n0)
    if g < 0:
        g = 0

    dn_dt = (I_inj / (q * V)) - (n / tau_r) - (v_g * Gamma * g * S)
    dS_dt = (Gamma * v_g * g * S) - (S / tau_p) + (beta_s * n / tau_r)
    return [dn_dt, dS_dt]

# Simulate I-P curve
current_values = np.linspace(0, 1.5 * I_th, 100) # Range of currents for simulation
output_powers = []
steady_state_n = []
steady_state_S = []

# Initial conditions for the ODE solver
n_initial = n0
S_initial = 0 # Start with no photons

for I_inj in current_values:
    # Solve the rate equations to reach steady state
    # Integrate for a sufficiently long time to reach steady state
    t_span = (0, 50 * tau_r) # simulate for 50 times the carrier lifetime
    sol = solve_ivp(rate_equations, t_span, [n_initial, S_initial], args=(I_inj,),
                    method='BDF', dense_output=True)

    # Get the steady-state values (last values of the simulation)
    n_ss, S_ss = sol.y[0][-1], sol.y[1][-1]
    steady_state_n.append(n_ss)
    steady_state_S.append(S_ss)

    # Calculate output power from steady-state photon density
    # P_out = (S_ss * V * h_planck * c * alpha_m) / (lambda_0 * (alpha_i + alpha_m))
    # The output power formula needs to be carefully chosen.
    # It's usually (S * V * h_nu) / tau_p_out where tau_p_out is related to mirror loss
    # P_out = (S_ss * V_cavity * h_planck * nu) * (v_g * alpha_m)
    # Total power generated by stimulated emission is P_stim = (Gamma * v_g * g * S_ss) * (h_planck * nu) * V
    # Power lost through mirrors is P_mirror_loss = S_ss * V * h_planck * nu * (v_g * alpha_m)
    # Output power is usually defined as the power emitted from *one* facet if R1=R2
    # If it's the total output power from both facets:
    # P_out = S_ss * (V_cavity) * h_planck * (c/lambda_0) * (v_g * alpha_m)
    # More accurately, P_out = Power_per_photon * Photon_flux_out * Area_of_facet
    # Or, P_out = S_ss * (V_cavity / tau_p_out) * h_planck * nu  where 1/tau_p_out = v_g * alpha_m
    # P_out = S_ss * V * h_planck * (c/lambda_0) * (v_g * alpha_m)  This seems reasonable for total power out of the cavity.
    # The V here is the active region volume. S_ss is photon density in active region.

    # Total photon energy in the cavity: E_photons = S_ss * V_cavity * h_planck * nu
    # Power lost through mirrors: P_mirror = E_photons / tau_mirror = E_photons * v_g * alpha_m
    # So, P_out = S_ss * V * h_planck * (c/lambda_0) * v_g * alpha_m  (This is for total output power from both facets)
    # The volume V for photon density needs to be the cavity volume where photons exist.
    # Often, V is used for active region. Let's assume here V is the effective optical mode volume.

    nu = c / lambda_0
    P_out = S_ss * V * h_planck * nu * v_g * alpha_m
    output_powers.append(P_out)

# Plot I-P curve
plt.figure(figsize=(10, 6))
plt.plot(np.array(current_values) * 1000, np.array(output_powers) * 1000, marker='o', markersize=3)
plt.xlabel("Current (mA)")
plt.ylabel("Output Power (mW)")
plt.title("I-P Curve of Semiconductor Laser")
plt.grid(True)
plt.axvline(I_th * 1000, color='r', linestyle='--', label=f'Threshold Current = {I_th*1000:.2f} mA')
plt.legend()
plt.show()

# Plot I-V curve (Current vs. Carrier Density) - Note: This is an I-n curve, not I-V (voltage)
# To get I-V, we'd need to model the voltage drop across the diode.
# The question asks for I-V and I-P, but "I-V" for semiconductor lasers usually means I-Voltage.
# However, within the context of rate equations, we typically get I-n and I-P.
# Let's plot I vs carrier density as a proxy, and mention the limitation.

plt.figure(figsize=(10, 6))
plt.plot(np.array(current_values) * 1000, np.array(steady_state_n), marker='o', markersize=3)
plt.xlabel("Current (mA)")
plt.ylabel("Steady-State Carrier Density (cm^-3)")
plt.title("I-n Curve of Semiconductor Laser")
plt.grid(True)
plt.axvline(I_th * 1000, color='r', linestyle='--', label=f'Threshold Current = {I_th*1000:.2f} mA')
plt.axhline(n_th, color='g', linestyle=':', label=f'Threshold Carrier Density = {n_th:.2e} cm^-3')
plt.legend()
plt.show()

# Determine output power when I = 1.2 * I_th
I_target = 1.2 * I_th

# Find the index of the current value closest to I_target
idx = np.argmin(np.abs(current_values - I_target))
P_out_at_1_2_Ith = output_powers[idx]

print(f"\nOutput Power at I = 1.2 * I_th ({I_target*1000:.2f} mA): {P_out_at_1_2_Ith*1000:.4f} mW")