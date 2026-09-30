""" 
AI Lotto Smart App 
 
Statistical analysis and weighted number generation 
based on historical lottery draws. 
 
Note: Lottery draws are independent random events. 
No statistical model can predict future draws. 
This tool is for data exploration and education only. 
""" 
 
import pandas as pd 
import random 
from collections import Counter 
 
 
# --------------------------------------------------------------------- 
# Configuration 
# --------------------------------------------------------------------- 
 
DATA_FILE = "lotto_data.csv" 
MAX_NUMBER = 50 
PICK_COUNT = 6 
OVERDUE_BONUS = 0.5 
NUM_SETS = 3

# --------------------------------------------------------------------- 
# Data loading 
# --------------------------------------------------------------------- 
 
def load_data(path=DATA_FILE): 
    """Read historical draws from CSV and sort by date.""" 
    df = pd.read_csv(path) 
    df["date"] = pd.to_datetime(df["date"]) 
    df = df.sort_values("date").reset_index(drop=True) 
 
    ball_cols = [c for c in df.columns if c.startswith("num")] 
    if len(ball_cols) != 6: 
        raise ValueError("CSV must contain columns num1 through num6") 
 
    return df 

# --------------------------------------------------------------------- 
# Analysis 
# --------------------------------------------------------------------- 
 
def compute_frequency(df, max_number=MAX_NUMBER): 
    """Count appearances of each number across all draws.""" 
    ball_cols = [c for c in df.columns if c.startswith("num")] 
    values = df[ball_cols].values.flatten().tolist() 
 
    freq = Counter(values) 
    for n in range(1, max_number + 1): 
        freq.setdefault(n, 0) 
 
    return dict(freq) 
 
 
def compute_overdue(df, max_number=MAX_NUMBER): 
    """Count draws since each number last appeared.""" 
    ball_cols = [c for c in df.columns if c.startswith("num")] 
    total = len(df) 
    overdue = {} 
 
    for n in range(1, max_number + 1): 
        last_index = -1 
        for idx, row in df.iterrows(): 
            if n in row[ball_cols].values: 
                last_index = idx 
        overdue[n] = total if last_index == -1 else total - 1 - last_index 
 
    return overdue 
 
 
def rank_numbers(freq, top=5): 
    """Return the most and least frequent numbers.""" 
    ordered = sorted(freq.items(), key=lambda item: item[1], reverse=True) 
    hot = ordered[:top] 
    cold = ordered[-top:] 
    return hot, cold 

# --------------------------------------------------------------------- 
# Weighting and generation 
# --------------------------------------------------------------------- 
 
def build_weights(freq, overdue, max_number=MAX_NUMBER, bonus=OVERDUE_BONUS): 
    """ 
    Assign each number a selection weight. 
 
    weight = appearances + (draws_since_last_seen * bonus) + base 
    """ 
    weights = [] 
    for n in range(1, max_number + 1): 
        appearances = freq.get(n, 0) 
        draws_since = overdue.get(n, 0) 
        weight = appearances + draws_since * bonus + 0.1 
        weights.append((n, weight, appearances, draws_since)) 
    return weights 
 
 
def draw_weighted(weights, count=PICK_COUNT): 
    """Select unique numbers using weighted sampling without replacement.""" 
    pool = list(weights) 
    chosen = [] 
 
    while len(chosen) < count and pool: 
        total = sum(w for _, w, _, _ in pool) 
        threshold = random.random() * total 
        running = 0.0 
        selected = pool[0] 
 
        for item in pool: 
            running += item[1] 
            if threshold <= running: 
                selected = item 
                break 
 
        chosen.append(selected) 
        pool.remove(selected) 
 
    return sorted(chosen, key=lambda item: item[0]) 



# --------------------------------------------------------------------- 
# Reporting 
# --------------------------------------------------------------------- 
 
def report_header(): 
    print("=" * 60) 
    print("AI Lotto Smart App") 
    print("Statistical analysis and weighted number generation") 
    print("=" * 60) 
 
 
def report_data_range(df): 
    start = df["date"].min().date() 
    end = df["date"].max().date() 
    print() 
    print("Draws loaded :", len(df)) 
    print("Date range   :", start, "to", end) 
 
 
def report_frequency(freq, overdue): 
    hot, cold = rank_numbers(freq, top=5) 
    most_overdue = sorted(overdue.items(), key=lambda item: item[1], reverse=True)[:5] 
 
    print() 
    print("Frequency analysis (numbers 1 to 50)") 
    print("  Most frequent :", ", ".join(f"{n} ({c}x)" for n, c in hot)) 
    print("  Least frequent:", ", ".join(f"{n} ({c}x)" for n, c in cold)) 
    print("  Most overdue  :", ", ".join(f"{n} ({d} draws)" for n, d in most_overdue)) 
 
 
def report_sets(weights, num_sets=NUM_SETS, count=PICK_COUNT): 
    print() 
    print("Generated sets") 
 
    first_set = None 
    for i in range(num_sets): 
        picks = draw_weighted(weights, count=count) 
        if i == 0: 
            first_set = picks 
 
        numbers = [item[0] for item in picks] 
        odds = sum(1 for n in numbers if n % 2 == 1) 
        evens = len(numbers) - odds 
        line = "  ".join(f"{n:2d}" for n in numbers) 
        print(f"  Set {i + 1}: {line}   (odd/even: {odds}/{evens})") 
 
    print() 
    print("Selection detail for Set 1") 
    for number, weight, appearances, draws_since in first_set: 
        print( 
            f"  {number:2d}  appearances={appearances}  " 
            f"draws_since_last={draws_since}  weight={weight:.2f}" 
        ) 
 
 
def report_footer(): 
    print() 
    print("-" * 60) 
    print("This output is a weighted heuristic, not a prediction.") 
    print("Lottery draws are independent random events.") 



# --------------------------------------------------------------------- 
# Entry point 
# --------------------------------------------------------------------- 
 
def main(): 
    report_header() 
 
    try: 
        df = load_data(DATA_FILE) 
    except FileNotFoundError: 
        print() 
        print(f"Error: {DATA_FILE} not found in the current directory.") 
        return 
    except ValueError as err: 
        print() 
        print(f"Error: {err}") 
        return 
 
    freq = compute_frequency(df) 
    overdue = compute_overdue(df) 
    weights = build_weights(freq, overdue) 
 
    report_data_range(df) 
    report_frequency(freq, overdue) 
    report_sets(weights) 
    report_footer() 
 
 
if __name__ == "__main__": 
    main() 