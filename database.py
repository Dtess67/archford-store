import sqlite3
import os
from datetime import datetime

DB_PATH = 'archford.db'

# ─────────────────────────────────────────────
# DATABASE INIT
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables and seed data if users table is missing or empty."""
    conn = get_db()
    c = conn.cursor()

    # Determine if initialization is required based on users table data
    need_init = False
    try:
        # Try to read from users; if table doesn't exist, this will raise
        c.execute('SELECT COUNT(*) FROM users')
        count = c.fetchone()[0]
        if count == 0:
            need_init = True
    except sqlite3.Error:
        # Table doesn't exist or other DB error — trigger full init
        need_init = True

    if not need_init:
        conn.close()
        return

    print("Building local database...")

    # USERS (mirrors dbo_AR_MasterTable)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        school_name TEXT,
        customer_id TEXT,
        contact_name TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        phone TEXT,
        email TEXT,
        tax_code TEXT,
        discount_code TEXT,
        terms_code TEXT
    )''')

    # INVENTORY CODES (mirrors dbo_IN_InventoryCode)
    c.execute('''CREATE TABLE IF NOT EXISTS inventory_codes (
        code TEXT PRIMARY KEY,
        description TEXT,
        tax_flag INTEGER DEFAULT 0,
        sales_tax_code TEXT
    )''')

    # PRODUCTS (mirrors dbo_IN_Master)
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        vendor TEXT,
        cat TEXT NOT NULL,
        pkg TEXT,
        price REAL NOT NULL,
        price2 REAL,
        price3 REAL,
        price4 REAL,
        price5 REAL,
        img TEXT,
        taxable INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        location TEXT DEFAULT 'MAIN'
    )''')

    # ORDERS (mirrors dbo_WebOrderExport)
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_num TEXT UNIQUE,
        username TEXT,
        school TEXT,
        contact TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        po_number TEXT,
        payment TEXT,
        ship_later TEXT DEFAULT 'N',
        notes TEXT,
        subtotal REAL,
        shipping REAL,
        total REAL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT
    )''')

    # ORDER ITEMS
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_num TEXT,
        item_id TEXT,
        name TEXT,
        description TEXT,
        cat TEXT,
        pkg TEXT,
        qty INTEGER,
        unit_price REAL,
        tax_code TEXT,
        taxable INTEGER DEFAULT 0,
        line_total REAL,
        FOREIGN KEY (order_num) REFERENCES orders(order_num)
    )''')

    conn.commit()

    # SEED DATA
    _seed_inventory_codes(conn)
    _seed_products(conn)
    _seed_users(conn)

    conn.close()
    print(f"Database built successfully at {DB_PATH}")

# ─────────────────────────────────────────────
# SEED INVENTORY CODES
# ─────────────────────────────────────────────
def _seed_inventory_codes(conn):
    codes = [
        ('AA', 'ART', 0, 'NT'),
        ('BB', 'ATHLETIC', 0, '15-04'),
        ('CC', 'CUSTODIAL', 0, '15-04'),
        ('DD', 'OFFICE SUPPLIES', 0, '15-04'),
        ('EE', 'EQUIPMENT/FURNITURE', 0, '15-04'),
        ('G2', 'INSTRUCTIONAL SUPPLIES', 0, 'NT'),
        ('GG', 'INSTRUCTIONAL SUPPLIES', 0, '15-04'),
        ('H2', 'PAPER PRODUCTS', 0, '15-04'),
        ('HH', 'PAPER PRODUCTS', 0, '15-04'),
        ('KK', 'COMPUTER', 0, '15-04'),
        ('LL', 'PROJECTION LAMPS', 0, 'NT'),
        ('M2', 'MARKERS/PENS', 0, 'NT'),
        ('MM', 'MARKERS/PENS', 0, '15-04'),
        ('R2', 'READING SUPPLIES', 0, 'NT'),
        ('RR', 'READING SUPPLIES', 0, '15-04'),
        ('VV', 'AUDIO/VISUAL', 0, 'NT'),
        ('XX', 'MISC', 0, '15-04'),
    ]
    conn.executemany(
        'INSERT OR IGNORE INTO inventory_codes VALUES (?,?,?,?)', codes)
    conn.commit()

# ─────────────────────────────────────────────
# SEED PRODUCTS (all 1,241 — key items loaded)
# ─────────────────────────────────────────────
def _seed_products(conn):
    products = [
        # ART
        ('A01-003','WHITE GLUE - 4 OZ','ELMERS #E1322NR','ELMERS','ART','EACH',1.93,None,None,None,None,'https://archford.com/Content/images/items/A01-003.jpg',0),
        ('A01-005','WHITE GLUE - 8 OZ','ELMERS #E1324NR','ELMERS','ART','EACH',2.79,None,None,None,None,'https://archford.com/Content/images/items/A01-005.jpg',0),
        ('A01-008','WHITE GLUE - GALLON','ELMERS #E1326NR','ELMERS','ART','EACH',18.31,None,None,None,None,'https://archford.com/Content/images/items/A01-008.jpg',0),
        ('A01-011','SCHOOL GLUE - 4 OZ','ELMERS #E304NR','ELMERS','ART','EACH',1.69,None,None,None,None,'https://archford.com/Content/images/items/A01-011.jpg',0),
        ('A01-013','SCHOOL GLUE - 8 OZ','ELMERS #E308NR','ELMERS','ART','EACH',2.49,None,None,None,None,'https://archford.com/Content/images/items/A01-013.jpg',0),
        ('A01-016','GALLON SCHOOL GLUE','ELMERS #E340NR','ELMERS','ART','EACH',17.62,None,None,None,None,'https://archford.com/Content/images/items/A01-016.jpg',0),
        ('A01-050','DAB N STICK SCHOOL GLUE 50ml','CLEAR SCHOOL GLUE #50798','PRANG','ART','EACH',2.75,None,None,None,None,'https://archford.com/Content/images/items/A01-050.jpg',0),
        ('A01-100','GLUE STICKS SMALL .21 OZ ELMERS','ELMERS #E510','ELMERS','ART','EACH',0.58,None,None,None,None,'https://archford.com/Content/images/items/A01-100.jpg',0),
        ('A01-105','GLUE STICKS LARGE 1.27 OZ PRANG','PRANG 15371','PRANG','ART','EACH',1.17,None,None,None,None,'https://archford.com/Content/images/items/A01-105.jpg',0),
        ('A01-120','4 OZ RUBBER CEMENT','ELMERS/ROSS #E904','ELMERS','ART','EACH',2.24,None,None,None,None,'https://archford.com/Content/images/items/A01-120.jpg',0),
        ('A01-128','RUBBER CEMENT QUART','ELMERS #E904','ELMERS','ART','EACH',12.38,None,None,None,None,'https://archford.com/Content/images/items/A01-128.jpg',0),
        ('A01-132','RUBBER CEMENT PINT','ELMERS RUBBER CEMENT','ELMERS','ART','EACH',8.25,None,None,None,None,'https://archford.com/Content/images/items/A01-132.jpg',0),
        ('A02-001','COLORED CHALK 12 COUNT','ASSORTED COLORS','PRANG','ART','BOX',1.45,None,None,None,None,'https://archford.com/Content/images/items/A02-001.jpg',0),
        ('A02-005','OIL PASTELS 12 COUNT','STUDENT GRADE','PRANG','ART','SET',2.15,None,None,None,None,'https://archford.com/Content/images/items/A02-005.jpg',0),
        ('A02-006','OIL PASTELS 16 COUNT','STUDENT GRADE','PRANG','ART','SET',2.85,None,None,None,None,'https://archford.com/Content/images/items/A02-006.jpg',0),
        ('A02-007','OIL PASTELS 25 COUNT','STUDENT GRADE','PRANG','ART','SET',3.95,None,None,None,None,'https://archford.com/Content/images/items/A02-007.jpg',0),
        ('A02-010','CRAYOLA CRAYONS 24 COUNT','CRAYOLA STANDARD','CRAYOLA','ART','BOX',2.25,None,None,None,None,'https://archford.com/Content/images/items/A02-010.jpg',0),
        ('A02-012','CRAYOLA CRAYONS 48 COUNT','CRAYOLA LARGE BOX','CRAYOLA','ART','BOX',4.50,None,None,None,None,'https://archford.com/Content/images/items/A02-012.jpg',0),
        ('A02-013','CRAYOLA CRAYONS 64 COUNT','CRAYOLA WITH SHARPENER','CRAYOLA','ART','BOX',6.75,None,None,None,None,'https://archford.com/Content/images/items/A02-013.jpg',0),
        ('A02-014','CRAYOLA CRAYONS 16 COUNT','CRAYOLA BASIC','CRAYOLA','ART','BOX',1.85,None,None,None,None,'https://archford.com/Content/images/items/A02-014.jpg',0),
        ('A02-015','CRAYOLA CRAYONS 8 COUNT','CRAYOLA STANDARD 8','CRAYOLA','ART','BOX',0.99,None,None,None,None,'https://archford.com/Content/images/items/A02-015.jpg',0),
        ('A02-018','CRAYOLA CRAYONS CLASSPACK 400','400 COUNT 8 COLORS','CRAYOLA','ART','EACH',28.50,None,None,None,None,'https://archford.com/Content/images/items/A02-018.jpg',0),
        ('A02-020','PENCIL BOX PLASTIC','STORAGE BOX FOR SUPPLIES','VARIOUS','ART','EACH',1.25,None,None,None,None,'https://archford.com/Content/images/items/A02-020.jpg',0),
        ('A02-025','CRAYOLA CLASSPACK 256','256 MARKERS 8 COLORS','CRAYOLA','ART','EACH',39.99,None,None,None,None,'https://archford.com/Content/images/items/A02-025.jpg',0),
        ('A02-026','CLASSPACK CONSTRUCTION PAPER CRAYONS','400 CT 25 OF 16 COLORS CRAYOLA #52-1617','CRAYOLA','ART','EACH',43.80,None,None,None,None,'https://archford.com/Content/images/items/A02-026.jpg',0),
        ('A02-100','COLORED PENCILS 12 COUNT','PRE-SHARPENED','PRANG','ART','SET',2.50,None,None,None,None,'https://archford.com/Content/images/items/A02-100.jpg',0),
        ('A02-105','COLORED PENCILS 24 COUNT','PREMIUM 24 COLORS','PRANG','ART','SET',4.25,None,None,None,None,'https://archford.com/Content/images/items/A02-105.jpg',0),
        ('A02-110','COLORED PENCILS 48 COUNT','PROFESSIONAL GRADE','PRANG','ART','SET',8.50,None,None,None,None,'https://archford.com/Content/images/items/A02-110.jpg',0),
        ('A02-200','ALPHACOLOR SQUARE CHALK','SQUARE CHALK SET','ALPHACOLOR','ART','BOX',4.99,None,None,None,None,'https://archford.com/Content/images/items/A02-200.jpg',0),
        ('A03-001','WATER COLOR PAINT 8 COLORS','OVAL PAN SET','PRANG','ART','EACH',2.15,None,None,None,None,'https://archford.com/Content/images/items/A03-001.jpg',0),
        ('A03-002','WIGGLY EYES ASSORTED','CRAFT EYES','VARIOUS','ART','PKG',2.99,None,None,None,None,'https://archford.com/Content/images/items/A03-002.jpg',0),
        ('A03-003','PIPE STEMS 12 INCH','CHENILLE STEMS','VARIOUS','ART','PKG',1.99,None,None,None,None,'https://archford.com/Content/images/items/A03-003.jpg',0),
        ('A03-050','PRANG LIQUID TEMPERA','LIQUID TEMPERA PAINT','PRANG','ART','EACH',3.85,None,None,None,None,'https://archford.com/Content/images/items/A03-050.jpg',0),
        ('A03-051','LIQUID TEMPERA SET','SET OF 6 COLORS','PRANG','ART','SET',18.50,None,None,None,None,'https://archford.com/Content/images/items/A03-051.jpg',0),
        ('A04-005','CONSTRUCTION PAPER 9X12 50 SHEETS','ASSORTED COLORS','PACON','ART','PACK',3.89,None,None,None,None,'https://archford.com/Content/images/items/A04-005.jpg',0),
        ('A04-010','CONSTRUCTION PAPER 12X18','ASSORTED COLORS 50 SHEETS','PACON','ART','PACK',5.25,None,None,None,None,'https://archford.com/Content/images/items/A04-010.jpg',0),
        ('A05-001','PAINT BRUSHES FLAT SET 12','ASSORTED FLAT BRUSHES','VARIOUS','ART','SET',4.75,None,None,None,None,'https://archford.com/Content/images/items/A05-001.jpg',0),
        ('A06-001','MODELING CLAY ASSORTED','MODELING CLAY 1 LB','VARIOUS','ART','EACH',4.25,None,None,None,None,'https://archford.com/Content/images/items/A06-001.jpg',0),
        # OFFICE SUPPLIES
        ('D01-002','STAPLER FULL STRIP SWINGLINE #747','VERY GOOD DESK STAPLER #74701','SWINGLINE','OFFICE SUPPLIES','EACH',13.99,None,None,None,None,'https://archford.com/Content/images/items/D01-002.jpg',1),
        ('D01-003','LARGE ONE ARM STAPLER SWINGLINE 39005','USES LARGER STAPLES NOT STANDARD SIZE','SWINGLINE','OFFICE SUPPLIES','EACH',35.95,None,None,None,None,'https://archford.com/Content/images/items/D01-003.jpg',1),
        ('D01-006','STAPLER FULL STRIP BOSTITCH B440','BOSTITCH B440','BOSTITCH','OFFICE SUPPLIES','EACH',9.95,None,None,None,None,'https://archford.com/Content/images/items/D01-006.jpg',1),
        ('D01-007','STAPLER HALF STRIP INEXPENSIVE','LEONARD 82105','LEONARD','OFFICE SUPPLIES','EACH',4.79,None,None,None,None,'https://archford.com/Content/images/items/D01-007.jpg',1),
        ('D01-008','STAPLER FULL STRIP INEXPENSIVE','PYRAMID 1111434','PYRAMID','OFFICE SUPPLIES','EACH',5.93,None,None,None,None,'https://archford.com/Content/images/items/D01-008.jpg',1),
        ('D01-010','STAPLES STANDARD CHISEL POINT 5000 BOX','STANDARD STAPLES','SWINGLINE','OFFICE SUPPLIES','BOX',2.49,None,None,None,None,'https://archford.com/Content/images/items/D01-010.jpg',1),
        ('D01-015','STAPLES HEAVY DUTY 1000 BOX','HEAVY DUTY STAPLES','SWINGLINE','OFFICE SUPPLIES','BOX',4.15,None,None,None,None,'https://archford.com/Content/images/items/D01-015.jpg',1),
        ('D02-010','SCISSORS 7 INCH POINTED','STANDARD CLASSROOM SCISSORS','FISKARS','OFFICE SUPPLIES','EACH',3.25,None,None,None,None,'https://archford.com/Content/images/items/D02-010.jpg',1),
        ('D02-015','SCISSORS 5 INCH BLUNT KIDS','SAFETY SCISSORS','FISKARS','OFFICE SUPPLIES','EACH',2.10,None,None,None,None,'https://archford.com/Content/images/items/D02-015.jpg',1),
        ('D02-020','SCISSORS TEACHER 8 INCH','TEACHER QUALITY SCISSORS','FISKARS','OFFICE SUPPLIES','EACH',5.50,None,None,None,None,'https://archford.com/Content/images/items/D02-020.jpg',1),
        ('D03-005','TAPE TRANSPARENT 3/4 X 1000','CLEAR TRANSPARENT TAPE','SCOTCH','OFFICE SUPPLIES','EACH',1.49,None,None,None,None,'https://archford.com/Content/images/items/D03-005.jpg',1),
        ('D03-010','MASKING TAPE 3/4 X 60 YARDS','GENERAL PURPOSE MASKING TAPE','3M','OFFICE SUPPLIES','EACH',2.89,None,None,None,None,'https://archford.com/Content/images/items/D03-010.jpg',1),
        ('D04-002','TAPE DISPENSER DESKTOP HEAVY DUTY','BLACK WEIGHTED BASE','SWINGLINE','OFFICE SUPPLIES','EACH',6.45,None,None,None,None,'https://archford.com/Content/images/items/D04-002.jpg',1),
        ('D05-010','BINDER CLIPS MEDIUM 12 BOX','BOX OF 12 MEDIUM CLIPS','ACCO','OFFICE SUPPLIES','BOX',1.89,None,None,None,None,'https://archford.com/Content/images/items/D05-010.jpg',1),
        ('D05-015','BINDER CLIPS LARGE 12 BOX','BOX OF 12 LARGE CLIPS','ACCO','OFFICE SUPPLIES','BOX',2.45,None,None,None,None,'https://archford.com/Content/images/items/D05-015.jpg',1),
        ('D05-020','PAPER CLIPS JUMBO 100 BOX','JUMBO VINYL COATED','ACCO','OFFICE SUPPLIES','BOX',1.25,None,None,None,None,'https://archford.com/Content/images/items/D05-020.jpg',1),
        ('D05-025','PAPER CLIPS STANDARD 100 BOX','STANDARD SIZE CLIPS','ACCO','OFFICE SUPPLIES','BOX',0.89,None,None,None,None,'https://archford.com/Content/images/items/D05-025.jpg',1),
        ('D05-051','BINDER CLIPS NARROW','NARROW BINDER CLIPS','ACCO','OFFICE SUPPLIES','BOX',1.45,None,None,None,None,'https://archford.com/Content/images/items/D05-051.jpg',1),
        ('D05-052','BINDER CLIPS ASSORTED','ASSORTED SIZES BOX','ACCO','OFFICE SUPPLIES','BOX',2.25,None,None,None,None,'https://archford.com/Content/images/items/D05-052.jpg',1),
        ('D06-005','MANILA FOLDERS LETTER 100 BOX','STANDARD MANILA FOLDERS','SMEAD','OFFICE SUPPLIES','BOX',12.75,None,None,None,None,'https://archford.com/Content/images/items/D06-005.jpg',1),
        ('D06-010','HANGING FOLDERS LETTER 25 BOX','GREEN HANGING FILES','SMEAD','OFFICE SUPPLIES','BOX',11.50,None,None,None,None,'https://archford.com/Content/images/items/D06-010.jpg',1),
        ('D07-001','3 RING BINDER 1 INCH WHITE','STANDARD 1 INCH BINDER','AVERY','OFFICE SUPPLIES','EACH',3.99,None,None,None,None,'https://archford.com/Content/images/items/D07-001.jpg',1),
        ('D07-002','3 RING BINDER 2 INCH BLUE','HEAVY DUTY D-RING BINDER','AVERY','OFFICE SUPPLIES','EACH',5.75,None,None,None,None,'https://archford.com/Content/images/items/D07-002.jpg',1),
        ('D07-003','COMPOSITION NOTEBOOK WIDE RULE','100 SHEETS WIDE RULED','MEAD','OFFICE SUPPLIES','EACH',2.25,None,None,None,None,'https://archford.com/Content/images/items/D07-003.jpg',1),
        ('D08-010','CORRECTION FLUID WHITE OUT','FAST DRY LIQUID PAPER','BIC','OFFICE SUPPLIES','EACH',1.95,None,None,None,None,'https://archford.com/Content/images/items/D08-010.jpg',1),
        ('D09-005','STICKY NOTES 3X3 YELLOW 12 PACK','12 PADS 100 SHEETS EACH','POST-IT','OFFICE SUPPLIES','PACK',8.99,None,None,None,None,'https://archford.com/Content/images/items/D09-005.jpg',1),
        ('D09-010','STICKY NOTES 3X5 ASSORTED','5 PADS ASSORTED COLORS','POST-IT','OFFICE SUPPLIES','PACK',6.25,None,None,None,None,'https://archford.com/Content/images/items/D09-010.jpg',1),
        ('D10-001','RUBBER BANDS ASSORTED 1/4 LB','ASSORTED SIZES BOX','ALLIANCE','OFFICE SUPPLIES','BOX',2.10,None,None,None,None,'https://archford.com/Content/images/items/D10-001.jpg',1),
        ('D11-005','FILE TRAY DESKTOP LETTER','BLACK PLASTIC LETTER TRAY','VARIOUS','OFFICE SUPPLIES','EACH',5.50,None,None,None,None,'https://archford.com/Content/images/items/D11-005.jpg',1),
        # MARKERS/PENS
        ('B01-005','WASHABLE MARKERS BROAD 8 PACK','CRAYOLA BROAD TIP 8 COLORS','CRAYOLA','MARKERS/PENS','PACK',2.99,None,None,None,None,'https://archford.com/Content/images/items/B01-005.jpg',0),
        ('B01-010','WASHABLE MARKERS CLASSIC 10 PACK','CRAYOLA WASHABLE 10 PACK','CRAYOLA','MARKERS/PENS','PACK',3.49,None,None,None,None,'https://archford.com/Content/images/items/B01-010.jpg',0),
        ('B01-015','WASHABLE MARKERS FINE 8 PACK','CRAYOLA FINE TIP 8 COLORS','CRAYOLA','MARKERS/PENS','PACK',3.25,None,None,None,None,'https://archford.com/Content/images/items/B01-015.jpg',0),
        ('B01-020','CLASSPACK WASHABLE MARKERS 256','CRAYOLA 256 MARKERS 8 COLORS','CRAYOLA','MARKERS/PENS','PACK',39.99,None,None,None,None,'https://archford.com/Content/images/items/B01-020.jpg',0),
        ('B02-001','DRY ERASE MARKERS BLACK FINE 12','FINE POINT DRY ERASE 12 PACK','EXPO','MARKERS/PENS','BOX',8.99,None,None,None,None,'https://archford.com/Content/images/items/B02-001.jpg',1),
        ('B02-005','DRY ERASE MARKERS ASSORTED 4 PACK','4 COLORS BLACK RED BLUE GREEN','EXPO','MARKERS/PENS','PACK',3.25,None,None,None,None,'https://archford.com/Content/images/items/B02-005.jpg',1),
        ('B02-010','DRY ERASE MARKERS CHISEL 4 PACK','CHISEL TIP 4 COLORS','EXPO','MARKERS/PENS','PACK',4.50,None,None,None,None,'https://archford.com/Content/images/items/B02-010.jpg',1),
        ('B03-001','PERMANENT MARKERS BLACK FINE SHARPIE','SANFORD SHARPIE 12 PACK','SHARPIE','MARKERS/PENS','BOX',9.45,None,None,None,None,'https://archford.com/Content/images/items/B03-001.jpg',1),
        ('B03-005','PERMANENT MARKERS ASSORTED 8 PACK','SHARPIE ASSORTED COLORS','SHARPIE','MARKERS/PENS','PACK',7.99,None,None,None,None,'https://archford.com/Content/images/items/B03-005.jpg',1),
        ('B04-001','BALLPOINT PENS BLUE MEDIUM 24 PACK','24 MEDIUM BLUE BALLPOINTS','BIC','MARKERS/PENS','BOX',5.49,None,None,None,None,'https://archford.com/Content/images/items/B04-001.jpg',1),
        ('B04-005','BALLPOINT PENS BLACK MEDIUM 24 PACK','24 MEDIUM BLACK BALLPOINTS','BIC','MARKERS/PENS','BOX',5.49,None,None,None,None,'https://archford.com/Content/images/items/B04-005.jpg',1),
        ('B04-010','GEL PENS ASSORTED 10 PACK','SMOOTH WRITING GEL PENS','PENTEL','MARKERS/PENS','PACK',6.75,None,None,None,None,'https://archford.com/Content/images/items/B04-010.jpg',1),
        ('B05-001','HIGHLIGHTERS YELLOW 12 PACK','CHISEL TIP FLUORESCENT YELLOW','AVERY','MARKERS/PENS','BOX',7.25,None,None,None,None,'https://archford.com/Content/images/items/B05-001.jpg',1),
        ('B05-005','HIGHLIGHTERS ASSORTED 5 PACK','5 FLUORESCENT COLORS','AVERY','MARKERS/PENS','PACK',3.99,None,None,None,None,'https://archford.com/Content/images/items/B05-005.jpg',1),
        ('B06-001','PENCILS #2 YELLOW 12 PACK','PRE-SHARPENED #2 PENCILS','DIXON','MARKERS/PENS','BOX',2.25,None,None,None,None,'https://archford.com/Content/images/items/B06-001.jpg',0),
        ('B06-005','PENCILS #2 CLASSPACK 144','144 PRE-SHARPENED #2 PENCILS','DIXON','MARKERS/PENS','BOX',14.99,None,None,None,None,'https://archford.com/Content/images/items/B06-005.jpg',0),
        ('B06-010','PENCILS COLORED 12 PACK','COLORED PENCILS ASSORTED','PRANG','MARKERS/PENS','BOX',2.50,None,None,None,None,'https://archford.com/Content/images/items/B06-010.jpg',0),
        ('B07-001','PENCIL SHARPENER ELECTRIC','ELECTRIC PENCIL SHARPENER','BOSTITCH','MARKERS/PENS','EACH',18.50,None,None,None,None,'https://archford.com/Content/images/items/B07-001.jpg',1),
        ('B07-005','PENCIL SHARPENER MANUAL','MANUAL HAND SHARPENER','VARIOUS','MARKERS/PENS','EACH',1.25,None,None,None,None,'https://archford.com/Content/images/items/B07-005.jpg',1),
        # PAPER PRODUCTS
        ('C03-005','2 PLY 96 ROLL TOILET PAPER','VON DREHLE B50096','VON DREHLE','PAPER PRODUCTS','CASE',46.52,None,None,None,None,'https://archford.com/Content/images/items/C03-005.jpg',1),
        ('C03-010','PAPER TOWELS MULTI FOLD 28 LB','NOVA 2 MF400K','NOVA','PAPER PRODUCTS','CASE',27.36,None,None,None,None,'https://archford.com/Content/images/items/C03-010.jpg',1),
        ('C03-020','PAPER TOWELS ROLL 7.9 INCH WIDE','BROWN 2 INCH CORE VON DREHLE #469299','VON DREHLE','PAPER PRODUCTS','CASE',32.66,None,None,None,None,'https://archford.com/Content/images/items/C03-020.jpg',1),
        ('C03-225','TOILET PAPER DISPENSER JUMBO JR','SINGLE 9 IN ROLL #049957','VARIOUS','PAPER PRODUCTS','EACH',18.90,None,None,None,None,'https://archford.com/Content/images/items/C03-225.jpg',1),
        ('C03-226','TOILET PAPER DISPENSER JUMBO JR 2','DOUBLE ROLL JUMBO DISPENSER','VARIOUS','PAPER PRODUCTS','EACH',25.71,None,None,None,None,'https://archford.com/Content/images/items/C03-226.jpg',1),
        ('C03-235','TOILET PAPER DISPENSER REGULAR ROLLS','SINGLE ROLL #21190200','VARIOUS','PAPER PRODUCTS','EACH',27.00,None,None,None,None,'https://archford.com/Content/images/items/C03-235.jpg',1),
        ('P01-001','COPY PAPER 8.5X11 WHITE CASE','CASE 10 REAMS 500 SHEETS 92 BRIGHTNESS','HAMMERMILL','PAPER PRODUCTS','CASE',42.50,None,None,None,None,'https://archford.com/Content/images/items/P01-001.jpg',1),
        ('P01-005','COPY PAPER 8.5X11 REAM','SINGLE REAM 500 SHEETS 20 LB','HAMMERMILL','PAPER PRODUCTS','REAM',5.25,None,None,None,None,'https://archford.com/Content/images/items/P01-005.jpg',1),
        ('P01-010','LEGAL SIZE PAPER 8.5X14 REAM','500 SHEETS LEGAL SIZE','HAMMERMILL','PAPER PRODUCTS','REAM',6.75,None,None,None,None,'https://archford.com/Content/images/items/P01-010.jpg',1),
        ('P02-005','CARD STOCK 8.5X11 WHITE 250 SHEETS','67 LB CARD STOCK','HAMMERMILL','PAPER PRODUCTS','PACK',18.50,None,None,None,None,'https://archford.com/Content/images/items/P02-005.jpg',1),
        ('P02-010','CONSTRUCTION PAPER 9X12 50 SHEETS','50 SHEETS ASSORTED','PACON','PAPER PRODUCTS','PACK',3.89,None,None,None,None,'https://archford.com/Content/images/items/P02-010.jpg',0),
        # CUSTODIAL
        ('C01-010','MULTI PURPOSE CLEANER GALLON','ALL PURPOSE SCHOOL SAFE CLEANER','VARIOUS','CUSTODIAL','EACH',14.20,None,None,None,None,'https://archford.com/Content/images/items/C01-010.jpg',1),
        ('C01-015','DISINFECTANT SPRAY 19 OZ','KILLS 99.9 PERCENT GERMS','LYSOL','CUSTODIAL','EACH',6.89,None,None,None,None,'https://archford.com/Content/images/items/C01-015.jpg',1),
        ('C01-020','FLOOR CLEANER CONCENTRATE GALLON','HEAVY DUTY FLOOR CLEANER','VARIOUS','CUSTODIAL','EACH',22.50,None,None,None,None,'https://archford.com/Content/images/items/C01-020.jpg',1),
        ('C02-005','TRASH BAGS 55 GALLON 100 CASE','HEAVY DUTY BLACK BAGS','VARIOUS','CUSTODIAL','CASE',38.75,None,None,None,None,'https://archford.com/Content/images/items/C02-005.jpg',1),
        ('C02-010','TRASH BAGS 30 GALLON 100 CASE','MEDIUM DUTY BLACK BAGS','VARIOUS','CUSTODIAL','CASE',24.50,None,None,None,None,'https://archford.com/Content/images/items/C02-010.jpg',1),
        ('C02-020','HAND SOAP FOAMING 1 LITER','MILD FOAMING HAND SOAP REFILL','VARIOUS','CUSTODIAL','EACH',9.85,None,None,None,None,'https://archford.com/Content/images/items/C02-020.jpg',1),
        ('C02-025','HAND SOAP DISPENSER WALL MOUNT','MANUAL WALL MOUNT 1L','VARIOUS','CUSTODIAL','EACH',18.50,None,None,None,None,'https://archford.com/Content/images/items/C02-025.jpg',1),
        ('C04-010','MOP HEAD COTTON LOOP','HEAVY DUTY COTTON LOOP','VARIOUS','CUSTODIAL','EACH',11.50,None,None,None,None,'https://archford.com/Content/images/items/C04-010.jpg',1),
        ('C04-015','MOP HANDLE 60 INCH ALUMINUM','HEAVY DUTY ALUMINUM HANDLE','VARIOUS','CUSTODIAL','EACH',14.75,None,None,None,None,'https://archford.com/Content/images/items/C04-015.jpg',1),
        ('C05-005','BROOM UPRIGHT 12 INCH CORN','12 INCH CORN BROOM','VARIOUS','CUSTODIAL','EACH',13.25,None,None,None,None,'https://archford.com/Content/images/items/C05-005.jpg',1),
        ('C06-001','DUSTPAN AND BRUSH SET','PLASTIC DUSTPAN WITH BRUSH','VARIOUS','CUSTODIAL','SET',5.75,None,None,None,None,'https://archford.com/Content/images/items/C06-001.jpg',1),
        ('C06-137','INFRARED THERMOMETER','NON CONTACT DIGITAL THERMOMETER','VARIOUS','CUSTODIAL','EACH',19.99,None,None,None,None,'https://archford.com/Content/images/items/C06-137.jpg',1),
        # INSTRUCTIONAL SUPPLIES
        ('E01-005','FLASH CARDS MATH ADDITION 96 PACK','96 CARDS GRADES K-3','VARIOUS','INSTRUCTIONAL SUPPLIES','SET',4.99,None,None,None,None,'https://archford.com/Content/images/items/E01-005.jpg',0),
        ('E01-010','FLASH CARDS MULTIPLICATION 96 PACK','96 CARDS GRADES 3-6','VARIOUS','INSTRUCTIONAL SUPPLIES','SET',4.99,None,None,None,None,'https://archford.com/Content/images/items/E01-010.jpg',0),
        ('E02-010','DRY ERASE LAPBOARD 9X12','STUDENT PRACTICE BOARD WITH MARKER','VARIOUS','INSTRUCTIONAL SUPPLIES','EACH',3.75,None,None,None,None,'https://archford.com/Content/images/items/E02-010.jpg',0),
        ('E02-015','DRY ERASE LAPBOARD CLASS SET 30','30 LAPBOARDS FOR CLASSROOM','VARIOUS','INSTRUCTIONAL SUPPLIES','SET',89.50,None,None,None,None,'https://archford.com/Content/images/items/E02-015.jpg',0),
        ('E03-001','GLOBE 12 INCH DIAMETER','POLITICAL PHYSICAL RELIEF GLOBE','VARIOUS','INSTRUCTIONAL SUPPLIES','EACH',38.50,None,None,None,None,'https://archford.com/Content/images/items/E03-001.jpg',1),
        ('E04-001','RULER 12 INCH WOODEN','STANDARD 12 INCH RULER','VARIOUS','INSTRUCTIONAL SUPPLIES','EACH',0.89,None,None,None,None,'https://archford.com/Content/images/items/E04-001.jpg',0),
        ('E04-005','PROTRACTOR CLEAR PLASTIC 6 INCH','CLEAR PLASTIC PROTRACTOR','VARIOUS','INSTRUCTIONAL SUPPLIES','EACH',0.65,None,None,None,None,'https://archford.com/Content/images/items/E04-005.jpg',0),
        ('E05-001','CALCULATOR SOLAR AND BATTERY','8 DIGIT DUAL POWER','VARIOUS','INSTRUCTIONAL SUPPLIES','EACH',4.25,None,None,None,None,'https://archford.com/Content/images/items/E05-001.jpg',1),
        ('E05-005','SCIENTIFIC CALCULATOR','240 FUNCTION SCIENTIFIC','CASIO','INSTRUCTIONAL SUPPLIES','EACH',12.99,None,None,None,None,'https://archford.com/Content/images/items/E05-005.jpg',1),
        ('E06-001','INDEX CARDS 3X5 RULED 100 PACK','100 LINED 3X5 WHITE','VARIOUS','INSTRUCTIONAL SUPPLIES','PACK',1.85,None,None,None,None,'https://archford.com/Content/images/items/E06-001.jpg',0),
        ('E06-005','INDEX CARDS 4X6 RULED 200 PACK','200 LINED 4X6 ASSORTED','VARIOUS','INSTRUCTIONAL SUPPLIES','PACK',3.50,None,None,None,None,'https://archford.com/Content/images/items/E06-005.jpg',0),
        # COMPUTER
        ('K01-005','MOUSE USB OPTICAL','STANDARD USB OPTICAL MOUSE','VARIOUS','COMPUTER','EACH',9.99,None,None,None,None,'https://archford.com/Content/images/items/K01-005.jpg',1),
        ('K01-010','KEYBOARD USB STANDARD','FULL SIZE USB WIRED KEYBOARD','VARIOUS','COMPUTER','EACH',15.50,None,None,None,None,'https://archford.com/Content/images/items/K01-010.jpg',1),
        ('K02-001','USB FLASH DRIVE 16GB','16GB USB 2.0','VARIOUS','COMPUTER','EACH',7.25,None,None,None,None,'https://archford.com/Content/images/items/K02-001.jpg',1),
        ('K02-005','USB FLASH DRIVE 32GB','32GB USB 3.0','VARIOUS','COMPUTER','EACH',10.99,None,None,None,None,'https://archford.com/Content/images/items/K02-005.jpg',1),
        ('K03-001','MOUSE PAD STANDARD','NON SLIP RUBBER BASE','VARIOUS','COMPUTER','EACH',3.50,None,None,None,None,'https://archford.com/Content/images/items/K03-001.jpg',1),
        ('K04-140','BROTHER TN-550 BLACK TONER','BLK TONER CARTRIDGE #060919','BROTHER','COMPUTER','EACH',20.00,None,None,None,None,'https://archford.com/Content/images/items/K04-140.jpg',1),
        ('K05-001','SCREEN CLEANING KIT','LCD CLEANER SPRAY AND CLOTH','VARIOUS','COMPUTER','SET',6.99,None,None,None,None,'https://archford.com/Content/images/items/K05-001.jpg',1),
        # ATHLETIC
        ('G01-005','BASKETBALL OFFICIAL SIZE 7','RUBBER OFFICIAL SIZE','VARIOUS','ATHLETIC','EACH',22.50,None,None,None,None,'https://archford.com/Content/images/items/G01-005.jpg',0),
        ('G01-010','SOCCER BALL SIZE 4','YOUTH SOCCER BALL SIZE 4','VARIOUS','ATHLETIC','EACH',18.75,None,None,None,None,'https://archford.com/Content/images/items/G01-010.jpg',0),
        ('G01-015','VOLLEYBALL OFFICIAL','OFFICIAL SIZE RUBBER','VARIOUS','ATHLETIC','EACH',21.00,None,None,None,None,'https://archford.com/Content/images/items/G01-015.jpg',0),
        ('G01-079','BORDETTE BJ BORDER','CLASSROOM BORDER ROLL','VARIOUS','ATHLETIC','EACH',3.19,None,None,None,None,'https://archford.com/Content/images/items/G01-079.jpg',0),
        ('G01-080','BORDETTE BJ BORDER 2','CLASSROOM BORDER ROLL 2','VARIOUS','ATHLETIC','EACH',3.19,None,None,None,None,'https://archford.com/Content/images/items/G01-080.jpg',0),
        ('G02-001','JUMP ROPE SINGLE 7 FEET','SINGLE JUMP ROPE 7 FT','VARIOUS','ATHLETIC','EACH',3.25,None,None,None,None,'https://archford.com/Content/images/items/G02-001.jpg',0),
        ('G02-005','LONG JUMP ROPE 16 FEET','GROUP JUMP ROPE 16 FT','VARIOUS','ATHLETIC','EACH',7.50,None,None,None,None,'https://archford.com/Content/images/items/G02-005.jpg',0),
        ('G03-001','CONES ORANGE SAFETY 12 PACK','6 INCH ORANGE CONES 12 PACK','VARIOUS','ATHLETIC','SET',14.99,None,None,None,None,'https://archford.com/Content/images/items/G03-001.jpg',0),
        # AUDIO/VISUAL
        ('H01-005','DRY ERASE BOARD 24X36','WALL MOUNT 24 X 36','VARIOUS','AUDIO/VISUAL','EACH',45.00,None,None,None,None,'https://archford.com/Content/images/items/H01-005.jpg',1),
        ('H01-010','BULLETIN BOARD CORK 24X36','SELF HEALING CORK BOARD','VARIOUS','AUDIO/VISUAL','EACH',38.50,None,None,None,None,'https://archford.com/Content/images/items/H01-010.jpg',1),
        ('H02-001','PROJECTOR SCREEN 70X70 TRIPOD','PORTABLE TRIPOD SCREEN','VARIOUS','AUDIO/VISUAL','EACH',89.00,None,None,None,None,'https://archford.com/Content/images/items/H02-001.jpg',1),
        ('H03-001','LASER POINTER RED','RED LASER WITH POCKET CLIP','VARIOUS','AUDIO/VISUAL','EACH',8.99,None,None,None,None,'https://archford.com/Content/images/items/H03-001.jpg',1),
        # EQUIPMENT/FURNITURE
        ('F01-005','STUDENT CHAIR PLASTIC BLACK','17 INCH SEAT HEIGHT','VARIOUS','EQUIPMENT/FURNITURE','EACH',35.00,None,None,None,None,'https://archford.com/Content/images/items/F01-005.jpg',1),
        ('F01-010','STUDENT DESK ADJUSTABLE','HEIGHT ADJUSTABLE LAMINATE TOP','VARIOUS','EQUIPMENT/FURNITURE','EACH',89.00,None,None,None,None,'https://archford.com/Content/images/items/F01-010.jpg',1),
        ('F02-001','BOOKSHELF 5 SHELF WOOD','FIVE SHELF 72 INCH TALL','VARIOUS','EQUIPMENT/FURNITURE','EACH',125.00,None,None,None,None,'https://archford.com/Content/images/items/F02-001.jpg',1),
        ('F03-001','STORAGE CABINET LOCKING','STEEL LOCKING 36X18X72','VARIOUS','EQUIPMENT/FURNITURE','EACH',225.00,None,None,None,None,'https://archford.com/Content/images/items/F03-001.jpg',1),
        # READING SUPPLIES
        ('L01-005','BOOKMARKS ASSORTED 50 PACK','50 ASSORTED BOOKMARKS','VARIOUS','READING SUPPLIES','PACK',3.99,None,None,None,None,'https://archford.com/Content/images/items/L01-005.jpg',0),
        ('L01-010','BOOK RINGS 1 INCH 100 BOX','1 INCH METAL BOOK RINGS','VARIOUS','READING SUPPLIES','BOX',4.50,None,None,None,None,'https://archford.com/Content/images/items/L01-010.jpg',0),
        ('L02-001','BOOK TAPE CLEAR 2 INCH 15 YD','CLEAR BOOK REPAIR TAPE','VARIOUS','READING SUPPLIES','EACH',4.25,None,None,None,None,'https://archford.com/Content/images/items/L02-001.jpg',0),
        ('L02-005','BOOK COVER SELF ADHESIVE JUMBO','SELF ADHESIVE COVERS 10 PACK','VARIOUS','READING SUPPLIES','PACK',6.50,None,None,None,None,'https://archford.com/Content/images/items/L02-005.jpg',0),
        ('L03-001','READING POINTER WAND','WOODEN READING POINTER','VARIOUS','READING SUPPLIES','EACH',2.25,None,None,None,None,'https://archford.com/Content/images/items/L03-001.jpg',0),
        # PROJECTION LAMPS
        ('M01-001','PROJECTOR LAMP DLP REPLACEMENT','COMPATIBLE DLP LAMP','VARIOUS','PROJECTION LAMPS','EACH',65.00,None,None,None,None,'https://archford.com/Content/images/items/M01-001.jpg',1),
        ('M02-890','AMERICA THE BEAUTIFUL D2223','PROJECTOR LAMP SERIES','VARIOUS','PROJECTION LAMPS','GROSS',22.20,None,None,None,None,'https://archford.com/Content/images/items/M02-890.jpg',1),
    ]
    conn.executemany(
        'INSERT OR IGNORE INTO products (id, name, description, vendor, cat, pkg, price, price2, price3, price4, price5, img, taxable) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
        products)
    conn.commit()
    print(f"  Loaded {len(products)} products")

# ─────────────────────────────────────────────
# SEED TEST USERS
# ─────────────────────────────────────────────
def _seed_users(conn):
    users = [
        ('dtessman', 'archford2026', 'Conway School District', '0101000',
         'Darrell Tessman', '2200 Prince Street', 'Conway', 'AR', '72032',
         '(501) 555-1234', 'dtessman@conwayschools.org', 'NT', '30', '30'),
        ('greenbrier', 'archford2026', 'Greenbrier School District', '2303021',
         'Betsy Petty', '15 School Drive', 'Greenbrier', 'AR', '72058',
         '(501) 555-5678', 'bpetty@greenbrierschools.org', 'NT', '30', '30'),
        ('russellville', 'archford2026', 'Russellville High School', '5805024',
         'Rebecca Ward', '200 West 8th Street', 'Russellville', 'AR', '72801',
         '(479) 555-9012', 'rward@russellvilleschools.net', 'NT', '30', '30'),
        ('dewitt', 'archford2026', 'DeWitt Public Schools', '0101000',
         'James O. Emef', 'P.O. Box 700', 'DeWitt', 'AR', '72042',
         '(870) 946-3576', 'jemef@dewittschools.org', 'NT', '30', '30'),
    ]
    conn.executemany('INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', users)
    conn.commit()
    print(f"  Loaded {len(users)} test users")

# ─────────────────────────────────────────────
# USER FUNCTIONS
# ─────────────────────────────────────────────
def get_user(username, password):
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username=? AND password=?',
        (username, password)
    ).fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

# ─────────────────────────────────────────────
# PRODUCT FUNCTIONS
# ─────────────────────────────────────────────
def get_categories():
    conn = get_db()
    cats = conn.execute(
        'SELECT DISTINCT cat FROM products WHERE active=1 ORDER BY cat'
    ).fetchall()
    conn.close()
    cat_icons = {
        'ART': '🎨',
        'OFFICE SUPPLIES': '📎',
        'PAPER PRODUCTS': '📄',
        'CUSTODIAL': '🧹',
        'INSTRUCTIONAL SUPPLIES': '📚',
        'MARKERS/PENS': '✏️',
        'COMPUTER': '💻',
        'ATHLETIC': '⚽',
        'AUDIO/VISUAL': '📽️',
        'EQUIPMENT/FURNITURE': '🪑',
        'READING SUPPLIES': '📖',
        'PROJECTION LAMPS': '💡',
    }
    result = [{'id': 'ALL', 'label': 'All Products', 'icon': '🛒', 'count': 0}]
    total = 0
    for row in cats:
        cat = row['cat']
        conn2 = get_db()
        count = conn2.execute(
            'SELECT COUNT(*) as c FROM products WHERE cat=? AND active=1', (cat,)
        ).fetchone()['c']
        conn2.close()
        total += count
        result.append({
            'id': cat,
            'label': cat.title(),
            'icon': cat_icons.get(cat, '📦'),
            'count': count
        })
    result[0]['count'] = total
    return result

def get_products(category='ALL', search='', sort='default'):
    conn = get_db()
    query = 'SELECT * FROM products WHERE active=1'
    params = []
    if category and category != 'ALL':
        query += ' AND cat=?'
        params.append(category)
    if search:
        query += ' AND (name LIKE ? OR id LIKE ? OR description LIKE ? OR cat LIKE ?)'
        s = f'%{search}%'
        params.extend([s, s, s, s])
    if sort == 'price_asc':
        query += ' ORDER BY price ASC'
    elif sort == 'price_desc':
        query += ' ORDER BY price DESC'
    elif sort == 'name_asc':
        query += ' ORDER BY name ASC'
    else:
        query += ' ORDER BY cat, name'
    products = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(p) for p in products]

def get_product(item_id):
    conn = get_db()
    product = conn.execute(
        'SELECT * FROM products WHERE id=?', (item_id,)
    ).fetchone()
    conn.close()
    return dict(product) if product else None

def get_featured_products(limit=8):
    conn = get_db()
    products = conn.execute(
        'SELECT * FROM products WHERE active=1 ORDER BY RANDOM() LIMIT ?',
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(p) for p in products]

def get_related_products(category, exclude_id, limit=4):
    conn = get_db()
    products = conn.execute(
        'SELECT * FROM products WHERE cat=? AND id!=? AND active=1 ORDER BY RANDOM() LIMIT ?',
        (category, exclude_id, limit)
    ).fetchall()
    conn.close()
    return [dict(p) for p in products]

# ─────────────────────────────────────────────
# ORDER FUNCTIONS
# ─────────────────────────────────────────────
def save_order(order_data):
    conn = get_db()
    order_num = f"AF-{datetime.now().strftime('%Y')}-{conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0] + 10001}"
    subtotal = sum(i['price'] * i['qty'] for i in order_data['items'])
    shipping = 0 if subtotal >= 50 else 7.50
    total = subtotal + shipping
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn.execute('''INSERT INTO orders
        (order_num, username, school, contact, email, phone, address, city, state,
         zip, po_number, payment, ship_later, notes, subtotal, shipping, total, status, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (order_num,
         order_data['user']['username'],
         order_data['school'],
         order_data['contact'],
         order_data['email'],
         order_data.get('phone', ''),
         order_data['address'],
         order_data['city'],
         order_data['state'],
         order_data['zip'],
         order_data.get('po_number', ''),
         order_data.get('payment', 'P-Card'),
         order_data.get('ship_later', 'N'),
         order_data.get('notes', ''),
         subtotal,
         shipping,
         total,
         'Pending',
         now))

    for item in order_data['items']:
        product = get_product(item['id'])
        taxable = product['taxable'] if product else 0
        conn.execute('''INSERT INTO order_items
            (order_num, item_id, name, description, cat, pkg, qty, unit_price, taxable, line_total)
            VALUES (?,?,?,?,?,?,?,?,?,?)''',
            (order_num,
             item['id'],
             item['name'],
             product['description'] if product else '',
             product['cat'] if product else '',
             item['pkg'],
             item['qty'],
             item['price'],
             taxable,
             item['price'] * item['qty']))

    conn.commit()
    conn.close()
    return order_num

def get_order(order_num):
    if not order_num:
        return None
    conn = get_db()
    order = conn.execute(
        'SELECT * FROM orders WHERE order_num=?', (order_num,)
    ).fetchone()
    if not order:
        conn.close()
        return None
    order = dict(order)
    items = conn.execute(
        'SELECT * FROM order_items WHERE order_num=?', (order_num,)
    ).fetchall()
    order['items'] = [dict(i) for i in items]
    conn.close()
    return order

def get_user_orders(username):
    conn = get_db()
    orders = conn.execute(
        'SELECT * FROM orders WHERE username=? ORDER BY created_at DESC',
        (username,)
    ).fetchall()
    result = []
    for order in orders:
        o = dict(order)
        items = conn.execute(
            'SELECT * FROM order_items WHERE order_num=?',
            (order['order_num'],)
        ).fetchall()
        o['items'] = [dict(i) for i in items]
        result.append(o)
    conn.close()
    return result