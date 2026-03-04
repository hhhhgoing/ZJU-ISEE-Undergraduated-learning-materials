%% 半导体激光器 I-P 曲线仿真

% 1. 材料和结构参数
L = 800e-6;     % 腔长 (m)
w = 10e-6;      % 有源层宽度 (m)
h = 50e-9;      % 有源层厚度 (m)
V = L * w * h;  % 有源区体积 (m^3)
V_cm3 = V * 1e6; % 有源区体积 (cm^3) - 确保与n0单位一致

% 2. 光学和腔特性参数
neff = 3.5;         % 有效折射率
lambda0 = 1550e-9;  % 中心波长 (m)
Gamma = 0.07;       % 光学限制因子
R1 = 0.35;          % 端面反射率 R1
R2 = 0.35;          % 端面反射率 R2
vg = 8.82e9;        % 群速度 (cm/s)
vg_m_s = vg * 0.01; % 群速度 (m/s)
alpha_i = 13;       % 内部损耗 (cm^-1)
alpha_i_m = alpha_i * 100; % 内部损耗 (m^-1)

% 3. 增益特性参数
g0 = 7e-6;          % 差分增益系数 (cm^3*s^-1) - 根据讨论，此为 v_g * a
n0 = 1.75e18;       % 透明载流子浓度 (cm^-3)

% 4. 其他参数
q = 1.602e-19;      % 电子电荷 (C)
tau_r = 1e-9;       % 载流子寿命 (s)
h_planck = 6.626e-34; % 普朗克常量 (J*s)
c = 3e8;            % 真空光速 (m/s)

%% 预计算
% 镜面损耗 (alpha_m)
alpha_m = (1 / (2 * L * 100)) * log(1 / (R1 * R2)); % 转换为 cm^-1
alpha_m_m = alpha_m * 100; % 镜面损耗 (m^-1)

% 阈值增益 (g_th) - 采用材料增益计算
% g_th_material = (alpha_i + alpha_m) / Gamma;  % cm^-1

% 计算差分增益 'a' (cm^2)
% g = a * (n - n0) => a = g0 / vg
a = g0 / vg; % cm^2

% 阈值材料增益 (cm^-1)
g_th_material = (alpha_i + alpha_m) / Gamma;

% 阈值载流子浓度 (n_th)
n_th = n0 + (g_th_material / a); % cm^-3

% 阈值电流 (I_th)
I_th = q * V_cm3 * (n_th / tau_r); % A

% 光子能量
h_nu = h_planck * c / lambda0; % J

% 外部微分量子效率 (eta_d)
% 注意：这里的eta_d是针对总输出功率（双面），如果只考虑单面输出，则再除以2
eta_d = Gamma * (alpha_m / (alpha_i + alpha_m)); 
% 如果要计算单面输出且包含eta_i=1，则 eta_d = 1 * (alpha_m / (alpha_i + alpha_m)) * (1/2) 
% 但由于alpha_m已经考虑了双端面损耗，并且Gamma是额外因子，所以采用此标准公式

%% I-P 曲线仿真
% 注入电流范围
I_min = 0;
I_max = 2 * I_th; % 仿真范围到阈值电流的两倍
num_points = 500;
I_inject = linspace(I_min, I_max, num_points); % A

% 初始化输出功率数组
P_out = zeros(size(I_inject));

% 遍历电流计算输出功率
for k = 1:num_points
    if I_inject(k) <= I_th
        % 低于阈值，输出功率主要为自发辐射（很小，近似为0）
        P_out(k) = 0; % 简化处理，实际有微弱自发辐射
    else
        % 高于阈值，输出功率线性增长
        P_out(k) = eta_d * (h_nu / q) * (I_inject(k) - I_th);
    end
end

%% I-V 曲线仿真（简化）
% 由于缺乏串联电阻等参数，I-V 曲线仅做概念性仿真
V_diode_turn_on = h_nu / q; % 激光器开启电压（对应光子能量）

V_voltage = zeros(size(I_inject));
R_s = 5; % 假设的串联电阻，用于演示电压随电流增长 (单位: Ohm)

for k = 1:num_points
    if I_inject(k) <= 0.05 * I_th % 假设在很小的电流下才开始导通
        V_voltage(k) = 0; % 简化：未导通
    else
        V_voltage(k) = V_diode_turn_on + I_inject(k) * R_s;
    end
end

%% 结果可视化
figure;

subplot(2,1,1);
plot(I_inject * 1000, P_out * 1000, 'b-', 'LineWidth', 2);
hold on;
plot(I_th * 1000, 0, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r'); % 标记阈值点
plot([I_th * 1000, I_th * 1000], [0, max(P_out) * 1000], 'r--', 'LineWidth', 1); % 阈值线
xlabel('注入电流 I (mA)');
ylabel('输出功率 P (mW)');
title('半导体激光器 I-P 曲线');
grid on;
legend('P-I 曲线', '阈值电流点', 'Location', 'northwest');
text(I_th * 1000 * 1.1, max(P_out) * 1000 * 0.1, sprintf('I_{th} = %.2f mA', I_th * 1000), 'Color', 'r', 'FontSize', 10);

subplot(2,1,2);
plot(I_inject * 1000, V_voltage, 'g-', 'LineWidth', 2);
xlabel('注入电流 I (mA)');
ylabel('电压 V (V)');
title('半导体激光器 I-V 曲线 (简化)');
grid on;
text(I_th * 1000 * 1.1, V_diode_turn_on * 1.2, sprintf('V_{turn-on} = %.2f V', V_diode_turn_on), 'Color', 'g', 'FontSize', 10);


%% 打印关键结果
fprintf('--- 仿真结果 ---\n');
fprintf('镜面损耗 alpha_m = %.3f cm^-1\n', alpha_m);
fprintf('阈值材料增益 g_th = %.2f cm^-1\n', g_th_material);
fprintf('阈值载流子浓度 n_th = %.3e cm^-3\n', n_th);
fprintf('阈值电流 I_th = %.2f mA\n', I_th * 1000);

% 计算 I = 1.2 * I_th 时的输出功率
I_op = 1.2 * I_th;
if I_op <= I_th
    P_op = 0;
else
    P_op = eta_d * (h_nu / q) * (I_op - I_th);
end
fprintf('当 I = 1.2 * I_th (%.2f mA) 时，输出功率 P = %.3f mW\n', I_op * 1000, P_op * 1000);
fprintf('----------------\n');