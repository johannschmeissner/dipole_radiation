import pygame
import numpy as np

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 1100, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dipole Radiation")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Consolas', 14)
bold_font = pygame.font.SysFont('Consolas', 16, bold=True)

# --- Physical Constants & Globals ---
EPS0 = 8.854e-12
C_VIS = 100.0 # Visualization speed of light (m/s) 
t = 0
paused = False
is_dark_theme = True
current_mode = "MAIN" 

# --- Parameters ---
q_val = 25.0
omega_val = 5.0
dragging_q = False
dragging_w = False

def get_colors(dark):
    if dark: return (15, 15, 20), (230, 230, 230), (0, 180, 255), (255, 70, 70), (40, 40, 45)
    return (245, 245, 245), (20, 20, 20), (0, 100, 255), (200, 0, 0), (220, 220, 225)

def calc_fields(x, y, t, q, omega):
    """ Calculates E and B fields using Hertzian dipole equations. """
    r = np.sqrt(x**2 + y**2) + 1e-6
    theta = np.arctan2(x, y) 
    k = omega / C_VIS
    phase = omega * (t - r / C_VIS)
    p0 = q * 0.1 
    coeff = p0 / (4 * np.pi * EPS0 * r**3)
    # Radial and Angular Electric field components
    Er = 2 * np.cos(theta) * coeff * (np.cos(phase) + k*r*np.sin(phase))
    Et = np.sin(theta) * coeff * ((1 - (k*r)**2)*np.cos(phase) + k*r*np.sin(phase))
    # Magnetic induction (B_phi) -> H = B/mu0
    Bp = (4e-7 * p0 * omega * np.sin(theta) / (r**2)) * (np.sin(phase) - k*r*np.cos(phase))
    ex = Er * np.sin(theta) + Et * np.cos(theta)
    ey = Er * np.cos(theta) - Et * np.sin(theta)
    return ex, ey, Bp

def draw_overlay(title, lines):
    """ Renders Info/Credits modal windows. """
    overlay = pygame.Surface((650, 400), pygame.SRCALPHA)
    overlay.fill((20, 20, 25, 240))
    pygame.draw.rect(overlay, (0, 180, 255), (0, 0, 650, 400), 2)
    screen.blit(overlay, (WIDTH//2 - 325, HEIGHT//2 - 200))
    screen.blit(bold_font.render(title, True, (0, 180, 255)), (WIDTH//2 - 300, HEIGHT//2 - 170))
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (220, 220, 220)), (WIDTH//2 - 300, HEIGHT//2 - 130 + i*25))
    screen.blit(bold_font.render("Press 'R' to return", True, (255, 70, 70)), (WIDTH//2 - 100, HEIGHT//2 + 150))

# --- Main Loop ---
running = True
while running:
    bg_color, text_color, e_color, b_color, ui_bg = get_colors(is_dark_theme)
    screen.fill(bg_color)
    
    wavelength = (2 * np.pi * C_VIS) / omega_val
    intensity = ( (q_val*0.1)**2 * omega_val**4 ) / (12 * np.pi * EPS0 * C_VIS**3)
    
    DRAW_WIDTH = WIDTH - 300
    cx, cy = DRAW_WIDTH // 2, HEIGHT // 2
    SCALE = DRAW_WIDTH / (2.2 * wavelength) 

    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t: is_dark_theme = not is_dark_theme
            if event.key == pygame.K_SPACE: paused = not paused
            if event.key == pygame.K_i: current_mode = "INFO"
            if event.key == pygame.K_c: current_mode = "CREDITS"
            if event.key == pygame.K_r: current_mode = "MAIN"
        
        if current_mode == "MAIN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if DRAW_WIDTH + 50 <= mx <= DRAW_WIDTH + 250:
                    if 100 <= my <= 120: dragging_q = True
                    if 170 <= my <= 190: dragging_w = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_q = False
                dragging_w = False

    # Sliding logic
    if dragging_q:
        q_val = np.clip(1 + (mx - (DRAW_WIDTH + 50)) / 4, 1.0, 51.0)
    if dragging_w:
        omega_val = np.clip(1 + (mx - (DRAW_WIDTH + 50)) / 2, 1.0, 101.0)

    # Symmetric Vector Grid
    step = 35
    nx, ny = (DRAW_WIDTH // 2) // step, (HEIGHT // 2) // step
    for ix in range(-nx, nx + 1):
        for iy in range(-ny, ny + 1):
            px, py = cx + ix * step, cy + iy * step
            if px < 0 or px > DRAW_WIDTH: continue
            rx, ry = (px - cx) / SCALE, (cy - py) / SCALE
            if abs(rx) < 0.1 and abs(ry) < 0.1: continue
            ex, ey, bp = calc_fields(rx, ry, t, q_val, omega_val)
            mag_e = np.sqrt(ex**2 + ey**2)
            if mag_e > 1e-6:
                elen = np.clip(mag_e * 0.05, 2, 22)
                pygame.draw.line(screen, e_color, (px, py), (px + (ex/mag_e)*elen, py - (ey/mag_e)*elen), 1)
            if abs(bp) > 1e-12:
                br = np.clip(abs(bp) * 2e8, 1, 8)
                pygame.draw.circle(screen, b_color, (px, py), br, 1)
                if bp > 0:
                    d = br * 0.7
                    pygame.draw.line(screen, b_color, (px-d, py-d), (px+d, py+d), 1)
                    pygame.draw.line(screen, b_color, (px + d, py - d), (px - d, py + d), 1)
                    
    # Dipole Visualization
    pygame.draw.line(screen, (0, 255, 0), (cx, cy - 15), (cx, cy + 15), 4)
    charge_y = cy + 15 * np.sin(omega_val * t)
    pygame.draw.circle(screen, (255, 255, 0), (cx, int(charge_y)), 5)

    # Tooltip Logic
    if current_mode == "MAIN" and mx < DRAW_WIDTH:
        rx, ry = (mx - cx) / SCALE, (cy - my) / SCALE
        ex, ey, bp = calc_fields(rx, ry, t, q_val, omega_val)
        tooltip_txt = f"E: {np.sqrt(ex**2+ey**2):.2e} V/m | H: {abs(bp)/1.25e-6:.2e} A/m"
        tw, th = font.size(tooltip_txt)
        pygame.draw.rect(screen, (0,0,0), (mx+15, my-15, tw+10, 20))
        screen.blit(font.render(tooltip_txt, True, (255, 255, 255)), (mx+20, my-12))

    # --- SIDEBAR UI ---
    pygame.draw.rect(screen, ui_bg, (DRAW_WIDTH, 0, 300, HEIGHT))
    ui_x = DRAW_WIDTH + 25 # Уменьшил отступ слева для вместимости текста
    
    # Control Block
    screen.blit(font.render(f"Charge q: {q_val:.1f} C", True, text_color), (ui_x, 80))
    pygame.draw.rect(screen, (100, 100, 100), (ui_x, 105, 200, 10))
    pygame.draw.circle(screen, (0, 255, 0), (ui_x + int(np.clip((q_val-1)*4, 0, 200)), 110), 8)

    screen.blit(font.render(f"Frequency w: {omega_val:.1f} rad/s", True, text_color), (ui_x, 150))
    pygame.draw.rect(screen, (100, 100, 100), (ui_x, 175, 200, 10))
    pygame.draw.circle(screen, (0, 255, 0), (ui_x + int(np.clip((omega_val-1)*2, 0, 200)), 180), 8)

    # Physical Values
    curr_y = 230
    screen.blit(font.render(f"C speed : {C_VIS} m/s", True, text_color), (ui_x, curr_y))
    screen.blit(font.render(f"Lambda λ : {wavelength:.2f} m", True, text_color), (ui_x, curr_y + 30))
    p_text = f"Intens. I: {intensity:.2e} W/m^2"
    screen.blit(font.render(p_text, True, text_color), (ui_x, curr_y + 60))

    # Hotkeys
    curr_y = 360
    screen.blit(font.render("'I' - Info", True, (150, 150, 150)), (ui_x, curr_y))
    screen.blit(font.render("'C' - Credits", True, (150, 150, 150)), (ui_x, curr_y + 25))
    screen.blit(font.render("'SPACE' - Pause", True, (150, 150, 150)), (ui_x, curr_y + 50))
    screen.blit(font.render("'T' - Theme", True, (150, 150, 150)), (ui_x, curr_y + 75))

    # Radiation Diagram
    screen.blit(bold_font.render("Radiation diagram", True, text_color), (ui_x - 5, 490))
    g_cnt = (DRAW_WIDTH + 150, 650)
    d_pts = []
    for a in np.linspace(0, 2*np.pi, 120):
        r_diag = 110 * (np.sin(a)**2)
        d_pts.append((g_cnt[0] + r_diag * np.sin(a), g_cnt[1] - r_diag * np.cos(a)))
    pygame.draw.circle(screen, (100, 100, 100), g_cnt, 2, 0)
    if len(d_pts) > 2: pygame.draw.lines(screen, (255, 215, 0), True, d_pts, 2)

    # --- Overlays ---
    if current_mode == "INFO":
        draw_overlay("PROGRAM INFO", [
            "Program visualizes dipole radiation.",
            "- Green line: Dipole.",
            "- Blue arrows: electric E vector on the screen plane.",
            "- Red circles: magnetic H vector (perpendicular to plane).",
            "- Near (r << L) and Far (r >> L) wave zones",
            "  are taking into account .",
            "The calculation is based on the solution of Hertzian vectors"
        ])
    elif current_mode == "CREDITS":
        draw_overlay("CREDITS", [
            "Author: Johann Schmeissner",
            "E-mail: vny007@mail.ru",
            "Project: Dipole Radiation",
            "GitHub: https://github.com/johannschmeissner",
            "",
            "Made for educational purposes"
        ])

    if not paused and current_mode == "MAIN": t += 0.05
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
