clc; clear; close all;

%% ================= FILE LIST =======================
incidentFiles = {
'DIAGONAL EMPTY.csv'
'diagonal 2nd side empty.csv'
'same side empty.csv'
'same 2nd side empty.csv'
'opposite gap 12 empty.csv'
'opposite gap 2 3 empty.csv'
};

totalFiles = {
'diagonal.csv'
'diagonal 2nd side.csv'
'same side.csv'
'same 2nd side.csv'
'opposite gap12.csv'
'opposite gap 2 3.csv'
};

Nt = length(incidentFiles);

%% ================= Z SLICE PARAMETERS =================
% Data analysis across all 6 antenna configurations:
%   - Z coverage per file:
%       diagonal, opposite_gap_2_3, opposite_gap_12, same_2nd_side : Z ~ -22 to  97 mm
%       same_side                                                   : Z ~  13 to 133 mm
%       diagonal_2nd_side                                           : Z ~  71 to 190 mm
%   - Overlap zone where ALL 6 files have data                      : Z ~  75 to  97 mm
%   - Strongest field energy in that overlap zone                   : Z ~ 94.5 mm
%
% --> Image the XY plane at Z = 94.5 mm (all 6 configurations contribute)

z_fixed_mm = 94.5;   % mm  — Z plane with peak field energy across all files
z_tol_mm   =  5.0;   % mm  — tolerance (±5 mm) to capture one Z layer per file

%% ================= INITIALISE ACCUMULATORS =================
Escat_all = [];
Einc_all  = [];
x_all     = [];
y_all     = [];

%% ================= LOAD, INTERPOLATE, SLICE AT Z =================

for t = 1:Nt
    fprintf('Processing file pair %d / %d : %s\n', t, Nt, totalFiles{t});

    inc = readmatrix(incidentFiles{t});
    tot = readmatrix(totalFiles{t});

    % --- Coordinates (mm → m) ---
    xi = inc(:,1)*1e-3;  yi = inc(:,2)*1e-3;  zi = inc(:,3)*1e-3;
    xt = tot(:,1)*1e-3;  yt = tot(:,2)*1e-3;  zt = tot(:,3)*1e-3;

    % --- Complex E-fields  [ExRe ExIm EyRe EyIm EzRe EzIm] ---
    Ex_i = inc(:,4) + 1j*inc(:,5);
    Ey_i = inc(:,6) + 1j*inc(:,7);
    Ez_i = inc(:,8) + 1j*inc(:,9);

    Ex_t = tot(:,4) + 1j*tot(:,5);
    Ey_t = tot(:,6) + 1j*tot(:,7);
    Ez_t = tot(:,8) + 1j*tot(:,9);

    % --- 3D interpolation: map incident fields onto total-field grid ---
    Ex_i_interp = griddata(xi,yi,zi, Ex_i, xt,yt,zt, 'linear');
    Ey_i_interp = griddata(xi,yi,zi, Ey_i, xt,yt,zt, 'linear');
    Ez_i_interp = griddata(xi,yi,zi, Ez_i, xt,yt,zt, 'linear');

    Ex_i_interp(isnan(Ex_i_interp)) = 0;
    Ey_i_interp(isnan(Ey_i_interp)) = 0;
    Ez_i_interp(isnan(Ez_i_interp)) = 0;

    % --- Complex vector norm (preserves amplitude AND phase, correct for
    %     unknown/mixed polarisation — avoids wrong scalar summation of
    %     orthogonal components) ---
    Einc  = sqrt(Ex_i_interp.^2 + Ey_i_interp.^2 + Ez_i_interp.^2);

    Ex_s  = Ex_t - Ex_i_interp;
    Ey_s  = Ey_t - Ey_i_interp;
    Ez_s  = Ez_t - Ez_i_interp;
    Escat = sqrt(Ex_s.^2 + Ey_s.^2 + Ez_s.^2);

    % --- Slice: keep only points near Z = z_fixed ---
    z_fixed = z_fixed_mm * 1e-3;
    z_tol   = z_tol_mm   * 1e-3;
    mask = abs(zt - z_fixed) < z_tol;

    Escat_all = [Escat_all; Escat(mask)];
    Einc_all  = [Einc_all;  Einc(mask)];
    x_all     = [x_all;     xt(mask)];
    y_all     = [y_all;     yt(mask)];
end

fprintf('\nXY slice ready: %d points  |  X: %.1f to %.1f mm  |  Y: %.1f to %.1f mm\n', ...
    length(x_all), min(x_all)*1e3, max(x_all)*1e3, ...
                   min(y_all)*1e3, max(y_all)*1e3);

%% ================= CREATE XY IMAGING GRID =================

Nx = 60;
Ny = 60;

xlin = linspace(min(x_all), max(x_all), Nx);
ylin = linspace(min(y_all), max(y_all), Ny);

[Ximg, Yimg] = meshgrid(xlin, ylin);
x_img = Ximg(:);
y_img = Yimg(:);
Npix  = length(x_img);

dx = abs(xlin(2) - xlin(1));
dy = abs(ylin(2) - ylin(1));

%% ================= MAP FIELDS ONTO XY GRID =================

Finc  = scatteredInterpolant(x_all, y_all, Einc_all,  'natural', 'none');
Fscat = scatteredInterpolant(x_all, y_all, Escat_all, 'natural', 'none');

Einc_img   = Finc( x_img, y_img);
Escat_meas = Fscat(x_img, y_img);

Einc_img(isnan(Einc_img))     = 0;
Escat_meas(isnan(Escat_meas)) = 0;

fprintf('Fields mapped onto %d x %d XY grid.\n', Nx, Ny);

%% ================= PHYSICS =================

f  = 2.4e9;
c  = 3e8;
k0 = 2*pi*f/c;

%% ================= 2D GREEN FUNCTION (XY plane) =================

fprintf('Building %d x %d Green matrix ...\n', Npix, Npix);
G = zeros(Npix, Npix);

for m = 1:Npix
    for n = 1:Npix
        R = hypot(x_img(m) - x_img(n), y_img(m) - y_img(n));
        if R > 1e-6
            G(m,n) = (1i/4) * besselh(0, 2, k0*R) * dx * dy;
        end
    end
end

fprintf('Green matrix complete.\n');

%% ================= TRUE CONTRAST RECTANGLE (XY plane) =================
% The object is a vertical column (40mm wide in X, long in Y).
% In the XY cross-section at any Z it appears as a 40mm x 200mm rectangle
% centred in the grid.

eps_bg  = 1;
eps_obj = 18;

tau_true = zeros(Npix, 1);

rect_X = 40e-3;    % width  along X — 40  mm
rect_Y = 200e-3;   % length along Y — 200 mm

x0 = mean(xlin);
y0 = mean(ylin);

x_min_r = x0 - rect_X/2;  x_max_r = x0 + rect_X/2;
y_min_r = y0 - rect_Y/2;  y_max_r = y0 + rect_Y/2;

in_rect = (x_img >= x_min_r) & (x_img <= x_max_r) & ...
          (y_img >= y_min_r) & (y_img <= y_max_r);
tau_true(in_rect) = k0^2 * (eps_obj - eps_bg);

tau_true_grid = reshape(tau_true, Ny, Nx);
tau_true_grid = tau_true_grid ./ (max(abs(tau_true_grid(:))) + eps);

%% ================= DBIM RECONSTRUCTION =================

tau   = zeros(Npix, 1);
Nit   = 10;
alpha = 1e-1;

for it = 1:Nit
    fprintf('DBIM iteration %d / %d\n', it, Nit);

    A    = eye(Npix) - diag(tau) * G;
    Etot = A \ Einc_img;

    Escat_pred = G * (tau .* Etot);
    b          = Escat_meas - Escat_pred;

    J         = G * diag(Etot);
    delta_tau = (J'*J + alpha*eye(Npix)) \ (J'*b);

    tau = tau + delta_tau;
end

fprintf('DBIM reconstruction complete.\n');

tau_rec_grid = reshape(real(tau), Ny, Nx);
tau_rec_grid = tau_rec_grid ./ (max(abs(tau_rec_grid(:))) + eps);

%% ================= PLOTS =================

xlin_mm = xlin * 1e3;
ylin_mm = ylin * 1e3;

figure('Name', sprintf('DBIM XY Imaging — Z = %.1f mm (peak field slice)', z_fixed_mm), ...
       'Position', [80 80 1200 520]);

% --- True contrast ---
subplot(1,2,1)
imagesc(xlin_mm, ylin_mm, tau_true_grid);
axis equal tight;
set(gca, 'YDir', 'normal');
colormap(gca, hot); colorbar;
title(sprintf('TRUE Contrast  (\\epsilon_r = %g)', eps_obj), 'FontSize', 13);
xlabel('X (mm)', 'FontSize', 12);
ylabel('Y (mm)', 'FontSize', 12);
hold on;
xr = [x_min_r x_max_r x_max_r x_min_r x_min_r]*1e3;
yr = [y_min_r y_min_r y_max_r y_max_r y_min_r]*1e3;
plot(xr, yr, '--w', 'LineWidth', 1.5);

% --- DBIM reconstruction ---
subplot(1,2,2)
imagesc(xlin_mm, ylin_mm, tau_rec_grid);
axis equal tight;
set(gca, 'YDir', 'normal');
colormap(gca, hot); colorbar;
title(sprintf('DBIM Reconstruction  (XY plane, Z = %.1f mm)', z_fixed_mm), 'FontSize', 13);
xlabel('X (mm)', 'FontSize', 12);
ylabel('Y (mm)', 'FontSize', 12);
hold on;
plot(xr, yr, '--w', 'LineWidth', 1.5);

sgtitle(sprintf(['2.4 GHz Microwave Imaging — XY Cross-Section at Z = %.1f mm  |  ' ...
    '6 Configurations  |  Peak-field slice (all antennas contributing)'], z_fixed_mm), ...
    'FontSize', 11);
