# 🛒 Smart Trolley System – Demo_PC 

A powerful and intuitive Python desktop application that transforms the shopping experience with **real-time barcode scanning**, automatic billing — all from a clean, modern GUI!

---

## 🌟 Why You'll Love It

✅ **Live Barcode Scanning** – Scan any product instantly using your webcam, no manual entry needed.

✅ **Smart Product Lookup** – Fetches product details directly from a local SQLite database in milliseconds.

✅ **Auto Billing System** – Automatically calculates totals and updates your cart in real time.

✅ **Duplicate Item Handling** – Detects already-scanned products and smartly accumulates quantities.

✅ **Multiple Payment Methods** – Supports Easypaisa, JazzCash, and Debit Card payments.

✅ **Clean & Responsive UI** – A modern Tkinter-based interface that's easy to use for anyone.

✅ **Detailed Cart Breakdown:**

- 🏷️ **Product Name** – Clearly labeled items in your cart.
- 
- 💰 **Unit Price** – Per-item cost fetched straight from the database.
- 
- 🔢 **Quantity** – Fully adjustable per scan.
- 
- 🧾 **Line Total** – Auto-calculated for each product.
- 
- 💵 **Grand Total** – Always up to date as you scan.

✅ **Threaded Scanning** – Camera runs on a background thread so the UI never freezes.

✅ **Smart Error Handling** – Gracefully handles unknown barcodes, camera errors, and invalid inputs.

---

## ⚙️ Tech Stack

🔹 **Python 3.8+** – The backbone of the application.

🔹 **Tkinter & ttk** – Provides a sleek, native desktop GUI.

🔹 **OpenCV (`cv2`)** – Handles real-time webcam capture and image processing.

🔹 **pyzbar** – Decodes barcodes and QR codes from live camera frames.

🔹 **SQLite3** – Lightweight, built-in local database for product storage. 

🔹 **threading** – Keeps the camera running without blocking the UI.

---

## 🏗️ How It Works

🔹 Step 1: Launch the app and click **"Start Scanning"**.

🔹 Step 2: Hold a product barcode in front of your webcam.

🔹 Step 3: Enter the quantity when prompted — item is added to your cart instantly.

🔹 Step 4: Click **"Scan Another Item"** to keep adding products.

🔹 Step 5: When done, click **"Proceed to Payment"** and choose your payment method.

🔹 step 6: Enter your payment details and complete the checkout. ✅

---

## 🚀 Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/smart-trolley.git
cd smart-trolley
```

### Step 2: Install Dependencies

```bash
pip install opencv-python pyzbar
```

> ⚠️ **Windows Users:** `pyzbar` requires the ZBar DLL. Download it from [zbar.sourceforge.net](http://zbar.sourceforge.net) and add it to your system PATH.

> ⚠️ **Linux Users:** Install the ZBar system library first:
> ```bash
> sudo apt-get install libzbar0
> ```

### Step 3: Set Up the Database

Create a file called `setup_db.py` and paste the following:

```python
import sqlite3

conn = sqlite3.connect("products.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        barcode TEXT PRIMARY KEY,
        name    TEXT NOT NULL,
        price   REAL NOT NULL
    )
""")

sample_products = [
    ("8961014255188", "Lux Soap",  25.0),
    ("L-EK-0600017",  "Shoes",   1000.0),
    ("9876543210987", "Olay Soap", 35.0),
]

cursor.executemany(
    "INSERT OR IGNORE INTO products (barcode, name, price) VALUES (?, ?, ?)",
    sample_products
)

conn.commit()
conn.close()
print("✅ Database ready!")
```

Then run it once:

```bash
python setup_db.py
```

### Step 4: Run the App

```bash
python smart_trolley.py
```
---

## 🔍 Under the Hood

- **Real-Time Frame Processing** – OpenCV captures frames continuously and pyzbar decodes barcodes on the fly.
- **Thread-Safe UI** – All UI updates are routed through `root.after()` to safely communicate between the camera thread and the main GUI thread.
- **Persistent Database** – SQLite stores your full product catalog locally — no internet required.
- **Duplicate Detection** – If the same barcode is scanned twice, quantities are merged automatically.
- **Graceful Error Handling** – Unknown barcodes trigger a friendly error dialog instead of crashing the app.
- **Clean Shutdown** – The database connection closes safely when the window is closed.

---

## 🔮 Future Enhancements

✨ **Real Payment Gateway** – Integrate actual Easypaisa/JazzCash APIs for live transactions.
✨ **Admin Panel** – Add, edit, and remove products directly from the GUI.
✨ **Receipt Printing** – Generate and print PDF receipts after checkout.
✨ **QR Code Support** – Extend scanning to QR-coded products.
✨ **Dark Mode UI** – Optional dark theme for low-light environments.
✨ **Sales Reports** – Track daily/weekly sales from the database.
✨ **Cross-Platform Camera Fix** – Remove Windows-only `CAP_DSHOW` for macOS/Linux compatibility.

---

## 📁 Project Structure

```
smart-trolley/
│
├── smart_trolley.py      # Main application (GUI + scanning logic)
├── setup_db.py           # One-time database initialization script
├── products.db           # SQLite product database (auto-created)
└── README.md             # Project documentation
```

---

## 📜 License

This project is licensed under the **MIT License** – free to use, modify, and share!

---

## 🙌 Acknowledgments

🛒 Barcode decoding powered by **[pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)**
📷 Camera integration via **[OpenCV](https://opencv.org/)**
🗄️ Data management using **Python's built-in SQLite3**

---

🚀 **Developed by [Prem Kumar]** – [premkumar11x@gmail.com]
