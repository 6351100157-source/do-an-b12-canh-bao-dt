# -*- coding: utf-8 -*-
"""
Kiem thu cac kich ban thi cong - dung de kiem tra module tinh toan
va de lay so lieu viet Chuong 4 + Chuong 6 cua thuyet minh.
"""
import copy
from nhiet_btkl import ThongSoDauVao, mo_phong_truong_nhiet, tong_hop_ket_qua

goc = ThongSoDauVao()

kich_ban = {
    "KB1 - Thi cong thong thuong (mat tren de ho)": dict(),

    "KB2 - Chi phu nilon + coppha go": dict(U_tren=5.2),

    "KB3 - Phu bao tai am + nilon + xop 20mm": dict(U_tren=1.7),

    "KB4 - KB3 + ha T0 ve 28 oC (dung da vay)": dict(U_tren=1.7,
                                                     nhiet_do_bt_tuoi=28.0),

    "KB5 - KB4 + tang tro bay len 30% (XM 280, TB 120)":
        dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0,
             luong_xi_mang=280.0, luong_tro_bay=120.0),

    "KB6 - KB5 + chia 2 lop do (chieu day 1.25 m)":
        dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0,
             luong_xi_mang=280.0, luong_tro_bay=120.0,
             chieu_day=1.25),
}

print("=" * 104)
print(f"{'Kich ban':<52} {'dT_ad':>7} {'Tmax':>7} {'t_peak':>7} "
      f"{'dTmax':>7} {'MTmax':>7} {'k_min':>7} {'Dat?':>6}")
print("=" * 104)

for ten, sua in kich_ban.items():
    ts = copy.deepcopy(goc)
    for k, v in sua.items():
        setattr(ts, k, v)

    df, _, _, info = mo_phong_truong_nhiet(ts)
    kq = tong_hop_ket_qua(df)

    dat = "DAT" if (kq["dat_dT"] and kq["dat_MT"] and kq["dat_Tmax"]) else "KHONG"
    print(f"{ten:<52} {info['dT_ad_vo_cuc']:>7.1f} {kq['T_max_tam']:>7.1f} "
          f"{kq['thoi_diem_T_max']:>7.0f} {kq['dT_max']:>7.1f} "
          f"{kq['MT_max']:>7.1f} {kq['he_so_an_toan_min']:>7.2f} {dat:>6}")

print("=" * 104)
print("Ghi chu: dT_ad [oC] | Tmax tai tam [oC] | t_peak [gio] | "
      "dTmax [oC] | MTmax [oC/m] | k_min = he so an toan chong nut")
