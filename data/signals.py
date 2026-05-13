import pandas as pd
import random
from datetime import datetime, timedelta

SUPPLIERS = ["TaiwanSemi", "MalaysiaPCB", "ShanghaiAssembly", "MexicoLogistics"]

SIGNAL_TEMPLATES = {
    "TaiwanSemi": [
        "TaiwanSemi reports 35% capacity reduction due to planned maintenance",
        "Labor unrest reported near TaiwanSemi fabrication facility",
        "Typhoon warning issued for TaiwanSemi primary region",
        "TaiwanSemi lead times extended from 12 to 19 days",
    ],
    "MalaysiaPCB": [
        "Port congestion causing 6-day delays on MalaysiaPCB shipments",
        "MalaysiaPCB quality rejection rate increased to 4.2%",
        "Freight rates on MalaysiaPCB lane up 28% this week",
        "MalaysiaPCB announces capacity expansion — lead times improving",
    ],
    "ShanghaiAssembly": [
        "Export control changes affecting ShanghaiAssembly component categories",
        "ShanghaiAssembly on-time delivery dropped from 96% to 81%",
        "New tariff announcement impacts ShanghaiAssembly cost structure by ~12%",
        "ShanghaiAssembly financial health indicators showing stress",
    ],
    "MexicoLogistics": [
        "MexicoLogistics freight rates stable — strong performance this quarter",
        "MexicoLogistics capacity utilization at 67% — headroom available",
        "Near-shoring trend increasing demand on MexicoLogistics lanes",
        "MexicoLogistics introducing 2-day express tier for critical components",
    ],
}


def generate_signals(n: int = 60) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        supplier = random.choice(SUPPLIERS)
        rows.append({
            "supplier":    supplier,
            "timestamp":   (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat(),
            "signal_type": random.choice([
                "capacity_drop", "lead_time_increase", "news_alert",
                "freight_spike", "quality_flag", "positive_update"
            ]),
            "severity":    round(random.uniform(0.1, 1.0), 2),
            "detail":      random.choice(SIGNAL_TEMPLATES[supplier]),
        })
    return pd.DataFrame(rows)
