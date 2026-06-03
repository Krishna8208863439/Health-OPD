import sqlite3
from datetime import datetime, timedelta
from collections import Counter
import json

class AnalyticsEngine:
    def __init__(self):
        self.conn = sqlite3.connect("healthcare.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def get_statistics(self):
        """Get overall statistics for dashboard"""
        cur = self.conn.cursor()
        
        # Total patients
        total_patients = cur.execute("SELECT COUNT(*) as count FROM users WHERE role='patient'").fetchone()['count']
        
        # Total predictions
        total_predictions = cur.execute("SELECT COUNT(*) as count FROM predictions").fetchone()['count']
        
        # Recent predictions (last 10)
        recent = cur.execute("""
            SELECT p.*, u.full_name, u.age 
            FROM predictions p
            JOIN users u ON p.patient_id = u.id
            ORDER BY p.timestamp DESC
            LIMIT 10
        """).fetchall()
        
        # Disease distribution
        diseases = cur.execute("SELECT disease, COUNT(*) as count FROM predictions GROUP BY disease").fetchall()
        disease_data = {row['disease']: row['count'] for row in diseases}
        
        # Severity distribution
        severity = cur.execute("SELECT severity, COUNT(*) as count FROM predictions GROUP BY severity").fetchall()
        severity_data = {row['severity']: row['count'] for row in severity}
        
        # Predictions over time (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        timeline = cur.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM predictions 
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (thirty_days_ago,)).fetchall()
        timeline_data = {row['date']: row['count'] for row in timeline}
        
        return {
            'total_patients': total_patients,
            'total_predictions': total_predictions,
            'recent_predictions': [dict(row) for row in recent],
            'disease_distribution': disease_data,
            'severity_distribution': severity_data,
            'timeline': timeline_data
        }
    
    def get_chart_data(self):
        """Get data formatted for charts"""
        stats = self.get_statistics()
        
        return {
            'disease_labels': list(stats['disease_distribution'].keys()),
            'disease_values': list(stats['disease_distribution'].values()),
            'severity_labels': list(stats['severity_distribution'].keys()),
            'severity_values': list(stats['severity_distribution'].values()),
            'timeline_labels': list(stats['timeline'].keys()),
            'timeline_values': list(stats['timeline'].values())
        }
