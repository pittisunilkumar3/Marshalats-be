#!/usr/bin/env python3
"""
Email Monitoring and Logging System
Provides monitoring, log        if success:
            self.stats['total_sent'] += 1
            self.stats['daily_stats'][today]['sent'] += 1
            email_logger.info(f"[SUCCESS] {email_type} email sent to {to_email}")
        else:
            self.stats['total_failed'] += 1
            self.stats['daily_stats'][today]['failed'] += 1
            email_logger.error(f"[FAILURE] {email_type} email failed to {to_email}: {error}")d diagnostic capabilities for email delivery
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Configure logging for email monitoring
email_logger = logging.getLogger('email_monitor')
email_logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent / 'email_logs'
logs_dir.mkdir(exist_ok=True)

# File handler for email logs
log_file = logs_dir / f'email_delivery_{datetime.now().strftime("%Y%m%d")}.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

email_logger.addHandler(file_handler)
email_logger.addHandler(console_handler)

class EmailMonitor:
    """Email monitoring and logging system"""
    
    def __init__(self):
        self.stats_file = logs_dir / 'email_stats.json'
        self.load_stats()
    
    def load_stats(self):
        """Load email statistics from file"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            else:
                self.stats = {
                    'total_sent': 0,
                    'total_failed': 0,
                    'password_resets': 0,
                    'last_reset': None,
                    'daily_stats': {},
                    'error_types': {}
                }
        except Exception as e:
            email_logger.error(f"Failed to load email stats: {e}")
            self.stats = {
                'total_sent': 0,
                'total_failed': 0,
                'password_resets': 0,
                'last_reset': None,
                'daily_stats': {},
                'error_types': {}
            }
    
    def save_stats(self):
        """Save email statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except Exception as e:
            email_logger.error(f"Failed to save email stats: {e}")
    
    def log_email_attempt(self, email_type: str, to_email: str, success: bool, error: Optional[str] = None):
        """Log an email sending attempt"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update daily stats
        if today not in self.stats['daily_stats']:
            self.stats['daily_stats'][today] = {'sent': 0, 'failed': 0}
        
        if success:
            self.stats['total_sent'] += 1
            self.stats['daily_stats'][today]['sent'] += 1
            email_logger.info(f"[SUCCESS] {email_type} email sent successfully to {to_email}")
        else:
            self.stats['total_failed'] += 1
            self.stats['daily_stats'][today]['failed'] += 1
            email_logger.error(f"[FAILURE] {email_type} email failed to {to_email}: {error}")
            
            # Track error types
            if error:
                error_type = type(error).__name__ if isinstance(error, Exception) else str(error)
                self.stats['error_types'][error_type] = self.stats['error_types'].get(error_type, 0) + 1
        
        # Update specific counters
        if email_type == 'password_reset':
            if success:
                self.stats['password_resets'] += 1
                self.stats['last_reset'] = datetime.now().isoformat()
        
        self.save_stats()
    
    def log_password_reset(self, email: str, success: bool, error: Optional[str] = None):
        """Log a password reset email attempt"""
        self.log_email_attempt('password_reset', email, success, error)
    
    def get_daily_stats(self, days: int = 7) -> Dict:
        """Get email statistics for the last N days"""
        stats = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            stats[date] = self.stats['daily_stats'].get(date, {'sent': 0, 'failed': 0})
        return stats
    
    def get_summary(self) -> Dict:
        """Get email delivery summary"""
        total_attempts = self.stats['total_sent'] + self.stats['total_failed']
        success_rate = (self.stats['total_sent'] / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'total_sent': self.stats['total_sent'],
            'total_failed': self.stats['total_failed'],
            'total_attempts': total_attempts,
            'success_rate': round(success_rate, 2),
            'password_resets': self.stats['password_resets'],
            'last_reset': self.stats['last_reset'],
            'top_errors': dict(sorted(self.stats['error_types'].items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    def print_summary(self):
        """Print email delivery summary"""
        summary = self.get_summary()
        
        print("\n📊 EMAIL DELIVERY SUMMARY")
        print("=" * 40)
        print(f"📧 Total Sent: {summary['total_sent']}")
        print(f"❌ Total Failed: {summary['total_failed']}")
        print(f"📈 Success Rate: {summary['success_rate']}%")
        print(f"🔑 Password Resets: {summary['password_resets']}")
        
        if summary['last_reset']:
            print(f"⏰ Last Reset: {summary['last_reset']}")
        
        if summary['top_errors']:
            print("\n🚨 Top Error Types:")
            for error, count in summary['top_errors'].items():
                print(f"   - {error}: {count}")
        
        print(f"\n📁 Log File: {log_file}")
        print(f"📊 Stats File: {self.stats_file}")

# Global email monitor instance
_email_monitor = None

def get_email_monitor() -> EmailMonitor:
    """Get or create the global email monitor instance"""
    global _email_monitor
    if _email_monitor is None:
        _email_monitor = EmailMonitor()
    return _email_monitor

# Convenience functions
def log_password_reset_attempt(email: str, success: bool, error: Optional[str] = None):
    """Log a password reset email attempt"""
    monitor = get_email_monitor()
    monitor.log_password_reset(email, success, error)

def log_email_attempt(email_type: str, to_email: str, success: bool, error: Optional[str] = None):
    """Log an email sending attempt"""
    monitor = get_email_monitor()
    monitor.log_email_attempt(email_type, to_email, success, error)

def get_email_summary():
    """Get email delivery summary"""
    monitor = get_email_monitor()
    return monitor.get_summary()

def print_email_summary():
    """Print email delivery summary"""
    monitor = get_email_monitor()
    monitor.print_summary()

if __name__ == "__main__":
    # Print current email statistics
    print_email_summary()
