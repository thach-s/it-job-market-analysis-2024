-- =============================================================================
-- Báo cáo phân tích: cleaned_job_market_2024
-- Engine: DuckDB hoặc SQLite (ghi chú khác biệt ở từng câu nếu có)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Nạp dữ liệu (DuckDB — chạy một lần trước khi query)
-- -----------------------------------------------------------------------------
-- CREATE OR REPLACE TABLE jobs AS
-- SELECT * FROM read_csv_auto('cleaned_job_market_2024.csv', header=true);

-- SQLite: import CSV vào bảng `jobs` bằng .import hoặc pandas.to_sql


-- =============================================================================
-- CÂU 1: Lương TB và số lượng việc theo job_title_short × experience_level
-- =============================================================================
SELECT
    job_title_short,
    experience_level,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_year_avg), 2) AS avg_salary_year
FROM jobs
GROUP BY
    job_title_short,
    experience_level
ORDER BY
    avg_salary_year DESC;


-- =============================================================================
-- CÂU 2: Tỷ lệ % WFH theo tháng năm 2024 (từ job_posted_date)
-- =============================================================================
-- DuckDB
SELECT
    strftime(job_posted_date, '%Y-%m') AS posting_month,
    COUNT(*) AS total_jobs,
    SUM(
        CASE
            WHEN job_work_from_home IN (TRUE, 1)
              OR LOWER(CAST(job_work_from_home AS VARCHAR)) IN ('true', '1', 'yes')
            THEN 1
            ELSE 0
        END
    ) AS wfh_jobs,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN job_work_from_home IN (TRUE, 1)
                  OR LOWER(CAST(job_work_from_home AS VARCHAR)) IN ('true', '1', 'yes')
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS wfh_pct
FROM jobs
WHERE job_posted_date >= DATE '2024-01-01'
  AND job_posted_date < DATE '2025-01-01'
GROUP BY posting_month
ORDER BY posting_month;

-- SQLite (thay DATE literal nếu cần: job_posted_date >= '2024-01-01')
-- SELECT
--     strftime('%Y-%m', job_posted_date) AS posting_month,
--     ...


-- =============================================================================
-- CÂU 3: Top 10 kỹ năng cho "Data Analyst" + lương TB (bảng skills đã explode)
-- =============================================================================
-- Giả định bảng job_skills_long(job_title_short, skill, salary_year_avg)
-- mỗi dòng = một kỹ năng của một tin tuyển dụng

SELECT
    skill,
    COUNT(*) AS skill_mentions,
    ROUND(AVG(salary_year_avg), 2) AS avg_salary_with_skill
FROM job_skills_long
WHERE job_title_short = 'Data Analyst'
GROUP BY skill
ORDER BY skill_mentions DESC
LIMIT 10;
