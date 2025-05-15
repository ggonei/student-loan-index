import re

def parse_file(period):
    data = {}
    with open(period + ".data", 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                country = parts[0]
                threshold = parts[3]
                amount = parts[4]
                data[country] = {
                    f"threshold_{period}": threshold,
                    f"amount_{period}": amount
                }
    return data

def parse_money(money_str):
    """Convert currency like '£12,345.67' to 12345.67"""
    money_str = money_str.replace(',', '')  # Remove commas
    match = re.search(r'([\d.]+)', money_str)
    return float(match.group(1)) if match else 0.0

def percent_increase(values):
    try:
        t1 = parse_money(values['threshold_2425'])
        t2 = parse_money(values['threshold_2526'])
        if t1 == 0:
            return float('inf')
        return ((t2 - t1) / t1) * 100
    except KeyError:
        return float('-inf')

# Load both files
data_2425 = parse_file("2425")
data_2526 = parse_file("2526")

# Combine into a single mapping by country
combined = data_2425
for country, values in data_2526.items():
    if country not in combined:
        combined[country] = {}
    combined[country].update(values)

big_mac_change = {}
with open("bm2425.data", "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 3:
            country = " ".join(parts[:-2])
            change = float(parts[-1])
            big_mac_change[country] = change

# Print differences
print(f"{'Rank':<5} {'Country':<40} {'ΔThreshold':>10} {'Δ% Threshold':>13} {'2526 vs UK%':>14} {'Δ Amount':>12} {'BM Δ%':>10}")
print("-" * 80)

for i, (country, values) in enumerate(sorted(combined.items(), key=lambda item: percent_increase(item[1])), start=1):
    try:
        t1 = parse_money(values['threshold_2425'])
        t2 = parse_money(values['threshold_2526'])
        a1 = parse_money(values['amount_2425'])
        a2 = parse_money(values['amount_2526'])
        dt = t2 - t1
        pct_thresh = ((t2 - t1) / t1) * 100 if t1 != 0 else float('inf')
        pct_vs_uk = (t2 / 26065) * 100
        da = a2 - a1
        bm_pct = big_mac_change.get(country, '')
        print(f"{i:<5} {country:<40} {dt:10.2f} {pct_thresh:13.2f} {pct_vs_uk:14.2f} {da:12.2f} {str(bm_pct):>10}")
    except KeyError:
        print(f"{country} not in both sets")


#ChatGPT, thanks
big_mac_countries = []
for country, bm_pct in big_mac_change.items():
    if country in combined:
        values = combined[country]
        try:
            t2 = parse_money(values['threshold_2526'])
            pct_vs_uk = (t2 / 26065) * 100 if t2 else float('-inf')
            big_mac_countries.append((country, bm_pct, pct_vs_uk))
        except KeyError:
            pass

# Sort by Big Mac % change, then by pct_vs_uk
big_mac_countries.sort(key=lambda x: (x[1], x[2]))

print("=== Big Mac Countries Sorted by BM % Change and 2526 vs UK% ===")
print(f"{'Rank':<5} {'Country':<40} {'BM Δ%':>10} {'2526 vs UK%':>12}")
print("-" * 70)
for i, (country, bm_pct, pct_vs_uk) in enumerate(big_mac_countries, start=1):
    print(f"{i:<5} {country:<40} {bm_pct:10.2f} {pct_vs_uk:12.2f}")


from countryplotter import FlagScatterPlot

plotter = FlagScatterPlot()
plotter.plot(big_mac_countries, title="Big Mac Index vs UK-relative Thresholds")

