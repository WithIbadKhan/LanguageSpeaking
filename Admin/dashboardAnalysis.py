from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from collections import defaultdict
import os
import logging

# Database setup
MONGO_URI = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(MONGO_URI)
db = client['CEFRL']

logging.basicConfig(level=logging.INFO)

DashboardData = APIRouter()

@DashboardData.get("/dashboard-data", response_model=dict)
async def get_dashboard_data():
    try:
        # 1. Get session traffic data (sessions per day from conversations collection)
        conversations = await db['conversations'].find({}, {"created_at": 1, "session_id": 1}).to_list(1000)  # Limiting to 1000 sessions for now
        session_count_by_date = defaultdict(int)
        for conversation in conversations:
            if "created_at" in conversation:
                session_date = conversation["created_at"].strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
                session_count_by_date[session_date] += 1
        
        session_traffic_data = [{"date": date, "session_count": count} for date, count in sorted(session_count_by_date.items())]

        # 2. Total tests started
        total_tests_started = len(conversations)

        # 3. Total tests completed (session_id exists in results)
        completed_sessions = await db['results'].distinct("session_id")  # Get all unique session_ids in results
        total_tests_completed = await db['conversations'].count_documents({
            "session_id": {"$in": completed_sessions}
        })

        # 4. Average test duration (assuming you have a field like 'duration_in_seconds' in results)
        durations = await db['results'].find({}, {"duration_in_seconds": 1}).to_list(1000)
        total_duration = sum(item.get('duration_in_seconds', 0) for item in durations)
        average_test_duration = total_duration // len(durations) if durations else 0  # Avoid division by zero

        # 5. Get the average user level from `results` collection based on 'Overall Score'
        results = await db['results'].find({}, {"result.Overall Score": 1}).to_list(1000)
        level_map = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
        total_levels = 0
        total_tests_with_levels = 0
        for result in results:
            overall_score = result.get("result", {}).get("Overall Score", None)
            if overall_score and overall_score in level_map:
                total_levels += level_map[overall_score]
                total_tests_with_levels += 1

        average_user_level = None
        if total_tests_with_levels > 0:
            average_user_level = round(total_levels / total_tests_with_levels)

        # Mapping back to levels (e.g., 1 -> A1, 2 -> A2, etc.)
        reverse_level_map = {v: k for k, v in level_map.items()}
        average_user_level_label = reverse_level_map.get(average_user_level, "N/A")

        # 6. Prepare and return the dashboard data
        return {
            "session_traffic_data": session_traffic_data,
            "total_tests_started": total_tests_started,
            "total_tests_completed": total_tests_completed,
            "average_test_duration": f"{average_test_duration // 60} min",  # Convert seconds to minutes
            "average_user_level": average_user_level_label  # Label like 'B2'
        }

    except Exception as e:
        logging.error(f"An error occurred while fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching dashboard data: {e}")
