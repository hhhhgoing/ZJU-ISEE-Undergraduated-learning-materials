%% Semiconductor Laser I-P Curve Simulation

% 1. Material and Structure Parameters
L = 800e-6;     % Cavity length (m)
w = 10e-6;      % Active layer width (m)
h = 50e-9;      % Active layer thickness (m)
V = L * w * h;  % Active region volume (m^3)
V_cm3 = V * 1e6; % Active region volume (cm^3) - for consistency with n0 unit

% 2. Optical and Cavity Properties
neff = 3.5;         % Effective refractive index
lambda0 = 1550e-9;  % Central wavelength (m)
Gamma = 0.07;       % Optical confinement factor
R1 = 0.35;          % Facet reflectivity R1
R2 = 0.35;          % Facet reflectivity R2
vg = 8.82e9;        % Group velocity (cm/s)
vg_m_s = vg * 0.01; % Group velocity (m/s)
alpha_i = 13;       % Internal loss (cm^-1)
alpha_i_m = alpha_i * 100; % Internal loss (m^-1)

% 3. Gain Characteristics
g0 = 7e-6;          % Differential gain coefficient (cm^3*s^-1) - interpreted as v_g * a
n0 = 1.75e18;       % Transparent carrier concentration (cm^-3)

% 4. Other Parameters
q = 1.602e-19;      % Electron charge (C)
tau_r = 1e-9;       % Carrier lifetime (s)
h_planck = 6.626e-34; % Planck's constant (J*s)
c = 3e8;            % Speed of light in vacuum (m/s)

%% Pre-calculations
% Mirror loss (alpha_m)
alpha_m = (1 / (2 * L * 100)) * log(1 / (R1 * R2)); % Convert L to cm for cm^-1 unit
alpha_m_m = alpha_m * 100; % Mirror loss (m^-1)

% Calculate differential gain 'a' (cm^2)
% Based on previous discussion, g = a * (n - n0) where 'a' is differential gain (cm^2)
% and the given g0 (cm^3*s^-1) is interpreted as a * vg.
a = g0 / vg; % cm^2

% Threshold material gain (g_th_material) (cm^-1)
g_th_material = (alpha_i + alpha_m) / Gamma;

% Threshold carrier concentration (n_th) (cm^-3)
n_th = n0 + (g_th_material / a); 

% Threshold current (I_th) (A)
I_th = q * V_cm3 * (n_th / tau_r); 

% Photon energy (h_nu) (J)
h_nu = h_planck * c / lambda0; 

% External differential quantum efficiency (eta_d)
% Note: This eta_d is for total output power (both facets). If single-sided output
% from identical facets is desired, divide this eta_d by 2.
eta_d = Gamma * (alpha_m / (alpha_i + alpha_m)); 

%% I-P Curve Simulation
% Injection current range
I_min = 0;
I_max = 2 * I_th; % Simulation range up to twice the threshold current
num_points = 500;
I_inject = linspace(I_min, I_max, num_points); % A

% Initialize output power array
P_out = zeros(size(I_inject));

% Iterate through current to calculate output power
for k = 1:num_points
    if I_inject(k) <= I_th
        % Below threshold, output power is mainly spontaneous emission (approximated as 0)
        P_out(k) = 0; 
    else
        % Above threshold, output power increases linearly
        P_out(k) = 0.5*eta_d * (h_nu / q) * (I_inject(k) - I_th);
    end
end

%% I-V Curve Simulation (Simplified)
% Due to lack of parameters like series resistance, I-V curve is conceptual.
V_diode_turn_on = h_nu / q; % Laser turn-on voltage (corresponding to photon energy)

V_voltage = zeros(size(I_inject));
R_s = 5; % Assumed series resistance for demonstration (Ohms)

for k = 1:num_points
    if I_inject(k) <= 0.05 * I_th % Assume turn-on current is 5% of I_th
        V_voltage(k) = 0; % Simplified: not yet conducting
    else
        V_voltage(k) = V_diode_turn_on + I_inject(k) * R_s;
    end
end

%% Results Visualization
figure;

subplot(2,1,1);
plot(I_inject * 1000, P_out * 1000, 'b-', 'LineWidth', 2);
hold on;
plot(I_th * 1000, 0, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r'); % Mark threshold point
plot([I_th * 1000, I_th * 1000], [0, max(P_out) * 1000], 'r--', 'LineWidth', 1); % Threshold line
xlabel('Injection Current I (mA)');
ylabel('Output Power P (mW)');
title('Semiconductor Laser I-P Curve');
grid on;
legend('P-I Curve', 'Threshold Current Point', 'Location', 'northwest');
text(I_th * 1000 * 1.1, max(P_out) * 1000 * 0.1, sprintf('I_{th} = %.2f mA', I_th * 1000), 'Color', 'r', 'FontSize', 10);

subplot(2,1,2);
plot(I_inject * 1000, V_voltage, 'g-', 'LineWidth', 2);
xlabel('Injection Current I (mA)');
ylabel('Voltage V (V)');
title('Semiconductor Laser I-V Curve (Simplified)');
grid on;
text(I_th * 1000 * 1.1, V_diode_turn_on * 1.2, sprintf('V_{turn-on} = %.2f V', V_diode_turn_on), 'Color', 'g', 'FontSize', 10);


%% Print Key Results
fprintf('--- Simulation Results ---\n');
fprintf('Mirror Loss alpha_m = %.3f cm^-1\n', alpha_m);
fprintf('Threshold Material Gain g_th = %.2f cm^-1\n', g_th_material);
fprintf('Threshold Carrier Concentration n_th = %.3e cm^-3\n', n_th);
fprintf('Threshold Current I_th = %.2f mA\n', I_th * 1000);

% Calculate output power at I = 1.2 * I_th
I_op = 1.2 * I_th;
if I_op <= I_th
    P_op = 0;
else
    P_op = eta_d * (h_nu / q) * (I_op - I_th);
end
fprintf('At I = 1.2 * I_th (%.2f mA), Output Power P = %.3f mW\n', I_op * 1000, P_op * 1000);
fprintf('--------------------------\n');