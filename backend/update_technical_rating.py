#!/usr/bin/env python3
"""
Update technical rating calculation for all existing trails in the database.
This fixes the issue where all trails were showing 10/10 technical rating.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY") 
supabase: Client = create_client(supabase_url, supabase_key)

def calculate_technical_rating(max_slope, avg_slope, rolling_hills_index):
    """
    Calculate technical rating using the new fixed formula.
    Returns a value between 1-10.
    """
    # Handle None values
    max_slope = max_slope or 0
    avg_slope = avg_slope or 0 
    rolling_hills_index = rolling_hills_index or 0
    
    # Fixed technical difficulty calculation (1-10 scale)
    # Factors: max slope (40%), rolling hills (35%), avg slope (25%)
    technical_rating = round(
        max(
            1.0,
            min(
                10.0,
                1 + (max_slope / 100) * 3.5  # Max slope: 0-100% -> 0-3.5 points
                + (min(rolling_hills_index / 50, 1.0) * 3.5)  # Rolling hills normalized: 0-50 -> 0-3.5 points  
                + (avg_slope / 30) * 2.0  # Avg slope: 0-30% -> 0-2 points
            ),
        ),
    )
    
    return technical_rating

def update_all_technical_ratings():
    """Update technical ratings for all trails in the database."""
    
    print("🔄 Fetching all trails from database...")
    
    # Fetch all trails
    response = supabase.table('trails').select('*').execute()
    trails = response.data
    
    print(f"📊 Found {len(trails)} trails to update")
    print("=" * 80)
    
    updated_count = 0
    
    for trail in trails:
        trail_id = trail['id']
        name = trail['name']
        max_slope = trail.get('max_slope')
        avg_slope = trail.get('avg_slope')  
        rolling_hills_index = trail.get('rolling_hills_index')
        old_rating = trail.get('technical_rating')
        
        # Calculate new technical rating
        new_rating = calculate_technical_rating(max_slope, avg_slope, rolling_hills_index)
        
        # Update in database
        update_response = supabase.table('trails').update({
            'technical_rating': new_rating
        }).eq('id', trail_id).execute()
        
        if update_response.data:
            updated_count += 1
            print(f"✅ {name[:30]:30} | Old: {old_rating:2}/10 -> New: {new_rating:2}/10")
            print(f"   {'':30} | Max slope: {max_slope:.1f}% | Avg slope: {avg_slope:.1f}% | Rolling: {rolling_hills_index:.1f}")
            print()
        else:
            print(f"❌ Failed to update {name}")
    
    print("=" * 80)
    print(f"🎉 Successfully updated {updated_count} trails!")
    
    # Show summary of new ratings
    print("\n📈 Technical Rating Distribution:")
    print("-" * 40)
    
    # Fetch updated trails
    response = supabase.table('trails').select('name, technical_rating').execute()
    updated_trails = response.data
    
    # Group by rating
    rating_counts = {}
    for trail in updated_trails:
        rating = trail['technical_rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    for rating in sorted(rating_counts.keys()):
        count = rating_counts[rating]
        print(f"Rating {rating}/10: {count} trail{'s' if count != 1 else ''}")

if __name__ == "__main__":
    print("🚀 Starting technical rating recalculation...")
    print("This will update all trails with the new technical rating formula.")
    print()
    
    try:
        update_all_technical_ratings()
        print("\n✨ Technical rating update completed successfully!")
    except Exception as e:
        print(f"\n💥 Error occurred: {e}")
        import traceback
        traceback.print_exc()