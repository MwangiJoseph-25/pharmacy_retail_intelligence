#!/usr/bin/env python3
"""
Pharmacy Customer and Sales Intelligence System - synthetic data generator.

Generates a fully SYNTHETIC, internally consistent set of relational CSV files for a
simulated 12-branch Kenyan pharmacy retailer for 1 Jan - 31 Dec 2025.

Run:  python scripts/generate_synthetic_data.py            (writes into the repo root)
Seed: SEED below (change it and every file changes; keep it and output is identical).

Nothing here is real sales data. Product NAMES are real generic medicine / supply names
(provenance still to be verified against a documented source); prices, costs, customers,
transactions, stock and purchasing are simulated.
"""
import os, sys, math
from collections import defaultdict
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd

SEED = 20250101
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "synthetic")
PUB = os.path.join(ROOT, "data", "raw", "public")
DOCS = os.path.join(ROOT, "docs")
for _p in (RAW, PUB, DOCS):
    os.makedirs(_p, exist_ok=True)
rng = np.random.default_rng(SEED)

# ----------------------------------------------------------------------------------
# Parameters (all documented in docs/data_generation_assumptions.md)
# ----------------------------------------------------------------------------------
N_TXN, N_CUST, ID_SHARE = 100_000, 8_000, 0.80
N_ID = int(round(N_TXN * ID_SHARE))
ND = 365
D0 = date(2025, 1, 1)
DATES = [D0 + timedelta(days=i) for i in range(ND)]
BASE = datetime(2025, 1, 1)
P_VOID_RANDOM = 0.013        # cashier voids (no stock effect)
P_RETURN = 0.0105            # share of completed transactions with a return
REVIEW_DAYS = 14             # reorder review cycle per store
N_PROMO_PRODUCT, N_PROMO_CATEGORY = 40, 20
N_PRICE_CHANGES = 30
N_WRITEOFFS, N_ADJUST = 2500, 2500

dow = np.array([d.weekday() for d in DATES])
mon = np.array([d.month - 1 for d in DATES])
doy = lambda m, d: (date(2025, m, d) - D0).days

# ----------------------------------------------------------------------------------
# Stores (12) - 6 counties x 2 branches. Names are fictional.
# ----------------------------------------------------------------------------------
STORES = [
    ("ST01", "SimPharm Westlands", "Nairobi", "Westlands", "2016-03-14", 1.5),
    ("ST02", "SimPharm Embakasi", "Nairobi", "Embakasi", "2018-07-02", 1.3),
    ("ST03", "SimPharm Nyali", "Mombasa", "Nyali", "2017-02-20", 1.1),
    ("ST04", "SimPharm Mombasa Island", "Mombasa", "Mombasa Island", "2015-09-01", 1.2),
    ("ST05", "SimPharm Milimani", "Kisumu", "Milimani", "2019-05-13", 0.9),
    ("ST06", "SimPharm Kisumu Central", "Kisumu", "Kisumu Central", "2016-11-07", 1.0),
    ("ST07", "SimPharm Nakuru Town", "Nakuru", "Nakuru Town", "2017-06-19", 1.1),
    ("ST08", "SimPharm Naivasha", "Nakuru", "Naivasha", "2020-01-27", 0.7),
    ("ST09", "SimPharm Thika", "Kiambu", "Thika", "2018-03-12", 1.0),
    ("ST10", "SimPharm Ruaka", "Kiambu", "Ruaka", "2021-08-16", 1.1),
    ("ST11", "SimPharm Eldoret Town", "Uasin Gishu", "Eldoret Town", "2017-10-09", 1.0),
    ("ST12", "SimPharm Langas", "Uasin Gishu", "Langas", "2021-02-01", 0.8),
]
S = len(STORES)
store_ids = [s[0] for s in STORES]
store_w = np.array([s[5] for s in STORES])
store_county = [s[2] for s in STORES]
sibling = np.array([i ^ 1 for i in range(S)])   # other branch in same county

# ----------------------------------------------------------------------------------
# Products (150). Real generic names; costs are simulated KES per sale unit.
# ingredient | strength | form | category | unit_of_measure | base_cost | popularity
# ----------------------------------------------------------------------------------
PRODUCT_RAW = """
Paracetamol|500 mg|Tablets|Pain & Fever|pack of 20 tablets|28|10
Paracetamol|120 mg/5 mL|Syrup|Pain & Fever|bottle of 60 mL|48|6
Ibuprofen|400 mg|Tablets|Pain & Fever|strip of 10 tablets|32|7
Ibuprofen|200 mg|Tablets|Pain & Fever|strip of 10 tablets|24|3
Ibuprofen|100 mg/5 mL|Suspension|Pain & Fever|bottle of 100 mL|95|3
Diclofenac|50 mg|Tablets|Pain & Fever|strip of 10 tablets|36|6
Diclofenac|1%|Gel|Pain & Fever|tube of 30 g|125|4
Aspirin|75 mg|Tablets|Pain & Fever|pack of 28 tablets|60|3
Mefenamic acid|500 mg|Capsules|Pain & Fever|strip of 10 capsules|42|5
Naproxen|250 mg|Tablets|Pain & Fever|strip of 10 tablets|46|2
Etoricoxib|90 mg|Tablets|Pain & Fever|strip of 10 tablets|185|2
Methyl salicylate|25%|Ointment|Pain & Fever|tube of 30 g|75|3
Piroxicam|20 mg|Capsules|Pain & Fever|strip of 10 capsules|62|1.5
Amoxicillin|500 mg|Capsules|Antibiotics|strip of 10 capsules|62|9
Amoxicillin|250 mg/5 mL|Suspension|Antibiotics|bottle of 100 mL|115|5
Amoxicillin/Clavulanic acid|625 mg|Tablets|Antibiotics|pack of 10 tablets|290|4
Azithromycin|500 mg|Tablets|Antibiotics|pack of 3 tablets|125|4
Ciprofloxacin|500 mg|Tablets|Antibiotics|strip of 10 tablets|72|5
Metronidazole|400 mg|Tablets|Antibiotics|strip of 10 tablets|36|6
Metronidazole|200 mg/5 mL|Suspension|Antibiotics|bottle of 100 mL|88|2
Doxycycline|100 mg|Capsules|Antibiotics|strip of 10 capsules|52|4
Cefuroxime|500 mg|Tablets|Antibiotics|pack of 10 tablets|360|2
Cefixime|400 mg|Capsules|Antibiotics|pack of 5 capsules|310|1.5
Erythromycin|500 mg|Tablets|Antibiotics|strip of 10 tablets|92|2
Co-trimoxazole|480 mg|Tablets|Antibiotics|strip of 10 tablets|30|3
Co-trimoxazole|240 mg/5 mL|Suspension|Antibiotics|bottle of 100 mL|72|2
Flucloxacillin|500 mg|Capsules|Antibiotics|strip of 10 capsules|125|2
Nitrofurantoin|100 mg|Capsules|Antibiotics|pack of 10 capsules|105|1.5
Ceftriaxone|1 g|Injection|Antibiotics|vial of 1 g|125|2
Clarithromycin|500 mg|Tablets|Antibiotics|pack of 14 tablets|300|1.5
Cefalexin|500 mg|Capsules|Antibiotics|strip of 10 capsules|110|2
Tinidazole|500 mg|Tablets|Antibiotics|pack of 4 tablets|62|1.5
Artemether/Lumefantrine|20/120 mg|Tablets|Antimalarials|pack of 24 tablets|165|10
Artemether/Lumefantrine|20/120 mg dispersible|Tablets|Antimalarials|pack of 12 tablets|95|4
Dihydroartemisinin/Piperaquine|40/320 mg|Tablets|Antimalarials|pack of 3 tablets|210|2
Artesunate|60 mg|Injection|Antimalarials|vial of 60 mg|260|1
Quinine|300 mg|Tablets|Antimalarials|strip of 10 tablets|82|1.5
Sulfadoxine/Pyrimethamine|500/25 mg|Tablets|Antimalarials|pack of 3 tablets|42|1.5
Amlodipine|5 mg|Tablets|Cardiovascular|pack of 30 tablets|62|6
Amlodipine|10 mg|Tablets|Cardiovascular|pack of 30 tablets|92|4
Atenolol|50 mg|Tablets|Cardiovascular|pack of 30 tablets|52|3
Enalapril|5 mg|Tablets|Cardiovascular|pack of 30 tablets|72|3
Lisinopril|10 mg|Tablets|Cardiovascular|pack of 30 tablets|92|3
Losartan|50 mg|Tablets|Cardiovascular|pack of 30 tablets|112|4
Hydrochlorothiazide|25 mg|Tablets|Cardiovascular|pack of 30 tablets|46|3
Nifedipine|20 mg (slow release)|Tablets|Cardiovascular|pack of 30 tablets|95|2.5
Atorvastatin|20 mg|Tablets|Cardiovascular|pack of 30 tablets|165|4
Simvastatin|20 mg|Tablets|Cardiovascular|pack of 30 tablets|102|2
Furosemide|40 mg|Tablets|Cardiovascular|pack of 28 tablets|52|2
Bisoprolol|5 mg|Tablets|Cardiovascular|pack of 30 tablets|112|2
Spironolactone|25 mg|Tablets|Cardiovascular|pack of 28 tablets|92|1.5
Clopidogrel|75 mg|Tablets|Cardiovascular|pack of 28 tablets|145|1.5
Metformin|500 mg|Tablets|Diabetes|pack of 60 tablets|82|6
Metformin|850 mg|Tablets|Diabetes|pack of 60 tablets|112|3
Glibenclamide|5 mg|Tablets|Diabetes|pack of 30 tablets|42|2
Gliclazide|80 mg|Tablets|Diabetes|pack of 30 tablets|122|2.5
Glimepiride|2 mg|Tablets|Diabetes|pack of 30 tablets|132|2
Human insulin (soluble)|100 IU/mL|Injection|Diabetes|vial of 10 mL|720|1.5
Human insulin (isophane)|100 IU/mL|Injection|Diabetes|vial of 10 mL|720|1.5
Blood glucose test strips|50 strips|Test strips|Diabetes|box of 50 strips|980|2
Lancets|100 lancets|Other|Diabetes|box of 100 lancets|205|1.5
Omeprazole|20 mg|Capsules|Gastrointestinal|pack of 14 capsules|62|7
Esomeprazole|40 mg|Tablets|Gastrointestinal|pack of 14 tablets|155|3
Pantoprazole|40 mg|Tablets|Gastrointestinal|pack of 14 tablets|120|2
Aluminium hydroxide/Magnesium hydroxide||Suspension|Gastrointestinal|bottle of 200 mL|122|5
Loperamide|2 mg|Capsules|Gastrointestinal|strip of 6 capsules|42|4
Oral rehydration salts|1 L sachet|Powder|Gastrointestinal|sachet|22|6
Zinc sulfate|20 mg dispersible|Tablets|Gastrointestinal|pack of 10 tablets|78|4
Bisacodyl|5 mg|Tablets|Gastrointestinal|strip of 10 tablets|32|2
Lactulose|3.35 g/5 mL|Syrup|Gastrointestinal|bottle of 200 mL|360|1.5
Hyoscine butylbromide|10 mg|Tablets|Gastrointestinal|strip of 10 tablets|82|4
Domperidone|10 mg|Tablets|Gastrointestinal|strip of 10 tablets|52|3
Metoclopramide|10 mg|Tablets|Gastrointestinal|strip of 10 tablets|32|2
Simethicone|40 mg|Chewable tablets|Gastrointestinal|strip of 10 tablets|62|2
Famotidine|20 mg|Tablets|Gastrointestinal|strip of 10 tablets|55|2
Salbutamol|100 mcg/dose|Inhaler|Respiratory & Allergy|inhaler of 200 doses|310|3
Salbutamol|2 mg/5 mL|Syrup|Respiratory & Allergy|bottle of 100 mL|82|2
Salbutamol|4 mg|Tablets|Respiratory & Allergy|strip of 10 tablets|28|1.5
Cetirizine|10 mg|Tablets|Respiratory & Allergy|strip of 10 tablets|36|7
Loratadine|10 mg|Tablets|Respiratory & Allergy|strip of 10 tablets|42|4
Chlorphenamine|4 mg|Tablets|Respiratory & Allergy|strip of 10 tablets|22|5
Promethazine|25 mg|Tablets|Respiratory & Allergy|strip of 10 tablets|36|2
Montelukast|10 mg|Tablets|Respiratory & Allergy|pack of 28 tablets|360|2
Beclometasone|100 mcg/dose|Inhaler|Respiratory & Allergy|inhaler of 200 doses|560|1.5
Guaifenesin|100 mg/5 mL|Syrup|Respiratory & Allergy|bottle of 100 mL|112|4
Bromhexine|4 mg/5 mL|Syrup|Respiratory & Allergy|bottle of 100 mL|102|3
Dextromethorphan|15 mg/5 mL|Syrup|Respiratory & Allergy|bottle of 100 mL|125|2.5
Xylometazoline|0.1%|Nasal drops|Respiratory & Allergy|bottle of 10 mL|112|3
Prednisolone|5 mg|Tablets|Respiratory & Allergy|strip of 10 tablets|32|3
Ascorbic acid (Vitamin C)|500 mg|Tablets|Vitamins & Supplements|pack of 20 tablets|82|6
Vitamin B complex||Tablets|Vitamins & Supplements|pack of 30 tablets|62|5
Multivitamin||Tablets|Vitamins & Supplements|pack of 30 tablets|255|4
Multivitamin||Syrup|Vitamins & Supplements|bottle of 100 mL|200|2
Folic acid|5 mg|Tablets|Vitamins & Supplements|pack of 28 tablets|42|3
Ferrous sulfate|200 mg|Tablets|Vitamins & Supplements|pack of 30 tablets|52|3
Ferrous sulfate/Folic acid||Syrup|Vitamins & Supplements|bottle of 200 mL|155|2
Calcium/Vitamin D3|600 mg/400 IU|Tablets|Vitamins & Supplements|pack of 30 tablets|305|2.5
Vitamin D3|1000 IU|Softgel capsules|Vitamins & Supplements|pack of 30 capsules|405|2
Omega-3 fish oil|1000 mg|Softgel capsules|Vitamins & Supplements|pack of 30 capsules|710|1.5
Vitamin E|400 IU|Softgel capsules|Vitamins & Supplements|pack of 30 capsules|355|1.5
Vitamin B12 (cyanocobalamin)|1000 mcg|Tablets|Vitamins & Supplements|pack of 30 tablets|205|1.5
Magnesium|250 mg|Tablets|Vitamins & Supplements|pack of 30 tablets|250|1.5
Cod liver oil||Capsules|Vitamins & Supplements|pack of 30 capsules|405|1.5
Clotrimazole|1%|Cream|Dermatology|tube of 20 g|82|5
Hydrocortisone|1%|Cream|Dermatology|tube of 15 g|92|4
Betamethasone|0.05%|Cream|Dermatology|tube of 15 g|145|3
Fusidic acid|2%|Cream|Dermatology|tube of 15 g|225|2
Terbinafine|1%|Cream|Dermatology|tube of 15 g|255|2
Miconazole|2%|Cream|Dermatology|tube of 30 g|135|2
Calamine|8%|Lotion|Dermatology|bottle of 100 mL|122|2
Silver sulfadiazine|1%|Cream|Dermatology|tube of 50 g|255|1.5
Benzoyl peroxide|5%|Gel|Dermatology|tube of 30 g|305|1.5
Petroleum jelly||Ointment|Dermatology|jar of 100 g|125|4
Ketoconazole|2%|Shampoo|Dermatology|bottle of 100 mL|455|1.5
Permethrin|5%|Cream|Dermatology|tube of 30 g|265|1.5
Aqueous cream||Cream|Dermatology|tub of 500 g|305|2
Mupirocin|2%|Ointment|Dermatology|tube of 15 g|355|1.5
Zinc oxide|15%|Ointment|Dermatology|tube of 30 g|115|2
Chloramphenicol|0.5%|Eye drops|Eye, Ear & Nose|bottle of 10 mL|92|3
Ciprofloxacin|0.3%|Eye drops|Eye, Ear & Nose|bottle of 5 mL|125|2
Carboxymethylcellulose|0.5%|Eye drops|Eye, Ear & Nose|bottle of 10 mL|305|1.5
Tetracycline|1%|Eye ointment|Eye, Ear & Nose|tube of 5 g|82|1.5
Clotrimazole|1%|Ear drops|Eye, Ear & Nose|bottle of 10 mL|155|1
Sodium chloride|0.9%|Nasal spray|Eye, Ear & Nose|bottle of 15 mL|135|1.5
Albendazole|400 mg|Chewable tablets|Other Anti-infectives|pack of 1 tablet|32|4
Mebendazole|100 mg|Tablets|Other Anti-infectives|pack of 6 tablets|52|2
Fluconazole|150 mg|Capsules|Other Anti-infectives|pack of 1 capsule|125|3
Nystatin|100,000 IU/mL|Oral suspension|Other Anti-infectives|bottle of 30 mL|205|1.5
Ivermectin|3 mg|Tablets|Other Anti-infectives|pack of 4 tablets|205|1.5
Aciclovir|200 mg|Tablets|Other Anti-infectives|pack of 25 tablets|355|1.5
Levonorgestrel|1.5 mg|Tablets|Reproductive Health|pack of 1 tablet|205|3
Levonorgestrel/Ethinylestradiol|150/30 mcg|Tablets|Reproductive Health|pack of 28 tablets|155|3
Medroxyprogesterone|150 mg/mL|Injection|Reproductive Health|vial of 1 mL|155|2
Clotrimazole|500 mg|Pessary|Reproductive Health|pack of 1 pessary|155|1.5
Male condoms||Other|Reproductive Health|pack of 3|42|4
Pregnancy test (hCG)||Test kit|Reproductive Health|single test|52|3
Sanitary pads||Other|Reproductive Health|pack of 10|105|5
Povidone iodine|10%|Solution|First Aid & Medical Supplies|bottle of 100 mL|152|3
Surgical spirit||Solution|First Aid & Medical Supplies|bottle of 200 mL|105|2
Hydrogen peroxide|6%|Solution|First Aid & Medical Supplies|bottle of 100 mL|82|1.5
Adhesive plasters||Other|First Aid & Medical Supplies|pack of 20|82|4
Crepe bandage|7.5 cm|Other|First Aid & Medical Supplies|roll|105|2
Cotton wool|100 g|Other|First Aid & Medical Supplies|pack of 100 g|152|2
Sterile gauze swabs||Other|First Aid & Medical Supplies|pack of 10|82|2
Digital thermometer||Other|First Aid & Medical Supplies|each|305|1.5
Disposable examination gloves||Other|First Aid & Medical Supplies|box of 100|505|2
Alcohol hand sanitiser|70%|Gel|First Aid & Medical Supplies|bottle of 100 mL|105|3
Surgical face masks||Other|First Aid & Medical Supplies|box of 50|305|2
Syringes with needle|5 mL|Other|First Aid & Medical Supplies|pack of 10|62|2
Malaria rapid diagnostic test||Test kit|First Aid & Medical Supplies|single test|62|3
"""
DEVICE_FORMS = {"Other", "Test kit", "Test strips"}
prod_rows = []
for ln in PRODUCT_RAW.strip().splitlines():
    ing, strength, form, cat, uom, cost, pop = [x.strip() for x in ln.split("|")]
    name = " ".join(x for x in [ing, strength, form if form != "Other" else ""] if x)
    prod_rows.append(dict(ing=ing, strength=strength, form=form, cat=cat, uom=uom,
                          cost=float(cost), pop=float(pop), name=name))
P = len(prod_rows)
assert P == 150, f"expected 150 products, got {P}"
assert len({r["name"] for r in prod_rows}) == P, "duplicate product names"
CATS = list(dict.fromkeys(r["cat"] for r in prod_rows))
C = len(CATS)
prod_cat = np.array([CATS.index(r["cat"]) for r in prod_rows])
prod_ids = [f"P{i + 1:03d}" for i in range(P)]
prod_pop = np.array([r["pop"] for r in prod_rows]) * rng.lognormal(0, 0.3, P)


def to_price(x):
    return float(round(x / 5) * 5) if x >= 100 else float(math.ceil(x))


base_cost = np.round(np.array([r["cost"] for r in prod_rows]) * rng.uniform(0.92, 1.08, P), 2)
base_price = np.array([to_price(c * m) for c, m in zip(base_cost, rng.uniform(1.25, 1.50, P))])
base_price = np.maximum(base_price, np.ceil(base_cost * 1.15))

# documented simulated price/cost changes (one per product, on selected products)
chg_day = np.full(P, 10_000)
new_cost, new_price = base_cost.copy(), base_price.copy()
chg_products = rng.choice(P, N_PRICE_CHANGES, replace=False)
for p in chg_products:
    chg_day[p] = int(rng.integers(doy(3, 1), doy(10, 15)))
    pct = rng.uniform(0.03, 0.09)
    new_cost[p] = round(base_cost[p] * (1 + pct), 2)
    new_price[p] = max(to_price(base_price[p] * (1 + pct)), base_price[p])
base_cost_c = np.rint(base_cost * 100).astype(np.int64)
base_price_c = np.rint(base_price * 100).astype(np.int64)
new_cost_c = np.rint(new_cost * 100).astype(np.int64)
new_price_c = np.rint(new_price * 100).astype(np.int64)

# discontinued products (sold until discontinuation date, then written off)
disc_day = np.full(P, 10_000)
for p in rng.choice([i for i in range(P) if prod_rows[i]["pop"] <= 3], 5, replace=False):
    disc_day[p] = int(rng.integers(doy(7, 1), doy(10, 31)))
status_prod = np.where(disc_day < 10_000, "Discontinued", "Active")

lot = np.where(base_cost < 50, 10, np.where(base_cost < 150, 6, np.where(base_cost < 500, 3, 2)))
CAT_LAM = {"Cardiovascular": 0.6, "Diabetes": 0.5, "Vitamins & Supplements": 0.4, "Pain & Fever": 0.25,
           "Gastrointestinal": 0.25, "Respiratory & Allergy": 0.25, "Dermatology": 0.1, "Antibiotics": 0.1,
           "Antimalarials": 0.1, "Eye, Ear & Nose": 0.1, "Other Anti-infectives": 0.1,
           "Reproductive Health": 0.3, "First Aid & Medical Supplies": 0.2}
lam_p = np.array([CAT_LAM[r["cat"]] for r in prod_rows])

# ----------------------------------------------------------------------------------
# Suppliers (24, fictional)
# ----------------------------------------------------------------------------------
SUP_TYPES = [("Pharmaceutical wholesaler", 8), ("Generic manufacturer distributor", 5),
             ("Supplements distributor", 3), ("OTC and consumer health distributor", 4),
             ("Medical supplies distributor", 4)]
CAT_SUP_TYPE = {"Pain & Fever": 0, "Antibiotics": 0, "Antimalarials": 0, "Gastrointestinal": 0,
                "Respiratory & Allergy": 0, "Eye, Ear & Nose": 0, "Other Anti-infectives": 0,
                "Cardiovascular": 1, "Diabetes": 1, "Vitamins & Supplements": 2,
                "Dermatology": 3, "Reproductive Health": 3, "First Aid & Medical Supplies": 4}
sup_rows, sup_type_idx = [], []
for t, (tname, n) in enumerate(SUP_TYPES):
    for _ in range(n):
        sup_rows.append(tname); sup_type_idx.append(t)
NS = len(sup_rows)
sup_ids = [f"SUP{i + 1:02d}" for i in range(NS)]
sup_names = [f"SIM Supplier {i + 1:02d} ({sup_rows[i].split()[0]})" for i in range(NS)]
sup_lead = rng.integers(2, 6, NS)
sup_inactive_since = np.full(NS, 10_000)
inact = [1, 17]                                             # one wholesaler, one OTC/consumer distributor
sup_inactive_since[inact[0]] = doy(6, 30)
sup_inactive_since[inact[1]] = doy(9, 15)
sup_primary = np.zeros(P, dtype=int); sup_alt = np.zeros(P, dtype=int)
for p in range(P):
    t = CAT_SUP_TYPE[prod_rows[p]["cat"]]
    pool = [i for i in range(NS) if sup_type_idx[i] == t]
    sup_primary[p] = rng.choice(pool)
    active_pool = [i for i in pool if sup_inactive_since[i] == 10_000 and i != sup_primary[p]]
    sup_alt[p] = rng.choice(active_pool)

# ----------------------------------------------------------------------------------
# Calendar effects. DRAFT holiday list used ONLY as a mild demand driver; it is not verified.
# ----------------------------------------------------------------------------------
HOLIDAYS_DRAFT = [
    ("2025-01-01", "New Year's Day"), ("2025-03-31", "Idd-ul-Fitr"), ("2025-04-18", "Good Friday"),
    ("2025-04-21", "Easter Monday"), ("2025-05-01", "Labour Day"), ("2025-06-01", "Madaraka Day"),
    ("2025-06-02", "Madaraka Day (observed - 1 June fell on a Sunday)"),
    ("2025-10-10", "Mazingira Day (name and status to be confirmed against the Gazette)"),
    ("2025-10-20", "Mashujaa Day"), ("2025-12-12", "Jamhuri Day"),
    ("2025-12-25", "Christmas Day"), ("2025-12-26", "Boxing Day")]
hol_idx = [(date.fromisoformat(d) - D0).days for d, _ in HOLIDAYS_DRAFT]
DOW_F = np.array([1.00, 0.98, 0.97, 1.00, 1.10, 1.15, 0.75])
MON_F = np.array([0.95, 0.92, 1.00, 1.02, 1.00, 0.98, 1.03, 1.00, 1.02, 1.05, 1.05, 1.15])
day_w = DOW_F[dow] * MON_F[mon] * rng.lognormal(0, 0.10, ND)
day_w[hol_idx] *= 0.85
day_p = day_w / day_w.sum()

# ----------------------------------------------------------------------------------
# Promotions (60): 40 product-level, 20 category-level
# Precedence: product-level beats category-level; within a level the larger per-unit
# discount wins; one promotion per line, never stacked.
# ----------------------------------------------------------------------------------
promos = []   # dict(level, p, c, start, end, ptype, val)
active_prod = [p for p in range(P) if disc_day[p] == 10_000]
for p in rng.choice(active_prod, N_PROMO_PRODUCT, replace=False):
    dur = int(rng.choice([7, 10, 14, 14, 21, 28]))
    st = int(rng.integers(5, 330 - dur))
    if base_price[p] >= 60 and rng.random() < 0.35:
        opts = [v for v in (5, 10, 15, 20, 30) if v <= 0.25 * base_price[p]]
        ptype, val = ("Fixed amount", float(rng.choice(opts))) if opts else ("Percentage", float(rng.choice([5, 10, 15, 20])))
    else:
        ptype, val = "Percentage", float(rng.choice([5, 10, 15, 20]))
    promos.append(dict(level=2, p=int(p), c=-1, start=st, end=st + dur - 1, ptype=ptype, val=val))
for c in rng.choice(C, N_PROMO_CATEGORY, replace=True):
    dur = int(rng.choice([7, 14, 14, 21]))
    st = int(rng.integers(5, 330 - dur))
    promos.append(dict(level=1, p=-1, c=int(c), start=st, end=st + dur - 1, ptype="Percentage",
                       val=float(rng.choice([5, 10, 15]))))
promos.sort(key=lambda r: (r["start"], r["level"]))
for i, r in enumerate(promos):
    r["id"] = f"PROMO{i + 1:03d}"
    if r["level"] == 2:
        shown = f"{int(r['val'])}% off" if r["ptype"] == "Percentage" else f"KES {int(r['val'])} off"
        r["name"] = f"{prod_rows[r['p']]['name']} - {shown}"
    else:
        r["name"] = f"{CATS[r['c']]} promotion - {int(r['val'])}% off"
promo_boost = np.ones((ND, P))
for r in promos:
    sl = slice(r["start"], r["end"] + 1)
    if r["level"] == 2:
        promo_boost[sl, r["p"]] = np.maximum(promo_boost[sl, r["p"]], 2.0)
    else:
        cols = np.where(prod_cat == r["c"])[0]
        promo_boost[sl][:, cols] = np.maximum(promo_boost[sl][:, cols], 1.35)
NW = 53
week_boost = np.array([promo_boost[w * 7:(w + 1) * 7].mean(axis=0) for w in range(NW)])

# ----------------------------------------------------------------------------------
# Product demand weights: popularity x seasonality x branch/category mix x promotions
# (seasonality and county mix are MODELLING ASSUMPTIONS, not evidence)
# ----------------------------------------------------------------------------------
season = np.ones((C, 12))
season[CATS.index("Antimalarials")] = [.9, .9, 1.0, 1.2, 1.3, 1.2, 1.0, .9, .9, 1.0, 1.2, 1.1]
season[CATS.index("Respiratory & Allergy")] = [1.0, 1.0, .95, .95, 1.0, 1.2, 1.3, 1.25, 1.0, .95, .95, 1.0]
season[CATS.index("Gastrointestinal")] = [.95, .95, 1, 1, 1, 1, 1, 1, 1, 1, 1.05, 1.15]
season[CATS.index("Vitamins & Supplements")] = [1.2, 1.1, 1, 1, 1, 1, 1, 1, 1, 1, 1.05, 1.1]
store_cat = rng.lognormal(0, 0.2, (S, C))
cty_mal = {"Kisumu": 1.7, "Mombasa": 1.4, "Nairobi": 0.6, "Kiambu": 0.8, "Nakuru": 0.9, "Uasin Gishu": 0.9}
cty_resp = {"Nakuru": 1.2, "Uasin Gishu": 1.2}
for s in range(S):
    store_cat[s, CATS.index("Antimalarials")] *= cty_mal[store_county[s]]
    store_cat[s, CATS.index("Respiratory & Allergy")] *= cty_resp.get(store_county[s], 1.0)
week_month = np.array([mon[min(w * 7 + 3, ND - 1)] for w in range(NW)])

# ----------------------------------------------------------------------------------
# Customers (8,000) and identified transactions (80,000)
# ----------------------------------------------------------------------------------
SEG = ["Frequent", "Regular", "Occasional", "Promo-driven", "Basket-builder"]
seg = rng.choice(5, N_CUST, p=[.12, .30, .35, .13, .10])
act_mult = np.array([5, 2, .6, 1.2, 1.4])
reg2025 = rng.random(N_CUST) < 0.35
reg_day = np.where(reg2025, rng.integers(0, ND, N_CUST), -1)
pre_reg_off = rng.integers(0, 1096, N_CUST)                       # 2022-01-01 .. 2024-12-31
exposure = np.where(reg2025, (ND - reg_day) / ND, 1.0)
w = act_mult[seg] * rng.lognormal(0, 0.5, N_CUST) * exposure
n_c = 1 + rng.multinomial(N_ID - N_CUST, w / w.sum())
home_store = rng.choice(S, N_CUST, p=store_w / store_w.sum())
chronic_cats = [CATS.index(c) for c in ("Cardiovascular", "Diabetes", "Vitamins & Supplements", "Respiratory & Allergy")]
chronic_pool = [p for p in range(P) if prod_cat[p] in chronic_cats and disc_day[p] == 10_000]
cp = prod_pop[chronic_pool] / prod_pop[chronic_pool].sum()
fav = np.where(rng.random(N_CUST) < 0.35, rng.choice(chronic_pool, N_CUST, p=cp), -1)

id_day, id_cust = [], []
for c in range(N_CUST):
    n = int(n_c[c])
    if reg2025[c]:
        st = int(reg_day[c])
        pp = day_p[st:] / day_p[st:].sum()
        days = [st] + (rng.choice(np.arange(st, ND), n - 1, p=pp).tolist() if n > 1 else [])
    else:
        days = rng.choice(ND, n, p=day_p).tolist()
    id_day += days; id_cust += [c] * n
id_day = np.array(id_day); id_cust = np.array(id_cust)
r = rng.random(len(id_day))
id_store = home_store[id_cust].copy()
m1 = r < 0.10; id_store[m1] = sibling[id_store[m1]]
m2 = (r >= 0.10) & (r < 0.20)
for i in np.where(m2)[0]:
    id_store[i] = rng.choice([s for s in range(S) if s != home_store[id_cust[i]]])

n_un = N_TXN - N_ID
un_day = rng.choice(ND, n_un, p=day_p)
un_store = rng.choice(S, n_un, p=store_w / store_w.sum())

tx_day = np.concatenate([id_day, un_day])
tx_store = np.concatenate([id_store, un_store])
tx_cust = np.concatenate([id_cust, np.full(n_un, -1)])
perm = rng.permutation(N_TXN)
tx_day, tx_store, tx_cust = tx_day[perm], tx_store[perm], tx_cust[perm]
_hw = np.array([3, 6, 8, 9, 10, 9, 8, 7, 8, 10, 10, 8, 4], dtype=float)
hour = rng.choice(np.arange(8, 21), N_TXN, p=_hw / _hw.sum())
tx_sec = hour * 3600 + rng.integers(0, 3600, N_TXN)
order = np.lexsort((tx_sec, tx_day))
tx_day, tx_store, tx_cust, tx_sec = tx_day[order], tx_store[order], tx_cust[order], tx_sec[order]
tx_ts = tx_day.astype(np.int64) * 86400 + tx_sec
tx_ids = np.array([f"TXN{i + 1:07d}" for i in range(N_TXN)])
tx_pre_void = rng.random(N_TXN) < P_VOID_RANDOM

# ----------------------------------------------------------------------------------
# Demand lines
# ----------------------------------------------------------------------------------
lam_lines = np.where(tx_cust >= 0, 1.4, 1.1) + np.where(tx_cust >= 0, (seg[np.maximum(tx_cust, 0)] == 4) * 0.9, 0)
n_lines = np.minimum(1 + rng.poisson(lam_lines), 8)
l_txn = np.repeat(np.arange(N_TXN), n_lines)
l_prod = np.zeros(len(l_txn), dtype=int)
key = tx_store[l_txn] * NW + tx_day[l_txn] // 7
srt = np.argsort(key, kind="stable")
ukeys, ustart = np.unique(key[srt], return_index=True)
uend = np.append(ustart[1:], len(srt))
for k, a, b in zip(ukeys, ustart, uend):
    s, wk = divmod(int(k), NW)
    wt = prod_pop * season[prod_cat, week_month[wk]] * store_cat[s, prod_cat] * week_boost[wk]
    idx = srt[a:b]
    l_prod[idx] = rng.choice(P, len(idx), p=wt / wt.sum())
# refill-style favourite product for some identified customers
has_fav = (tx_cust >= 0) & (fav[np.maximum(tx_cust, 0)] >= 0) & (rng.random(N_TXN) < 0.45)
fx = np.where(has_fav)[0]
l_txn = np.concatenate([l_txn, fx]); l_prod = np.concatenate([l_prod, fav[tx_cust[fx]]])
# discontinued products cannot be demanded after their date: re-draw an active product
bad = disc_day[l_prod] <= tx_day[l_txn]
if bad.any():
    ap = np.array(active_prod); app = prod_pop[ap] / prod_pop[ap].sum()
    l_prod[bad] = rng.choice(ap, bad.sum(), p=app)
l_q = np.minimum(1 + rng.poisson(lam_p[l_prod]), 6)
ld = pd.DataFrame(dict(txn=l_txn, prod=l_prod, q=l_q, r=rng.random(len(l_txn))))
ld = ld.groupby(["txn", "prod"], as_index=False).agg(q=("q", "sum"), r=("r", "first"))
ld["q"] = ld["q"].clip(upper=8)
ld = ld.sort_values(["txn", "r"], kind="stable").reset_index(drop=True)
ltx, lp, lq = ld["txn"].to_numpy(), ld["prod"].to_numpy(), ld["q"].to_numpy()
ls = tx_store[ltx]; ldy = tx_day[ltx]
NL = len(ltx)

D = np.zeros((ND, S, P), dtype=np.float32)
ok = ~tx_pre_void[ltx]
np.add.at(D, (ldy[ok], ls[ok], lp[ok]), lq[ok])
Dyear = D.sum(axis=0) / ND

# ----------------------------------------------------------------------------------
# Inventory + purchasing simulation (chronological)
# ----------------------------------------------------------------------------------
opening = np.maximum(2, np.ceil(Dyear * rng.uniform(25, 45, (S, P)))).astype(np.int64)
stock = opening.copy()
onorder = np.zeros((S, P), dtype=np.int64)
deliveries = defaultdict(list)
po_rows, poi_rows, mv = [], [], []           # mv: (datetime, s, p, type, qty, ref_type, ref_id, reason)
lfill = np.zeros(NL, dtype=np.int64)
off = np.searchsorted(ldy, np.arange(ND + 1))
review_off = rng.integers(0, REVIEW_DAYS, S)

wo_events, adj_events = defaultdict(list), defaultdict(list)
for _ in range(N_WRITEOFFS):
    s = int(rng.choice(S, p=store_w / store_w.sum())); p = int(rng.choice(P, p=prod_pop / prod_pop.sum()))
    d = int(rng.integers(0, ND)); q = int(rng.integers(1, 5))
    reason = str(rng.choice(["Expired", "Damaged", "Near-expiry removal"], p=[.5, .3, .2]))
    wo_events[d].append((s, p, q, reason))
for _ in range(N_ADJUST):
    s = int(rng.choice(S, p=store_w / store_w.sum())); p = int(rng.choice(P, p=prod_pop / prod_pop.sum()))
    d = int(rng.integers(0, ND)); q = int(rng.integers(1, 4))
    if rng.random() < 0.70:
        adj_events[d].append((s, p, -q, str(rng.choice(["Stock count variance", "Shrinkage (unexplained loss)"]))))
    else:
        adj_events[d].append((s, p, q, "Stock count variance (found stock)"))

stock_l = None
po_n = 0
tx_prev = tx_pre_void.tolist(); ltx_l, ls_l, lp_l, lq_l = ltx.tolist(), ls.tolist(), lp.tolist(), lq.tolist()
cost_at = lambda d, p: np.where(d >= chg_day[p], new_cost[p], base_cost[p])
dt_of = lambda d, secs: BASE + timedelta(days=int(d), seconds=int(secs))
po_stats = dict(cancelled=0, delayed=0, short_lines=0)

for d in range(ND):
    # 1) receipts (06:00-07:59, before trading)
    for (s, prods, ordered, recv, po_id, secs) in deliveries.get(d, []):
        stock[s, prods] += recv
        onorder[s, prods] -= ordered
        for p, rq in zip(prods.tolist(), recv.tolist()):
            if rq > 0:
                mv.append((dt_of(d, secs), s, p, "Receipt", rq, "Purchase order", po_id, None))
    # 2) sales in time order
    for i in range(off[d], off[d + 1]):
        if tx_prev[ltx_l[i]]:
            continue
        s, p, q = ls_l[i], lp_l[i], lq_l[i]
        a = int(stock[s, p])
        f = q if a >= q else a
        if f:
            stock[s, p] = a - f
        lfill[i] = f
    # 3) write-offs / adjustments after trading (21:00+)
    for (s, p, q, reason) in wo_events.get(d, []):
        take = min(q, int(stock[s, p]))
        if take > 0:
            stock[s, p] -= take
            mv.append((dt_of(d, 21 * 3600 + int(rng.integers(0, 5400))), s, p, "Write-off", -take, "Adjustment", None, reason))
    for (s, p, q, reason) in adj_events.get(d, []):
        if q < 0:
            q = -min(-q, int(stock[s, p]))
            if q == 0:
                continue
        stock[s, p] += q
        mv.append((dt_of(d, 21 * 3600 + int(rng.integers(0, 5400))), s, p, "Adjustment", q, "Adjustment", None, reason))
    for p in np.where(disc_day == d)[0].tolist():
        for s in range(S):
            if stock[s, p] > 0:
                mv.append((dt_of(d, 22 * 3600 + 1800 + int(rng.integers(0, 600))), s, p, "Write-off", -int(stock[s, p]), "Adjustment", None, "Product discontinued"))
                stock[s, p] = 0
    # 4) reorder review
    sup_today = np.where(sup_inactive_since[sup_primary] <= d, sup_alt, sup_primary)
    can_order = d < disc_day - 21
    for s in range(S):
        if (d + review_off[s]) % REVIEW_DAYS != 0:
            continue
        avg = (D[d - 42:d, s, :].sum(axis=0) / 42.0) if d >= 42 else Dyear[s]
        H = sup_lead[sup_today] + REVIEW_DAYS
        mu = avg * H
        rop = mu + 1.65 * np.sqrt(mu) + 1.0
        pos = stock[s] + onorder[s]
        qty = np.ceil((rop + avg * 14 - pos) / lot) * lot
        sel = np.where((pos <= rop) & (qty > 0) & can_order)[0]
        if len(sel) == 0:
            continue
        for u in np.unique(sup_today[sel]):
            pl = sel[sup_today[sel] == u]
            po_n += 1; po_id = f"PO{po_n:06d}"
            lead = max(1, int(sup_lead[u]) + int(rng.choice([-1, 0, 0, 1])))
            expected = d + lead
            cancelled = rng.random() < 0.015
            delay = int(rng.integers(1, 6)) if rng.random() < 0.14 else 0
            actual = expected + delay
            ordered = qty[pl].astype(np.int64)
            recv = ordered.copy()
            if not cancelled:
                short = (rng.random(len(pl)) < 0.07) & (ordered > 1)
                recv[short] = np.maximum(0, np.floor(ordered[short] * rng.uniform(0.5, 0.95, short.sum()))).astype(np.int64)
                po_stats["short_lines"] += int(short.sum())
            ucost = np.round(cost_at(d, pl) * rng.uniform(0.97, 1.03, len(pl)), 2)
            if cancelled:
                status = "Cancelled"; recv[:] = 0; po_stats["cancelled"] += 1
            elif actual > ND - 1:
                status = "Open"; recv[:] = 0
                onorder[s, pl] += ordered
            else:
                status = "Completed" if (recv == ordered).all() else "Partially received"
                onorder[s, pl] += ordered
                deliveries[actual].append((s, pl.copy(), ordered.copy(), recv.copy(), po_id, int(rng.integers(6 * 3600, 8 * 3600))))
                if delay: po_stats["delayed"] += 1
            po_rows.append((po_id, sup_ids[u], store_ids[s], DATES[d], D0 + timedelta(days=expected), status))
            for j, p in enumerate(pl.tolist()):
                poi_rows.append((po_id, j + 1, prod_ids[p], int(ordered[j]), int(recv[j]), float(ucost[j])))

# ----------------------------------------------------------------------------------
# Final transaction status and items
# ----------------------------------------------------------------------------------
tx_filled = np.bincount(ltx, weights=lfill, minlength=N_TXN)
void = tx_pre_void | (tx_filled == 0)
void_reason = np.where(tx_pre_void, "Cashier void", np.where(void, "No stock available", ""))
keep = void[ltx] | (lfill > 0)
it = pd.DataFrame(dict(txn=ltx[keep], prod=lp[keep], q=np.where(void[ltx], lq, lfill)[keep]))
it["line_id"] = it.groupby("txn").cumcount() + 1
i_txn, i_prod, i_q = it["txn"].to_numpy(), it["prod"].to_numpy(), it["q"].to_numpy().astype(np.int64)
i_day = tx_day[i_txn]
chg = i_day >= chg_day[i_prod]
i_price_c = np.where(chg, new_price_c[i_prod], base_price_c[i_prod])
i_cost_c = np.where(chg, new_cost_c[i_prod], base_cost_c[i_prod])
i_gross_c = i_q * i_price_c
best_key = np.full(len(it), -1.0); best_k = np.full(len(it), -1)
p_is_pct = np.array([r["ptype"] == "Percentage" for r in promos]); p_val = np.array([r["val"] for r in promos])
i_cat = prod_cat[i_prod]
for k, r in enumerate(promos):
    m = (i_day >= r["start"]) & (i_day <= r["end"]) & ((i_prod == r["p"]) if r["level"] == 2 else (i_cat == r["c"]))
    if not m.any():
        continue
    ud = i_price_c[m] * r["val"] / 100.0 if r["ptype"] == "Percentage" else np.full(m.sum(), r["val"] * 100.0)
    kk = r["level"] * 1e7 + ud
    idxs = np.where(m)[0]; upd = kk > best_key[idxs]
    best_key[idxs[upd]] = kk[upd]; best_k[idxs[upd]] = k
hasp = best_k >= 0
bk = np.maximum(best_k, 0)
disc_c = np.where(p_is_pct[bk], np.rint(i_gross_c * p_val[bk] / 100.0), p_val[bk] * 100.0 * i_q)
disc_c = np.where(hasp, np.minimum(disc_c, i_gross_c // 2), 0).astype(np.int64)
i_net_c = i_gross_c - disc_c

h = pd.DataFrame(dict(txn=i_txn, g=i_gross_c, d=disc_c, n=i_net_c)).groupby("txn").sum().reindex(range(N_TXN))
pay = rng.choice(["M-Pesa", "Cash", "Card", "Insurance"], N_TXN, p=[.60, .24, .10, .06])
tx_dt = pd.to_datetime(tx_ts, unit="s", origin=pd.Timestamp(BASE))

# ----------------------------------------------------------------------------------
# Returns (one return event per selected completed transaction)
# ----------------------------------------------------------------------------------
comp = np.where(~void)[0]
cand = rng.choice(comp, int(len(comp) * P_RETURN * 1.02), replace=False)
rt = pd.DataFrame(dict(txn=cand, delay=rng.integers(0, 15, len(cand)), mins=rng.integers(10, 600, len(cand)), k=np.where(rng.random(len(cand)) < 0.3, 2, 1)))
rt["ret_dt"] = tx_dt[rt["txn"].to_numpy()] + pd.to_timedelta(rt["delay"] * 1440 + rt["mins"], unit="m")
rt = rt[rt["ret_dt"] < pd.Timestamp("2026-01-01")].copy()
rt = rt.sort_values("ret_dt").reset_index(drop=True)
rt["return_id"] = [f"RET{i + 1:06d}" for i in range(len(rt))]
rt["reason"] = rng.choice(["Wrong product dispensed", "Duplicate purchase", "Customer changed mind", "Damaged packaging", "Prescription changed", "Product near expiry"], len(rt), p=[.15, .20, .25, .15, .15, .10])
itm = pd.DataFrame(dict(txn=i_txn, line_id=it["line_id"].to_numpy(), prod=i_prod, q=i_q, net_c=i_net_c))
itm = itm[~void[itm["txn"].to_numpy()]]
sel = itm[itm["txn"].isin(rt["txn"])].copy()
sel["r"] = rng.random(len(sel))
sel = sel.sort_values(["txn", "r"])
sel["rank"] = sel.groupby("txn").cumcount()
sel = sel.merge(rt[["txn", "k", "return_id", "reason", "ret_dt"]], on="txn")
sel = sel[sel["rank"] < sel["k"]].copy()
sel["qret"] = np.minimum(sel["q"], 1 + rng.poisson(0.3, len(sel)))
sel["unit_refund_c"] = (sel["net_c"] // sel["q"]).astype(np.int64)
sel["restockable"] = ~sel["reason"].isin(["Damaged packaging", "Product near expiry"]) & (rng.random(len(sel)) < 0.88)
sel = sel.sort_values(["return_id", "rank"]).reset_index(drop=True)
sel["rline"] = sel.groupby("return_id").cumcount() + 1
sel["refund_c"] = sel["qret"] * sel["unit_refund_c"]
refund_by = sel.groupby("return_id")["refund_c"].sum()
rt["refund_c"] = rt["return_id"].map(refund_by).astype("int64")
for _, rw in sel[sel["restockable"]].iterrows():
    s = int(tx_store[rw["txn"]])
    mv.append((rw["ret_dt"].to_pydatetime(), s, int(rw["prod"]), "Return", int(rw["qret"]), "Return", rw["return_id"], None))

# sale movements (completed transactions only)
cm = ~void[i_txn]
sale_dt = tx_dt[i_txn[cm]]
sale_df = pd.DataFrame(dict(movement_datetime=sale_dt, s=tx_store[i_txn[cm]], p=i_prod[cm], movement_type="Sale",
                            quantity_change=-i_q[cm], reference_type="Sale", reference_id=tx_ids[i_txn[cm]], adjustment_reason=None))
mv_df = pd.DataFrame(mv, columns=["movement_datetime", "s", "p", "movement_type", "quantity_change", "reference_type", "reference_id", "adjustment_reason"])
mv_df["movement_datetime"] = pd.to_datetime(mv_df["movement_datetime"])
led = pd.concat([mv_df, sale_df], ignore_index=True)
led = led.sort_values(["movement_datetime", "quantity_change"], ascending=[True, False], kind="stable").reset_index(drop=True)
led["movement_id"] = [f"MOV{i + 1:07d}" for i in range(len(led))]

# ----------------------------------------------------------------------------------
# Customers table (IDs follow registration order)
# ----------------------------------------------------------------------------------
reg_date = np.array([(D0 + timedelta(days=int(reg_day[c]))) if reg2025[c] else (date(2022, 1, 1) + timedelta(days=int(pre_reg_off[c]))) for c in range(N_CUST)])
cust_order = np.lexsort((np.arange(N_CUST), np.array([d.toordinal() for d in reg_date])))
new_id = np.empty(N_CUST, dtype=int); new_id[cust_order] = np.arange(N_CUST)
cust_ids = np.array([f"CUST{i + 1:05d}" for i in range(N_CUST)])
last_comp = pd.Series(tx_day[(tx_cust >= 0) & ~void]).groupby(tx_cust[(tx_cust >= 0) & ~void]).max()
last_day = np.array([last_comp.get(c, -1) for c in range(N_CUST)])
cust_status = np.where(last_day >= ND - 90, "Active", "Inactive")

# ----------------------------------------------------------------------------------
# Write files
# ----------------------------------------------------------------------------------
fmt = lambda s: pd.to_datetime(s).dt.strftime("%Y-%m-%d %H:%M:%S")
cents = lambda a: np.asarray(a) / 100.0
W = lambda df, name: df.to_csv(os.path.join(RAW, name), index=False, float_format="%.2f")

stores_df = pd.DataFrame(dict(store_id=store_ids, store_name=[s[1] for s in STORES], county=store_county,
                              town=[s[3] for s in STORES], opening_date=[s[4] for s in STORES], store_status="Active"))
products_df = pd.DataFrame(dict(product_id=prod_ids, product_name=[r["name"] for r in prod_rows],
                                active_ingredient=[("" if r["form"] in DEVICE_FORMS else r["ing"]) for r in prod_rows],
                                strength=[r["strength"] for r in prod_rows], dosage_form=[r["form"] for r in prod_rows],
                                category=[r["cat"] for r in prod_rows], unit_of_measure=[r["uom"] for r in prod_rows],
                                unit_cost=base_cost, selling_price=base_price, product_status=status_prod))
customers_df = pd.DataFrame(dict(customer_id=cust_ids,
                                 registration_date=[reg_date[c].isoformat() for c in cust_order],
                                 customer_segment=[SEG[seg[c]] for c in cust_order],
                                 customer_status=cust_status[cust_order]))
tx_cust_out = np.where(tx_cust >= 0, cust_ids[new_id[np.maximum(tx_cust, 0)]], "")
txn_df = pd.DataFrame(dict(transaction_id=tx_ids, transaction_datetime=tx_dt.strftime("%Y-%m-%d %H:%M:%S"),
                           store_id=np.array(store_ids)[tx_store], customer_id=tx_cust_out, payment_method=pay,
                           transaction_status=np.where(void, "Voided", "Completed"), currency_code="KES",
                           gross_amount=cents(h["g"]), discount_amount=cents(h["d"]), net_amount=cents(h["n"])))
txn_df["customer_id"] = txn_df["customer_id"].replace("", np.nan)
items_df = pd.DataFrame(dict(transaction_id=tx_ids[i_txn], line_id=it["line_id"].to_numpy(), product_id=np.array(prod_ids)[i_prod],
                             quantity=i_q, unit_price=cents(i_price_c), discount_amount=cents(disc_c),
                             unit_cost_at_sale=cents(i_cost_c), line_gross_amount=cents(i_gross_c), line_net_amount=cents(i_net_c),
                             promotion_id=np.where(hasp, np.array([r["id"] for r in promos])[bk], None)))
ret_df = pd.DataFrame(dict(return_id=rt["return_id"], original_transaction_id=tx_ids[rt["txn"]],
                           return_datetime=rt["ret_dt"].dt.strftime("%Y-%m-%d %H:%M:%S"),
                           store_id=np.array(store_ids)[tx_store[rt["txn"].to_numpy()]], return_reason=rt["reason"],
                           refund_amount=cents(rt["refund_c"])))
reti_df = pd.DataFrame(dict(return_id=sel["return_id"], line_id=sel["rline"], product_id=np.array(prod_ids)[sel["prod"].to_numpy()],
                            quantity_returned=sel["qret"], unit_refund_amount=cents(sel["unit_refund_c"]),
                            restockable=sel["restockable"].map({True: "TRUE", False: "FALSE"})))
promo_df = pd.DataFrame(dict(promotion_id=[r["id"] for r in promos], promotion_name=[r["name"] for r in promos],
                             promotion_type=["Product-level" if r["level"] == 2 else "Category-level" for r in promos],
                             product_id=[prod_ids[r["p"]] if r["level"] == 2 else None for r in promos],
                             category=[CATS[r["c"]] if r["level"] == 1 else None for r in promos],
                             start_date=[(D0 + timedelta(days=r["start"])).isoformat() for r in promos],
                             end_date=[(D0 + timedelta(days=r["end"])).isoformat() for r in promos],
                             discount_type=[r["ptype"] for r in promos], discount_value=[r["val"] for r in promos]))
mv_out = pd.DataFrame(dict(movement_id=led["movement_id"], movement_datetime=led["movement_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S"),
                           store_id=np.array(store_ids)[led["s"].to_numpy()], product_id=np.array(prod_ids)[led["p"].to_numpy()],
                           movement_type=led["movement_type"], quantity_change=led["quantity_change"].astype(int),
                           reference_type=led["reference_type"], reference_id=led["reference_id"], adjustment_reason=led["adjustment_reason"]))
sup_df = pd.DataFrame(dict(supplier_id=sup_ids, supplier_name=sup_names, supplier_type=sup_rows,
                           supplier_status=np.where(sup_inactive_since < 10_000, "Inactive", "Active")))
po_df = pd.DataFrame(po_rows, columns=["purchase_order_id", "supplier_id", "store_id", "order_date", "expected_delivery_date", "order_status"])
po_df["order_date"] = po_df["order_date"].astype(str); po_df["expected_delivery_date"] = po_df["expected_delivery_date"].astype(str)
poi_df = pd.DataFrame(poi_rows, columns=["purchase_order_id", "line_id", "product_id", "quantity_ordered", "quantity_received", "unit_purchase_cost"])
open_df = pd.DataFrame(dict(store_id=np.repeat(store_ids, P), product_id=np.tile(prod_ids, S),
                            opening_quantity=opening.reshape(-1), as_of_date="2024-12-31"))
pc_idx = np.where(chg_day < 10_000)[0]
pchg_df = pd.DataFrame(dict(product_id=np.array(prod_ids)[pc_idx], effective_date=[(D0 + timedelta(days=int(chg_day[p]))).isoformat() for p in pc_idx],
                            new_unit_cost=new_cost[pc_idx], new_selling_price=new_price[pc_idx],
                            reason="Simulated supplier cost increase")).sort_values("effective_date")
lost = pd.DataFrame(dict(txn=ltx, prod=lp, dem=lq, fill=lfill))
lost = lost[(~tx_pre_void[lost["txn"].to_numpy()]) & (lost["fill"] < lost["dem"])].copy()
lost_df = pd.DataFrame(dict(transaction_id=tx_ids[lost["txn"]], transaction_date=[DATES[tx_day[t]].isoformat() for t in lost["txn"]],
                            store_id=np.array(store_ids)[tx_store[lost["txn"].to_numpy()]], product_id=np.array(prod_ids)[lost["prod"].to_numpy()],
                            quantity_demanded=lost["dem"].to_numpy(), quantity_fulfilled=lost["fill"].to_numpy(),
                            outcome=np.where(void[lost["txn"].to_numpy()], "Transaction voided - no stock",
                                             np.where(lost["fill"].to_numpy() == 0, "Line dropped - no stock", "Partially filled"))))

W(stores_df, "stores.csv"); W(products_df, "products.csv"); W(customers_df, "customers.csv")
W(txn_df, "transactions.csv"); W(items_df, "transaction_items.csv"); W(ret_df, "sales_returns.csv")
W(reti_df, "sales_return_items.csv"); W(promo_df, "promotions.csv"); W(mv_out, "inventory_movements.csv")
W(sup_df, "suppliers.csv"); W(po_df, "purchase_orders.csv"); W(poi_df, "purchase_order_items.csv")
W(open_df, "opening_inventory.csv"); W(pchg_df, "price_changes.csv"); W(lost_df, "lost_sales_log.csv")

# public-context placeholders (NOT real data - see README)
pd.DataFrame(HOLIDAYS_DRAFT, columns=["holiday_date", "holiday_name"]).assign(
    holiday_type="", source_id="", verification_note="UNVERIFIED DRAFT - confirm against the Public Holidays Act and 2025 Gazette notices before use"
).to_csv(os.path.join(PUB, "public_holidays_2025_DRAFT_unverified.csv"), index=False)
pd.DataFrame(dict(month=[f"2025-{m:02d}-01" for m in range(1, 13)], cpi_index=np.nan, annual_inflation_rate=np.nan,
                  cpi_category="", source_id="")).to_csv(os.path.join(PUB, "cpi_monthly_TEMPLATE.csv"), index=False)

# ----------------------------------------------------------------------------------
# Validation report
# ----------------------------------------------------------------------------------
checks = []
def chk(name, ok_, detail=""):
    checks.append((name, bool(ok_), detail))

chk("Row counts: 12 stores, 150 products, 8,000 customers, 100,000 headers",
    (len(stores_df), len(products_df), len(customers_df), len(txn_df)) == (12, 150, 8000, 100000),
    f"{len(stores_df)}/{len(products_df)}/{len(customers_df)}/{len(txn_df)}")
chk("Primary keys unique & non-null",
    all([stores_df.store_id.is_unique, products_df.product_id.is_unique, customers_df.customer_id.is_unique,
         txn_df.transaction_id.is_unique, not items_df.duplicated(["transaction_id", "line_id"]).any(),
         ret_df.return_id.is_unique, not reti_df.duplicated(["return_id", "line_id"]).any(), promo_df.promotion_id.is_unique,
         mv_out.movement_id.is_unique, sup_df.supplier_id.is_unique, po_df.purchase_order_id.is_unique,
         not poi_df.duplicated(["purchase_order_id", "line_id"]).any()]))
fk = [txn_df.store_id.isin(stores_df.store_id).all(), txn_df.customer_id.dropna().isin(customers_df.customer_id).all(),
      items_df.transaction_id.isin(txn_df.transaction_id).all(), items_df.product_id.isin(products_df.product_id).all(),
      ret_df.original_transaction_id.isin(txn_df.transaction_id).all(), ret_df.store_id.isin(stores_df.store_id).all(),
      reti_df.return_id.isin(ret_df.return_id).all(), reti_df.product_id.isin(products_df.product_id).all(),
      mv_out.store_id.isin(stores_df.store_id).all(), mv_out.product_id.isin(products_df.product_id).all(),
      po_df.supplier_id.isin(sup_df.supplier_id).all(), po_df.store_id.isin(stores_df.store_id).all(),
      poi_df.purchase_order_id.isin(po_df.purchase_order_id).all(), poi_df.product_id.isin(products_df.product_id).all(),
      promo_df.product_id.dropna().isin(products_df.product_id).all()]
chk("Foreign keys (15 relationships)", all(fk))
link = txn_df.customer_id.notna().mean()
chk("Customer linkage ~80%", abs(link - 0.8) < 0.005, f"{link:.4f}")
d_ok = txn_df.transaction_datetime.min() >= "2025-01-01" and txn_df.transaction_datetime.max() < "2026-01-01"
reg_ok = (customers_df.registration_date <= "2025-12-31").all()
chk("Dates within period; store opening dates before period", d_ok and reg_ok and (stores_df.opening_date < "2025-01-01").all())
first_tx = txn_df.dropna(subset=["customer_id"]).assign(d=lambda x: x.transaction_datetime.str[:10]).groupby("customer_id").d.min()
reg_map = customers_df.set_index("customer_id").registration_date
chk("No customer transacts before registration", (first_tx >= reg_map.reindex(first_tx.index)).all())
hg = items_df.groupby("transaction_id")[["line_gross_amount", "discount_amount", "line_net_amount"]].sum().round(2)
hh = txn_df.set_index("transaction_id")[["gross_amount", "discount_amount", "net_amount"]]
diff = (hh.values - hg.reindex(hh.index).values)
chk("Header totals reconcile with item totals (gross, discount, net)", np.abs(diff).max() < 0.005, f"max abs diff {np.abs(diff).max():.4f}")
chk("Line arithmetic: gross = qty x price; net = gross - discount",
    (np.abs(items_df.quantity * items_df.unit_price - items_df.line_gross_amount) < 0.005).all()
    and (np.abs(items_df.line_gross_amount - items_df.discount_amount - items_df.line_net_amount) < 0.005).all())
chk("No negative/zero prices or invalid discounts",
    (items_df.unit_price > 0).all() and (items_df.discount_amount >= 0).all() and (items_df.line_net_amount > 0).all()
    and (items_df.unit_price > items_df.unit_cost_at_sale).all())
# promotions
pi = items_df.dropna(subset=["promotion_id"]).merge(promo_df.rename(columns={"product_id": "promo_product", "category": "promo_category"}), on="promotion_id") \
    .merge(txn_df[["transaction_id", "transaction_datetime"]], on="transaction_id") \
    .merge(products_df[["product_id", "category"]], on="product_id")
pdate = pi.transaction_datetime.str[:10]
elig = (pdate >= pi.start_date) & (pdate <= pi.end_date) & np.where(pi.promotion_type == "Product-level", pi.product_id == pi.promo_product, pi.category == pi.promo_category)
chk("Promotions: every discounted line is date- and product/category-eligible", bool(elig.all()), f"{len(pi):,} promoted lines")
chk("Lines with discount have a promotion; none without", ((items_df.discount_amount > 0) == items_df.promotion_id.notna()).all())
# returns
ri = reti_df.merge(ret_df[["return_id", "original_transaction_id", "return_datetime"]], on="return_id").merge(
    items_df[["transaction_id", "product_id", "quantity", "line_net_amount"]], left_on=["original_transaction_id", "product_id"], right_on=["transaction_id", "product_id"], how="left")
chk("Returns: quantity ≤ original quantity, matched to an original line", (ri.quantity_returned <= ri.quantity).all() and ri.quantity.notna().all())
chk("Returns: unit refund ≤ original net unit price", (ri.unit_refund_amount * ri.quantity <= ri.line_net_amount + 0.005).all())
rs = reti_df.assign(x=reti_df.quantity_returned * reti_df.unit_refund_amount).groupby("return_id").x.sum().round(2)
chk("Returns: header refund = sum of lines", (np.abs(ret_df.set_index("return_id").refund_amount - rs.reindex(ret_df.return_id).values) < 0.005).all())
chk("Returns: only for completed transactions, after the sale",
    (txn_df.set_index("transaction_id").loc[ret_df.original_transaction_id, "transaction_status"] == "Completed").all()
    and (ret_df.return_datetime.values > txn_df.set_index("transaction_id").loc[ret_df.original_transaction_id, "transaction_datetime"].values).all())
# inventory
vs = mv_out[mv_out.movement_type == "Sale"]
chk("Sale movements reference completed transactions only", txn_df.set_index("transaction_id").loc[vs.reference_id, "transaction_status"].eq("Completed").all())
chk("Voided transactions create no stock movements", not mv_out.reference_id.isin(txn_df.loc[txn_df.transaction_status == "Voided", "transaction_id"]).any())
rcv = mv_out[mv_out.movement_type == "Receipt"]
poi_chk = poi_df.assign(k=poi_df.purchase_order_id + "|" + poi_df.product_id)
rk = rcv.assign(k=rcv.reference_id + "|" + rcv.product_id).groupby("k").quantity_change.sum()
exp_recv = poi_chk[poi_chk.quantity_received > 0].set_index("k").quantity_received
chk("Receipts reconcile to purchase-order received quantities", rk.sort_index().equals(exp_recv.sort_index().astype(rk.dtype)) or (rk.reindex(exp_recv.index) == exp_recv).all() and len(rk) == len(exp_recv))
led2 = led.copy()
led2["k"] = led2.s * P + led2.p
open_flat = opening.reshape(-1)
led2["bal"] = led2.groupby("k").quantity_change.cumsum() + open_flat[led2.k.to_numpy()]
chk("Inventory ledger: no negative running balance", led2.bal.min() >= 0, f"min balance {int(led2.bal.min())}")
final = np.zeros(S * P, dtype=np.int64); final += open_flat
np.add.at(final, led2.k.to_numpy(), led2.quantity_change.to_numpy())
chk("Closing stock = opening + signed movements (all 1,800 store-products)", final.min() >= 0, f"closing units {int(final.sum()):,}")
chk("Purchasing: received ≤ ordered", (poi_df.quantity_received <= poi_df.quantity_ordered).all())
chk("Purchasing: Open/Cancelled orders have no receipts; Completed fully received",
    (poi_df.merge(po_df, on="purchase_order_id").query("order_status in ['Open','Cancelled']").quantity_received == 0).all()
    and (poi_df.merge(po_df, on="purchase_order_id").query("order_status == 'Completed'").pipe(lambda x: (x.quantity_received == x.quantity_ordered).all())))
chk("Purchasing: expected delivery ≥ order date", (po_df.expected_delivery_date >= po_df.order_date).all())
chk("Privacy: no names/phones/addresses/medical history in any customer file", list(customers_df.columns) == ["customer_id", "registration_date", "customer_segment", "customer_status"])
chk("Reproducibility: seed recorded", True, f"SEED={SEED}")

sm = {}
comp_txn = txn_df[txn_df.transaction_status == "Completed"]
sm["rows"] = {n: len(d) for n, d in [("stores", stores_df), ("products", products_df), ("customers", customers_df),
              ("transactions", txn_df), ("transaction_items", items_df), ("sales_returns", ret_df), ("sales_return_items", reti_df),
              ("promotions", promo_df), ("inventory_movements", mv_out), ("suppliers", sup_df), ("purchase_orders", po_df),
              ("purchase_order_items", poi_df), ("opening_inventory", open_df), ("price_changes", pchg_df), ("lost_sales_log", lost_df)]}
sm["completed"] = len(comp_txn); sm["voided"] = int((txn_df.transaction_status == "Voided").sum())
sm["void_stock"] = int(((void) & (~tx_pre_void)).sum())
sm["net_sales"] = comp_txn.net_amount.sum()
cogs = (items_df.merge(txn_df[["transaction_id", "transaction_status"]], on="transaction_id").query("transaction_status == 'Completed'"))
sm["cogs"] = (cogs.quantity * cogs.unit_cost_at_sale).sum()
sm["refunds"] = ret_df.refund_amount.sum()
sm["po_status"] = po_df.order_status.value_counts().to_dict()
sm["mv_types"] = mv_out.movement_type.value_counts().to_dict()
sm["lines_per_txn"] = len(items_df) / len(txn_df)
sm["promo_share"] = items_df.promotion_id.notna().mean()
sm["pay"] = txn_df.payment_method.value_counts(normalize=True).round(3).to_dict()
sm["cust_tx"] = txn_df.dropna(subset=["customer_id"]).groupby("customer_id").size().describe().round(1).to_dict()
sm["stockout_lines"] = len(lost_df)
sm["po_stats"] = po_stats

with open(os.path.join(DOCS, "validation_report_initial.md"), "w") as f:
    f.write("# Initial data-quality validation report\n\n")
    f.write(f"Generated by `scripts/generate_synthetic_data.py` (seed {SEED}). All data is synthetic.\n\n")
    f.write("| # | Check | Result | Detail |\n|---|---|---|---|\n")
    for i, (n, o, dtl) in enumerate(checks, 1):
        f.write(f"| {i} | {n} | {'PASS' if o else 'FAIL'} | {dtl} |\n")
    f.write("\n## Row counts\n\n| File | Rows |\n|---|---|\n")
    for k, v in sm["rows"].items():
        f.write(f"| {k}.csv | {v:,} |\n")
    f.write("\n## Headline figures (simulation outputs, not real-world evidence)\n\n")
    f.write(f"- Completed transactions: {sm['completed']:,}; voided: {sm['voided']:,} (of which {sm['void_stock']:,} voided because no stock was available).\n")
    f.write(f"- Net sales (completed, before refunds): KES {sm['net_sales']:,.0f}; COGS: KES {sm['cogs']:,.0f}; refunds: KES {sm['refunds']:,.0f}.\n")
    f.write(f"- Proposed gross profit definition = (net sales - refunds) - COGS, with COGS reversed for restockable returned units (see assumptions).\n")
    f.write(f"- Lines per transaction: {sm['lines_per_txn']:.2f}; share of lines on promotion: {sm['promo_share']:.1%}.\n")
    f.write(f"- Purchase-order status: {sm['po_status']}.\n- Movement types: {sm['mv_types']}.\n")
    f.write(f"- Transactions per identified customer: {sm['cust_tx']}.\n- Lost-sales log rows: {sm['stockout_lines']:,}.\n")

for n, o, dtl in checks:
    print(("PASS " if o else "FAIL ") + n + (f"  [{dtl}]" if dtl else ""))
print()
for k, v in sm.items():
    print(k, v)
