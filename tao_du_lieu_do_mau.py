# -*- coding: utf-8 -*-
"""
===============================================================================
 TAO FILE DU LIEU QUAN TRAC MAU (du_lieu_do_mau.csv)
-------------------------------------------------------------------------------
 File nay tao ra mot chuoi so lieu "do duoc tai hien truong" gia dinh,
 dung de thu nghiem Tab "Giam sat du lieu do" cua ung dung web.

 Cach tao: chay mo phong truong nhiet, sau do cong them NHIEU NGAU NHIEN
 mo phong sai so cua dau do (+-0,4 oC) va sai lech thuc te so voi ly thuyet.

 Cach chay:   python tao_du_lieu_do_mau.py
===============================================================================
"""

import numpy as np
import pandas as pd

from nhiet_btkl import ThongSoDauVao, mo_phong_truong_nhiet

# Dat hat giong ngau nhien de ket qua lap lai duoc (quan trong khi bao ve)
np.random.seed(2026)

# --- Kich ban duoc chon lam "thuc te": da phu nilon + coppha go -------------
ts = ThongSoDauVao()
ts.U_tren = 5.2                 # Co che phu nhung chua du
ts.thoi_gian_mo_phong = 168     # Quan trac 7 ngay

df, _, _, _ = mo_phong_truong_nhiet(ts)

# --- Lay mau theo chu ky 2 gio (thuc te doc 15 phut/lan, o day rut gon) -----
df_do = df[df["Gio"] % 2 == 0].copy().reset_index(drop=True)
n = len(df_do)

# --- Them nhieu ngau nhien mo phong sai so dau do ---------------------------
nhieu_tam = np.random.normal(0.0, 0.4, n)
nhieu_bm = np.random.normal(0.0, 0.6, n)       # Be mat dao dong manh hon
nhieu_kk = np.random.normal(0.0, 0.8, n)

# Them sai lech he thong: thuc te toa nhiet manh hon ly thuyet 3%
he_so_thuc_te = 1.03

ket_qua = pd.DataFrame({
    "Gio": df_do["Gio"].astype(int),
    "T_tam": np.round(
        ts.nhiet_do_bt_tuoi
        + (df_do["T_tam"] - ts.nhiet_do_bt_tuoi) * he_so_thuc_te
        + nhieu_tam, 1),
    "T_be_mat": np.round(df_do["T_mat_tren"] + nhieu_bm, 1),
    "T_khong_khi": np.round(df_do["T_khong_khi"] + nhieu_kk, 1),
})

ket_qua.to_csv("du_lieu_do_mau.csv", index=False, encoding="utf-8-sig")

dT = ket_qua["T_tam"] - ket_qua["T_be_mat"]
print("Da tao file: du_lieu_do_mau.csv")
print(f"  So ban ghi        : {len(ket_qua)} (chu ky 2 gio, 7 ngay)")
print(f"  T_tam lon nhat    : {ket_qua['T_tam'].max():.1f} oC")
print(f"  dT lon nhat       : {dT.max():.1f} oC tai gio thu "
      f"{int(ket_qua.loc[dT.idxmax(), 'Gio'])}")
print(f"  So lan dT >= 20 oC: {(dT >= 20).sum()} / {len(dT)}")
