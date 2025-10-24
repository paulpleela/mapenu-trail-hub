"""
Trail management routes
Handles trail CRUD operations, analytics, and similar trail matching
"""
from fastapi import APIRouter, HTTPException
from database import supabase, supabase_service
from utils.calculations import calculate_trail_similarity

router = APIRouter()


@router.get("/trails")
async def get_trails():
    """
    Retrieve all trails from database with enhanced difficulty level correction.
    Applies consistent difficulty calculation based on distance, elevation gain, and rolling hills.
    """
    try:
        response = supabase.table("trails").select("*").execute()
        trails = response.data

        if not trails:
            return {"success": True, "trails": [], "count": 0}

        # Correct difficulty levels using consistent algorithm
        for trail in trails:
            distance = trail.get("distance", 0)
            elevation_gain = trail.get("elevation_gain", 0)
            rolling_hills_index = trail.get("rolling_hills_index", 0)

            # Recalculate difficulty score
            distance_factor = min(distance / 10, 1) * 3  # 0-3 points
            elevation_factor = min(elevation_gain / 1000, 1) * 4  # 0-4 points
            normalized_rolling = min(rolling_hills_index / 50, 1)
            rolling_factor = normalized_rolling * 3  # 0-3 points
            difficulty_score = distance_factor + elevation_factor + rolling_factor

            # Assign difficulty level
            if difficulty_score <= 3:
                difficulty_level = "Easy"
            elif difficulty_score <= 6:
                difficulty_level = "Moderate"
            elif difficulty_score <= 8:
                difficulty_level = "Hard"
            else:
                difficulty_level = "Extreme"

            trail["difficulty_level"] = difficulty_level
            trail["difficulty_score"] = round(difficulty_score, 1)

        return {"success": True, "trails": trails, "count": len(trails)}

    except Exception as e:
        print(f"Error fetching trails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trail/{trail_id}/similar")
async def get_similar_trails(trail_id: int, limit: int = 5):
    """
    Find trails similar to the given trail based on distance, elevation gain, and terrain features.
    Uses sophisticated similarity scoring algorithm.
    """
    try:
        # Get the target trail
        target_response = (
            supabase.table("trails").select("*").eq("id", trail_id).execute()
        )
        if not target_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")

        target_trail = target_response.data[0]

        # Get all other trails
        all_trails_response = (
            supabase.table("trails").select("*").neq("id", trail_id).execute()
        )
        all_trails = all_trails_response.data

        if not all_trails:
            return {
                "success": True,
                "similar_trails": [],
                "message": "No other trails available for comparison",
            }

        # Calculate similarity scores
        similarities = []
        for trail in all_trails:
            similarity_score = calculate_trail_similarity(target_trail, trail)
            similarities.append({"trail": trail, "similarity_score": similarity_score})

        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

        # Return top N similar trails
        similar_trails = similarities[:limit]

        return {
            "success": True,
            "target_trail": target_trail.get("name", "Unknown"),
            "similar_trails": similar_trails,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error finding similar trails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/overview")
async def get_analytics_overview():
    """
    Get aggregate statistics across all trails.
    Provides insights into total distance, elevation, difficulty distribution, etc.
    """
    try:
        response = supabase.table("trails").select("*").execute()
        trails = response.data

        if not trails:
            return {
                "success": True,
                "total_trails": 0,
                "total_distance_km": 0,
                "total_elevation_gain_m": 0,
                "difficulty_distribution": {},
                "average_distance_km": 0,
                "average_elevation_gain_m": 0,
            }

        # Calculate aggregate statistics
        total_distance = sum(trail.get("distance", 0) for trail in trails)
        total_elevation = sum(trail.get("elevation_gain", 0) for trail in trails)
        avg_difficulty = sum(
            trail.get("difficulty_score", 0) for trail in trails
        ) / len(trails)

        # Difficulty distribution
        difficulty_counts = {"Easy": 0, "Moderate": 0, "Hard": 0, "Extreme": 0}
        for trail in trails:
            level = trail.get("difficulty_level", "Unknown")
            if level in difficulty_counts:
                difficulty_counts[level] += 1

        # Distance categories
        distance_categories = {
            "Short (<5km)": 0,
            "Medium (5-15km)": 0,
            "Long (>15km)": 0,
        }
        for trail in trails:
            distance = trail.get("distance", 0)
            if distance < 5:
                distance_categories["Short (<5km)"] += 1
            elif distance <= 15:
                distance_categories["Medium (5-15km)"] += 1
            else:
                distance_categories["Long (>15km)"] += 1

        return {
            "success": True,
            "total_trails": len(trails),
            "total_distance_km": round(total_distance, 2),
            "total_elevation_gain_m": int(total_elevation),
            "difficulty_distribution": difficulty_counts,
            "distance_categories": distance_categories,
            "average_distance_km": round(total_distance / len(trails), 2),
            "average_elevation_gain_m": int(total_elevation / len(trails)),
            "avg_difficulty_score": round(avg_difficulty, 1),
            "most_challenging": max(
                trails, key=lambda t: t.get("difficulty_score", 0), default={}
            ),
            "longest_trail": max(
                trails, key=lambda t: t.get("distance", 0), default={}
            ),
            "steepest_trail": max(
                trails, key=lambda t: t.get("elevation_gain", 0), default={}
            ),
        }

    except Exception as e:
        print(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trail/{trail_id}/weather")
async def get_trail_weather(trail_id: int):
    """
    Get real-time weather data for a specific trail location.
    Uses trail's max elevation coordinates for weather API call.
    """
    try:
        # Get trail data
        trail_response = (
            supabase.table("trails").select("*").eq("id", trail_id).execute()
        )
        if not trail_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")

        trail = trail_response.data[0]
        coordinates = trail.get("coordinates", [])

        if not coordinates:
            raise HTTPException(
                status_code=400, detail="Trail has no coordinate data"
            )

        # Use midpoint of trail for weather
        mid_idx = len(coordinates) // 2
        lat, lon = coordinates[mid_idx]

        # TODO: Integrate with weather API (OpenWeather, etc.)
        # For now, return mock weather data
        mock_weather = {
            "success": True,
            "trail_id": trail_id,
            "trail_name": trail.get("name", "Unknown"),
            "location": {"latitude": lat, "longitude": lon},
            "current_weather": {
                "temperature_celsius": 22,
                "condition": "Partly Cloudy",
                "humidity_percent": 65,
                "wind_speed_kmh": 15,
                "visibility_km": 10,
            },
            "forecast": {
                "today": {"high": 25, "low": 18, "condition": "Sunny"},
                "tomorrow": {"high": 24, "low": 17, "condition": "Cloudy"},
            },
            "note": "Weather API integration pending. This is mock data.",
        }

        return mock_weather

    except HTTPException:
        raise
    except Exception as e:
        print(f"Weather error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/trail/{trail_id}")
async def delete_trail(trail_id: int):
    """
    Delete a trail and all associated LiDAR files

    Args:
        trail_id: ID of the trail to delete
    """
    try:
        print(f"🔍 Looking up trail with ID: {trail_id}")

        # Get trail info
        trail_response = (
            supabase.table("trails").select("*").eq("id", trail_id).execute()
        )
        if not trail_response.data:
            raise HTTPException(
                status_code=404, detail=f"Trail with ID {trail_id} not found"
            )

        trail = trail_response.data[0]
        trail_name = trail.get("name")

        print(f"📂 Found trail: {trail_name}")

        # Delete associated LiDAR files first
        lidar_files = (
            supabase.table("lidar_files").select("*").eq("trail_id", trail_id).execute()
        )
        deleted_lidar_count = 0

        if lidar_files.data:
            print(f"🗑️  Deleting {len(lidar_files.data)} associated LiDAR file(s)")
            for lidar_file in lidar_files.data:
                filename = lidar_file.get("filename")
                file_url = lidar_file.get("file_url")

                # Delete from storage if not a local file
                if file_url and not file_url.startswith("local://") and filename:
                    try:
                        supabase.storage.from_("lidar-files").remove([filename])
                        print(f"   ✅ Deleted from storage: {filename}")
                    except Exception as e:
                        print(f"   ⚠️  Could not delete from storage: {filename} - {e}")

                # Delete from database
                db_client = supabase_service if supabase_service else supabase
                db_client.table("lidar_files").delete().eq(
                    "id", lidar_file["id"]
                ).execute()
                deleted_lidar_count += 1

            print(f"   ✅ Deleted {deleted_lidar_count} LiDAR file(s)")

        # Delete the trail
        print(f"🗑️  Deleting trail: {trail_name}")
        db_client = supabase_service if supabase_service else supabase
        db_client.table("trails").delete().eq("id", trail_id).execute()
        print(f"✅ Trail deleted")

        # Reinitialize LiDAR extractor if files were deleted
        if deleted_lidar_count > 0:
            import app_state

            lidar_extractor = app_state.get_lidar_extractor()
            if lidar_extractor:
                lidar_extractor.lidar_files = lidar_extractor._find_lidar_files()
                print(f"🔄 LiDAR extractor reinitialized")

        return {
            "success": True,
            "message": f"Trail '{trail_name}' and {deleted_lidar_count} associated LiDAR file(s) deleted successfully",
            "deleted_trail": trail,
            "deleted_lidar_count": deleted_lidar_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting trail: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
