# Bzo

Ung dung tuy chinh cho ERPNext 16 (Frappe Framework v16).

## Noi dung

- `bzo/hooks.py`: khai bao app, `doctype_js`, `doc_events`, `after_install`
- `bzo/install.py`: tao Custom Field (Customer, Address), Property Setter, mau dia chi VN, nhap du lieu
- `bzo/accounting/`: he thong tai khoan TT99/2025 (`data/vn_tt99.json`), nap vao ERPNext (`chart_of_accounts.py`), mau thue VAT (`tax_templates.py`), event Company (`company.py`)
- `bzo/address/`: Address (`address.py`), nhap 34 tinh va 3321 xa/phuong (`vn_divisions.py`, `data/vn_divisions.json`)
- `bzo/customer/`: validate Customer
- `bzo/public/js/`: JS mo rong form Address
- `bzo/bzo/doctype/`: `province`, `ward`
- `bzo/fixtures/`, `bzo/translations/`, `bzo/patches/`, `bzo/patches.txt`

## Cai dat moi truong (Windows -> WSL2 Ubuntu 24.04)

```powershell
wsl --install -d Ubuntu-24.04
```

Trong Ubuntu (tham khao yeu cau phien ban tai tai lieu Frappe v16: Python 3.14, Node 24, MariaDB 11.8, Redis):

```bash
sudo apt update && sudo apt install -y git redis-server mariadb-server libmariadb-dev pkg-config curl build-essential
# cai uv/pyenv cho Python 3.14, nvm cho Node 24, roi:
npm i -g yarn
pip install frappe-bench
bench init --frappe-branch version-16 frappe-bench
cd frappe-bench
bench new-site bzo.localhost --admin-password admin --mariadb-root-password <root_pw>
bench get-app --branch version-16 erpnext
bench --site bzo.localhost install-app erpnext
```

## Dua app nay vao bench

Workspace nay o `d:\Projects\2026\erpnext\bzo` (tren Windows: `/mnt/d/Projects/2026/erpnext/bzo` trong WSL).
Nen copy/clone vao o dia Linux de tranh cham:

```bash
cd ~/frappe-bench
git clone /mnt/d/Projects/2026/erpnext/bzo apps/bzo   # hoac: bench get-app /mnt/d/...
bench --site bzo.localhost install-app bzo
bench --site bzo.localhost set-config developer_mode 1
bench start
```

Mo http://bzo.localhost:8000 .

## Phat trien

```bash
bench --site bzo.localhost migrate        # dong bo DocType, chay patches
bench --site bzo.localhost clear-cache
bench build --app bzo                     # build assets
bench --site bzo.localhost export-fixtures
```

Tao DocType moi bang UI (developer mode, module `Bzo`) – file se tu sinh trong `bzo/bzo/doctype/`.
