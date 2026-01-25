# 🍜 Foody Sentiment Analysis & Data Pipeline

**Đề tài:** Xây dựng hệ thống thu thập, lưu trữ và phân tích cảm xúc khách hàng F&B trên Foody.vn  
**Sinh viên:** Lê Hoàng Hữu 
**MSSV:** Qe190142 
**Lớp/Môn học:** ADY201m

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![MinIO](https://img.shields.io/badge/DataLake-MinIO-red)
![Status](https://img.shields.io/badge/Status-In%20Progress-green)

---

## 📖 1. Giới thiệu (Overview)

Dự án này là một quy trình xử lý dữ liệu khép kín (**End-to-End Data Pipeline**), giải quyết bài toán phân tích dữ liệu phi cấu trúc trong ngành F&B. Hệ thống tự động thu thập hàng nghìn đánh giá từ Foody, lưu trữ vào Data Lake, làm sạch và lưu vào Data Warehouse để phục vụ phân tích cảm xúc và hành vi người dùng theo vùng miền (Bắc - Trung - Nam).

### 🎯 Mục tiêu chính:
- **Automation:** Crawler đa luồng, tự động vượt rào cản kỹ thuật.
- **Data Engineering:** Xây dựng Data Lake (MinIO) và Data Warehouse (PostgreSQL) bằng Docker.
- **Analytics:** So sánh khẩu vị, độ hài lòng và "từ khóa tử huyệt" giữa các vùng miền.

---

## 🏗 2. Kiến trúc Hệ thống (Architecture)

Quy trình xử lý dữ liệu (Data Flow):

1.  **Ingestion:** Python Selenium Crawler thu thập dữ liệu thô (HTML/Text) -> JSON Lines.
2.  **Data Lake (Storage):** Dữ liệu thô được đẩy tự động lên **MinIO Object Storage**.
3.  **Processing (ETL):** Làm sạch dữ liệu, xử lý tiếng Việt, gán nhãn vùng miền.
4.  **Data Warehouse:** Lưu trữ dữ liệu sạch vào **PostgreSQL**.
5.  **Serving:** Truy vấn SQL và trực quan hóa (bằng Python/Dashboard).

