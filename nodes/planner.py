from datetime import datetime,timedelta,timezone
from state import NewsLetterState
async def planner_node(state:NewsLetterState)->dict:
    now=datetime.now(timezone.utc)
    start=now-timedelta(hours=24)
    return {
        "date":now.date().isoformat(),
        "time_window":(
            f"{start.isoformat()} to {now.isoformat()}"
        ),
        "progress":[
            "planner:initialized 24 hours research window"
        ],
    }