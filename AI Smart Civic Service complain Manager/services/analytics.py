class AnalyticsService:
    def __init__(self, db):
        self.db = db

    def overview(self):
        stats=self.db.stats()
        categories=self.db.complaint_counts_by_category()
        priorities=self.db.complaint_counts_by_priority()
        recent=self.db.recent_complaints(10)
        total=stats["total"]
        if not total:
            insight="No complaints yet. Submit a complaint or load demo data to populate the dashboard."
        else:
            top=categories[0]["category"] if categories and isinstance(categories[0],dict) else (categories[0][0] if categories else "Unknown")
            rate=round(stats["resolved"]/total*100,1)
            insight=f"{top} is the most reported category. {stats['critical']} critical complaint(s) need attention. Resolution rate: {rate}%."
        return {"stats":stats,"categories":categories,"priorities":priorities,"recent":recent,"insight":insight}

    def analytics(self):
        return {
            "stats": self.db.stats(),
            "departments": self.db.complaints_by_department(),
            "locations": self.db.complaints_by_location(),
            "days": self.db.complaints_by_day(),
            "resolution": self.db.resolution_by_category(),
            "categories": self.db.complaint_counts_by_category(),
            "priorities": self.db.complaint_counts_by_priority()
        }
