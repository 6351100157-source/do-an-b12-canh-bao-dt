# -*- coding: utf-8 -*-
"""
===============================================================================
 MODULE LOI TINH TOAN NHIET BE TONG KHOI LON
 Do an mon hoc: Cong nghe va Quan ly xay dung nang cao - De tai B12
 Noi dung: Mo phong truong nhiet thuy hoa va canh bao chenh lech nhiet do dT
===============================================================================

 File nay CHI chua phan TINH TOAN, khong chua giao dien.
 File giao dien web (app.py) se goi cac ham trong file nay.

 Tai sao tach lam 2 file?
   - De kiem tra phan tinh toan rieng, khong phu thuoc giao dien
   - Giang vien co the chay thu phan tinh toan bang 1 dong lenh
   - Khi sua cong thuc chi can sua 1 cho

 CO SO LY THUYET:
   1) Phuong trinh truyen nhiet 1 chieu co nguon nhiet noi sinh:
         dT/dt = a * d2T/dx2 + q(t) / (rho * c)
      voi a = lambda / (rho * c)  -- he so khuech tan nhiet [m2/h]

   2) Giai bang phuong phap SAI PHAN HUU HAN HIEN (explicit FDM)

   3) Tieu chi kiem soat (TCVN 9341:2012 / TCXDVN 305:2004 / TCVN 14334:2025):
         - Chenh lech nhiet do tam - be mat:  dT <= 20 oC
         - Mo dun chenh lech nhiet do:        MT <= 50 oC/m
         - Nhiet do lon nhat trong khoi:      Tmax <= 70 oC (phong ngua DEF)
===============================================================================
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass


# =============================================================================
# PHAN 1 - CAC HANG SO VA NGUONG KIEM SOAT THEO TIEU CHUAN
# =============================================================================

NGUONG_DT = 20.0        # Chenh lech nhiet do gioi han [oC] - TCVN 9341:2012
NGUONG_MT = 50.0        # Mo dun chenh lech nhiet do gioi han [oC/m]
NGUONG_TMAX = 70.0      # Nhiet do lon nhat cho phep trong khoi [oC]

# An nhiet nong chay cua nuoc da, quy doi ra do C (334 kJ/kg / 4.187 kJ/kg.K)
AN_NHIET_DA = 79.8      # [oC.kg/kg]


# =============================================================================
# PHAN 2 - CAU TRUC DU LIEU DAU VAO
# =============================================================================

@dataclass
class ThongSoDauVao:
    """
    Gom toan bo so lieu dau vao cua bai toan vao 1 cho cho de quan ly.

    Dung @dataclass de khong phai viet ham __init__ thu cong.
    Moi thuoc tinh deu co GIA TRI MAC DINH = bo so lieu dai mong 12x10x2.5 m.
    """

    # --- 2.1. Kich thuoc ket cau -------------------------------------------
    chieu_day: float = 2.50         # H - chieu cao (chieu day) khoi do [m]
    chieu_dai: float = 12.0         # D [m] - dung de tinh khoi luong be tong
    chieu_rong: float = 10.0        # R [m]

    # --- 2.2. Cap phoi be tong (cho 1 m3) ----------------------------------
    luong_xi_mang: float = 320.0    # C - luong xi mang [kg/m3]
    luong_tro_bay: float = 80.0     # F - luong tro bay [kg/m3]
    nhiet_thuy_hoa_xm: float = 350.0  # Hu cua xi mang [kJ/kg]
    he_so_tro_bay: float = 0.30     # Tro bay toa nhiet bang 30% xi mang

    # --- 2.3. Thong so nhiet vat ly cua be tong ----------------------------
    khoi_luong_the_tich: float = 2400.0   # rho [kg/m3]
    nhiet_dung_rieng: float = 1.00        # c [kJ/(kg.K)]
    he_so_dan_nhiet: float = 2.60         # lambda [W/(m.K)]

    # --- 2.4. Duong cong toa nhiet (mo hinh Schindler - Folliard) ----------
    # dT_ad(t) = dT_ad_vo_cuc * exp( -(tau/t)^beta )
    tau: float = 22.0               # Hang so thoi gian [gio]
    beta: float = 1.10              # Hang so hinh dang duong cong [-]

    # --- 2.5. Nhiet do ban dau va moi truong -------------------------------
    nhiet_do_bt_tuoi: float = 32.0  # T0 - nhiet do be tong tuoi khi do [oC]
    nhiet_kk_trung_binh: float = 30.0   # Nhiet do khong khi trung binh [oC]
    bien_do_nhiet_kk: float = 5.0   # Bien do dao dong ngay dem [oC]
    nhiet_do_dat: float = 28.0      # Nhiet do nen dat duoi day dai [oC]

    # --- 2.6. He so truyen nhiet cua bien ----------------------------------
    U_tren: float = 13.6            # Mat tren (hoac lop che phu) [W/(m2.K)]
    U_duoi: float = 1.50            # Mat duoi (be tong lot + dat) [W/(m2.K)]

    # --- 2.7. Thong so co hoc (de kiem tra ung suat keo nhiet) -------------
    mo_dun_dan_hoi_28: float = 32500.0  # E28 [MPa]
    he_so_tu_bien: float = 2.00         # phi [-]
    he_so_gian_no_nhiet: float = 10e-6  # alpha_c [1/oC]
    cuong_do_keo_28: float = 1.20       # Rbt,28 [MPa]
    he_so_kiem_che: float = 0.50        # R - he so kiem che bien dang [-]

    # --- 2.8. Thong so luoi tinh toan --------------------------------------
    so_lop_chia: int = 20           # So doan chia theo chieu day
    thoi_gian_mo_phong: int = 240   # Tong thoi gian mo phong [gio] = 10 ngay

    # --- Cac dai luong dan xuat (tinh tu cac thong so tren) ----------------
    @property
    def the_tich(self) -> float:
        """The tich be tong cua khoi do [m3]."""
        return self.chieu_dai * self.chieu_rong * self.chieu_day

    @property
    def he_so_khuech_tan(self) -> float:
        """
        He so khuech tan nhiet a = lambda / (rho * c), don vi [m2/h].

        Luu y don vi:
          lambda [W/(m.K)] = [J/(s.m.K)] -> nhan 3.6 de doi sang [kJ/(h.m.K)]
          rho*c [kJ/(m3.K)]
        => a = 3.6 * lambda / (rho * c)  [m2/h]
        """
        return 3.6 * self.he_so_dan_nhiet / (
            self.khoi_luong_the_tich * self.nhiet_dung_rieng
        )

    @property
    def nhiet_dung_the_tich(self) -> float:
        """Nhiet dung the tich rho*c [kJ/(m3.K)]."""
        return self.khoi_luong_the_tich * self.nhiet_dung_rieng

    @property
    def do_tang_nhiet_doan_nhiet(self) -> float:
        """
        Do tang nhiet doan nhiet toan phan dT_ad [oC].

            dT_ad = (C * Hu + F * k * Hu) / (rho * c)

        Day la do tang nhiet neu khoi be tong KHONG trao doi nhiet voi
        ben ngoai (truong hop bat loi nhat ve ly thuyet).
        """
        nhiet_sinh_ra = (
            self.luong_xi_mang * self.nhiet_thuy_hoa_xm
            + self.luong_tro_bay * self.he_so_tro_bay * self.nhiet_thuy_hoa_xm
        )  # [kJ/m3]
        return nhiet_sinh_ra / self.nhiet_dung_the_tich


# =============================================================================
# PHAN 3 - CAC HAM TINH TOAN THANH PHAN
# =============================================================================

def tinh_nhiet_do_be_tong_tuoi(
    T_cot_lieu: float, M_cot_lieu: float,
    T_xi_mang: float, M_xi_mang: float,
    T_nuoc: float, M_nuoc: float,
    M_nuoc_da: float = 0.0,
    T_nuoc_da: float = 0.0,
) -> float:
    """
    Tinh nhiet do be tong tuoi T0 theo phuong trinh can bang nhiet (ACI 305R).

                0.22*(Ta*Ma + Tc*Mc) + Tw*Mw + Ti*Mi - 79.8*Mi
        T0 = ---------------------------------------------------
                    0.22*(Ma + Mc) + Mw + Mi

    Trong do:
        0.22 la ty so nhiet dung rieng cua cot lieu/xi mang so voi nuoc
        79.8 la an nhiet nong chay cua nuoc da quy doi ra oC

    Tham so:
        T_cot_lieu, M_cot_lieu : nhiet do [oC] va khoi luong cot lieu [kg]
        T_xi_mang, M_xi_mang   : nhiet do [oC] va khoi luong xi mang [kg]
        T_nuoc, M_nuoc         : nhiet do [oC] va khoi luong nuoc tron [kg]
        M_nuoc_da              : khoi luong nuoc da thay the nuoc [kg]
        T_nuoc_da              : nhiet do nuoc da [oC], thuong lay 0

    Tra ve:
        T0 : nhiet do be tong tuoi [oC]
    """
    tu_so = (
        0.22 * (T_cot_lieu * M_cot_lieu + T_xi_mang * M_xi_mang)
        + T_nuoc * M_nuoc
        + T_nuoc_da * M_nuoc_da
        - AN_NHIET_DA * M_nuoc_da
    )
    mau_so = 0.22 * (M_cot_lieu + M_xi_mang) + M_nuoc + M_nuoc_da
    return tu_so / mau_so


def duong_cong_doan_nhiet(t_gio, dT_ad_vo_cuc: float,
                          tau: float, beta: float):
    """
    Duong cong do tang nhiet doan nhiet theo thoi gian (Schindler - Folliard).

        dT_ad(t) = dT_ad_vo_cuc * exp( -(tau/t)^beta )

    Mo hinh nay mo ta dung thuc te hon ham mu don gian vi no the hien duoc
    GIAI DOAN CAM UNG (vai gio dau xi mang gan nhu chua toa nhiet).

    Tham so:
        t_gio         : thoi gian [gio], co the la so hoac mang numpy
        dT_ad_vo_cuc  : do tang nhiet doan nhiet toan phan [oC]
        tau           : hang so thoi gian [gio]
        beta          : hang so hinh dang [-]

    Tra ve:
        dT_ad(t) [oC]
    """
    t = np.asarray(t_gio, dtype=float)
    # Tranh chia cho 0 tai t = 0
    t = np.where(t <= 1e-6, 1e-6, t)
    return dT_ad_vo_cuc * np.exp(-((tau / t) ** beta))


def ty_le_phat_trien_cuong_do(t_gio, a_aci: float = 4.0, b_aci: float = 0.85):
    """
    Ty le phat trien cuong do be tong theo tuoi (ACI 209):

        f(t) / f(28) = t / (a + b*t)      voi t tinh bang NGAY

    Dung de xac dinh cuong do chiu keo Rbt(t) va mo dun dan hoi E(t)
    tai thoi diem dang xet, phuc vu kiem tra nut.
    """
    t_ngay = np.asarray(t_gio, dtype=float) / 24.0
    t_ngay = np.where(t_ngay <= 1e-6, 1e-6, t_ngay)
    return t_ngay / (a_aci + b_aci * t_ngay)


def nhiet_do_khong_khi(t_gio, T_tb: float, bien_do: float):
    """
    Mo hinh hoa dao dong nhiet do khong khi theo chu ky ngay dem:

        T_kk(t) = T_tb + A * sin( 2*pi*(t - 8) / 24 )

    Chon pha -8 gio de nhiet do cuc dai roi vao khoang 14h chieu
    (sin dat cuc dai khi t = 14).
    """
    t = np.asarray(t_gio, dtype=float)
    return T_tb + bien_do * np.sin(2.0 * np.pi * (t - 8.0) / 24.0)


# =============================================================================
# PHAN 4 - HAM MO PHONG TRUONG NHIET (TRAI TIM CUA CHUONG TRINH)
# =============================================================================

def mo_phong_truong_nhiet(ts: ThongSoDauVao):
    """
    Mo phong dien bien nhiet do trong khoi be tong theo thoi gian
    bang phuong phap SAI PHAN HUU HAN HIEN (explicit finite difference).

    SO DO LUOI (truc x huong len tren):

        nut N  ---- mat tren khoi be tong (tiep xuc khong khi qua lop che phu)
        nut N-1
          ...
        nut 1
        nut 0  ---- day dai (tiep xuc be tong lot + nen dat)

    PHUONG TRINH SAI PHAN:

      * Nut ben trong (i = 1 .. N-1):
            T_i(n+1) = T_i(n) + Fo*[T_(i-1) - 2*T_i + T_(i+1)] + dq_i

      * Nut bien tren (i = N), can bang nang luong nua o luoi:
            T_N(n+1) = T_N(n) + 2*Fo*[T_(N-1) - T_N]
                             + 2*Fo*Bi_tren*[T_kk - T_N] + dq_N

      * Nut bien duoi (i = 0): tuong tu voi Bi_duoi va T_dat

      Trong do:
            Fo = a*dt/dx^2     (so Fourier luoi)
            Bi = U*dx/lambda   (so Biot luoi)
            dq = do tang nhiet do nguon noi sinh trong buoc thoi gian dt

    DIEU KIEN ON DINH (bat buoc, neu vi pham ket qua se "no"):
            Fo * (1 + Bi_max) <= 0.5

    Tra ve:
        df     : DataFrame ket qua theo tung gio
        T_luoi : mang 2 chieu [so_gio+1, N+1] - nhiet do tai moi nut, moi gio
        x      : toa do cac nut [m]
    """

    # -------------------------------------------------------------------
    # BUOC 1: Thiet lap luoi khong gian
    # -------------------------------------------------------------------
    N = ts.so_lop_chia                      # So doan chia
    dx = ts.chieu_day / N                   # Buoc luoi [m]
    x = np.linspace(0.0, ts.chieu_day, N + 1)   # Toa do N+1 nut

    a = ts.he_so_khuech_tan                 # [m2/h]
    rho_c = ts.nhiet_dung_the_tich          # [kJ/(m3.K)]

    # So Biot luoi cua 2 bien (U doi tu W/(m2.K) sang kJ/(h.m2.K): nhan 3.6)
    Bi_tren = 3.6 * ts.U_tren * dx / (3.6 * ts.he_so_dan_nhiet)
    Bi_duoi = 3.6 * ts.U_duoi * dx / (3.6 * ts.he_so_dan_nhiet)
    Bi_max = max(Bi_tren, Bi_duoi)

    # -------------------------------------------------------------------
    # BUOC 2: Tu dong chon buoc thoi gian thoa dieu kien on dinh
    # -------------------------------------------------------------------
    # Tu Fo*(1+Bi) <= 0.5  =>  dt <= 0.5*dx^2 / (a*(1+Bi))
    dt_gioi_han = 0.5 * dx ** 2 / (a * (1.0 + Bi_max))
    # Lay he so an toan 0.4 va lam tron de 1 gio chia het cho dt
    so_buoc_moi_gio = int(np.ceil(1.0 / (0.4 * dt_gioi_han)))
    so_buoc_moi_gio = max(so_buoc_moi_gio, 1)
    dt = 1.0 / so_buoc_moi_gio              # [gio]

    Fo = a * dt / dx ** 2                   # So Fourier luoi

    # -------------------------------------------------------------------
    # BUOC 3: Dieu kien ban dau - toan khoi o nhiet do be tong tuoi T0
    # -------------------------------------------------------------------
    T = np.full(N + 1, ts.nhiet_do_bt_tuoi, dtype=float)

    so_gio = ts.thoi_gian_mo_phong
    T_luoi = np.zeros((so_gio + 1, N + 1))  # Luu ket qua tung gio
    T_luoi[0, :] = T

    dT_ad_inf = ts.do_tang_nhiet_doan_nhiet

    # -------------------------------------------------------------------
    # BUOC 4: Vong lap theo thoi gian
    # -------------------------------------------------------------------
    t_hien_tai = 0.0
    for gio in range(1, so_gio + 1):
        for _ in range(so_buoc_moi_gio):

            # (a) Do tang nhiet do nguon noi sinh trong buoc dt:
            #     lay hieu cua duong cong doan nhiet tai 2 thoi diem
            dq = (
                duong_cong_doan_nhiet(t_hien_tai + dt, dT_ad_inf,
                                      ts.tau, ts.beta)
                - duong_cong_doan_nhiet(t_hien_tai, dT_ad_inf,
                                        ts.tau, ts.beta)
            )
            dq = float(dq)

            # (b) Nhiet do khong khi tai thoi diem dang xet
            T_kk = float(nhiet_do_khong_khi(
                t_hien_tai, ts.nhiet_kk_trung_binh, ts.bien_do_nhiet_kk))

            T_moi = T.copy()

            # (c) Cac nut ben trong
            T_moi[1:N] = (
                T[1:N] + Fo * (T[0:N - 1] - 2.0 * T[1:N] + T[2:N + 1]) + dq
            )

            # (d) Nut bien TREN (tiep xuc khong khi qua lop che phu)
            T_moi[N] = (
                T[N]
                + 2.0 * Fo * (T[N - 1] - T[N])
                + 2.0 * Fo * Bi_tren * (T_kk - T[N])
                + dq
            )

            # (e) Nut bien DUOI (tiep xuc be tong lot + nen dat)
            T_moi[0] = (
                T[0]
                + 2.0 * Fo * (T[1] - T[0])
                + 2.0 * Fo * Bi_duoi * (ts.nhiet_do_dat - T[0])
                + dq
            )

            T = T_moi
            t_hien_tai += dt

        T_luoi[gio, :] = T

    # -------------------------------------------------------------------
    # BUOC 5: Trich xuat cac dai luong can danh gia
    # -------------------------------------------------------------------
    gio_arr = np.arange(0, so_gio + 1, dtype=float)

    i_tam = N // 2                          # Nut giua chieu day = tam khoi
    T_tam = T_luoi[:, i_tam]
    T_mat_tren = T_luoi[:, N]
    T_mat_duoi = T_luoi[:, 0]
    T_kk_arr = nhiet_do_khong_khi(
        gio_arr, ts.nhiet_kk_trung_binh, ts.bien_do_nhiet_kk)

    # Nhiet do lon nhat trong toan khoi tai moi thoi diem
    T_max_khoi = T_luoi.max(axis=1)

    # Chenh lech nhiet do tam - be mat (lay be mat BAT LOI nhat = nho nhat)
    T_be_mat = np.minimum(T_mat_tren, T_mat_duoi)
    dT = T_tam - T_be_mat

    # Mo dun chenh lech nhiet do MT [oC/m]:
    # chenh nhiet giua 2 diem cach nhau 1 m, lay gia tri lon nhat
    MT = _tinh_mo_dun_chenh_nhiet(T_luoi, x)

    # Toc do bien thien cua dT [oC/gio] - dung cho canh bao som
    toc_do_dT = np.gradient(dT, gio_arr)

    # Kiem tra ung suat keo nhiet
    ty_le = ty_le_phat_trien_cuong_do(gio_arr)
    Rbt_t = ts.cuong_do_keo_28 * ty_le                      # [MPa]
    E_t = ts.mo_dun_dan_hoi_28 * np.sqrt(ty_le)             # [MPa]
    E_hieu_dung = E_t / (1.0 + ts.he_so_tu_bien)            # [MPa]
    ung_suat = (
        ts.he_so_kiem_che * E_hieu_dung
        * ts.he_so_gian_no_nhiet * dT
    )                                                        # [MPa]
    # He so an toan chong nut (tranh chia cho 0 o gio dau)
    he_so_an_toan = np.divide(
        Rbt_t, ung_suat,
        out=np.full_like(ung_suat, np.nan),
        where=ung_suat > 1e-6,
    )

    df = pd.DataFrame({
        "Gio": gio_arr.astype(int),
        "Ngay": gio_arr / 24.0,
        "T_tam": T_tam,
        "T_mat_tren": T_mat_tren,
        "T_mat_duoi": T_mat_duoi,
        "T_be_mat_batloi": T_be_mat,
        "T_khong_khi": T_kk_arr,
        "T_max_khoi": T_max_khoi,
        "dT": dT,
        "MT": MT,
        "toc_do_dT": toc_do_dT,
        "Rbt": Rbt_t,
        "ung_suat_keo": ung_suat,
        "he_so_an_toan": he_so_an_toan,
    })

    thong_tin_luoi = {
        "so_nut": N + 1,
        "dx": dx,
        "dt": dt,
        "Fo": Fo,
        "Bi_tren": Bi_tren,
        "Bi_duoi": Bi_duoi,
        "kiem_tra_on_dinh": Fo * (1.0 + Bi_max),
        "he_so_khuech_tan": a,
        "dT_ad_vo_cuc": dT_ad_inf,
    }

    return df, T_luoi, x, thong_tin_luoi


def _tinh_mo_dun_chenh_nhiet(T_luoi: np.ndarray, x: np.ndarray):
    """
    Tinh mo dun chenh lech nhiet do MT [oC/m] tai moi thoi diem.

    Dinh nghia theo TCXDVN 305:2004: muc chenh nhiet do giua HAI DIEM
    trong khoi be tong CACH NHAU 1 m.

    Cach lam: voi moi nut i, noi suy nhiet do tai diem cach no 1 m,
    lay tri tuyet doi cua hieu, roi lay gia tri lon nhat.
    Neu chieu day khoi < 1 m thi quy doi gradient ve 1 m.
    """
    so_gio = T_luoi.shape[0]
    H = x[-1] - x[0]
    MT = np.zeros(so_gio)

    for n in range(so_gio):
        T_n = T_luoi[n, :]
        if H >= 1.0:
            # Cac diem xuat phat sao cho diem thu hai van nam trong khoi
            x_dau = x[x <= (x[-1] - 1.0)]
            T_dau = np.interp(x_dau, x, T_n)
            T_cuoi = np.interp(x_dau + 1.0, x, T_n)
            MT[n] = np.max(np.abs(T_cuoi - T_dau)) if len(x_dau) else 0.0
        else:
            # Khoi mong: quy doi gradient lon nhat ve don vi oC/m
            MT[n] = np.max(np.abs(np.gradient(T_n, x)))
    return MT


# =============================================================================
# PHAN 5 - PHAN CAP CANH BAO
# =============================================================================

def phan_cap_canh_bao(dT: float, T_max: float, MT: float,
                      toc_do_dT: float = 0.0,
                      dT_du_bao_6h: float = None) -> dict:
    """
    Phan cap canh bao theo 4 muc dua tren cac tieu chi kiem soat nhiet.

    Tham so:
        dT            : chenh lech nhiet do tam - be mat hien tai [oC]
        T_max         : nhiet do lon nhat trong khoi hien tai [oC]
        MT            : mo dun chenh lech nhiet do hien tai [oC/m]
        toc_do_dT     : toc do bien thien cua dT [oC/gio]
        dT_du_bao_6h  : gia tri dT du bao sau 6 gio [oC] (neu co)

    Tra ve:
        dict gom: cap, mau, tieu_de, ly_do, hanh_dong
    """
    ly_do = []

    # ---- CAP 4: NGUY HIEM -------------------------------------------------
    if dT >= NGUONG_DT:
        ly_do.append(f"dT = {dT:.1f} oC >= {NGUONG_DT:.0f} oC")
    if MT >= NGUONG_MT:
        ly_do.append(f"MT = {MT:.1f} oC/m >= {NGUONG_MT:.0f} oC/m")
    if T_max >= NGUONG_TMAX:
        ly_do.append(f"Tmax = {T_max:.1f} oC >= {NGUONG_TMAX:.0f} oC")

    if ly_do:
        return {
            "cap": 4,
            "ten": "NGUY HIEM",
            "mau": "#C62828",
            "ly_do": "; ".join(ly_do),
            "hanh_dong": (
                "DUNG ngay viec thao coppha va go lop che phu. "
                "Phu kin toan bo be mat bang bao tai am + nilon + tam xop. "
                "Tang luu luong nuoc ong lam mat nhung GIU chenh nhiet "
                "nuoc vao - ra khong qua 10 oC. Bao chi huy truong cong "
                "truong, lap bien ban va hop xu ly ky thuat trong 2 gio."
            ),
        }

    # ---- CAP 3: CANH BAO --------------------------------------------------
    if dT_du_bao_6h is not None and dT_du_bao_6h >= NGUONG_DT:
        ly_do.append(f"Du bao dT sau 6 gio = {dT_du_bao_6h:.1f} oC >= 20 oC")
    if dT >= 18.0:
        ly_do.append(f"dT = {dT:.1f} oC, da vao vung 18 - 20 oC")

    if ly_do:
        return {
            "cap": 3,
            "ten": "CANH BAO",
            "mau": "#EF6C00",
            "ly_do": "; ".join(ly_do),
            "hanh_dong": (
                "Bo sung ngay lop giu nhiet be mat de nang nhiet do be mat. "
                "Kiem tra do kin cua lop phu o goc va canh khoi. "
                "Tang tan suat do len 10 phut/lan. "
                "Bao can bo ky thuat truc tiep phu trach."
            ),
        }

    # ---- CAP 2: CHU Y -----------------------------------------------------
    if dT >= 15.0:
        ly_do.append(f"dT = {dT:.1f} oC, da vao vung 15 - 18 oC")
    if toc_do_dT > 1.5:
        ly_do.append(f"Toc do tang dT = {toc_do_dT:.2f} oC/gio > 1.5 oC/gio")

    if ly_do:
        return {
            "cap": 2,
            "ten": "CHU Y",
            "mau": "#F9A825",
            "ly_do": "; ".join(ly_do),
            "hanh_dong": (
                "Tang tan suat do len 10 phut/lan. "
                "Kiem tra lai tinh trang lop che phu va do am be mat. "
                "Chuan bi san vat lieu giu nhiet du phong."
            ),
        }

    # ---- CAP 1: BINH THUONG -----------------------------------------------
    return {
        "cap": 1,
        "ten": "BINH THUONG",
        "mau": "#2E7D32",
        "ly_do": f"dT = {dT:.1f} oC < 15 oC, Tmax = {T_max:.1f} oC < 70 oC",
        "hanh_dong": (
            "Duy tri che do bao duong va che phu hien tai. "
            "Ghi nhat ky quan trac theo chu ky 15 phut/lan."
        ),
    }


def du_bao_dT(thoi_gian, gia_tri_dT, so_gio_du_bao: float = 6.0,
              cua_so_gio: float = 6.0):
    """
    Du bao gia tri dT sau mot so gio bang NGOAI SUY TUYEN TINH.

    Y tuong: lay cac diem do trong CUA SO THOI GIAN gan nhat, khop 1 duong
    thang bac nhat bang phuong phap binh phuong toi thieu, roi keo dai
    duong thang do ve phia truoc.

    Day chinh la diem tao nen "CANH BAO SOM": he thong bao truoc khi dT
    thuc su vuot nguong, cho doi thi cong co thoi gian xu ly.

    LUU Y VE THIET KE:
        Dung CUA SO THOI GIAN (vi du 6 gio gan nhat) chu khong dung
        SO DIEM CO DINH. Ly do: chu ky do co the thay doi (15 phut khi
        binh thuong, 5 phut khi canh bao). Neu dung so diem co dinh thi
        khi tang tan suat do, cua so hoi quy bi thu ngan lai va ket qua
        du bao se khac di - dieu nay khong hop ly ve mat ky thuat.

    Tham so:
        thoi_gian     : mang thoi gian [gio]
        gia_tri_dT    : mang gia tri dT tuong ung [oC]
        so_gio_du_bao : du bao truoc bao nhieu gio
        cua_so_gio    : do dai cua so du lieu dung de hoi quy [gio]

    Tra ve:
        gia tri dT du bao [oC], hoac None neu khong du du lieu
    """
    t = np.asarray(thoi_gian, dtype=float)
    y = np.asarray(gia_tri_dT, dtype=float)

    if len(t) < 2:
        return None

    # Chi lay cac diem nam trong cua so thoi gian gan nhat
    mask = t >= (t[-1] - cua_so_gio)
    t_cuoi = t[mask]
    y_cuoi = y[mask]

    # Can it nhat 2 diem moi khop duoc duong thang
    if len(t_cuoi) < 2:
        t_cuoi = t[-2:]
        y_cuoi = y[-2:]

    # Neu moi diem deu trung thoi gian thi khong hoi quy duoc
    if np.ptp(t_cuoi) < 1e-9:
        return float(y_cuoi[-1])

    # polyfit bac 1 -> tra ve [he_so_goc, he_so_tu_do]
    he_so_goc, he_so_tu_do = np.polyfit(t_cuoi, y_cuoi, 1)
    return float(he_so_goc * (t[-1] + so_gio_du_bao) + he_so_tu_do)


def ap_dung_do_tre(danh_sach_cap, so_lan_xac_nhan: int = 2):
    """
    Ap dung DO TRE (hysteresis) cho chuoi cap canh bao.

    VAN DE: nhiet do be mat dao dong theo chu ky ngay dem, nen dT co the
    dao qua dao lai quanh nguong. Neu de nguyen, he thong se lien tuc nhay
    cap 4 -> cap 3 -> cap 4 chi trong vai gio. Mot he canh bao "keu lien
    tuc" se bi doi thi cong bo qua - day la loi thiet ke thuong gap trong
    thuc te quan ly canh bao.

    NGUYEN TAC XU LY (theo thong le quan ly canh bao cong nghiep):
        - NANG cap: thuc hien NGAY LAP TUC (an toan la uu tien)
        - HA cap : chi thuc hien khi da co du 'so_lan_xac_nhan' lan do
                   lien tiep cho gia tri thap hon

    Tham so:
        danh_sach_cap   : danh sach cap canh bao tho [1..4] theo thu tu
        so_lan_xac_nhan : so lan do lien tiep can co de duoc ha cap

    Tra ve:
        danh sach cap canh bao sau khi loc do tre
    """
    ket_qua = []
    cap_hien_hanh = danh_sach_cap[0] if len(danh_sach_cap) else 1
    dem_ha = 0

    for cap_tho in danh_sach_cap:
        if cap_tho > cap_hien_hanh:
            # Nang cap ngay lap tuc
            cap_hien_hanh = cap_tho
            dem_ha = 0
        elif cap_tho < cap_hien_hanh:
            # De nghi ha cap -> phai dem du so lan xac nhan
            dem_ha += 1
            if dem_ha >= so_lan_xac_nhan:
                cap_hien_hanh = cap_tho
                dem_ha = 0
        else:
            dem_ha = 0
        ket_qua.append(cap_hien_hanh)

    return ket_qua


# =============================================================================
# PHAN 6 - HAM TONG HOP KET QUA
# =============================================================================

def tong_hop_ket_qua(df: pd.DataFrame) -> dict:
    """
    Trich xuat cac gia tri dac trung tu bang ket qua mo phong,
    phuc vu viet ket luan trong thuyet minh.
    """
    i_Tmax = int(df["T_tam"].idxmax())
    i_dTmax = int(df["dT"].idxmax())

    return {
        "T_max_tam": float(df["T_tam"].max()),
        "thoi_diem_T_max": float(df.loc[i_Tmax, "Gio"]),
        "T_be_mat_luc_do": float(df.loc[i_Tmax, "T_be_mat_batloi"]),
        "dT_max": float(df["dT"].max()),
        "thoi_diem_dT_max": float(df.loc[i_dTmax, "Gio"]),
        "MT_max": float(df["MT"].max()),
        "ung_suat_max": float(df["ung_suat_keo"].max()),
        "he_so_an_toan_min": float(np.nanmin(df["he_so_an_toan"].values)),
        "dat_dT": bool(df["dT"].max() < NGUONG_DT),
        "dat_MT": bool(df["MT"].max() < NGUONG_MT),
        "dat_Tmax": bool(df["T_tam"].max() < NGUONG_TMAX),
    }


# =============================================================================
# PHAN 7 - CHAY THU TRUC TIEP FILE NAY (de kiem tra nhanh)
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("KIEM TRA NHANH MODULE TINH TOAN NHIET BE TONG KHOI LON")
    print("=" * 70)

    ts = ThongSoDauVao()
    df, T_luoi, x, info = mo_phong_truong_nhiet(ts)
    kq = tong_hop_ket_qua(df)

    print(f"\nThe tich khoi do        : {ts.the_tich:.1f} m3")
    print(f"He so khuech tan nhiet a : {info['he_so_khuech_tan']:.5f} m2/h")
    print(f"Buoc luoi dx             : {info['dx']:.4f} m")
    print(f"Buoc thoi gian dt        : {info['dt']:.4f} gio")
    print(f"So Fourier Fo            : {info['Fo']:.4f}")
    print(f"Kiem tra on dinh Fo(1+Bi): {info['kiem_tra_on_dinh']:.4f} "
          f"(yeu cau <= 0.5)")
    print(f"Do tang nhiet doan nhiet : {info['dT_ad_vo_cuc']:.1f} oC")

    print(f"\nT max tai tam            : {kq['T_max_tam']:.1f} oC "
          f"tai gio thu {kq['thoi_diem_T_max']:.0f}")
    print(f"dT max                   : {kq['dT_max']:.1f} oC "
          f"tai gio thu {kq['thoi_diem_dT_max']:.0f}")
    print(f"MT max                   : {kq['MT_max']:.1f} oC/m")
    print(f"Ung suat keo lon nhat    : {kq['ung_suat_max']:.2f} MPa")
    print(f"He so an toan nho nhat   : {kq['he_so_an_toan_min']:.2f}")

    print(f"\nDat dT <= 20 oC          : {kq['dat_dT']}")
    print(f"Dat MT <= 50 oC/m        : {kq['dat_MT']}")
    print(f"Dat Tmax <= 70 oC        : {kq['dat_Tmax']}")
