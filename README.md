# 📊 Phân Tích Thị Trường Việc Làm và Xu Hướng Lương Ngành IT 2024

Dự án này xây dựng một hệ thống xử lý dữ liệu cuối-đến-cuối (End-to-End Data Pipeline) bằng Python để làm sạch, chuẩn hóa thông tin tuyển dụng ngành công nghệ thông tin từ nguồn dữ liệu thô (Excel đa sheet)[cite: 1, 2], sau đó ứng dụng SQL để khai thác các chỉ số chuyên sâu về xu hướng lương, thị trường làm việc từ xa (WFH)[cite: 3], và các kỹ năng công nghệ cốt lõi[cite: 3].

## 🔗 Đường Dẫn Dashboard Tương Tác
👉 **[Bấm vào đây để xem Dashboard tương tác trên Tableau Public](https://public.tableau.com/shared/84DF5P2XT?:display_count=n&:origin=viz_share_link)**

---

## 🛠️ Tính Năng Kỹ Thuật và Luồng Xử Lý

### 1. Khai Thác & Làm Sạch Dữ Liệu (Python / Pandas)
- **Hợp nhất dữ liệu:** Tự động đọc và gộp dữ liệu từ 12 sheet tương ứng với 12 tháng trong năm 2024 từ file Excel gốc[cite: 1, 2].
- **Xử lý dữ liệu khuyết thiếu:** Lọc bỏ hoàn toàn các bản ghi không công khai thông tin lương để đảm bảo tính chính xác cho các mô hình thống kê[cite: 1, 2].
- **Kỹ nghệ lập trình tính năng (Feature Engineering):** Sử dụng **Regular Expressions (Regex)** để bóc tách tiêu đề công việc thô, phân loại nhân sự thành 3 cấp bậc kinh nghiệm chuẩn: *Senior, Mid-level, Junior*[cite: 1, 2].
- **Chuẩn hóa cấu trúc dữ liệu phức tạp:** Ứng dụng thư viện `ast.literal_eval` để chuyển đổi trường thông tin kỹ năng từ dạng chuỗi thô sang dạng mảng (List Python) nhằm phục vụ công tác bóc tách dữ liệu mảng[cite: 1, 2].

### 2. Truy Vấn Phân Tích Chuyên Sâu (SQL - DuckDB/SQLite)
- Tính toán mức lương trung bình năm theo từng vị trí công việc cụ thể nhân với từng cấp bậc kinh nghiệm tương ứng[cite: 3].
- Theo dõi sự dịch chuyển và tỷ lệ phần trăm các công việc cho phép làm việc từ xa (WFH) biến động qua 12 tháng trong năm 2024[cite: 3].
- Thực hiện kỹ thuật tách mảng (Explode List) dữ liệu kỹ năng bằng Python để tạo bảng phẳng `job_skills_long`, từ đó dùng SQL truy vấn ra Top 10 kỹ năng công nghệ được săn đón nhất đối với vị trí *Data Analyst*[cite: 3].

### 3. Trực Quan Hóa (Tableau Public Dashboard)
- **Bản đồ Lương Toàn Cầu:** Trực quan hóa mật độ phân bố thu nhập trung bình theo địa lý quốc gia.
- **Biểu đồ Cột Phân Nhóm:** So sánh trực quan mức tăng tiến thu nhập giữa các cấp bậc (Junior vs Senior) ở từng vị trí (Data Analyst, Data Scientist, Data Engineer)[cite: 3].
- **Đường Xu Hướng & Bộ Lọc Động:** Tích hợp tính năng *Use as Filter* giữa các biểu đồ, cho phép người dùng cuối tự động lọc toàn bộ số liệu hệ thống chỉ bằng một cú click chuột vào biểu đồ bất kỳ.

---

## 📂 Cấu Trúc Thư Mục Dự Án
- `/data`: Chứa thông tin hướng dẫn tải tập dữ liệu gốc từ Kaggle.
- `/src`: Chứa mã nguồn Python (`.py` và `.ipynb`) thực hiện công đoạn ETL làm sạch dữ liệu[cite: 1, 2].
- `/sql`: Chứa file script `.sql` thực hiện các câu lệnh truy vấn phân tích số liệu[cite: 3].

## 📈 Kết Quả Phân Tích Chính (Key Insights)
- Cấp bậc kinh nghiệm có ảnh hưởng tuyến tính mạnh mẽ đến mức lương; các vị trí liên quan đến Kỹ sư Dữ liệu lớn (Data Engineer) và Học máy (Machine Learning Engineer) có biên độ dao động lương năm cao vượt trội[cite: 3].
- Xu hướng làm việc từ xa (WFH) có sự duy trì ổn định nhưng phân bổ không đồng đều giữa các nhóm ngành kỹ thuật và nhóm ngành phân tích kinh doanh[cite: 3].