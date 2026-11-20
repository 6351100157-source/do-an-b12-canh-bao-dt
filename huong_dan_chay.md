# HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY CHƯƠNG TRÌNH

**Đồ án: Công nghệ và Quản lý xây dựng nâng cao — Đề tài B12**
Hệ thống cảnh báo chênh lệch nhiệt độ ΔT trong thi công bê tông khối lớn

---

## 1. Danh sách file

| File | Vai trò | Có cần sửa không? |
|---|---|---|
| `nhiet_btkl.py` | **Phần lõi tính toán.** Chứa toàn bộ công thức: truyền nhiệt, tỏa nhiệt đoạn nhiệt, ứng suất kéo nhiệt, phân cấp cảnh báo | Chỉ sửa khi muốn đổi công thức |
| `app.py` | **Giao diện web.** Nhập số liệu, vẽ biểu đồ, hiện cảnh báo | Chỉ sửa khi muốn đổi giao diện |
| `tao_du_lieu_do_mau.py` | Sinh file dữ liệu quan trắc giả định để thử nghiệm | Chạy 1 lần |
| `xuat_hinh_bao_cao.py` | Xuất 8 hình PNG 300 dpi để chèn vào thuyết minh | Chạy 1 lần |
| `kiem_thu_kich_ban.py` | Chạy nhanh 6 kịch bản, in bảng kết quả ra màn hình | Dùng khi cần số liệu nhanh |
| `du_lieu_do_mau.csv` | Dữ liệu quan trắc mẫu (85 bản ghi, 7 ngày) | Dùng để thử tab Giám sát |
| `requirements.txt` | Danh sách thư viện cần cài | Không sửa |

> **Quan trọng:** `app.py` và `nhiet_btkl.py` phải nằm **cùng một thư mục**, nếu không chương trình sẽ báo lỗi `ModuleNotFoundError: No module named 'nhiet_btkl'`.

---

## 2. Cài đặt (chỉ làm một lần)

### Bước 1 — Cài Python

Tải Python 3.10 trở lên tại <https://www.python.org/downloads/>.

Khi cài trên Windows, **bắt buộc tích vào ô "Add Python to PATH"** ở màn hình đầu tiên. Nếu quên, các lệnh ở bước sau sẽ báo *"python không phải là lệnh nội bộ"* và bạn phải gỡ ra cài lại.

Kiểm tra bằng cách mở Command Prompt (Windows) hoặc Terminal (macOS) và gõ:

```
python --version
```

Màn hình phải hiện ra số phiên bản, ví dụ `Python 3.12.3`.

### Bước 2 — Mở cửa sổ lệnh đúng vị trí

Việc này quan trọng vì máy tính cần biết các file của bạn nằm ở đâu.

**Trên Windows:** mở thư mục chứa các file, gõ `cmd` vào thanh địa chỉ của File Explorer rồi nhấn Enter.

**Trên macOS:** mở Terminal, gõ `cd ` (có dấu cách) rồi kéo thả thư mục vào cửa sổ Terminal, nhấn Enter.

### Bước 3 — Cài thư viện

```
pip install -r requirements.txt
```

Lệnh này tải về 4 thư viện: `streamlit` (tạo web), `numpy` (tính toán ma trận), `pandas` (xử lý bảng số liệu), `matplotlib` (vẽ biểu đồ). Quá trình mất khoảng 1–3 phút tùy tốc độ mạng.

---

## 3. Chạy chương trình

Trong cùng cửa sổ lệnh đó, gõ:

```
streamlit run app.py
```

Trình duyệt sẽ tự động mở trang `http://localhost:8501`. Nếu không tự mở, bạn copy địa chỉ đó dán vào trình duyệt.

**Để dừng chương trình:** quay lại cửa sổ lệnh, nhấn `Ctrl + C`.

---

## 4. Cách sử dụng từng tab

### Tab 1 — Dự báo trường nhiệt

Đây là tab chính. Bạn nhập số liệu ở **thanh bên trái** (chia thành 8 nhóm), chương trình tự động tính lại và cập nhật biểu đồ ngay.

Kết quả gồm:
- 4 ô chỉ số tổng hợp: T_max, ΔT_max, M_T max, hệ số an toàn nứt
- Bảng đối chiếu với 4 tiêu chí kiểm soát, kết luận ĐẠT / KHÔNG ĐẠT
- 5 biểu đồ
- Khung cảnh báo tại thời điểm bất lợi nhất
- Bảng số liệu chi tiết, có nút tải về file CSV để đưa vào Phụ lục

### Tab 2 — Giám sát dữ liệu đo

Dùng khi đã có số liệu quan trắc thực tế. Tải lên file CSV có 3 cột bắt buộc: `Gio`, `T_tam`, `T_be_mat` (cột `T_khong_khi` là tùy chọn).

Nếu chưa có số liệu thật, hãy dùng file `du_lieu_do_mau.csv` kèm theo.

Chương trình sẽ:
- Tính ΔT hiện tại và **dự báo ΔT sau 6 giờ** bằng ngoại suy tuyến tính
- Phát cảnh báo theo 4 cấp
- So sánh số liệu đo với kết quả mô phỏng, tính sai số
- Lập nhật ký cảnh báo toàn bộ chuỗi đo, có nút tải về

### Tab 3 — So sánh kịch bản

Nhấn nút để chương trình chạy lại mô hình với 6 tổ hợp biện pháp kiểm soát nhiệt khác nhau, rồi lập bảng so sánh. Bảng này dùng trực tiếp cho Chương 6 của thuyết minh.

### Tab 4 — Cơ sở lý thuyết

Liệt kê toàn bộ công thức đã dùng, ma trận ngưỡng cảnh báo, danh mục tiêu chuẩn viện dẫn và phần nêu rõ giới hạn của mô hình.

---

## 5. Chuẩn bị tài liệu nộp

Chạy lần lượt hai lệnh sau để sinh ra số liệu và hình vẽ cho thuyết minh:

```
python tao_du_lieu_do_mau.py
python xuat_hinh_bao_cao.py
```

Lệnh thứ hai tạo thư mục `hinh_bao_cao/` chứa 8 file PNG ở độ phân giải 300 dpi, chèn thẳng vào Word được mà không bị vỡ hình khi in.

---

## 6. Xử lý một số lỗi thường gặp

| Thông báo lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `'python' is not recognized` | Chưa thêm Python vào PATH | Gỡ Python, cài lại và tích ô "Add Python to PATH" |
| `ModuleNotFoundError: No module named 'streamlit'` | Chưa cài thư viện | Chạy lại `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'nhiet_btkl'` | Hai file không cùng thư mục, hoặc cửa sổ lệnh đang đứng ở thư mục khác | Kiểm tra lại Bước 2 |
| `Port 8501 is already in use` | Đang có một phiên Streamlit khác chạy | Chạy `streamlit run app.py --server.port 8502` |
| Biểu đồ hiện ô vuông thay cho chữ có dấu | Hệ thống thiếu phông chữ | Cài phông DejaVu Sans, hoặc thêm vào đầu `app.py`: `plt.rcParams["font.family"] = "Arial"` |
| File CSV tải lên báo thiếu cột | Tên cột không đúng | Tải file CSV mẫu trong Tab 2 để xem đúng định dạng |

---

## 7. Gợi ý khi bảo vệ đồ án

Nên chuẩn bị sẵn 3 thao tác để trình diễn trực tiếp trước hội đồng:

1. **Mở Tab 1 với số liệu gốc** → chỉ ra bảng kết luận KHÔNG ĐẠT, giải thích vì sao ΔT = 33,5 °C vượt ngưỡng.
2. **Vào thanh bên, đổi phương án che phủ** từ "Để hở" sang "Bao tải ẩm + nilon + xốp PE" → biểu đồ cập nhật ngay, ΔT tụt xuống còn khoảng 12,6 °C. Đây là lúc chỉ ra nghịch lý: ΔT đạt nhưng T_max lại vọt lên 72,7 °C, vẫn KHÔNG ĐẠT.
3. **Hạ T₀ xuống 28 °C** → cả hai tiêu chí cùng đạt. Kết luận: phải phối hợp biện pháp, không thể dùng đơn lẻ.

Thao tác thứ hai là điểm nhấn kỹ thuật của đồ án, nên dành thời gian giải thích kỹ.
