#!/usr/bin/env python3
"""
Pharmacy Customer and Sales Intelligence System - synthetic data generator.

Generates a fully SYNTHETIC, internally consistent set of relational CSV files for a
simulated 12-branch Kenyan pharmacy retailer for 1 Jan - 31 Dec 2025.

Run:  python script/generate_synthetic_data.py             (writes into the repo root)
Seed: SEED below (change it and every file changes; keep it and output is identical).

Nothing here is real sales data. Product NAMES are real generic medicine / supply names
(provenance still to be verified against a documented source); prices, costs, customers,
transactions, stock and purchasing are simulated.
"""
import os, sys, math
from collections import defaultdict
