# -*- coding: utf-8 -*-
"""
===============================================================================
 XUAT HINH VE DO PHAN GIAI CAO DE CHEN VAO THUYET MINH
-------------------------------------------------------------------------------
 Chay file nay se tao ra thu muc 'hinh_bao_cao' chua cac file PNG 300 dpi,
 chen truc tiep vao file Word duoc.

 Cach chay:   python xuat_hinh_bao_cao.py
===============================================================================
"""

import os
import copy

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nhiet_btkl import (
    ThongSoDauVao, mo_phong_truong_nhiet, tong_hop_ket_qua,
    duong_cong_doan_nhiet, NGUONG_DT, NGUONG_TMAX,
)

THU_MUC = "hinh_bao_cao"
os.makedirs(THU_MUC, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def luu(fig, ten):
    """Luu hinh va dong lai de giai phong bo nho."""
    duong_dan = os.path.join(THU_MUC, ten)
    fig.savefig(duong_dan)
    plt.close(fig)
    print(f"  Da luu: {duong_dan}")


# =============================================================================
# Kich ban goc (KB1) - thi cong thong thuong
# =============================================================================
ts = ThongSoDauVao()
df, T_luoi, x, info = mo_phong_truong_nhiet(ts)
kq = tong_hop_ket_qua(df)

print("Dang xuat hinh ve...")

# --- Hinh 1: Duong cong toa nhiet doan nhiet --------------------------------
t = np.linspace(0, 240, 500)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(t, duong_cong_doan_nhiet(t, info["dT_ad_vo_cuc"], ts.tau, ts.beta),
        linewidth=2.2, color="#C62828")
ax.set_xlabel("Thời gian (giờ)")
ax.set_ylabel("Độ tăng nhiệt đoạn nhiệt ΔT$_{ad}$ (°C)")
ax.set_title("Hình 1. Đường cong tỏa nhiệt đoạn nhiệt của bê tông")
for ngay in [1, 3, 7]:
    gt = float(duong_cong_doan_nhiet(ngay * 24, info["dT_ad_vo_cuc"],
                                     ts.tau, ts.beta))
    ax.plot(ngay * 24, gt, "o", color="#1565C0", markersize=6)
    ax.annotate(f"{ngay} ngày: {gt:.1f} °C", (ngay * 24, gt),
                textcoords="offset points", xytext=(8, -12), fontsize=9)
luu(fig, "Hinh_1_duong_cong_toa_nhiet.png")

# --- Hinh 2: Dien bien nhiet do ---------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(df["Gio"], df["T_tam"], linewidth=2.4, color="#C62828",
        label="Tâm khối")
ax.plot(df["Gio"], df["T_mat_tren"], linewidth=2.0, color="#1565C0",
        label="Bề mặt trên")
ax.plot(df["Gio"], df["T_mat_duoi"], linewidth=1.6, color="#2E7D32",
        linestyle="--", label="Mặt dưới (đáy đài)")
ax.plot(df["Gio"], df["T_khong_khi"], linewidth=1.2, color="#757575",
        linestyle=":", label="Không khí")
ax.axhline(NGUONG_TMAX, color="#C62828", linestyle="-.", linewidth=1.3,
           label="Ngưỡng T$_{max}$ = 70 °C")
ax.annotate(f"T$_{{max}}$ = {kq['T_max_tam']:.1f} °C\n"
            f"tại giờ {kq['thoi_diem_T_max']:.0f}",
            (kq["thoi_diem_T_max"], kq["T_max_tam"]),
            textcoords="offset points", xytext=(15, -25), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#333333"))
ax.set_xlabel("Thời gian (giờ)")
ax.set_ylabel("Nhiệt độ (°C)")
ax.set_title("Hình 2. Diễn biến nhiệt độ trong khối bê tông (KB1)")
ax.legend(loc="lower right", fontsize=9)
luu(fig, "Hinh_2_dien_bien_nhiet_do.png")

# --- Hinh 3: Chenh lech nhiet do dT ------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(df["Gio"], df["dT"], linewidth=2.6, color="#6A1B9A",
        label="ΔT = T$_{tâm}$ − T$_{bề mặt}$")
ax.axhline(NGUONG_DT, color="#C62828", linestyle="--", linewidth=1.8,
           label="Ngưỡng cho phép 20 °C")
ax.axhline(18, color="#EF6C00", linestyle=":", linewidth=1.3,
           label="Ngưỡng cảnh báo 18 °C")
ax.axhline(15, color="#F9A825", linestyle=":", linewidth=1.3,
           label="Ngưỡng chú ý 15 °C")
ax.fill_between(df["Gio"], NGUONG_DT, df["dT"],
                where=(df["dT"] > NGUONG_DT), color="#C62828", alpha=0.18)
ax.annotate(f"ΔT$_{{max}}$ = {kq['dT_max']:.1f} °C",
            (kq["thoi_diem_dT_max"], kq["dT_max"]),
            textcoords="offset points", xytext=(12, 8), fontsize=10,
            fontweight="bold", color="#C62828")
ax.set_xlabel("Thời gian (giờ)")
ax.set_ylabel("ΔT (°C)")
ax.set_title("Hình 3. Chênh lệch nhiệt độ tâm − bề mặt (KB1)")
ax.legend(loc="lower right", fontsize=9)
luu(fig, "Hinh_3_chenh_lech_nhiet_do.png")

# --- Hinh 4: Phan bo nhiet theo chieu day ------------------------------------
fig, ax = plt.subplots(figsize=(6, 5))
mocs = [6, 12, 24, 48, 72, 100, 168, 240]
mau = plt.cm.plasma(np.linspace(0, 0.88, len(mocs)))
for m, g in zip(mau, mocs):
    g = min(g, T_luoi.shape[0] - 1)
    ax.plot(T_luoi[g, :], x, linewidth=2, color=m, label=f"{g} giờ")
ax.set_xlabel("Nhiệt độ (°C)")
ax.set_ylabel("Cao độ tính từ đáy đài (m)")
ax.set_title("Hình 4. Phân bố nhiệt độ theo chiều dày")
ax.legend(fontsize=9, loc="center left", bbox_to_anchor=(1.02, 0.5))
luu(fig, "Hinh_4_phan_bo_nhiet_chieu_day.png")

# --- Hinh 5: Kiem tra ung suat keo nhiet -------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(df["Gio"], df["ung_suat_keo"], linewidth=2.4, color="#C62828",
        label="Ứng suất kéo nhiệt σ$_t$(t)")
ax.plot(df["Gio"], df["Rbt"], linewidth=2.4, color="#2E7D32",
        label="Cường độ chịu kéo R$_{bt}$(t)")
ax.fill_between(df["Gio"], df["Rbt"], df["ung_suat_keo"],
                where=(df["ung_suat_keo"] > df["Rbt"]),
                color="#C62828", alpha=0.18, label="Vùng có nguy cơ nứt")
ax.set_xlabel("Thời gian (giờ)")
ax.set_ylabel("Ứng suất (MPa)")
ax.set_title("Hình 5. Kiểm tra nguy cơ nứt do ứng suất kéo nhiệt (KB1)")
ax.legend(loc="best", fontsize=9)
luu(fig, "Hinh_5_ung_suat_keo_nhiet.png")

# --- Hinh 6 va 7: So sanh cac kich ban ---------------------------------------
kich_ban = {
    "KB1 — Để hở": dict(U_tren=13.6),
    "KB2 — Nilon + cốp pha gỗ": dict(U_tren=5.2),
    "KB3 — Bao tải + nilon + xốp": dict(U_tren=1.7),
    "KB4 — KB3 + T₀ = 28 °C": dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0),
    "KB5 — KB4 + tro bay 30%": dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0,
                                    luong_xi_mang=280.0,
                                    luong_tro_bay=120.0),
    "KB6 — KB5 + chia 2 lớp": dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0,
                                   luong_xi_mang=280.0,
                                   luong_tro_bay=120.0, chieu_day=1.25),
}

fig_dT, ax_dT = plt.subplots(figsize=(8.5, 4.8))
fig_T, ax_T = plt.subplots(figsize=(8.5, 4.8))
mau = plt.cm.tab10(np.linspace(0, 0.9, len(kich_ban)))
tom_tat = []

for m, (ten, sua) in zip(mau, kich_ban.items()):
    t_i = copy.deepcopy(ts)
    for k, v in sua.items():
        setattr(t_i, k, v)
    df_i, _, _, _ = mo_phong_truong_nhiet(t_i)
    kq_i = tong_hop_ket_qua(df_i)
    ax_dT.plot(df_i["Gio"], df_i["dT"], linewidth=2.1, color=m, label=ten)
    ax_T.plot(df_i["Gio"], df_i["T_tam"], linewidth=2.1, color=m, label=ten)
    tom_tat.append((ten, kq_i["T_max_tam"], kq_i["dT_max"],
                    kq_i["he_so_an_toan_min"]))

ax_dT.axhline(NGUONG_DT, color="#000000", linestyle="--", linewidth=1.8,
              label="Ngưỡng 20 °C")
ax_dT.set_xlabel("Thời gian (giờ)")
ax_dT.set_ylabel("ΔT (°C)")
ax_dT.set_title("Hình 6. So sánh ΔT giữa các kịch bản thi công")
ax_dT.legend(fontsize=8.5, loc="upper right")
luu(fig_dT, "Hinh_6_so_sanh_dT_kich_ban.png")

ax_T.axhline(NGUONG_TMAX, color="#000000", linestyle="--", linewidth=1.8,
             label="Ngưỡng 70 °C")
ax_T.set_xlabel("Thời gian (giờ)")
ax_T.set_ylabel("Nhiệt độ tâm khối (°C)")
ax_T.set_title("Hình 7. So sánh nhiệt độ tâm khối giữa các kịch bản")
ax_T.legend(fontsize=8.5, loc="lower right")
luu(fig_T, "Hinh_7_so_sanh_Tmax_kich_ban.png")

# --- Hinh 8: Bieu do cot so sanh dT va Tmax ----------------------------------
fig, ax1 = plt.subplots(figsize=(9, 4.8))
ten_ngan = [t[0].split(" — ")[0] for t in tom_tat]
vi_tri = np.arange(len(tom_tat))
rong = 0.38

c1 = ax1.bar(vi_tri - rong / 2, [t[2] for t in tom_tat], rong,
             color="#6A1B9A", label="ΔT$_{max}$ (°C)")
ax1.axhline(NGUONG_DT, color="#6A1B9A", linestyle="--", linewidth=1.5)
ax1.set_ylabel("ΔT$_{max}$ (°C)", color="#6A1B9A")
ax1.set_xticks(vi_tri)
ax1.set_xticklabels(ten_ngan)
ax1.bar_label(c1, fmt="%.1f", fontsize=8.5)

ax2 = ax1.twinx()
c2 = ax2.bar(vi_tri + rong / 2, [t[1] for t in tom_tat], rong,
             color="#C62828", label="T$_{max}$ (°C)")
ax2.axhline(NGUONG_TMAX, color="#C62828", linestyle="--", linewidth=1.5)
ax2.set_ylabel("T$_{max}$ tại tâm (°C)", color="#C62828")
ax2.set_ylim(0, 90)
ax2.grid(False)
ax2.bar_label(c2, fmt="%.1f", fontsize=8.5)

ax1.set_title("Hình 8. Hiệu quả các biện pháp: ΔT giảm nhưng T$_{max}$ tăng")
luu(fig, "Hinh_8_hieu_qua_bien_phap.png")

print("\nBang tom tat de doi chieu:")
print(f"{'Kich ban':<32} {'Tmax':>7} {'dTmax':>7} {'k':>6}")
for ten, Tm, dTm, k in tom_tat:
    print(f"{ten:<32} {Tm:>7.1f} {dTm:>7.1f} {k:>6.2f}")
print(f"\nDa xuat xong toan bo hinh vao thu muc '{THU_MUC}/'")
