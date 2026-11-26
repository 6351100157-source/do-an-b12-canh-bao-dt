# -*- coding: utf-8 -*-
"""
===============================================================================
 UNG DUNG WEB: HE THONG CANH BAO CHENH LECH NHIET DO (dT)
 TRONG THI CONG BE TONG KHOI LON
-------------------------------------------------------------------------------
 Do an mon hoc: Cong nghe va Quan ly xay dung nang cao
 De tai B12 - Nhiet be tong khoi lon (Canh bao dT) - Muc 70%
===============================================================================

 CACH CHAY CHUONG TRINH (xem chi tiet trong file huong_dan_chay.md):

     Buoc 1: Cai thu vien (chi lam 1 lan)
         pip install streamlit numpy pandas matplotlib

     Buoc 2: Mo cua so lenh tai thu muc chua file nay, go:
         streamlit run app.py

     Buoc 3: Trinh duyet se tu dong mo trang http://localhost:8501

-------------------------------------------------------------------------------
 CAU TRUC FILE:
     Phan 1 - Thiet lap trang va dinh dang
     Phan 2 - Thanh ben: nhap toan bo so lieu dau vao
     Phan 3 - Tab 1: Du bao truong nhiet va canh bao
     Phan 4 - Tab 2: Giam sat du lieu do thuc te
     Phan 5 - Tab 3: So sanh cac kich ban thi cong
     Phan 6 - Tab 4: Co so ly thuyet va tieu chuan
===============================================================================
"""

import io
import copy

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # Dung backend khong giao dien cho web
import matplotlib.pyplot as plt
import streamlit as st

# Nhap cac ham tinh toan tu file nhiet_btkl.py (phai nam cung thu muc)
from nhiet_btkl import (
    ThongSoDauVao,
    mo_phong_truong_nhiet,
    tong_hop_ket_qua,
    phan_cap_canh_bao,
    du_bao_dT,
    ap_dung_do_tre,
    tinh_nhiet_do_be_tong_tuoi,
    duong_cong_doan_nhiet,
    NGUONG_DT,
    NGUONG_MT,
    NGUONG_TMAX,
)


# =============================================================================
# PHAN 1 - THIET LAP TRANG
# =============================================================================

st.set_page_config(
    page_title="Canh bao dT - Be tong khoi lon",
    page_icon="🌡️",
    layout="wide",
)

# Dinh dang bieu do cho dong nhat toan chuong trinh
plt.rcParams["font.size"] = 10
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
plt.rcParams["figure.autolayout"] = True

st.title("🌡️ Hệ thống cảnh báo chênh lệch nhiệt độ ΔT")
st.caption(
    "Đồ án Công nghệ và Quản lý xây dựng nâng cao — Đề tài B12: "
    "Nhiệt bê tông khối lớn. "
    "Tiêu chí kiểm soát theo TCXDVN 305:2004 / TCVN 9341:2012 / "
    "TCVN 14334:2025."
)


# =============================================================================
# PHAN 2 - THANH BEN: NHAP SO LIEU DAU VAO
# =============================================================================

def nhap_so_lieu() -> ThongSoDauVao:
    """
    Ve toan bo cac o nhap lieu tren thanh ben va tra ve doi tuong ThongSoDauVao.

    Moi nhom so lieu duoc dat trong 1 expander cho gon gang.
    Gia tri mac dinh = bo so lieu dai mong 12 x 10 x 2,5 m.
    """
    ts = ThongSoDauVao()          # Khoi tao voi gia tri mac dinh

    st.sidebar.header("📋 Số liệu đầu vào")

    # ---- 2.1. Kich thuoc ket cau ------------------------------------------
    with st.sidebar.expander("1. Kích thước kết cấu", expanded=True):
        ts.chieu_dai = st.number_input(
            "Chiều dài D (m)", 1.0, 100.0, 12.0, 0.5)
        ts.chieu_rong = st.number_input(
            "Chiều rộng R (m)", 1.0, 100.0, 10.0, 0.5)
        ts.chieu_day = st.number_input(
            "Chiều dày / chiều cao H (m)", 0.5, 10.0, 2.5, 0.1,
            help="Đây là kích thước quyết định bài toán nhiệt. "
                 "Nếu phân lớp đổ thì nhập chiều dày 1 lớp.")
        st.info(f"Khối lượng bê tông: **{ts.the_tich:,.1f} m³**")

    # ---- 2.2. Cap phoi be tong --------------------------------------------
    with st.sidebar.expander("2. Cấp phối bê tông (cho 1 m³)"):
        ts.luong_xi_mang = st.number_input(
            "Lượng xi măng C (kg/m³)", 100.0, 600.0, 320.0, 10.0)
        ts.luong_tro_bay = st.number_input(
            "Lượng tro bay F (kg/m³)", 0.0, 300.0, 80.0, 10.0)
        ts.nhiet_thuy_hoa_xm = st.number_input(
            "Nhiệt thủy hóa xi măng Hu (kJ/kg)", 200.0, 500.0, 350.0, 10.0,
            help="PC40/PCB40 thường 330–370 kJ/kg. "
                 "Xi măng tỏa nhiệt thấp: 250–300 kJ/kg.")
        ts.he_so_tro_bay = st.slider(
            "Hệ số tỏa nhiệt của tro bay (so với xi măng)",
            0.0, 0.6, 0.30, 0.05)

        ckd = ts.luong_xi_mang + ts.luong_tro_bay
        ty_le_tb = ts.luong_tro_bay / ckd * 100 if ckd > 0 else 0
        st.info(
            f"Chất kết dính: **{ckd:,.0f} kg/m³**  \n"
            f"Tỷ lệ tro bay: **{ty_le_tb:.1f}%**  \n"
            f"Độ tăng nhiệt đoạn nhiệt ΔT_ad = "
            f"**{ts.do_tang_nhiet_doan_nhiet:.1f} °C**"
        )

    # ---- 2.3. Thong so nhiet vat ly ---------------------------------------
    with st.sidebar.expander("3. Thông số nhiệt vật lý"):
        ts.khoi_luong_the_tich = st.number_input(
            "Khối lượng thể tích ρ (kg/m³)", 2000.0, 2700.0, 2400.0, 10.0)
        ts.nhiet_dung_rieng = st.number_input(
            "Nhiệt dung riêng c (kJ/kg·K)", 0.80, 1.20, 1.00, 0.01)
        ts.he_so_dan_nhiet = st.number_input(
            "Hệ số dẫn nhiệt λ (W/m·K)", 1.50, 3.50, 2.60, 0.05)
        st.info(
            f"Hệ số khuếch tán nhiệt a = λ/(ρ·c) = "
            f"**{ts.he_so_khuech_tan:.5f} m²/h**"
        )

    # ---- 2.4. Duong cong toa nhiet ----------------------------------------
    with st.sidebar.expander("4. Đường cong tỏa nhiệt"):
        ts.tau = st.number_input(
            "Hằng số thời gian τ (giờ)", 5.0, 60.0, 22.0, 1.0,
            help="τ càng nhỏ thì nhiệt tỏa ra càng sớm.")
        ts.beta = st.number_input(
            "Hằng số hình dạng β", 0.5, 2.0, 1.10, 0.05)
        pct3 = float(duong_cong_doan_nhiet(72.0, 1.0, ts.tau, ts.beta)) * 100
        st.info(f"Nhiệt tỏa ra sau 3 ngày: **{pct3:.0f}%** tổng nhiệt "
                f"(thực tế thường 70–85%)")

    # ---- 2.5. Nhiet do ban dau va moi truong ------------------------------
    with st.sidebar.expander("5. Nhiệt độ ban đầu và môi trường",
                             expanded=True):
        dung_aci = st.checkbox(
            "Tính T₀ từ nhiệt độ vật liệu (ACI 305R)", value=False)

        if dung_aci:
            st.caption("Nhập nhiệt độ và khối lượng từng thành phần:")
            c1, c2 = st.columns(2)
            with c1:
                T_cl = st.number_input("T cốt liệu (°C)", 10.0, 50.0, 32.0)
                T_xm = st.number_input("T xi măng (°C)", 10.0, 80.0, 45.0)
                T_n = st.number_input("T nước (°C)", 0.0, 40.0, 28.0)
                M_da = st.number_input("Nước đá (kg/m³)", 0.0, 120.0, 0.0,
                                       5.0)
            with c2:
                M_cl = st.number_input("KL cốt liệu (kg/m³)", 0.0, 2500.0,
                                       1800.0, 10.0)
                M_xm = st.number_input("KL chất kết dính (kg/m³)", 0.0,
                                       700.0, 400.0, 10.0)
                M_n = st.number_input("KL nước (kg/m³)", 0.0, 300.0, 165.0,
                                      5.0)
            # Nuoc da thay the mot phan nuoc tron
            M_n_con_lai = max(M_n - M_da, 0.0)
            T0 = tinh_nhiet_do_be_tong_tuoi(
                T_cl, M_cl, T_xm, M_xm, T_n, M_n_con_lai, M_da, 0.0)
            ts.nhiet_do_bt_tuoi = T0
            st.success(f"→ T₀ tính được = **{T0:.1f} °C**")
        else:
            ts.nhiet_do_bt_tuoi = st.number_input(
                "Nhiệt độ bê tông tươi T₀ (°C)", 10.0, 45.0, 32.0, 0.5)

        ts.nhiet_kk_trung_binh = st.number_input(
            "Nhiệt độ không khí trung bình (°C)", 5.0, 45.0, 30.0, 0.5)
        ts.bien_do_nhiet_kk = st.number_input(
            "Biên độ dao động ngày đêm (°C)", 0.0, 15.0, 5.0, 0.5)
        ts.nhiet_do_dat = st.number_input(
            "Nhiệt độ nền đất (°C)", 10.0, 40.0, 28.0, 0.5)

    # ---- 2.6. Bien va che phu ---------------------------------------------
    with st.sidebar.expander("6. Che phủ và điều kiện biên", expanded=True):
        phuong_an = st.selectbox(
            "Phương án che phủ mặt trên",
            [
                "Để hở (không che phủ) — U = 13,6",
                "Nilon + cốp pha gỗ phủ phim — U = 5,2",
                "Bao tải ẩm + nilon + xốp PE 20 mm — U = 1,7",
                "Tự nhập giá trị U",
            ],
        )
        bang_U = {
            "Để hở (không che phủ) — U = 13,6": 13.6,
            "Nilon + cốp pha gỗ phủ phim — U = 5,2": 5.2,
            "Bao tải ẩm + nilon + xốp PE 20 mm — U = 1,7": 1.7,
        }
        if phuong_an == "Tự nhập giá trị U":
            ts.U_tren = st.number_input(
                "U mặt trên (W/m²·K)", 0.2, 30.0, 13.6, 0.1)
        else:
            ts.U_tren = bang_U[phuong_an]
            st.caption(f"U mặt trên = {ts.U_tren} W/m²·K")

        ts.U_duoi = st.number_input(
            "U mặt dưới (W/m²·K)", 0.2, 20.0, 1.50, 0.1,
            help="Đáy đài trên lớp bê tông lót + nền đất, U nhỏ.")

    # ---- 2.7. Thong so kiem tra nut ---------------------------------------
    with st.sidebar.expander("7. Thông số kiểm tra nứt"):
        ts.cuong_do_keo_28 = st.number_input(
            "Cường độ chịu kéo R_bt,28 (MPa)", 0.5, 3.0, 1.20, 0.05)
        ts.mo_dun_dan_hoi_28 = st.number_input(
            "Mô đun đàn hồi E₂₈ (MPa)", 20000.0, 45000.0, 32500.0, 500.0)
        ts.he_so_tu_bien = st.number_input(
            "Hệ số từ biến φ", 0.0, 4.0, 2.00, 0.1)
        ts.he_so_kiem_che = st.slider(
            "Hệ số kiềm chế biến dạng R", 0.1, 1.0, 0.50, 0.05,
            help="R = 1,0: kiềm chế hoàn toàn. "
                 "Đài móng trên nền cọc thường 0,4–0,6.")

    # ---- 2.8. Thong so luoi -----------------------------------------------
    with st.sidebar.expander("8. Thông số lưới tính toán"):
        ts.so_lop_chia = st.slider("Số đoạn chia theo chiều dày", 8, 60, 20, 2)
        ts.thoi_gian_mo_phong = st.slider(
            "Thời gian mô phỏng (giờ)", 72, 480, 240, 24)

    return ts


ts = nhap_so_lieu()


# =============================================================================
# HAM VE BIEU DO DUNG CHUNG
# =============================================================================

def ve_bieu_do_nhiet_do(df: pd.DataFrame):
    """Biểu đồ 1: diễn biến nhiệt độ tâm, bề mặt, không khí theo thời gian."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(df["Gio"], df["T_tam"], linewidth=2.2,
            color="#C62828", label="Tâm khối")
    ax.plot(df["Gio"], df["T_mat_tren"], linewidth=1.8,
            color="#1565C0", label="Bề mặt trên")
    ax.plot(df["Gio"], df["T_mat_duoi"], linewidth=1.5,
            color="#2E7D32", linestyle="--", label="Mặt dưới (đáy)")
    ax.plot(df["Gio"], df["T_khong_khi"], linewidth=1.2,
            color="#757575", linestyle=":", label="Không khí")
    ax.axhline(NGUONG_TMAX, color="#C62828", linestyle="-.", linewidth=1.2,
               label=f"Ngưỡng Tmax = {NGUONG_TMAX:.0f} °C")
    ax.set_xlabel("Thời gian (giờ)")
    ax.set_ylabel("Nhiệt độ (°C)")
    ax.set_title("Diễn biến nhiệt độ trong khối bê tông")
    ax.legend(loc="best", fontsize=8)
    return fig


def ve_bieu_do_dT(df: pd.DataFrame):
    """Biểu đồ 2: ΔT theo thời gian, có tô màu vùng vượt ngưỡng."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(df["Gio"], df["dT"], linewidth=2.4, color="#6A1B9A",
            label="ΔT = T_tâm − T_bề mặt")
    ax.axhline(NGUONG_DT, color="#C62828", linestyle="--", linewidth=1.6,
               label=f"Ngưỡng cho phép ΔT = {NGUONG_DT:.0f} °C")
    ax.axhline(18.0, color="#EF6C00", linestyle=":", linewidth=1.2,
               label="Ngưỡng cảnh báo 18 °C")
    ax.axhline(15.0, color="#F9A825", linestyle=":", linewidth=1.2,
               label="Ngưỡng chú ý 15 °C")
    # To mau vung vuot nguong
    ax.fill_between(df["Gio"], NGUONG_DT, df["dT"],
                    where=(df["dT"] > NGUONG_DT),
                    color="#C62828", alpha=0.18)
    ax.set_xlabel("Thời gian (giờ)")
    ax.set_ylabel("ΔT (°C)")
    ax.set_title("Chênh lệch nhiệt độ giữa tâm và bề mặt")
    ax.legend(loc="best", fontsize=8)
    return fig


def ve_bieu_do_ung_suat(df: pd.DataFrame):
    """Biểu đồ 3: ứng suất kéo nhiệt so với cường độ chịu kéo."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(df["Gio"], df["ung_suat_keo"], linewidth=2.2, color="#C62828",
            label="Ứng suất kéo nhiệt σ_t")
    ax.plot(df["Gio"], df["Rbt"], linewidth=2.2, color="#2E7D32",
            label="Cường độ chịu kéo R_bt(t)")
    ax.fill_between(df["Gio"], df["Rbt"], df["ung_suat_keo"],
                    where=(df["ung_suat_keo"] > df["Rbt"]),
                    color="#C62828", alpha=0.18, label="Vùng có nguy cơ nứt")
    ax.set_xlabel("Thời gian (giờ)")
    ax.set_ylabel("Ứng suất (MPa)")
    ax.set_title("Kiểm tra nguy cơ nứt do ứng suất kéo nhiệt")
    ax.legend(loc="best", fontsize=8)
    return fig


def ve_phan_bo_nhiet(T_luoi: np.ndarray, x: np.ndarray, danh_sach_gio):
    """Biểu đồ 4: phân bố nhiệt độ theo chiều dày tại một số thời điểm."""
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    mau = plt.cm.viridis(np.linspace(0, 0.9, len(danh_sach_gio)))
    for mau_i, gio in zip(mau, danh_sach_gio):
        gio = int(min(gio, T_luoi.shape[0] - 1))
        ax.plot(T_luoi[gio, :], x, linewidth=2, color=mau_i,
                label=f"{gio} giờ")
    ax.set_xlabel("Nhiệt độ (°C)")
    ax.set_ylabel("Cao độ tính từ đáy (m)")
    ax.set_title("Phân bố nhiệt độ theo chiều dày")
    ax.legend(loc="best", fontsize=8)
    return fig


def hien_thi_canh_bao(cb: dict):
    """Hiển thị khung cảnh báo với màu tương ứng cấp độ."""
    st.markdown(
        f"""
        <div style="background-color:{cb['mau']};padding:14px 18px;
                    border-radius:8px;color:white;">
            <div style="font-size:20px;font-weight:700;">
                CẤP {cb['cap']} — {cb['ten']}
            </div>
            <div style="font-size:14px;margin-top:6px;">
                <b>Lý do:</b> {cb['ly_do']}
            </div>
            <div style="font-size:14px;margin-top:6px;">
                <b>Hành động yêu cầu:</b> {cb['hanh_dong']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# CHAY MO PHONG (co luu dem de khong tinh lai khi khong doi so lieu)
# =============================================================================

@st.cache_data(show_spinner="Đang tính toán trường nhiệt...")
def chay_mo_phong(ts_dict: dict):
    """
    Chay mo phong. Nhan vao dict thay vi doi tuong de Streamlit
    co the bam (hash) duoc va luu dem ket qua.
    """
    ts_local = ThongSoDauVao(**ts_dict)
    return mo_phong_truong_nhiet(ts_local)


ts_dict = {k: v for k, v in ts.__dict__.items()}
df, T_luoi, x, info = chay_mo_phong(ts_dict)
kq = tong_hop_ket_qua(df)


# =============================================================================
# CAC TAB CHINH
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Dự báo trường nhiệt",
    "📡 Giám sát dữ liệu đo",
    "⚖️ So sánh kịch bản",
    "📚 Cơ sở lý thuyết",
])


# -----------------------------------------------------------------------------
# PHAN 3 - TAB 1: DU BAO TRUONG NHIET VA CANH BAO
# -----------------------------------------------------------------------------
with tab1:

    st.subheader("1. Kết quả tổng hợp")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("T_max tại tâm", f"{kq['T_max_tam']:.1f} °C",
              f"Giờ thứ {kq['thoi_diem_T_max']:.0f}")
    c2.metric("ΔT lớn nhất", f"{kq['dT_max']:.1f} °C",
              f"{kq['dT_max'] - NGUONG_DT:+.1f} so với ngưỡng",
              delta_color="inverse")
    c3.metric("M_T lớn nhất", f"{kq['MT_max']:.1f} °C/m",
              f"{kq['MT_max'] - NGUONG_MT:+.1f} so với ngưỡng",
              delta_color="inverse")
    c4.metric("Hệ số an toàn nứt", f"{kq['he_so_an_toan_min']:.2f}",
              "Yêu cầu ≥ 1,00",
              delta_color="off")

    # ---- Bang doi chieu tieu chuan ---------------------------------------
    st.markdown("**Đối chiếu với tiêu chí kiểm soát:**")
    bang_kt = pd.DataFrame({
        "Tiêu chí": [
            "Chênh lệch nhiệt độ ΔT",
            "Mô đun chênh lệch nhiệt độ M_T",
            "Nhiệt độ lớn nhất T_max",
            "Hệ số an toàn chống nứt k",
        ],
        "Giá trị tính được": [
            f"{kq['dT_max']:.1f} °C",
            f"{kq['MT_max']:.1f} °C/m",
            f"{kq['T_max_tam']:.1f} °C",
            f"{kq['he_so_an_toan_min']:.2f}",
        ],
        "Giới hạn": [
            f"≤ {NGUONG_DT:.0f} °C",
            f"≤ {NGUONG_MT:.0f} °C/m",
            f"≤ {NGUONG_TMAX:.0f} °C",
            "≥ 1,00",
        ],
        "Kết luận": [
            "ĐẠT" if kq["dat_dT"] else "KHÔNG ĐẠT",
            "ĐẠT" if kq["dat_MT"] else "KHÔNG ĐẠT",
            "ĐẠT" if kq["dat_Tmax"] else "KHÔNG ĐẠT",
            "ĐẠT" if kq["he_so_an_toan_min"] >= 1.0 else "KHÔNG ĐẠT",
        ],
    })
    st.dataframe(bang_kt, use_container_width=True, hide_index=True)

    tat_ca_dat = (kq["dat_dT"] and kq["dat_MT"] and kq["dat_Tmax"]
                  and kq["he_so_an_toan_min"] >= 1.0)
    if tat_ca_dat:
        st.success(
            "✅ Phương án thi công ĐẠT toàn bộ tiêu chí kiểm soát nhiệt."
        )
    else:
        st.error(
            "❌ Phương án thi công KHÔNG ĐẠT. "
            "Cần áp dụng biện pháp kiểm soát nhiệt — xem tab *So sánh kịch bản*."
        )

    st.divider()

    # ---- Bieu do ----------------------------------------------------------
    st.subheader("2. Biểu đồ diễn biến nhiệt độ")
    st.pyplot(ve_bieu_do_nhiet_do(df))

    st.subheader("3. Biểu đồ chênh lệch nhiệt độ ΔT")
    st.pyplot(ve_bieu_do_dT(df))

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("4. Kiểm tra nguy cơ nứt")
        st.pyplot(ve_bieu_do_ung_suat(df))
    with c2:
        st.subheader("5. Phân bố nhiệt theo chiều dày")
        mocs = [12, 24, 48, 72,
                int(kq["thoi_diem_T_max"]), 168,
                ts.thoi_gian_mo_phong]
        mocs = sorted(set(m for m in mocs if m <= ts.thoi_gian_mo_phong))
        st.pyplot(ve_phan_bo_nhiet(T_luoi, x, mocs))

    st.divider()

    # ---- Canh bao tai thoi diem bat loi nhat ------------------------------
    st.subheader("6. Cảnh báo tại thời điểm bất lợi nhất")
    i_xau = int(df["dT"].idxmax())
    cb = phan_cap_canh_bao(
        dT=float(df.loc[i_xau, "dT"]),
        T_max=float(df.loc[i_xau, "T_max_khoi"]),
        MT=float(df.loc[i_xau, "MT"]),
        toc_do_dT=float(df.loc[i_xau, "toc_do_dT"]),
    )
    st.caption(f"Thời điểm: giờ thứ {int(df.loc[i_xau, 'Gio'])} "
               f"({df.loc[i_xau, 'Ngay']:.1f} ngày sau khi đổ)")
    hien_thi_canh_bao(cb)

    st.divider()

    # ---- Bang so lieu chi tiet + tai ve -----------------------------------
    st.subheader("7. Bảng số liệu chi tiết")
    buoc_hien = st.select_slider(
        "Hiển thị theo bước (giờ)", [1, 2, 3, 6, 12, 24], value=6)
    df_hien = df[df["Gio"] % buoc_hien == 0].copy()
    cot_hien = ["Gio", "T_tam", "T_mat_tren", "T_mat_duoi", "T_khong_khi",
                "dT", "MT", "ung_suat_keo", "Rbt", "he_so_an_toan"]
    st.dataframe(
        df_hien[cot_hien].round(2),
        use_container_width=True, hide_index=True, height=320,
    )

    st.download_button(
        "⬇️ Tải toàn bộ kết quả (CSV) để đưa vào Phụ lục",
        data=df.round(3).to_csv(index=False).encode("utf-8-sig"),
        file_name="ketqua_mophong_nhiet.csv",
        mime="text/csv",
    )

    with st.expander("🔧 Thông tin kiểm tra mô hình số (đưa vào mục 4.4)"):
        st.dataframe(pd.DataFrame({
            "Thông số": ["Số nút lưới", "Bước lưới Δx (m)",
                         "Bước thời gian Δt (giờ)", "Số Fourier Fo",
                         "Số Biot mặt trên", "Số Biot mặt dưới",
                         "Kiểm tra ổn định Fo·(1+Bi)",
                         "Hệ số khuếch tán a (m²/h)",
                         "Độ tăng nhiệt đoạn nhiệt ΔT_ad (°C)"],
            "Giá trị": [info["so_nut"], round(info["dx"], 4),
                        round(info["dt"], 4), round(info["Fo"], 4),
                        round(info["Bi_tren"], 4),
                        round(info["Bi_duoi"], 4),
                        round(info["kiem_tra_on_dinh"], 4),
                        round(info["he_so_khuech_tan"], 5),
                        round(info["dT_ad_vo_cuc"], 2)],
        }), use_container_width=True, hide_index=True)
        if info["kiem_tra_on_dinh"] <= 0.5:
            st.success("Điều kiện ổn định Fo·(1+Bi) ≤ 0,5 được thỏa mãn.")
        else:
            st.error("Vi phạm điều kiện ổn định — hãy tăng số đoạn chia.")


# -----------------------------------------------------------------------------
# PHAN 4 - TAB 2: GIAM SAT DU LIEU DO THUC TE
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Giám sát dữ liệu quan trắc thực tế")
    st.markdown(
        "Tải lên file CSV ghi nhận từ hệ thống đầu đo tại hiện trường. "
        "File cần có các cột: **Gio**, **T_tam**, **T_be_mat** "
        "và (tùy chọn) **T_khong_khi**."
    )

    # Nut tai file mau de nguoi dung biet dinh dang
    mau_csv = pd.DataFrame({
        "Gio": [0, 6, 12, 18, 24],
        "T_tam": [32.0, 38.5, 46.2, 53.0, 58.4],
        "T_be_mat": [32.0, 35.1, 38.0, 40.2, 41.5],
        "T_khong_khi": [30.0, 33.5, 29.0, 26.5, 30.0],
    })
    st.download_button(
        "⬇️ Tải file CSV mẫu (để biết đúng định dạng)",
        data=mau_csv.to_csv(index=False).encode("utf-8-sig"),
        file_name="mau_du_lieu_do.csv",
        mime="text/csv",
    )

    file_tai_len = st.file_uploader("Chọn file CSV dữ liệu đo", type=["csv"])

    if file_tai_len is None:
        st.info("Chưa có file nào được tải lên. "
                "Bạn có thể dùng file `du_lieu_do_mau.csv` kèm theo đồ án.")
    else:
        try:
            # Doc file CSV. Dung encoding utf-8-sig de bo dau BOM ma Excel
            # thuong them vao dau file khi luu dang CSV UTF-8.
            dfd = pd.read_csv(file_tai_len, encoding="utf-8-sig")

            # Neu chi doc duoc 1 cot thi file co the dung dau ';' lam dau
            # phan cach (thuong gap khi Excel chay o dinh dang Viet Nam).
            if dfd.shape[1] == 1:
                file_tai_len.seek(0)
                dfd = pd.read_csv(file_tai_len, sep=";", encoding="utf-8-sig")

            # Chuan hoa ten cot (cho phep viet hoa/thuong, co dau cach, BOM)
            doi_ten = {}
            for c in dfd.columns:
                k = str(c).replace("﻿", "").strip().lower()
                k = k.replace(" ", "_")
                if k in ("gio", "giờ", "t", "thoi_gian", "time"):
                    doi_ten[c] = "Gio"
                elif k in ("t_tam", "ttam", "t_tâm", "tam"):
                    doi_ten[c] = "T_tam"
                elif k in ("t_be_mat", "t_bm", "tbm", "be_mat", "surface"):
                    doi_ten[c] = "T_be_mat"
                elif k in ("t_khong_khi", "t_kk", "tkk", "khong_khi", "air"):
                    doi_ten[c] = "T_khong_khi"
            dfd = dfd.rename(columns=doi_ten)

            thieu = [c for c in ["Gio", "T_tam", "T_be_mat"]
                     if c not in dfd.columns]
            if thieu:
                st.error(f"File thiếu các cột bắt buộc: {', '.join(thieu)}")
            else:
                # Tinh dT va toc do bien thien
                dfd = dfd.sort_values("Gio").reset_index(drop=True)
                dfd["dT"] = dfd["T_tam"] - dfd["T_be_mat"]
                dfd["toc_do_dT"] = np.gradient(
                    dfd["dT"].values, dfd["Gio"].values.astype(float))

                # Du bao dT sau 6 gio
                dT_du_bao = du_bao_dT(dfd["Gio"].values, dfd["dT"].values, 6.0)

                # --- Cac chi so hien tai ---
                hien_tai = dfd.iloc[-1]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("T_tâm hiện tại", f"{hien_tai['T_tam']:.1f} °C")
                c2.metric("T_bề mặt hiện tại",
                          f"{hien_tai['T_be_mat']:.1f} °C")
                c3.metric("ΔT hiện tại", f"{hien_tai['dT']:.1f} °C",
                          f"{hien_tai['dT'] - NGUONG_DT:+.1f} so với ngưỡng",
                          delta_color="inverse")
                c4.metric("Dự báo ΔT sau 6 giờ",
                          f"{dT_du_bao:.1f} °C" if dT_du_bao else "—",
                          f"Tốc độ {hien_tai['toc_do_dT']:+.2f} °C/giờ",
                          delta_color="off")

                # --- Canh bao ---
                st.markdown("**Cảnh báo tại thời điểm đo gần nhất:**")
                cb = phan_cap_canh_bao(
                    dT=float(hien_tai["dT"]),
                    T_max=float(hien_tai["T_tam"]),
                    MT=0.0,                 # Không đo được M_T từ 2 đầu đo
                    toc_do_dT=float(hien_tai["toc_do_dT"]),
                    dT_du_bao_6h=dT_du_bao,
                )
                hien_thi_canh_bao(cb)

                # --- So sanh do thuc te voi du bao mo phong ---
                st.subheader("So sánh số liệu đo với kết quả mô phỏng")
                fig, ax = plt.subplots(figsize=(9, 4.4))
                ax.plot(df["Gio"], df["dT"], linewidth=1.8, color="#9E9E9E",
                        linestyle="--", label="ΔT mô phỏng")
                ax.plot(dfd["Gio"], dfd["dT"], linewidth=2.4,
                        marker="o", markersize=3.5, color="#6A1B9A",
                        label="ΔT đo thực tế")
                ax.axhline(NGUONG_DT, color="#C62828", linestyle="--",
                           linewidth=1.6, label="Ngưỡng 20 °C")
                ax.set_xlabel("Thời gian (giờ)")
                ax.set_ylabel("ΔT (°C)")
                ax.set_title("Đối chiếu ΔT đo thực tế và ΔT mô phỏng")
                ax.legend(loc="best", fontsize=8)
                st.pyplot(fig)

                # --- Sai so giua mo phong va thuc do ---
                dT_mp = np.interp(dfd["Gio"].values,
                                  df["Gio"].values, df["dT"].values)
                sai_so = dfd["dT"].values - dT_mp
                c1, c2 = st.columns(2)
                c1.metric("Sai số trung bình",
                          f"{np.mean(sai_so):+.2f} °C")
                c2.metric("Sai số tuyệt đối lớn nhất",
                          f"{np.max(np.abs(sai_so)):.2f} °C")

                # --- Nhat ky canh bao toan bo chuoi do ---
                st.subheader("Nhật ký cảnh báo toàn bộ chuỗi đo")

                so_xac_nhan = st.slider(
                    "Số lần đo liên tiếp cần có để được hạ cấp cảnh báo "
                    "(độ trễ chống nhiễu)", 1, 5, 2,
                    help="Nâng cấp cảnh báo luôn thực hiện ngay lập tức. "
                         "Chỉ việc hạ cấp mới cần xác nhận, nhằm tránh "
                         "hệ thống báo động liên tục khi ΔT dao động "
                         "quanh ngưỡng.")

                nhat_ky = []
                cap_tho = []
                for i in range(len(dfd)):
                    db = du_bao_dT(dfd["Gio"].values[:i + 1],
                                   dfd["dT"].values[:i + 1], 6.0) \
                        if i >= 1 else None
                    c = phan_cap_canh_bao(
                        dT=float(dfd.loc[i, "dT"]),
                        T_max=float(dfd.loc[i, "T_tam"]),
                        MT=0.0,
                        toc_do_dT=float(dfd.loc[i, "toc_do_dT"]),
                        dT_du_bao_6h=db,
                    )
                    cap_tho.append(c["cap"])
                    nhat_ky.append({
                        "Giờ": dfd.loc[i, "Gio"],
                        "T_tâm": round(dfd.loc[i, "T_tam"], 1),
                        "T_bề mặt": round(dfd.loc[i, "T_be_mat"], 1),
                        "ΔT": round(dfd.loc[i, "dT"], 1),
                        "ΔT dự báo +6h": round(db, 1) if db else None,
                        "Cấp thô": c["cap"],
                        "Mức cảnh báo": c["ten"],
                        "Lý do": c["ly_do"],
                    })

                # Ap dung do tre de chong hien tuong nhay cap lien tuc
                cap_loc = ap_dung_do_tre(cap_tho, so_xac_nhan)
                ten_cap = {1: "BÌNH THƯỜNG", 2: "CHÚ Ý",
                           3: "CẢNH BÁO", 4: "NGUY HIỂM"}
                for i, cl in enumerate(cap_loc):
                    nhat_ky[i]["Cấp phát lệnh"] = cl
                    nhat_ky[i]["Mức phát lệnh"] = ten_cap[cl]

                so_lan_nhay_tho = sum(
                    1 for i in range(1, len(cap_tho))
                    if cap_tho[i] != cap_tho[i - 1])
                so_lan_nhay_loc = sum(
                    1 for i in range(1, len(cap_loc))
                    if cap_loc[i] != cap_loc[i - 1])
                c1, c2 = st.columns(2)
                c1.metric("Số lần đổi cấp khi chưa lọc", so_lan_nhay_tho)
                c2.metric("Số lần đổi cấp sau khi lọc độ trễ",
                          so_lan_nhay_loc,
                          f"{so_lan_nhay_loc - so_lan_nhay_tho:+d}",
                          delta_color="inverse")

                df_nk = pd.DataFrame(nhat_ky)
                st.dataframe(df_nk, use_container_width=True,
                             hide_index=True, height=300)

                st.download_button(
                    "⬇️ Tải nhật ký cảnh báo (CSV)",
                    data=df_nk.to_csv(index=False).encode("utf-8-sig"),
                    file_name="nhat_ky_canh_bao.csv",
                    mime="text/csv",
                )

                # Thong ke so lan vao tung cap
                st.markdown("**Thống kê số lần ở mỗi cấp cảnh báo "
                            "(sau khi lọc độ trễ):**")
                tk = df_nk["Mức phát lệnh"].value_counts().reset_index()
                tk.columns = ["Mức cảnh báo", "Số lần"]
                st.dataframe(tk, use_container_width=True, hide_index=True)

                # Bieu do truc quan hoa cap canh bao theo thoi gian
                fig, ax = plt.subplots(figsize=(9, 3.0))
                ax.step(df_nk["Giờ"], df_nk["Cấp thô"], where="post",
                        linewidth=1.2, color="#9E9E9E", linestyle="--",
                        label="Cấp thô (chưa lọc)")
                ax.step(df_nk["Giờ"], df_nk["Cấp phát lệnh"], where="post",
                        linewidth=2.4, color="#C62828",
                        label="Cấp phát lệnh (đã lọc độ trễ)")
                ax.set_yticks([1, 2, 3, 4])
                ax.set_yticklabels(["Bình thường", "Chú ý",
                                    "Cảnh báo", "Nguy hiểm"])
                ax.set_xlabel("Thời gian (giờ)")
                ax.set_title("Diễn biến cấp cảnh báo theo thời gian")
                ax.legend(loc="best", fontsize=8)
                st.pyplot(fig)

        except Exception as loi:
            st.error(f"Không đọc được file. Chi tiết lỗi: {loi}")


# -----------------------------------------------------------------------------
# PHAN 5 - TAB 3: SO SANH KICH BAN THI CONG
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("So sánh hiệu quả các biện pháp kiểm soát nhiệt")
    st.markdown(
        "Chương trình chạy lại mô hình với từng tổ hợp biện pháp, "
        "giữ nguyên các số liệu khác đang nhập ở thanh bên. "
        "Kết quả bảng này dùng trực tiếp cho Chương 6 của thuyết minh."
    )

    if st.button("▶️ Chạy so sánh 6 kịch bản", type="primary"):

        danh_sach = {
            "KB1 — Thi công thông thường, mặt trên để hở":
                dict(U_tren=13.6),
            "KB2 — Phủ nilon + cốp pha gỗ phủ phim":
                dict(U_tren=5.2),
            "KB3 — Phủ bao tải ẩm + nilon + xốp PE 20 mm":
                dict(U_tren=1.7),
            "KB4 — KB3 + hạ T₀ về 28 °C bằng đá vảy":
                dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0),
            "KB5 — KB4 + tăng tro bay lên 30% (XM 280 / TB 120)":
                dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0,
                     luong_xi_mang=280.0, luong_tro_bay=120.0),
            "KB6 — KB5 + chia 2 lớp đổ (mỗi lớp H/2)":
                dict(U_tren=1.7, nhiet_do_bt_tuoi=28.0,
                     luong_xi_mang=280.0, luong_tro_bay=120.0,
                     chieu_day=ts.chieu_day / 2.0),
        }

        ket_qua = []
        bang_chay = st.progress(0.0)
        luu_df = {}

        for i, (ten, sua) in enumerate(danh_sach.items()):
            d = dict(ts_dict)
            d.update(sua)
            df_i, _, _, info_i = chay_mo_phong(d)
            kq_i = tong_hop_ket_qua(df_i)
            luu_df[ten] = df_i

            dat = (kq_i["dat_dT"] and kq_i["dat_MT"] and kq_i["dat_Tmax"]
                   and kq_i["he_so_an_toan_min"] >= 1.0)
            ket_qua.append({
                "Kịch bản": ten,
                "ΔT_ad (°C)": round(info_i["dT_ad_vo_cuc"], 1),
                "T_max (°C)": round(kq_i["T_max_tam"], 1),
                "t_peak (giờ)": int(kq_i["thoi_diem_T_max"]),
                "ΔT_max (°C)": round(kq_i["dT_max"], 1),
                "M_T max (°C/m)": round(kq_i["MT_max"], 1),
                "k an toàn": round(kq_i["he_so_an_toan_min"], 2),
                "Kết luận": "ĐẠT" if dat else "KHÔNG ĐẠT",
            })
            bang_chay.progress((i + 1) / len(danh_sach))

        df_ss = pd.DataFrame(ket_qua)
        st.dataframe(df_ss, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Tải bảng so sánh (CSV)",
            data=df_ss.to_csv(index=False).encode("utf-8-sig"),
            file_name="so_sanh_kich_ban.csv",
            mime="text/csv",
        )

        # Bieu do so sanh dT cua cac kich ban
        fig, ax = plt.subplots(figsize=(10, 4.8))
        mau = plt.cm.tab10(np.linspace(0, 1, len(luu_df)))
        for mau_i, (ten, df_i) in zip(mau, luu_df.items()):
            ax.plot(df_i["Gio"], df_i["dT"], linewidth=2,
                    color=mau_i, label=ten.split(" — ")[0])
        ax.axhline(NGUONG_DT, color="#C62828", linestyle="--",
                   linewidth=1.8, label="Ngưỡng 20 °C")
        ax.set_xlabel("Thời gian (giờ)")
        ax.set_ylabel("ΔT (°C)")
        ax.set_title("So sánh ΔT giữa các kịch bản thi công")
        ax.legend(loc="best", fontsize=8, ncol=2)
        st.pyplot(fig)

        st.warning(
            "⚠️ **Lưu ý kỹ thuật quan trọng:** che phủ giữ nhiệt làm "
            "GIẢM ΔT nhưng đồng thời làm TĂNG nhiệt độ lớn nhất ở tâm. "
            "Vì vậy không thể chỉ dùng một biện pháp che phủ, mà phải kết "
            "hợp với hạ nhiệt độ bê tông tươi và giảm lượng xi măng để "
            "đồng thời thỏa mãn cả hai tiêu chí ΔT ≤ 20 °C và "
            "T_max ≤ 70 °C."
        )
    else:
        st.info("Nhấn nút phía trên để chạy so sánh.")


# -----------------------------------------------------------------------------
# PHAN 6 - TAB 4: CO SO LY THUYET
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Cơ sở lý thuyết và tiêu chuẩn áp dụng")

    st.markdown("#### 1. Phương trình truyền nhiệt")
    st.latex(r"\frac{\partial T}{\partial t} = a\,"
             r"\frac{\partial^2 T}{\partial x^2} + \frac{q(t)}{\rho c}"
             r"\qquad ; \qquad a = \frac{\lambda}{\rho c}")

    st.markdown("#### 2. Độ tăng nhiệt đoạn nhiệt")
    st.latex(r"\Delta T_{ad} = \frac{C \cdot H_u + F \cdot k_F \cdot H_u}"
             r"{\rho \cdot c}")
    st.latex(r"\Delta T_{ad}(t) = \Delta T_{ad,\infty}\cdot"
             r"\exp\left[-\left(\frac{\tau}{t}\right)^{\beta}\right]")

    st.markdown("#### 3. Sơ đồ sai phân hữu hạn hiện")
    st.latex(r"T_i^{n+1} = T_i^{n} + Fo\left(T_{i-1}^{n} - 2T_i^{n} "
             r"+ T_{i+1}^{n}\right) + \Delta q")
    st.latex(r"T_N^{n+1} = T_N^{n} + 2Fo\left(T_{N-1}^{n}-T_N^{n}\right) "
             r"+ 2Fo\,Bi\left(T_{kk}-T_N^{n}\right) + \Delta q")
    st.latex(r"Fo = \frac{a\,\Delta t}{\Delta x^{2}} \quad ; \quad "
             r"Bi = \frac{U\,\Delta x}{\lambda} \quad ; \quad "
             r"Fo\,(1+Bi) \leq 0{,}5")

    st.markdown("#### 4. Nhiệt độ bê tông tươi (ACI 305R)")
    st.latex(r"T_0 = \frac{0{,}22\,(T_aM_a + T_cM_c) + T_wM_w "
             r"+ T_iM_i - 79{,}8\,M_i}"
             r"{0{,}22\,(M_a+M_c) + M_w + M_i}")

    st.markdown("#### 5. Kiểm tra ứng suất kéo nhiệt")
    st.latex(r"\sigma_t(t) = R \cdot E_{eff}(t)\cdot \alpha_c \cdot "
             r"\Delta T(t) \quad ; \quad "
             r"E_{eff}(t) = \frac{E(t)}{1+\varphi}")
    st.latex(r"k = \frac{R_{bt}(t)}{\sigma_t(t)} \geq 1{,}0")

    st.markdown("#### 6. Tiêu chí kiểm soát và ngưỡng cảnh báo")
    st.dataframe(pd.DataFrame({
        "Cấp": [1, 2, 3, 4],
        "Tên": ["BÌNH THƯỜNG", "CHÚ Ý", "CẢNH BÁO", "NGUY HIỂM"],
        "Điều kiện": [
            "ΔT < 15 °C và T_max < 65 °C",
            "15 ≤ ΔT < 18 °C hoặc dΔT/dt > 1,5 °C/giờ",
            "18 ≤ ΔT < 20 °C hoặc dự báo ΔT(t+6h) ≥ 20 °C",
            "ΔT ≥ 20 °C hoặc M_T ≥ 50 °C/m hoặc T_max ≥ 70 °C",
        ],
        "Chu kỳ đo": ["15 phút", "10 phút", "10 phút", "5 phút"],
    }), use_container_width=True, hide_index=True)

    st.markdown("#### 7. Tiêu chuẩn viện dẫn")
    st.markdown(
        """
- **TCXDVN 305:2004** — Bê tông khối lớn. Quy phạm thi công và nghiệm thu.
- **TCVN 9341:2012** — Bê tông khối lớn. Thi công và nghiệm thu
  (ΔT ≤ 20 °C; M_T ≤ 50 °C/m).
- **TCVN 14334:2025** — Kết cấu bê tông khối lớn. Thi công và nghiệm thu
  (áp dụng cho bê tông nặng B20–B70).
- **TCVN 4453:1995** — Kết cấu bê tông và bê tông cốt thép toàn khối.
- **TCVN 5574:2018** — Thiết kế kết cấu bê tông và bê tông cốt thép.
- **ACI 207.1R / ACI 207.2R** — Mass Concrete; Thermal and Volume Change
  Effects on Cracking of Mass Concrete.
- **ACI 301** — Specifications for Concrete Construction.
- **ACI 305R** — Guide to Hot Weather Concreting.
- **ACI 209R** — Prediction of Creep, Shrinkage and Temperature Effects.
        """
    )

    st.markdown("#### 8. Giới hạn của mô hình")
    st.info(
        "Mô hình dùng sơ đồ truyền nhiệt **một chiều theo phương chiều dày**, "
        "bỏ qua thất thoát nhiệt qua các mặt bên. Với kết cấu có tỷ lệ "
        "mặt bên / thể tích nhỏ (đài móng rộng), giả thiết này thiên về "
        "an toàn vì cho kết quả T_max và ΔT lớn hơn thực tế. "
        "Mô hình cũng chưa xét bức xạ mặt trời trực tiếp và hệ ống làm mát "
        "tuần hoàn; ảnh hưởng của ống làm mát được quy đổi gần đúng thông "
        "qua việc giảm nhiệt độ bê tông tươi T₀."
    )

st.sidebar.divider()
st.sidebar.caption(
    "Chương trình thực hiện trong khuôn khổ đồ án môn học "
    "Công nghệ và Quản lý xây dựng nâng cao — Đề tài B12."
)
