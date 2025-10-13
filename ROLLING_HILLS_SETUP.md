# 🚀 Rolling Hills Count Feature - Setup Guide

## What's Been Done

✅ **Backend Changes:**

- Modified `analyze_rolling_hills()` to return both index and count
- Updated `upload_gpx` endpoint to save `rolling_hills_count`
- Added debug output for hills count
- Updated database update script

✅ **Frontend Changes:**

- Added normalization function for Rolling Intensity display (0-10 scale)
- Added new "Hills Count" metric card
- Updated all Rolling Intensity displays to show normalized values

✅ **Database Migration:**

- Created SQL migration file to add `rolling_hills_count` column

## ⚠️ Action Required: Add Database Column

You need to add the `rolling_hills_count` column to your Supabase database:

### Option 1: Using Supabase Dashboard (Recommended)

1. Go to https://supabase.com/dashboard
2. Select your MAPENU project
3. Click on "SQL Editor" in the left sidebar
4. Click "New Query"
5. Paste this SQL:

```sql
ALTER TABLE trails
ADD COLUMN IF NOT EXISTS rolling_hills_count INTEGER DEFAULT 0;

COMMENT ON COLUMN trails.rolling_hills_count IS 'Number of significant elevation changes (1m+ threshold) detected in the trail';
```

6. Click "Run" or press Cmd+Enter
7. You should see "Success. No rows returned"

### Option 2: Using Supabase CLI

If you have Supabase CLI installed:

```bash
cd /Users/yokurawee/Documents/MAPENU/backend
supabase db execute -f add_rolling_hills_count_column.sql
```

## 🔄 After Adding the Column

Once the column is added, run the update script to populate it for existing trails:

```bash
cd /Users/yokurawee/Documents/MAPENU/backend
python3 update_database.py
```

This will:

- Recalculate rolling hills index for all trails (no change expected)
- **Add the hills count** for each trail (NEW!)
- Recalculate technical difficulty (should remain 10/10 for your trails)

Expected output:

```
Processing: Scorpion-Track (ID: 41)
  📊 Rolling Hills: 19.05 → 19.05
  📈 Rolling Hills Count: 24 hills
  🏔️  Technical Difficulty: 10 → 10
  ✅ Updated successfully
```

## 📊 What You'll See

After completing the above steps and refreshing your frontend:

1. **Rolling Intensity** - Now shows normalized 0-10 scale:

   - Your trail with index 36.23 will show as ~9.8/10
   - Your trail with index 19.05 will show as ~7.6/10
   - Your trail with index 14.99 will show as ~6.7/10

2. **Hills Count** - New metric showing raw numbers:

   - Scorpion-Track: 24 hills
   - 43-Mt-Coot-Tha: 106 hills
   - 375-Botanic-Gardens: 90 hills
   - Trail 1: 38 hills
   - Trail 2: 32 hills

3. **Technical Difficulty** - Remains at 10/10 (your trails are genuinely very technical!)

## 🧮 How It Works

### Rolling Intensity (Normalized Display)

- **Raw Index**: Calculated as `0.6 × (hills_per_km) + 0.4 × (avg_hill_size/20)`
- **Display**: Normalized using logarithmic scale to map to 0-10
- Formula: `10 × (1 - e^(-rawIndex/15))`
- This prevents values like 362.3/10 and gives meaningful 0-10 ratings

### Hills Count

- Counts every elevation change ≥ 1 meter
- Simple, easy to understand metric
- Shows actual "bumpiness" of the trail

## 🐛 Troubleshooting

**If you see "Could not find the 'rolling_hills_count' column":**

- The column hasn't been added yet - run the SQL migration first

**If Rolling Intensity still shows >10:**

- Refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for errors

**If Hills Count shows 0:**

- Make sure you ran the update_database.py script AFTER adding the column

## Next Steps

1. Add the database column (see above)
2. Run the update script
3. Refresh your frontend
4. Upload new trails to test (they'll automatically get both metrics)
