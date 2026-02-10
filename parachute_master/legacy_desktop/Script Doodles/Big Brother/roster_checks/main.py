import csv
from datetime import datetime, timedelta, date
from collections import defaultdict

# --- Load source data ---
schedules = []
with open('input.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            start = datetime.strptime(row['Schedule Start Time'].strip(), '%m/%d/%Y %H:%M')
            end = datetime.strptime(row['Schedule End Time'].strip(), '%m/%d/%Y %H:%M')
            schedules.append((start, end))
        except (ValueError, KeyError):
            continue

print(f"Loaded {len(schedules)} valid schedules")

# --- Define probes ---
# Each probe: (shift_type, hour_offset, period, next_day, label)
probes = []

# Day shift: 7:30 through 18:30
for h in range(7, 19):
    offset_minutes = h * 60 + 30
    if h + 0.5 < 10.5:
        period = "P1"
    elif h + 0.5 < 14:
        period = "P2"
    elif h + 0.5 < 17.5:
        period = "P3"
    else:
        period = "Transition"
    
    t = datetime(2000, 1, 1, h, 30)
    label = t.strftime('%I:%M %p').lstrip('0')
    probes.append(("Day", h, 30, period, False, label))

# Night shift: 19:30 through 6:30 (next day for hours 0-6)
for i in range(12):
    h = (19 + i) % 24
    next_day = h < 12
    
    if 19 <= h or h >= 19:
        raw = h + 0.5
    else:
        raw = h + 0.5
    
    # For period assignment, think in terms of the actual hour
    if h >= 19 and h + 0.5 < 22.5:
        period = "P1"
    elif h >= 22 or h < 2:
        # 22:30, 23:30, 0:30, 1:30
        if h >= 22 and h + 0.5 >= 22.5:
            period = "P2"
        elif h < 2:
            period = "P2"
        else:
            period = "P1"
    elif h >= 2 and h + 0.5 < 5.5:
        period = "P3"
    else:
        period = "Transition"
    
    t = datetime(2000, 1, 1, h, 30)
    label = t.strftime('%I:%M %p').lstrip('0')
    probes.append(("Night", h, 30, period, next_day, label))

# --- Find date range ---
min_date = min(s[0].date() for s in schedules)
max_date = max(s[1].date() for s in schedules)
print(f"Date range: {min_date} to {max_date}")

# --- Generate report ---
results = []
current = min_date
while current <= max_date:
    for shift_type, hour, minute, period, next_day, label in probes:
        if next_day:
            probe_dt = datetime(current.year, current.month, current.day, hour, minute) + timedelta(days=1)
        else:
            probe_dt = datetime(current.year, current.month, current.day, hour, minute)
        
        hc = sum(1 for s in schedules if s[0] <= probe_dt and s[1] > probe_dt)
        results.append((current.strftime('%m/%d/%Y'), shift_type, label, period, hc))
    
    current += timedelta(days=1)

# --- Write output ---
with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Shift Date', 'Shift', 'Hour', 'Period', 'Scheduled HC'])
    for r in results:
        writer.writerow(r)

print(f"Wrote {len(results)} rows to output.csv")

# --- Quick validation ---
print("\n--- 2/8 Day shift ---")
for r in results:
    if r[0] == '02/08/2026' and r[1] == 'Day':
        print(f"  {r[2]:>10}  {r[3]:>12}  HC={r[4]}")

print("\n--- 2/8 Night shift ---")
for r in results:
    if r[0] == '02/08/2026' and r[1] == 'Night':
        print(f"  {r[2]:>10}  {r[3]:>12}  HC={r[4]}")