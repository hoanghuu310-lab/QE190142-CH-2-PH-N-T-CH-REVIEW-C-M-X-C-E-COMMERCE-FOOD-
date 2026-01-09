import time
import json
import re
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

########################################
# 1. CẤU HÌNH (CONFIG)
########################################
PLATFORM = "shopeefood" 
SHOP_URL = "https://shopeefood.vn/ho-chi-minh/manmaru-am-thuc-nhat-ban-mac-dinh-chi"
LIMIT_REVIEWS = 50
OUTPUT_FILE = "reviews_topic2.json"

########################################
# 2. CÔNG CỤ HỖ TRỢ (UTILS)
########################################
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'@\w+', '', text)
    return text.strip()

def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    # Giữ trình duyệt không tự đóng để bạn có thể giải Captcha nếu cần
    options.add_experimental_option("detach", True) 
    return webdriver.Chrome(options=options)

########################################
# 3. HÀM CÀO DỮ LIỆU SHOPEEFOOD
########################################
def crawl_shopeefood(driver, url, limit):
    print(f"Đang truy cập: {url}")
    driver.get(url)
    
    # Chờ trang tải và để người dùng giải Captcha nếu có
    print("Vui lòng đợi 10s để trang tải hoặc giải Captcha (nếu có)...")
    time.sleep(10) 

    # Lấy tên Shop (Yêu cầu bài tập)
    try:
        shop_name = driver.find_element(By.CSS_SELECTOR, "h1.name-res, .info-res h1").text
    except:
        shop_name = "Quán ăn ShopeeFood"

    # Cuộn trang để load thêm review
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    reviews_data = []
    # Tìm các phần tử review bằng Selector linh hoạt
    items = driver.find_elements(By.CSS_SELECTOR, "div.review-item, div.comment-item")
    print(f"Tìm thấy {len(items)} đánh giá trên màn hình.")

    for r in items[:limit]:
        try:
            username = r.find_element(By.CSS_SELECTOR, ".username, .txt-blue").text
            content = r.find_element(By.CSS_SELECTOR, ".review-content, .comment-content").text
            
            # Lấy Rating chính xác (Dùng cho câu hỏi CỨNG)
            stars_active = r.find_elements(By.CSS_SELECTOR, ".icon-star.active, .shopee-rating-stars__star--filled")
            rating = len(stars_active) if stars_active else 5
            
            try:
                date = r.find_element(By.CSS_SELECTOR, ".review-date, .time").text
            except:
                date = time.strftime("%d/%m/%Y")

            reviews_data.append({
                "platform": "ShopeeFood",
                "shop_name": shop_name,
                "username": username,
                "rating": rating,
                "content": clean_text(content),
                "date": date
            })
        except:
            continue

    return reviews_data

########################################
# 4. HÀM PHÂN TÍCH (CHO CÂU HỎI CỨNG)
########################################
def analyze_results(data):
    if not data:
        print("Không có dữ liệu để phân tích.")
        return

    count_1 = sum(1 for r in data if r['rating'] == 1)
    count_5 = sum(1 for r in data if r['rating'] == 5)
    
    # Tính tỷ lệ 1 sao / 5 sao
    ratio = (count_1 / count_5) if count_5 > 0 else 0
    
    print("\n" + "="*30)
    print("KẾT QUẢ PHÂN TÍCH TOPIC 2:")
    print(f"- Tổng số đánh giá đã thu thập: {len(data)}")
    print(f"- Tỷ lệ 1 sao / 5 sao: {ratio:.2f}")
    
    # Tìm 10 từ khóa phổ biến
    all_content = " ".join([r['content'] for r in data]).lower()
    words = re.findall(r'\w+', all_content)
    stop_words = ['là', 'và', 'có', 'của', 'cho', 'mình', 'ăn', 'quán', 'rất', 'đã']
    keywords = [w for w in words if w not in stop_words and len(w) > 1]
    
    top_10 = Counter(keywords).most_common(10)
    print("- 10 từ khóa xuất hiện nhiều nhất:")
    for word, count in top_10:
        print(f"  + {word}: {count} lần")
    print("="*30)

########################################
# 5. CHƯƠNG TRÌNH CHÍNH (MAIN)
########################################
def main():
    driver = init_driver()
    try:
        if PLATFORM == "shopeefood":
            data = crawl_shopeefood(driver, SHOP_URL, LIMIT_REVIEWS)
        else:
            print("Vui lòng chọn lại platform phù hợp.")
            return

        # Lưu vào file JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\nĐã lưu thành công vào {OUTPUT_FILE}")
        
        # Chạy phân tích ngay lập tức
        analyze_results(data)

    finally:
        # Bạn có thể bỏ comment dòng dưới nếu muốn trình duyệt tự đóng
        # driver.quit() 
        print("\nHoàn tất chương trình.")

if __name__ == "__main__":
    main()
