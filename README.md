# 🔍 Simple Network Scanner

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python_3.10+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Library-Scapy-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Scan-ARP%20%7C%20ICMP-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Export-CSV%20%7C%20TXT%20%7C%20JSON-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge" />
</p>

<p align="center">
  Tool quét mạng nội bộ viết bằng <strong>Python</strong>, phát hiện thiết bị đang kết nối, đo ping, quét port, nhận diện hệ điều hành và lưu kết quả tự động.
</p>

---

## 📌 Giới thiệu

Dự án **Simple Network Scanner** được phát triển nhằm xây dựng công cụ **giám sát và phân tích mạng nội bộ** theo thời gian thực.  
Tool tự động phát hiện dải mạng đang dùng, quét toàn bộ thiết bị và phân tích chi tiết thông qua:
- 🖥️ **ARP Scan** – quét nhanh, lấy được MAC address, cần quyền admin
- 📡 **Ping Sweep** – quét song song 100 luồng, không cần quyền admin
- 🔍 **Port Scanner** – kiểm tra các port phổ biến trên mỗi thiết bị
- 💾 **Auto Export** – tự động lưu kết quả ra CSV, TXT, JSON

---

## ⚙️ Chức năng chính

- **Tự động phát hiện dải mạng** – không cần nhập tay, tự suy từ IP máy
- **2 chế độ quét:** `ARP Scan` (có MAC) và `Ping Sweep` (không cần admin)
- **Đo thời gian ping** – hiển thị độ trễ ms của từng thiết bị
- **Quét port phổ biến** – 21, 22, 23, 80, 443, 3306, 3389, 8080, 8443
- **Nhận diện hệ điều hành** – Windows, Linux, iOS/macOS, Android, Router/AP
- **So sánh lần quét trước** – cảnh báo nếu có thiết bị lạ mới vào mạng
- **Lưu kết quả tự động** – CSV (mở bằng Excel), TXT (đọc thẳng), JSON (lịch sử)

---

## 🧩 Sơ đồ hoạt động

<p align="center">
  <img width="700" alt="Sơ đồ hoạt động" src="https://github.com/khanhly-dn/IoT_Network_Scanner/blob/main/SDHD.png?raw=true" />
</p>

```
Chạy scanner.py
        ↓
Tự tìm dải mạng (192.168.x.0/24)
        ↓
Có scapy không?
   CÓ  →  ARP Scan  (cần admin, có MAC)
 KHÔNG  →  Ping Sweep (100 luồng song song)
        ↓
Với mỗi thiết bị tìm thấy:
  → Đo ping (ms)
  → Lấy hostname
  → Quét port: 22, 80, 443, 3389...
  → Nhận diện HDH: Windows / Linux / Router...
        ↓
In bảng kết quả ra terminal
        ↓
So sánh với lần quét trước → cảnh báo thiết bị lạ
        ↓
Lưu tự động: CSV · TXT · JSON
```

---

## 💻 Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.10+
- **Thư viện:**
  - `scapy` – gửi gói ARP, lấy MAC address
  - `socket` – lấy hostname, quét port
  - `ipaddress` – xử lý dải CIDR
  - `concurrent.futures` – chạy 100 luồng song song
  - `csv`, `json` – xuất file kết quả
- **Giao thức:** ARP (Layer 2), ICMP ping (Layer 3)
- **Nền tảng:** Windows · Linux · macOS

---

## 📊 Thông số kỹ thuật

| Thông số | Giá trị |
|---|---|
| Số luồng ping song song | 100 workers |
| Timeout ping (Windows) | 1000ms |
| Timeout ping (Linux/macOS) | 1000ms |
| Timeout quét port | 500ms / port |
| Port được quét | 21, 22, 23, 80, 443, 3306, 3389, 8080, 8443 |
| Dung lượng lịch sử | Toàn bộ lần quét gần nhất |
| Định dạng xuất file | CSV · TXT · JSON |

---

## 🚀 Hướng dẫn cài đặt

**1. Clone repo**
```bash
git clone https://github.com/khanhly-dn/IoT_Network_Scanner.git
cd IoT_Network_Scanner
```

**2. Cài thư viện**
```bash
pip install -r requirements.txt
```

> **Windows:** Cài thêm [Npcap](https://npcap.com/) để dùng chế độ ARP Scan.

**3. Chạy tool**
```bash
# Tự động tìm mạng, dùng ARP (cần admin/sudo)
sudo python scanner.py

# Quét dải mạng tùy chọn
sudo python scanner.py 192.168.1.0/24

# Chạy không cần admin (ping sweep)
python scanner.py --ping

# Kết hợp
python scanner.py 192.168.100.0/24 --ping
```

---

## 📷 Kết quả Demo

<p align="center">
  <img width="750" alt="Kết quả Demo" src="https://github.com/khanhly-dn/IoT_Network_Scanner/blob/main/KQ_DEMO.png?raw=true" />
</p>
🎬 **Video hoạt động:** *https://drive.google.com/file/d/1G395lE1OFZ3vAfFdqbZliQLi1CdW4kU9/view?usp=sharing*


---

## 🗂️ Cấu trúc project

```
IoT_Network_Scanner/
│
├── scanner.py              # File chạy chính
├── requirements.txt        # Thư viện cần cài
├── lich_su_quet.json       # Lịch sử quét (tự tạo sau lần đầu)
├── ket_qua_YYYYMMDD.csv    # Kết quả xuất CSV (tự tạo)
├── ket_qua_YYYYMMDD.txt    # Kết quả xuất TXT (tự tạo)
└── README.md
```

---

## 🚀 Hướng phát triển

- [ ] Thêm **giao diện Web Dashboard** xem kết quả trực tiếp trên trình duyệt
- [ ] Gửi **cảnh báo Telegram** khi phát hiện thiết bị lạ
- [ ] Chế độ **theo dõi liên tục** – tự quét mỗi X phút
- [ ] Vẽ **biểu đồ lịch sử** thiết bị theo thời gian
- [ ] Hỗ trợ **quét IPv6**
- [ ] Xuất thêm định dạng **PDF / HTML report**

---

## 👤 Thực hiện

**Lý Gia Khánh**  
Khoa Công nghệ Thông tin – Trường Đại học Đại Nam

---

<p align="center">
  Made with Python · Scapy · Socket · Threading
</p>
