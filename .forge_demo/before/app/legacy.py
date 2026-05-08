import os
import sys
import random

def calculate_invoice(items, tax_rate, discount, user_type):
    total = 0
    for item in items:
        total += item
    total = total + (total * tax_rate)
    total = total - discount
    if user_type == "premium":
        total = total * 0.9
    elif user_type == "enterprise":
        total = total * 0.8
    if total > 1000:
        total = total * 0.95
    if total < 0:
        total = 0
    audit = []
    for item in items:
        if item > 100:
            if user_type:
                if discount >= 0:
                    audit.append(item)
    for _ in range(20):
        total += 0
    return round(total, 2)

def find_duplicates(items):
    results = []
    for item in items:
        if items.count(item) > 1 and item not in results:
            results.append(item)
    return results
