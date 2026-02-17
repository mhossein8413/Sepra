
from flask import Flask, request, render_template, jsonify, send_file
import sys
import os
import traceback
import requests
import json
import re
import pickle
from datetime import datetime
from typing import Optional, Tuple, Dict, List, Any
import networkx as nx

# اضافه کردن مسیر فایل map.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تلاش برای وارد کردن map.py
try:
    from map import (
        create_osmGraph, nearest_drive, nearest_walk,
        add_edge_from_start_end, dijkstra, real_path,
        snap, total_cost, traffic_factor,
        G_drive, G_walk, D,
        save_real, node_drive, node_walk,
        bus_routes, taxi_routes,
        WALK_SPEED, BUS_COST, TAXI_COST, WAIT_TAXI, BUS_START, BUS_END
    )
    MAP_LOADED = True
    print("✅ map.py با موفقیت بارگذاری شد")
except ImportError as e:
    print(f"⚠️ خطا در وارد کردن map.py: {e}")
    MAP_LOADED = False
    # ایجاد متغیرهای پیش‌فرض
    G_drive = G_walk = D = None
    save_real = node_drive = node_walk = {}
    bus_routes = {}
    taxi_routes = []

app = Flask(__name__)

# ==================== توابع کمکی ====================

def is_coordinate(input_str: str) -> Optional[Tuple[float, float]]:
    """
    بررسی می‌کند آیا ورودی مختصات جغرافیایی است
    فرمت‌های قابل قبول:
    30.285424, 57.012086
    30.285424,57.012086
    ۳۰٫۲۸۵۴۲۴, ۵۷٫۰۱۲۰۸۶  (اعداد فارسی)
    30.285424 57.012086 (با فاصله)
    """
    if not input_str:
        return None
    
    # حذف فاصله‌های اضافی
    cleaned = input_str.strip()
    
    # جایگزینی اعداد فارسی با انگلیسی
    persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹٫', '0123456789.')
    cleaned = cleaned.translate(persian_to_english)
    
    # حذف کاراکترهای غیرضروری
    cleaned = re.sub(r'[°\'"\s]+', ' ', cleaned)
    
    # الگوهای مختلف مختصات
    patterns = [
        # فرمت: lat, lon با کاما
        r'^(-?\d+\.?\d*)\s*[,،]\s*(-?\d+\.?\d*)$',
        # فرمت: lat lon با فاصله
        r'^(-?\d+\.?\d*)\s+(-?\d+\.?\d*)$',
        # فرمت: lat,lon بدون فاصله
        r'^(-?\d+\.?\d*)[,،](-?\d+\.?\d*)$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, cleaned)
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                
                # اعتبارسنجی محدوده (محدوده کرمان)
                if 29.0 <= lat <= 31.0 and 56.0 <= lon <= 58.0:
                    return (lat, lon)
                else:
                    print(f"⚠️ مختصات خارج از محدوده کرمان: ({lat}, {lon})")
            except ValueError as e:
                print(f"⚠️ خطا در تبدیل مختصات: {e}")
                continue
    
    return None

def geocode_input(user_input: str) -> Tuple[float, float]:
    """
    ورودی کاربر را پردازش می‌کند:
    1. اگر مختصات بود، مستقیماً برمی‌گرداند
    2. اگر آدرس بود، geocode می‌کند
    3. اگر نام مکان معروف بود، از دیکشنری برمی‌گرداند
    """
    if not user_input:
        print("⚠️ ورودی خالی است، بازگشت به مرکز کرمان")
        return (30.2839, 57.0834)
    
    print(f"🔍 پردازش ورودی: '{user_input}'")
    
    # 1. بررسی آیا مختصات است
    coordinates = is_coordinate(user_input)
    if coordinates:
        print(f"📍 تشخیص داده شد به عنوان مختصات: {coordinates}")
        return coordinates
    
    # 2. بررسی در دیکشنری مکان‌های معروف
    input_lower = user_input.strip().lower()
    
    # دیکشنری کامل مکان‌های کرمان
    KERMAN_LOCATIONS = {
        # میدان‌ها
        "میدان شهید باهنر": (30.293556, 57.085553),
        "میدان شهدا": (30.281539, 57.084850),
        "میدان غدیر": (30.270045, 57.093193),
        "میدان امام": (30.290954, 57.066992),
        "میدان امام خمینی": (30.290954, 57.066992),
        "میدان آزادی": (30.294815, 57.057554),
        
        # پارک‌ها
        "پارک ملت": (30.287257, 57.053020),
        "پارک شهیدان": (30.292371, 57.072765),
        "پارک مادر": (30.299178, 57.053883),
        "پارک بانوان": (30.294815, 57.057554),
        "پارک بهشت": (30.286805, 57.070736),
        
        # دانشگاه‌ها
        "دانشگاه شهید باهنر": (30.296862, 56.980585),
        "دانشگاه باهنر": (30.296862, 56.980585),
        "دانشگاه آزاد کرمان": (30.305449, 57.048575),
        "دانشگاه علوم پزشکی": (30.297584, 57.063164),
        "دانشگاه علوم پزشکی کرمان": (30.297584, 57.063164),
        "دانشگاه پیام نور": (30.284217, 57.038102),
        
        # مراکز خرید
        "مجتمع تجاری آفتاب": (30.294815, 57.057554),
        "بازار کرمان": (30.286805, 57.070736),
        "مجتمع الماس": (30.283629, 57.072924),
        "مجتمع تجاری الماس": (30.283629, 57.072924),
        "بازار گنج": (30.292099, 57.067025),
        
        # ترمینال‌ها
        "ترمینال مسافربری": (30.262750, 56.971877),
        "ترمینال": (30.262750, 56.971877),
        "فرودگاه کرمان": (30.258306, 57.083596),
        "فرودگاه": (30.258306, 57.083596),
        "ایستگاه راه آهن": (30.272900, 57.001179),
        
        # بیمارستان‌ها
        "بیمارستان افضلی": (30.292099, 57.067025),
        "بیمارستان شریعتی": (30.286805, 57.070736),
        "بیمارستان بهارلو": (30.297584, 57.063164),
        "بیمارستان سیدالشهدا": (30.294815, 57.057554),
        
        # مناطق و خیابان‌ها
        "بلوار جمهوری": (30.284217, 57.038102),
        "بلوار امام": (30.286904, 57.049716),
        "خیابان شریعتی": (30.292099, 57.067025),
        "خیابان امام": (30.286904, 57.049716),
        "شهرک صنعتی": (30.262750, 56.971877),
        "شهرک امام": (30.278510, 57.017524),
        
        # اماکن تاریخی
        "گنبد جبلیه": (30.283629, 57.072924),
        "باغ شاهزاده ماهان": (30.060278, 57.271111),
        "بازار بزرگ کرمان": (30.286805, 57.070736),
        "مسجد جامع کرمان": (30.292371, 57.072765),
        
        # هتل‌ها
        "هتل پارس": (30.290954, 57.066992),
        "هتل اخوان": (30.292099, 57.067025),
        "هتل گنج": (30.294815, 57.057554),
        
        # ادارات دولتی
        "استانداری کرمان": (30.293556, 57.085553),
        "شهرداری کرمان": (30.290954, 57.066992),
        "دانشگاه علوم پزشکی": (30.297584, 57.063164),
    }
    
    # جستجوی دقیق در دیکشنری
    for name, coords in KERMAN_LOCATIONS.items():
        name_lower = name.lower()
        if (name_lower == input_lower or 
            name_lower in input_lower or 
            input_lower in name_lower):
            print(f"📍 یافت در دیکشنری: '{name}' -> {coords}")
            return coords
    
    # 3. اگر نه مختصات بود و نه در دیکشنری، از Nominatim استفاده کن
    print(f"🔍 جستجوی آدرس در Nominatim: '{user_input}'")
    
    try:
        # استفاده از Nominatim OpenStreetMap
        url = "https://nominatim.openstreetmap.org/search"
        
        # اگر کاربر "کرمان" را وارد نکرده، اضافه کن
        search_query = user_input
        if "کرمان" not in user_input and "kerman" not in user_input.lower():
            search_query = f"{user_input}, کرمان, ایران"
        
        params = {
            'q': search_query,
            'format': 'json',
            'limit': 1,
            'accept-language': 'fa',
            'countrycodes': 'ir',  # محدود به ایران
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'SepraRouteFinder/3.0 (contact@sepra.com)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                display_name = data[0].get('display_name', 'نامشخص')
                
                print(f"📍 یافت در Nominatim: {display_name[:50]}...")
                print(f"   مختصات: ({lat:.6f}, {lon:.6f})")
                
                # اعتبارسنجی مختصات برگشتی
                if 29.0 <= lat <= 31.0 and 56.0 <= lon <= 58.0:
                    return (lat, lon)
                else:
                    print(f"⚠️ مختصات برگشتی خارج از محدوده کرمان")
            else:
                print(f"⚠️ آدرس '{user_input}' در Nominatim پیدا نشد")
        else:
            print(f"⚠️ خطا در ارتباط با Nominatim: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"⚠️ زمان انتظار برای Nominatim به پایان رسید")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ خطای شبکه در ارتباط با Nominatim: {e}")
    except Exception as e:
        print(f"⚠️ خطای غیرمنتظره در geocoding: {e}")
    
    # 4. اگر همه روش‌ها شکست خوردند، مرکز کرمان برگردان
    print(f"⚠️ نتوانستیم '{user_input}' را پیدا کنیم، بازگشت به مرکز کرمان")
    return (30.2839, 57.0834)

def parse_time(time_str: str) -> int:
    """تبدیل زمان از رشته به دقیقه"""
    try:
        # حذف فاصله‌ها
        cleaned = time_str.strip()
        
        # چند فرمت مختلف
        formats = [
            r'^(\d{1,2}):(\d{2})$',      # 8:20
            r'^(\d{1,2})\.(\d{2})$',     # 8.20
            r'^(\d{1,2})\s+(\d{2})$',    # 8 20
        ]
        
        for fmt in formats:
            match = re.match(fmt, cleaned)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                
                if 0 <= hour < 24 and 0 <= minute < 60:
                    return hour * 60 + minute
        
        print(f"⚠️ فرمت زمان نامعتبر: '{time_str}'، استفاده از پیش‌فرض 8:20")
        return 8 * 60 + 20  # پیش‌فرض 8:20
        
    except Exception as e:
        print(f"⚠️ خطا در تجزیه زمان: {e}")
        return 8 * 60 + 20

# ==================== Routes اصلی ====================

@app.route("/")
def home():
    """صفحه اصلی"""
    return render_template("index.html")

@app.route("/route", methods=["POST"])
def calculate_route():
    """محاسبه مسیر بر اساس ورودی کاربر"""
    try:
        print("\n" + "="*70)
        print("📍 دریافت درخواست مسیریابی جدید")
        print("="*70)
        
        # دریافت داده‌های فرم
        start_input = request.form.get("start", "").strip()
        end_input = request.form.get("end", "").strip()
        start_time_str = request.form.get("start_time", "8:20").strip()
        
        print(f"📝 ورودی کاربر:")
        print(f"   مبدأ: '{start_input}'")
        print(f"   مقصد: '{end_input}'")
        print(f"   زمان: '{start_time_str}'")
        
        # تبدیل ورودی‌ها به مختصات
        start_coords = geocode_input(start_input)
        end_coords = geocode_input(end_input)
        
        print(f"\n📌 مختصات نهایی:")
        print(f"   مبدأ: ({start_coords[0]:.6f}, {start_coords[1]:.6f})")
        print(f"   مقصد: ({end_coords[0]:.6f}, {end_coords[1]:.6f})")
        
        # تبدیل زمان
        user_time_min = parse_time(start_time_str)
        print(f"⏰ زمان حرکت: {user_time_min} دقیقه از نیمه شب")
        print(f"   (معادل: {user_time_min//60}:{user_time_min%60:02d})")
        
        # اگر map.py لود نشده، داده تستی برگردان
        if not MAP_LOADED:
            print("⚠️ map.py لود نشده، استفاده از داده تستی")
            return jsonify(get_test_data(start_coords, end_coords, user_time_min))
        
        # محاسبه مسیر با map.py
        result = calculate_route_with_map(
            start_coords, 
            end_coords, 
            user_time_min
        )
        
        if result:
            # اضافه کردن اطلاعات دیباگ
            result["debug"] = {
                "start_input": start_input,
                "end_input": end_input,
                "start_coords": start_coords,
                "end_coords": end_coords,
                "time_input": start_time_str,
                "time_minutes": user_time_min,
                "map_loaded": MAP_LOADED,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"\n✅ نتایج آماده ارسال به کاربر:")
            print(f"   زمان مسیر ۱: {result['route1']['time']}")
            print(f"   هزینه مسیر ۱: {result['route1']['cost']}")
            print(f"   نوع مسیر ۱: {result['route1']['mode']}")
            print(f"   زمان مسیر ۲: {result['route2']['time']}")
            print(f"   هزینه مسیر ۲: {result['route2']['cost']}")
            
            return jsonify(result)
        else:
            print("❌ خطا در محاسبه مسیر، استفاده از داده تستی")
            return jsonify(get_test_data(start_coords, end_coords, user_time_min))
            
    except Exception as e:
        print(f"🔥 خطای عمومی در calculate_route: {e}")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "message": "خطا در پردازش درخواست",
            "route1": {
                "time": "خطا در محاسبه",
                "cost": "خطا در محاسبه", 
                "mode": "خطا در محاسبه"
            },
            "route2": {
                "time": "خطا در محاسبه",
                "cost": "خطا در محاسبه",
                "mode": "خطا در محاسبه"
            },
            "map_data": {},
            "debug": {"error": str(e), "timestamp": datetime.now().isoformat()}
        }), 500
    
def calculate_route_with_map(start_coords, end_coords, user_time_min):
    """تابع اصلی محاسبه مسیر با map.py"""
    try:
        lat, lon = start_coords
        lat1, lon1 = end_coords
        
        print("\n" + "="*60)
        print("🔍 شروع محاسبه مسیر با map.py")
        print("="*60)
        print(f"📌 مختصات ورودی به map.py:")
        print(f"   مبدأ: ({lat:.6f}, {lon:.6f})")
        print(f"   مقصد: ({lat1:.6f}, {lon1:.6f})")
        print(f"   زمان: {user_time_min} دقیقه ({user_time_min//60}:{user_time_min%60:02d})")
            
        # اضافه کردن گره‌های شروع و پایان
        D.add_node("start")
        D.add_node("end")
        
        # پیدا کردن نزدیک‌ترین گره‌ها
        node_drive["start"] = nearest_drive(G_drive, lat, lon)
        node_walk["start"] = nearest_walk(G_walk, lat, lon)
        node_drive["end"] = nearest_drive(G_drive, lat1, lon1)
        node_walk["end"] = nearest_walk(G_walk, lat1, lon1)
        
        print(f"\n📍 نزدیک‌ترین گره‌ها:")
        print(f"   پیاده مبدأ: {node_walk['start']}")
        print(f"   رانندگی مبدأ: {node_drive['start']}")
        print(f"   پیاده مقصد: {node_walk['end']}")
        print(f"   رانندگی مقصد: {node_drive['end']}")
        
        # اضافه کردن یال‌های پیاده‌روی
        add_edge_from_start_end(G_walk, D, node_walk)
        
        # اجرای دیجکسترا
        print(f"\n🚀 اجرای الگوریتم Dijkstra...")
        output = dijkstra(D, 'start', 'end', user_time_min)
        
        if not output:
            print("❌ Dijkstra مسیری پیدا نکرد")
            return None
        
        print(f"\n✅ Dijkstra اجرا شد:")
        print(f"   زمان کل: {output['time']} ثانیه ({output['time'] // 60} دقیقه)")
        print(f"   هزینه کل: {output['cost']:,} ریال")
        print(f"   تعداد مراحل: {len(output['edge_path'])}")
        
        # محاسبه هزینه با تابع total_cost
        cost = total_cost(output['edge_path'])
        print(f"💰 هزینه محاسبه شده: {cost:,} تومان")
        
        # استخراج انواع حمل و نقل
        modes = []
        mode_details = []
        for edge in output['edge_path']:
            if edge['mode'] == 'walk' and 'پیاده' not in modes:
                modes.append('پیاده')
            elif edge['mode'] == 'bus' and 'اتوبوس' not in modes:
                modes.append('اتوبوس')
            elif edge['mode'] == 'taxi' and 'تاکسی' not in modes:
                modes.append('تاکسی')
        
        route1_mode = " + ".join(modes) if modes else "نامشخص"
        
        # محاسبه مسیر اسنپ
        print(f"\n🚕 محاسبه مسیر مستقیم (اسنپ)...")
        snap_path, snap_cost_val , time_snap = snap(
            node_drive["start"], 
            node_drive["end"], 
            user_time_min
        )
        
        print(f"✅ مسیر اسنپ محاسبه شد:")
        print(f"   تعداد نقاط: {len(snap_path) if snap_path else 0}")
        print(f"   هزینه: {int(snap_cost_val):,} تومان")
        print(f"   زمان: {int(time_snap // 60)} دقیقه")
        
        # تولید داده‌های نقشه از مسیر دیجکسترا
        print(f"\n🗺️ تولید داده‌های نقشه...")
        map_data = real_path(
            output['edge_path'], 
            save_real, 
            G_walk, 
            G_drive, 
            node_walk, 
            node_drive
        )
        
        # اضافه کردن مسیر اسنپ به نقشه
        if snap_path and len(snap_path) > 0:
            map_data['snap'] = [snap_path]
            print(f"   SNAP: {len(snap_path)} نقطه")
        
        # اضافه کردن نشانگرهای مبدأ و مقصد جدید
        map_data['markers'] = {
            'start': [list(start_coords)],  # تبدیل tuple به list برای JSON
            'end': [list(end_coords)]
        }
        
        # ساخت نتیجه نهایی
        result = {
            "route1": {
                "time": f"{output['time'] // 60} دقیقه",
                "cost": f"{int(cost):,} تومان",
                "mode": route1_mode,
                "steps": len(output['edge_path']),
                "modes": modes,  # لیست حالت‌های حمل‌ونقل برای نقشه
                "map_modes": list(map_data.keys()) if 'markers' not in map_data else [k for k in map_data.keys() if k != 'markers']
            },
            "route2": {
                "time": f"{int(time_snap // 60)} دقیقه",
                "cost": f"{int(snap_cost_val):,} تومان",
                "mode": "تاکسی اینترنتی مستقیم",
                "steps": 1,
                "note": "مسیر مستقیم بدون توقف"
            },
            "map_data": map_data,
            "debug_info": {
                "dijkstra_time_seconds": output['time'],
                "edge_count": len(output['edge_path']),
                "modes_found": modes
            }
        }
        
        print(f"\n✅ محاسبه کامل شد!")
        print("="*60)
        
        return result
        
    except Exception as e:
        print(f"🔥 خطا در calculate_route_with_map: {e}")
        traceback.print_exc()
        return None
    
def get_test_data(start_coords, end_coords, user_time_min):
    """داده تستی برای وقتی که map.py کار نمی‌کند"""
    print("🧪 تولید داده تستی...")
    
    # ایجاد مسیر تستی بین مختصات واقعی
    test_path = []
    steps = 20
    
    # ایجاد نقاط میانی بین مبدأ و مقصد
    for i in range(steps + 1):
        lat = start_coords[0] + (end_coords[0] - start_coords[0]) * i / steps
        lon = start_coords[1] + (end_coords[1] - start_coords[1]) * i / steps
        test_path.append([lat, lon])
    
    # تقسیم مسیر به بخش‌های مختلف
    split1 = len(test_path) // 3
    split2 = 2 * len(test_path) // 3
    
    # زمان و هزینه تستی
    distance = ((end_coords[0] - start_coords[0])**2 + (end_coords[1] - start_coords[1])**2)**0.5 * 111  # تقریب کیلومتر
    test_time = int(distance * 3)  # تقریب زمان بر اساس فاصله
    test_cost = int(distance * 1500)  # تقریب هزینه
    
    snap_time = int(distance * 2)
    snap_cost = int(distance * 2500)
    
    return {
        "route1": {
            "time": f"{test_time} دقیقه",
            "cost": f"{test_cost:,} تومان",
            "mode": "پیاده + اتوبوس + تاکسی",
            "steps": 3,
            "details": [
                {"mode": "walk", "count": 1},
                {"mode": "bus", "count": 1},
                {"mode": "taxi", "count": 1}
            ]
        },
        "route2": {
            "time": f"{snap_time} دقیقه",
            "cost": f"{snap_cost:,} تومان",
            "mode": "تاکسی اینترنتی مستقیم",
            "steps": 1,
            "note": "مسیر مستقیم - داده تستی"
        },
        "map_data": {
            "walk": [test_path[:split1]],
            "bus": [test_path[split1:split2]],
            "taxi": [test_path[split2:]],
            "snap": [test_path],
            "markers": {
                "start": [list(start_coords)],
                "end": [list(end_coords)]
            }
        },
        "debug_info": {
            "note": "داده تستی (map.py لود نشد)",
            "start_coords": start_coords,
            "end_coords": end_coords,
            "user_time_min": user_time_min,
            "distance_km": round(distance, 2),
            "test_data": True
        }
    }

# ==================== Routes کمکی و اطلاعاتی ====================

@app.route("/help")
def help_page():
    """صفحه راهنما"""
    return render_template("help.html")

@app.route("/test_coordinates", methods=["GET"])
def test_coordinates():
    """تست تبدیل مختصات"""
    address = request.args.get("address", "")
    if not address:
        return jsonify({"error": "آدرس الزامی است"}), 400
    
    coords = geocode_input(address)
    return jsonify({
        "address": address,
        "coordinates": {
            "lat": coords[0],
            "lon": coords[1]
        },
        "is_coordinate": bool(is_coordinate(address))
    })

@app.route("/system_info", methods=["GET"])
def system_info():
    """اطلاعات سیستم و وضعیت"""
    info = {
        "status": "active",
        "version": "3.0",
        "map_loaded": MAP_LOADED,
        "timestamp": datetime.now().isoformat(),
        "city": "کرمان",
        "coordinates_range": {
            "min_lat": 29.0,
            "max_lat": 31.0,
            "min_lon": 56.0,
            "max_lon": 58.0
        },
        "bus_schedule": {
            "start": "8:00",
            "end": "20:00",
            "routes_count": len(bus_routes) if MAP_LOADED else 0
        },
        "costs": {
            "bus": "۲,۵۰۰ تومان",
            "taxi": "۱۵,۰۰۰ تومان",
            "snap": "متغیر"
        }
    }
    
    if MAP_LOADED:
        info["graph_info"] = {
            "drive_nodes": len(G_drive.nodes()),
            "drive_edges": len(G_drive.edges()),
            "walk_nodes": len(G_walk.nodes()),
            "walk_edges": len(G_walk.edges()),
            "multimodal_nodes": len(D.nodes()),
            "multimodal_edges": len(D.edges())
        }
    
    return jsonify(info)

@app.route("/nearby_bus_stops", methods=["GET"])
def nearby_bus_stops():
    """ایستگاه‌های اتوبوس نزدیک به مختصات"""
    try:
        lat = float(request.args.get("lat", 30.2839))
        lon = float(request.args.get("lon", 57.0834))
        
        if not MAP_LOADED:
            return jsonify({"error": "map.py لود نشده"}), 500
        
        nearest_node = nearest_walk(G_walk, lat, lon)
        
        # پیدا کردن نزدیک‌ترین ایستگاه‌های اتوبوس
        bus_stops = []
        for bus_name, bus_info in bus_routes.items():
            for stop_name, stop_lat, stop_lon in bus_info["stops"]:
                stop_node = nearest_walk(G_walk, stop_lat, stop_lon)
                try:
                    distance = nx.shortest_path_length(
                        G_walk,
                        nearest_node,
                        stop_node,
                        weight="length"
                    )
                    
                    if distance < 2000:  # کمتر از 2 کیلومتر
                        bus_stops.append({
                            "name": stop_name,
                            "bus": bus_name,
                            "coordinates": [stop_lat, stop_lon],
                            "distance_meters": int(distance),
                            "walk_time_minutes": int(distance / (WALK_SPEED * 60))
                        })
                except:
                    continue
        
        # مرتب‌سازی بر اساس فاصله
        bus_stops.sort(key=lambda x: x["distance_meters"])
        
        return jsonify({
            "current_location": [lat, lon],
            "nearest_node": str(nearest_node),
            "bus_stops": bus_stops[:10],  # فقط 10 تا نزدیک‌ترین
            "count": len(bus_stops)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug_info", methods=["GET"])
def get_debug_info():
    """دریافت اطلاعات دیباگ"""
    try:
        # خواندن آخرین 5 فایل دیباگ
        debug_files = [f for f in os.listdir('.') if f.startswith('debug_') and f.endswith('.json')]
        debug_files.sort(reverse=True)
        
        debug_data = []
        for file in debug_files[:5]:  # فقط 5 فایل آخر
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                debug_data.append({
                    "file": file,
                    "timestamp": data.get("timestamp", ""),
                    "summary": {
                        "start": data.get("input", {}).get("start_coords", []),
                        "end": data.get("input", {}).get("end_coords", []),
                        "edges": data.get("dijkstra_output", {}).get("edge_count", 0)
                    }
                })
            except:
                continue
        
        return jsonify({
            "status": "success",
            "count": len(debug_data),
            "files": debug_data,
            "current_time": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

# ==================== Routes استاتیک و فایل‌ها ====================

@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico') if os.path.exists('static/favicon.ico') else ('', 204)

# ==================== راه‌اندازی سرور ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 سپرا - سرویس مسیریابی هوشمند")
    print("="*70)
    print(f"📍 شهر: کرمان")
    print(f"📍 ورژن: 3.0")
    print(f"📍 وضعیت map.py: {'✅ لود شده' if MAP_LOADED else '❌ لود نشده'}")
    
    if MAP_LOADED:
        print(f"📍 اطلاعات گراف:")
        print(f"   • رانندگی: {len(G_drive.nodes())} گره, {len(G_drive.edges())} یال")
        print(f"   • پیاده‌روی: {len(G_walk.nodes())} گره, {len(G_walk.edges())} یال")
        print(f"   • چندحالته: {len(D.nodes())} گره, {len(D.edges())} یال")
        print(f"📍 خطوط اتوبوس: {len(bus_routes)} خط")
        print(f"📍 مسیرهای تاکسی: {len(taxi_routes)} مسیر")
    
    print(f"📍 محدوده مختصات: عرض ۲۹-۳۱، طول ۵۶-۵۸")
    print(f"📍 زمان فعالیت اتوبوس: ۸:۰۰ تا ۲۰:۰۰")
    print(f"📍 آدرس سرور: http://127.0.0.1:5000")
    print("="*70)
    print("💡 نکته: برای دیباگ، کنسول مرورگر (F12) و ترمینال سرور را باز نگه دارید")
    print("="*70)
    
    app.run(debug=True, port=5000, host='0.0.0.0')