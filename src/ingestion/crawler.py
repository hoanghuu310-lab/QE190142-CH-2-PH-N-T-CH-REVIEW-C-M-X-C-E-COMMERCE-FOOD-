import requests
import json
import time
import random
import os
from schema_sentiment import ReviewItem

# --- CẤU HÌNH ---
DATA_FOLDER = "data_sentiment"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Header giả lập (ShopeeFood API khá dễ, chỉ cần header cơ bản)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'x-foody-client-type': '1',
    'x-foody-client-version': '3.0.0',
    'x-foody-api-version': '1',
}

def get_reviews_of_restaurant(restaurant_id, restaurant_name, city_name, limit=50):
    """Hàm lấy review của 1 quán cụ thể"""
    print(f"   ... Đang lấy review cho quán: {restaurant_name} (ID: {restaurant_id})")
    
    reviews_collected = []
    
    # API lấy Review (Tham số: request_id là ID quán)
    # Lấy comment mới nhất (sort_type=1)
    url = f"https://gappapi.deliverynow.vn/api/delivery/get_reply?id_type=1&request_id={restaurant_id}&sort_type=1&limit={limit}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"⚠️ Lỗi API Review: {response.status_code}")
            return []
            
        data = response.json()
        reply_list = data.get('reply', {}).get('reply_list', [])
        
        for reply in reply_list:
            # Mapping dữ liệu ShopeeFood -> Schema Sentiment
            item = ReviewItem(
                review_id=reply.get('id'),
                restaurant_id=restaurant_id,
                restaurant_name=restaurant_name,
                city=city_name,
                user_name=reply.get('name', 'Anonymous'),
                comment=reply.get('comment', ''),
                rating=reply.get('rating', 0), # Rating trên thang 10 hoặc 5
                review_date=reply.get('created_on', '')
            )
            reviews_collected.append(item)
            
    except Exception as e:
        print(f"❌ Lỗi khi crawl quán {restaurant_name}: {e}")
        
    return reviews_collected

def crawl_by_category(city_name, city_id, category_id, max_restaurants=20):
    print(f"\n🚀 BẮT ĐẦU CRAWL: {city_name} (Category ID: {category_id})")
    output_file = os.path.join(DATA_FOLDER, f"reviews_{city_name}_cat{category_id}.jsonl")
    
    # 1. Lấy danh sách quán ăn theo category và city
    # API Get Delivery From Category
    list_url = "https://gappapi.deliverynow.vn/api/delivery/get_from_category"
    params = {
        "city_id": city_id,
        "category_id": category_id,
        "page_size": max_restaurants,
        "new_id": 0,
        "sort_type": 1 # Sắp xếp theo phổ biến
    }
    
    try:
        res = requests.get(list_url, headers=HEADERS, params=params)
        items = res.json().get('reply', {}).get('delivery_infos', [])
        
        print(f"-> Tìm thấy {len(items)} quán. Bắt đầu quét review...")
        
        with open(output_file, 'a', encoding='utf-8', buffering=1) as f:
            for shop in items:
                delivery_id = shop.get('delivery_id') # Đây là ID quán dùng để lấy review
                name = shop.get('name')
                
                # Gọi hàm lấy review cho quán này
                reviews = get_reviews_of_restaurant(delivery_id, name, city_name, limit=50) # Lấy 50 review/quán
                
                # Ghi xuống file
                for rev in reviews:
                    f.write(rev.to_json_line() + "\n")
                
                print(f"      + Đã lưu {len(reviews)} review của quán: {name}")
                time.sleep(random.uniform(1, 2)) # Nghỉ nhẹ
                
    except Exception as e:
        print(f"❌ Lỗi Lấy Danh Sách Quán: {e}")

# --- MAIN RUN ---
if __name__ == "__main__":
    
    # ID CÁC THÀNH PHỐ TRÊN SHOPEEFOOD (QUAN TRỌNG ĐỂ SO SÁNH VÙNG MIỀN)
    CITY_HCM = 217
    CITY_HN = 218
    CITY_DANANG = 219
    
    # ID DANH MỤC (Ví dụ: 1=Cơm, 12=Trà sữa, ...)
    CAT_COM = 1
    CAT_TRASUA = 12
    
    # --- KỊCH BẢN CHẠY ---
    
    # 1. Crawl Cơm ở TP.HCM
    crawl_by_category(city_name="HCM", city_id=CITY_HCM, category_id=CAT_COM, max_restaurants=10)
    
    # 2. Crawl Cơm ở Hà Nội (Để so sánh)
    crawl_by_category(city_name="HaNoi", city_id=CITY_HN, category_id=CAT_COM, max_restaurants=10)
    
    print("\n✅ HOÀN TẤT! Kiểm tra thư mục 'data_sentiment'")
