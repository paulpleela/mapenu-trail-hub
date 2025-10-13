# 🏔️ Hills Counting Algorithm Documentation

## Overview

The `count_rolling_hills()` function intelligently counts the number of distinct "hills" in a trail's elevation profile by identifying peaks and valleys.

## Algorithm Explanation

### What is a "Hill"?

A hill is defined as **either a peak OR a valley** in the elevation profile:

- **Peak**: A point higher than both its neighbors (⛰️)
- **Valley**: A point lower than both its neighbors (🏞️)

Each peak or valley represents a change in terrain direction, which is what makes a trail "rolling" or "bumpy."

### Step-by-Step Process

1. **Iterate through elevation data** (excluding first and last points)
2. **For each point, check if it's a local extremum**:
   - Is it higher than BOTH neighbors? → Peak candidate
   - Is it lower than BOTH neighbors? → Valley candidate
3. **Apply significance filter** (3m minimum prominence):
   - Only count peaks/valleys with at least 3m elevation difference
   - This filters out GPS noise and minor variations
4. **Sum total**: `total_hills = peaks + valleys`

### Example

```
Elevation Profile:
100m → 110m → 105m → 115m → 100m → 95m → 105m
  ↗    ⛰️     ↘     ⛰️     ↘    🏞️    ↗

Points analyzed:
- 110m: Peak (110 > 100 AND 110 > 105) ✅ +1
- 105m: Neither (105 > 100 but 105 < 115) ❌
- 115m: Peak (115 > 105 AND 115 > 100) ✅ +1
- 100m: Neither (100 < 115 but 100 > 95) ❌
- 95m: Valley (95 < 100 AND 95 < 105) ✅ +1

Total Hills = 3 (2 peaks + 1 valley)
```

## Key Parameters

### `min_prominence = 3` meters

This threshold filters out minor variations caused by:

- GPS inaccuracies
- Small rocks or bumps
- Signal noise

**Why 3 meters?**

- GPS elevation accuracy: ±3-5 meters
- Human perception: 3m is noticeable when hiking
- Filters noise while keeping meaningful terrain features

## Comparison: Old vs New Algorithm

### Old Algorithm (Simple)

```python
# Counted EVERY elevation change ≥ 1m
for i in range(1, len(elevations)):
    if abs(elevations[i] - elevations[i-1]) >= 1:
        count += 1
```

**Problem**: A single hill with 10 data points = 10 "hills" ❌

### New Algorithm (Smart)

```python
# Counts distinct peaks and valleys ≥ 3m
- Identifies actual terrain features
- Groups consecutive changes into single hills
- Filters GPS noise
```

**Result**: A single hill = 1 peak or 1 valley ✅

## Expected Results

For your trails:

- **Scorpion-Track**: ~12-20 hills (shorter trail with moderate rolling)
- **43-Mt-Coot-Tha**: ~30-50 hills (longer trail with consistent elevation changes)
- **375-Botanic-Gardens**: ~25-40 hills (moderate length, rolling terrain)
- **Trail 1 & 2**: ~15-35 hills (varies by terrain characteristics)

These numbers are much more realistic than the previous 24-106 range, which counted every tiny GPS variation.

## Code Location

### Main Implementation

`backend/main.py` - lines ~88-145

- `count_rolling_hills(elevations)` - Peak/valley detection
- `analyze_rolling_hills(elevations, distances)` - Full analysis including index

### Database Update Script

`backend/update_database.py` - lines ~16-95

- Same algorithm for recalculating existing trails

## Usage

The function is called automatically when:

1. **Uploading a new GPX file** → Calculates and saves both index and count
2. **Running update script** → Recalculates for all existing trails

## Technical Notes

### Time Complexity

- **O(n)** where n = number of elevation points
- Single pass through elevation data
- Very efficient for typical GPX files (100-10,000 points)

### Edge Cases Handled

- ✅ Less than 3 elevation points → returns 0
- ✅ Flat terrain (no peaks/valleys) → returns 0
- ✅ Monotonic (only up or only down) → returns 0
- ✅ All changes < 3m → returns 0 (noise filtered)

### Integration with Rolling Hills Index

The **count** and **index** serve different purposes:

| Metric            | Purpose                           | Range                | User Value                                    |
| ----------------- | --------------------------------- | -------------------- | --------------------------------------------- |
| **Hills Count**   | How many distinct ups/downs       | 0-100+               | "This trail has 23 hills to climb"            |
| **Rolling Index** | How intense/tiring the rolling is | 0-∞ (typically 0-50) | Calculation input (displayed normalized 0-10) |

Both are calculated together in `analyze_rolling_hills()` for efficiency.

## Future Enhancements

Potential improvements:

1. **Adjustable prominence threshold** (let users set 2m, 3m, or 5m)
2. **Separate peak/valley counts** ("15 climbs, 14 descents")
3. **Categorize by size** ("5 small hills, 3 major climbs")
4. **Elevation gain per hill** (average climb height)

## Testing

To test the algorithm with debug output:

```bash
cd /Users/yokurawee/Documents/MAPENU/backend
# Upload a GPX file and check terminal for:
🔍 Rolling Hills Debug:
   - Actual hills (peaks + valleys): 23
   - Significant elevation changes: 156
   - Total distance: 5.32 km
   ...
```

The "actual hills" number is what's displayed to users.
