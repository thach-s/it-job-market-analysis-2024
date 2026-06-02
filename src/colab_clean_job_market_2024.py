# =============================================================================
# Phân tích thị trường việc làm IT 2024 — Làm sạch dữ liệu (Google Colab)
# Chạy từng khối trong Colab hoặc chạy toàn bộ file.
# =============================================================================

import ast
import re
from pathlib import Path

import pandas as pd

# -----------------------------------------------------------------------------
# Cấu hình (Colab: upload .xlsx hoặc mount Google Drive)
# -----------------------------------------------------------------------------
XLSX_FILE = Path("/content/job_postings_monthly.xlsx")
OUTPUT_FILE = Path("/content/cleaned_job_market_2024.csv")

# "all_sheets" = gộp mọi sheet | "single_sheet" = một sheet chứa cả năm
READ_MODE = "all_sheets"
SINGLE_SHEET_NAME = None  # None = sheet đầu tiên
MONTHLY_SHEETS = None  # None = đọc hết; hoặc [f"{m:02d}-2024" for m in range(1, 13)]

# Các cột cần giữ (có thể bỏ comment nếu file có thêm cột khác)
KEY_COLUMNS = [
    "job_title_short",
    "job_title",
    "salary_year_avg",
    "job_skills",
    "job_work_from_home",
]


# -----------------------------------------------------------------------------
# Bước 1: Đọc file Excel (.xlsx) — cần: pip install openpyxl
# -----------------------------------------------------------------------------
def load_from_xlsx(
    xlsx_path: Path,
    read_mode: str = "all_sheets",
    single_sheet_name: str | None = None,
    monthly_sheets: list[str] | None = None,
) -> pd.DataFrame:
    """
    Đọc job_postings_monthly.xlsx:
    - all_sheets: mỗi sheet = một tháng, gộp bằng concat
    - single_sheet: toàn bộ dữ liệu nằm trên một sheet
    """
    if not xlsx_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {xlsx_path}")

    xl = pd.ExcelFile(xlsx_path)
    print("Các sheet:", xl.sheet_names)

    if read_mode == "single_sheet":
        sheet = single_sheet_name or xl.sheet_names[0]
        df = pd.read_excel(xl, sheet_name=sheet)
        df["posting_month"] = sheet
        print(f"Đọc 1 sheet '{sheet}' — {len(df):,} dòng.")
        return df

    if read_mode == "all_sheets":
        names = monthly_sheets if monthly_sheets else xl.sheet_names
        frames = []
        for name in names:
            if name not in xl.sheet_names:
                print(f"  Bỏ qua (không có sheet): {name}")
                continue
            df_month = pd.read_excel(xl, sheet_name=name)
            df_month["posting_month"] = name
            frames.append(df_month)
        df = pd.concat(frames, ignore_index=True)
        print(f"Đã gộp {len(frames)} sheet — tổng {len(df):,} dòng.")
        return df

    raise ValueError('read_mode phải là "all_sheets" hoặc "single_sheet"')


# -----------------------------------------------------------------------------
# Bước 2: Lọc bỏ dòng thiếu lương (salary_year_avg)
# -----------------------------------------------------------------------------
def drop_missing_salary(df: pd.DataFrame) -> pd.DataFrame:
    """Loại bỏ NaN và chuỗi rỗng ở cột salary_year_avg."""
    before = len(df)
    # Ép kiểu số: giá trị không hợp lệ thành NaN
    df = df.copy()
    df["salary_year_avg"] = pd.to_numeric(df["salary_year_avg"], errors="coerce")
    df = df.dropna(subset=["salary_year_avg"])
    after = len(df)
    print(f"Đã loại {before - after:,} dòng thiếu salary — còn {after:,} dòng.")
    return df


# -----------------------------------------------------------------------------
# Bước 3: Tạo cột experience_level từ job_title
# -----------------------------------------------------------------------------
SENIOR_PATTERN = re.compile(
    r"\b(Senior|Principal|Lead|Manager)\b", re.IGNORECASE
)
JUNIOR_PATTERN = re.compile(
    r"\b(Junior|Intern|Entry)\b", re.IGNORECASE
)


def classify_experience(job_title: str) -> str:
    """
    Phân loại kinh nghiệm:
    - Senior: Senior, Principal, Lead, Manager
    - Junior: Junior, Intern, Entry
    - Còn lại: Mid-level
    Ưu tiên Senior nếu title chứa cả hai nhóm từ khóa (hiếm).
    """
    if pd.isna(job_title):
        return "Mid-level"
    title = str(job_title)
    if SENIOR_PATTERN.search(title):
        return "Senior"
    if JUNIOR_PATTERN.search(title):
        return "Junior"
    return "Mid-level"


def add_experience_level(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["experience_level"] = df["job_title"].apply(classify_experience)
    print("Phân bố experience_level:")
    print(df["experience_level"].value_counts())
    return df


# -----------------------------------------------------------------------------
# Bước 4: Làm sạch job_skills — chuỗi → list Python thật
# -----------------------------------------------------------------------------
def parse_skills_cell(value) -> list:
    """
    Chuyển chuỗi dạng "['sql', 'python']" thành list.
    Hỗ trợ: list sẵn, ast.literal_eval, hoặc tách thủ công khi lỗi.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return [str(s).strip().lower() for s in value if str(s).strip()]

    text = str(value).strip()
    if not text or text in ("[]", "nan", "None"):
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(s).strip().lower() for s in parsed if str(s).strip()]
    except (ValueError, SyntaxError):
        pass

    # Fallback: bỏ ngoặc vuông/dấu nháy, tách theo dấu phẩy
    cleaned = text.strip("[]").replace("'", "").replace('"', "")
    parts = [p.strip().lower() for p in cleaned.split(",") if p.strip()]
    return parts


def clean_job_skills(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["job_skills"] = df["job_skills"].apply(parse_skills_cell)
    empty = (df["job_skills"].apply(len) == 0).sum()
    print(f"Số dòng có job_skills rỗng sau làm sạch: {empty:,}")
    return df


# -----------------------------------------------------------------------------
# Bước 5: Xuất file CSV
# -----------------------------------------------------------------------------
def export_cleaned(df: pd.DataFrame, output_path: Path) -> None:
    """
    Xuất CSV. Cột job_skills (list) được lưu dạng chuỗi Python
    để đọc lại bằng ast.literal_eval khi phân tích kỹ năng.
    """
    df_out = df.copy()
    # CSV không lưu list trực tiếp — chuyển về chuỗi biể diễn list
    df_out["job_skills"] = df_out["job_skills"].apply(repr)
    df_out.to_csv(output_path, index=False)
    print(f"Đã lưu: {output_path} ({len(df_out):,} dòng).")


# -----------------------------------------------------------------------------
# Pipeline chính
# -----------------------------------------------------------------------------
def main():
    # --- Colab: bỏ comment một trong các cách sau để nạp dữ liệu ---
    # from google.colab import drive
    # drive.mount("/content/drive")
    # DATA_DIR = Path("/content/drive/MyDrive/IT-Job-Market-Analysis-2024/data")

    # from google.colab import files
    # uploaded = files.upload()  # upload từng file hoặc zip rồi giải nén

    df = load_from_xlsx(
        XLSX_FILE,
        read_mode=READ_MODE,
        single_sheet_name=SINGLE_SHEET_NAME,
        monthly_sheets=MONTHLY_SHEETS,
    )
    df = drop_missing_salary(df)
    df = add_experience_level(df)
    df = clean_job_skills(df)

    # Giữ cột quan trọng + posting_month + experience_level (nếu có đủ cột)
    extra = ["posting_month", "experience_level"]
    cols = [c for c in KEY_COLUMNS + extra if c in df.columns]
    df_final = df[cols] if cols else df

    export_cleaned(df_final, OUTPUT_FILE)
    return df_final


if __name__ == "__main__":
    df_clean = main()
