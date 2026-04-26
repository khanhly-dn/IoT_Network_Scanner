import sys
import csv
import json
import socket
import ipaddress
import argparse
import platform
import subprocess
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from scapy.all import ARP, Ether, srp
    CO_SCAPY = True
except ImportError:
    CO_SCAPY = False
PORT_PHO_BIEN = [21, 22, 23, 80, 443, 3306, 3389, 8080, 8443]

# ---- NHAN DIEN HE DIEU HANH ----
def nhan_dien_he_dieu_hanh(mac, ten_may):
    mac = mac.lower()
    ten_may = ten_may.lower()

    dau_hieu_windows = ["desktop", "laptop", "pc", "workstation"]
    dau_hieu_linux   = ["ubuntu", "linux", "raspberry", "debian", "server"]
    dau_hieu_android = ["android", "samsung", "xiaomi", "oppo", "vivo", "realme", "huawei", "pixel"]
    dau_hieu_ios     = ["iphone", "ipad", "macbook", "apple"]
    dau_hieu_router  = ["router", "gateway", "ap-", "tplink", "asus", "dlink", "archer"]
    for dh in dau_hieu_windows:
        if dh in ten_may:
            return "Windows"
    for dh in dau_hieu_linux:
        if dh in ten_may:
            return "Linux"
    for dh in dau_hieu_android:
        if dh in ten_may:
            return "Android"
    for dh in dau_hieu_ios:
        if dh in ten_may:
            return "iOS/macOS"
    for dh in dau_hieu_router:
        if dh in ten_may:
            return "Router/AP"

    prefix_ios     = ["a4:c3:f0", "f0:18:98", "3c:22:fb", "dc:a4:ca", "00:17:f2"]
    prefix_android = ["00:1a:11", "40:4e:36", "b4:ae:2b", "94:65:2d"]

    for p in prefix_ios:
        if mac.startswith(p):
            return "iOS/macOS"
    for p in prefix_android:
        if mac.startswith(p):
            return "Android"
    return "Khong xac dinh"

# ---- HAM HO TRO ----
def lay_ten_may(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Khong xac dinh"


def ping_may_voi_tg(ip):
    he_dieu_hanh = platform.system().lower()
    if he_dieu_hanh == "windows":
        lenh = ["ping", "-n", "1", "-w", "1000", str(ip)]
    else:
        lenh = ["ping", "-c", "1", "-W", "1", str(ip)]

    bat_dau = time.time()
    ket_qua = subprocess.run(
        lenh,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    tg_ms = round((time.time() - bat_dau) * 1000, 1)

    if ket_qua.returncode != 0:
        return False, 0
    output = ket_qua.stdout
    if he_dieu_hanh == "windows":
        for dong in output.split("\n"):
            if "time=" in dong or "time<" in dong:
                try:
                    if "time=" in dong:
                        tg_ms = float(dong.split("time=")[1].split("ms")[0].strip())
                    elif "time<" in dong:
                        tg_ms = 1.0
                except Exception:
                    pass
    else:
        for dong in output.split("\n"):
            if "time=" in dong:
                try:
                    tg_ms = float(dong.split("time=")[1].split(" ms")[0])
                except Exception:
                    pass
    return True, tg_ms

def quet_port(ip):
    port_mo = []
    for port in PORT_PHO_BIEN:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                port_mo.append(port)
            s.close()
        except Exception:
            pass
    return port_mo

def lay_dai_mang():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_may = s.getsockname()[0]
        s.close()
        phan = ip_may.rsplit(".", 1)
        return f"{phan[0]}.0/24"
    except Exception:
        return "192.168.1.0/24"

# ---- QUET MANG ----
def quet_bang_scapy(mang):
    print("[*] Dang quet bang ARP (can quyen admin)...\n")
    goi_arp  = ARP(pdst=mang)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    goi_tin  = broadcast / goi_arp
    tra_loi, _ = srp(goi_tin, timeout=2, verbose=False)

    danh_sach = []
    for _, nhan in tra_loi:
        ten_may = lay_ten_may(nhan.psrc)
        _, tg_ms = ping_may_voi_tg(nhan.psrc)
        port_mo  = quet_port(nhan.psrc)
        hdo      = nhan_dien_he_dieu_hanh(nhan.hwsrc, ten_may)
        danh_sach.append({
            "ip":      nhan.psrc,
            "mac":     nhan.hwsrc,
            "ten_may": ten_may,
            "ping_ms": tg_ms,
            "port_mo": port_mo,
            "hdo":     hdo,
        })
        print(f"  [+] {nhan.psrc:<18} {ten_may:<25} {hdo:<15} {tg_ms}ms  ports={port_mo}")
    return danh_sach

def _quet_mot_ip(ip):
    alive, tg_ms = ping_may_voi_tg(ip)
    if not alive:
        return None
    ten_may = lay_ten_may(ip)
    port_mo = quet_port(ip)
    hdo     = nhan_dien_he_dieu_hanh("", ten_may)
    return {
        "ip":      ip,
        "mac":     "Khong co (can ARP)",
        "ten_may": ten_may,
        "ping_ms": tg_ms,
        "port_mo": port_mo,
        "hdo":     hdo,
    }

def quet_bang_ping(mang):
    print("[*] Dang quet bang ping (khong can quyen admin)...\n")
    mang_ip   = ipaddress.IPv4Network(mang, strict=False)
    tat_ca_ip = [str(ip) for ip in mang_ip.hosts()]
    print(f"[*] Tong so IP can quet: {len(tat_ca_ip)}\n")

    danh_sach = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        tuong_lai = {executor.submit(_quet_mot_ip, ip): ip for ip in tat_ca_ip}
        for future in as_completed(tuong_lai):
            try:
                thiet_bi = future.result()
                if thiet_bi:
                    danh_sach.append(thiet_bi)
                    print(f"  [+] {thiet_bi['ip']:<18} {thiet_bi['ten_may']:<25} {thiet_bi['hdo']:<15} {thiet_bi['ping_ms']}ms  ports={thiet_bi['port_mo']}")
            except Exception:
                pass
    return danh_sach

# ---- SO SANH 2 LAN QUET ----
def so_sanh_lan_truoc(danh_sach_moi, file_lich_su):
    if not Path(file_lich_su).exists():
        return
    with open(file_lich_su, "r", encoding="utf-8") as f:
        danh_sach_cu = json.load(f)

    ip_cu  = {d["ip"] for d in danh_sach_cu}
    ip_moi = {d["ip"] for d in danh_sach_moi}
    thiet_bi_moi = ip_moi - ip_cu
    thiet_bi_mat = ip_cu  - ip_moi

    if thiet_bi_moi or thiet_bi_mat:
        print("\n" + "=" * 60)
        print("  CANH BAO - CO THAY DOI SO VOI LAN QUET TRUOC")
        print("=" * 60)
        for ip in thiet_bi_moi:
            print(f"  [!] THIET BI MOI XUAT HIEN : {ip}")
        for ip in thiet_bi_mat:
            print(f"  [-] Thiet bi da ngat ket noi: {ip}")
        print("=" * 60)
    else:
        print("\n  [OK] Mang khong co thay doi so voi lan quet truoc.")

# ---- LUU KET QUA ----
def luu_csv(danh_sach, ten_file):
    with open(ten_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ip", "mac", "ten_may", "ping_ms", "port_mo", "hdo"])
        writer.writeheader()
        for d in danh_sach:
            writer.writerow({**d, "port_mo": str(d["port_mo"])})
    print(f"  [+] Da luu CSV  : {ten_file}")

def luu_txt(danh_sach, ten_file, mang):
    with open(ten_file, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  Tool Quet Mang - Simple Network Scanner\n")
        f.write("=" * 70 + "\n")
        f.write(f"  Mang quet : {mang}\n")
        f.write(f"  Thoi gian : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"  Tong thiet bi: {len(danh_sach)}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"  {'IP':<18} {'MAC':<22} {'Ten may':<25} {'Ping':>7}  {'HDH':<15} {'Ports'}\n")
        f.write(f"  {'-'*17} {'-'*21} {'-'*24} {'-'*7}  {'-'*14} {'-'*20}\n")
        for d in danh_sach:
            f.write(f"  {d['ip']:<18} {d['mac']:<22} {d['ten_may']:<25} {str(d['ping_ms'])+' ms':>7}  {d['hdo']:<15} {d['port_mo']}\n")
    print(f"  [+] Da luu TXT  : {ten_file}")

def luu_lich_su(danh_sach, ten_file):
    with open(ten_file, "w", encoding="utf-8") as f:
        json.dump(danh_sach, f, ensure_ascii=False, indent=2)

# ---- IN KET QUA ----
def in_tieu_de(mang):
    print("=" * 70)
    print("   Tool Quet Mang - Simple Network Scanner")
    print("=" * 70)
    print(f"   Mang quet : {mang}")
    print(f"   Bat dau   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

def in_ket_qua(danh_sach, mang):
    danh_sach.sort(key=lambda d: int(d["ip"].split(".")[-1]))
    print()
    print("=" * 70)
    print(f"  KET QUA - Tim thay {len(danh_sach)} thiet bi")
    print("=" * 70)

    if not danh_sach:
        print("  Khong tim thay thiet bi nao.")
    else:
        print(f"  {'IP':<18} {'MAC':<22} {'Ten may':<22} {'Ping':>7}  {'HDH':<15} {'Ports'}")
        print(f"  {'-'*17} {'-'*21} {'-'*21} {'-'*7}  {'-'*14} {'-'*15}")
        for d in danh_sach:
            ports_str = str(d["port_mo"]) if d["port_mo"] else "[]"
            print(f"  {d['ip']:<18} {d['mac']:<22} {d['ten_may']:<22} {str(d['ping_ms'])+' ms':>7}  {d['hdo']:<15} {ports_str}")
    print("=" * 70)
    print(f"  Ket thuc : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    ten_csv      = f"ket_qua_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    ten_txt      = f"ket_qua_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    ten_lich_su  = "lich_su_quet.json"
    print()
    so_sanh_lan_truoc(danh_sach, ten_lich_su)
    print()
    luu_csv(danh_sach, ten_csv)
    luu_txt(danh_sach, ten_txt, mang)
    luu_lich_su(danh_sach, ten_lich_su)
    print(f"  [+] Da luu lich su: {ten_lich_su}")

# ---- CHAY CHINH ----
def main():
    parser = argparse.ArgumentParser(description="Tool quet mang noi bo")
    parser.add_argument("mang", nargs="?", default=None, help="Vi du: 192.168.1.0/24")
    parser.add_argument("--ping", action="store_true", help="Ep dung ping thay vi ARP")
    args = parser.parse_args()
    mang = args.mang or lay_dai_mang()

    try:
        ipaddress.IPv4Network(mang, strict=False)
    except ValueError:
        print(f"[!] Dia chi mang khong hop le: {mang}")
        sys.exit(1)
    in_tieu_de(mang)
    if CO_SCAPY and not args.ping:
        danh_sach = quet_bang_scapy(mang)
    else:
        if not CO_SCAPY:
            print("[!] Chua cai scapy, dung ping thay the.")
            print("[!] Cai bang lenh: pip install scapy\n")
        danh_sach = quet_bang_ping(mang)
    in_ket_qua(danh_sach, mang)

if __name__ == "__main__":
    main()