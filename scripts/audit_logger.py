"""
Comprehensive Audit Logging System

Gold Tier Feature: Centralized audit logging for all AI Employee actions.
Provides detailed logging, search, and reporting capabilities.

Usage:
    from audit_logger import AuditLogger
    
    logger = AuditLogger(vault_path)
    logger.log_action('email_send', {'to': 'client@example.com'}, 'success')
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ActionResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class ActionCategory(Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    PAYMENT = "payment"
    INVOICE = "invoice"
    APPROVAL = "approval"
    FILE_OPERATION = "file_operation"
    SYSTEM = "system"


@dataclass
class AuditEntry:
    """Represents a single audit log entry."""
    
    timestamp: str
    action_id: str
    action_type: str
    category: str
    actor: str
    target: str
    result: str
    details: Dict[str, Any]
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    approval_required: bool = False
    approval_status: Optional[str] = None
    approved_by: Optional[str] = None
    retry_count: int = 0
    related_entries: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Comprehensive audit logging system.

    Features:
    - Centralized logging for all actions
    - Search and filter capabilities
    - Daily log rotation
    - Error tracking and analysis
    - Compliance reporting
    """

    def __init__(self, vault_path: str):
        """
        Initialize the audit logger.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.audit_dir = self.logs_dir / 'Audit'
        
        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)

        # Current log file (daily rotation)
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.current_log_file = self.audit_dir / f'audit_{self.current_date}.jsonl'

        # Index for fast lookups
        self.index_file = self.audit_dir / 'audit_index.json'
        self._load_index()

    def _load_index(self):
        """Load the audit index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                'entries': {},
                'by_type': {},
                'by_category': {},
                'by_actor': {},
                'errors': [],
            }

    def _save_index(self):
        """Save the audit index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _generate_action_id(self, action_type: str, target: str, timestamp: str) -> str:
        """Generate a unique action ID."""
        content = f"{action_type}:{target}:{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _rotate_log_file(self):
        """Rotate log file if date changed."""
        new_date = datetime.now().strftime('%Y-%m-%d')
        if new_date != self.current_date:
            self.current_date = new_date
            self.current_log_file = self.audit_dir / f'audit_{self.current_date}.jsonl'

    def log_action(
        self,
        action_type: str,
        details: Dict[str, Any],
        result: str,
        category: str = 'system',
        actor: str = 'ai_employee',
        target: str = '',
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
        approval_required: bool = False,
        approval_status: Optional[str] = None,
        approved_by: Optional[str] = None,
        retry_count: int = 0,
        related_entries: Optional[List[str]] = None
    ) -> str:
        """
        Log an action to the audit system.

        Args:
            action_type: Type of action (e.g., 'email_send', 'payment')
            details: Action details/parameters
            result: Result status ('success', 'failure', 'partial', 'skipped')
            category: Action category
            actor: Who/what performed the action
            target: Target of the action
            error: Error message if failed
            duration_ms: Duration in milliseconds
            approval_required: Whether approval was required
            approval_status: Approval status if applicable
            approved_by: Who approved the action
            retry_count: Number of retry attempts
            related_entries: IDs of related audit entries

        Returns:
            Action ID for reference
        """
        self._rotate_log_file()

        timestamp = datetime.now().isoformat()
        action_id = self._generate_action_id(action_type, target, timestamp)

        entry = AuditEntry(
            timestamp=timestamp,
            action_id=action_id,
            action_type=action_type,
            category=category,
            actor=actor,
            target=target,
            result=result,
            details=details,
            error=error,
            duration_ms=duration_ms,
            approval_required=approval_required,
            approval_status=approval_status,
            approved_by=approved_by,
            retry_count=retry_count,
            related_entries=related_entries or []
        )

        # Write to log file
        with open(self.current_log_file, 'a') as f:
            f.write(entry.to_json() + '\n')

        # Update index
        self.index['entries'][action_id] = {
            'timestamp': timestamp,
            'action_type': action_type,
            'result': result,
        }

        # Index by type
        if action_type not in self.index['by_type']:
            self.index['by_type'][action_type] = []
        self.index['by_type'][action_type].append(action_id)

        # Index by category
        if category not in self.index['by_category']:
            self.index['by_category'][category] = []
        self.index['by_category'][category].append(action_id)

        # Index by actor
        if actor not in self.index['by_actor']:
            self.index['by_actor'][actor] = []
        self.index['by_actor'][actor].append(action_id)

        # Track errors
        if result == 'failure' and error:
            self.index['errors'].append({
                'action_id': action_id,
                'timestamp': timestamp,
                'action_type': action_type,
                'error': error,
            })
            # Keep only last 100 errors
            self.index['errors'] = self.index['errors'][-100:]

        self._save_index()

        return action_id

    def search(
        self,
        action_type: Optional[str] = None,
        category: Optional[str] = None,
        actor: Optional[str] = None,
        result: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Search audit logs.

        Args:
            action_type: Filter by action type
            category: Filter by category
            actor: Filter by actor
            result: Filter by result
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum results

        Returns:
            List of matching AuditEntry objects
        """
        results = []

        # Determine which files to search
        files_to_search = []
        if start_date and end_date:
            # Search specific date range
            current = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            while current <= end:
                file_path = self.audit_dir / f'audit_{current.strftime("%Y-%m-%d")}.jsonl'
                if file_path.exists():
                    files_to_search.append(file_path)
                current += timedelta(days=1)
        else:
            # Search today's log
            files_to_search = [self.current_log_file]

        # Search files
        for log_file in files_to_search:
            if not log_file.exists():
                continue

            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        
                        # Apply filters
                        if action_type and data.get('action_type') != action_type:
                            continue
                        if category and data.get('category') != category:
                            continue
                        if actor and data.get('actor') != actor:
                            continue
                        if result and data.get('result') != result:
                            continue

                        results.append(AuditEntry(**data))

                        if len(results) >= limit:
                            return results

                    except Exception as e:
                        continue

        return results

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get audit statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        entries = self.search(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            limit=10000
        )

        stats = {
            'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
            'total_actions': len(entries),
            'by_result': {},
            'by_category': {},
            'by_actor': {},
            'errors': 0,
            'approvals_required': 0,
            'approvals_approved': 0,
            'approvals_rejected': 0,
            'avg_duration_ms': 0,
            'retries': 0,
        }

        durations = []

        for entry in entries:
            # Count by result
            if entry.result not in stats['by_result']:
                stats['by_result'][entry.result] = 0
            stats['by_result'][entry.result] += 1

            # Count by category
            if entry.category not in stats['by_category']:
                stats['by_category'][entry.category] = 0
            stats['by_category'][entry.category] += 1

            # Count by actor
            if entry.actor not in stats['by_actor']:
                stats['by_actor'][entry.actor] = 0
            stats['by_actor'][entry.actor] += 1

            # Count errors
            if entry.result == 'failure':
                stats['errors'] += 1

            # Count approvals
            if entry.approval_required:
                stats['approvals_required'] += 1
                if entry.approval_status == 'approved':
                    stats['approvals_approved'] += 1
                elif entry.approval_status == 'rejected':
                    stats['approvals_rejected'] += 1

            # Track durations
            if entry.duration_ms:
                durations.append(entry.duration_ms)

            # Count retries
            if entry.retry_count > 0:
                stats['retries'] += entry.retry_count

        # Calculate average duration
        if durations:
            stats['avg_duration_ms'] = sum(durations) / len(durations)

        return stats

    def get_error_report(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get error report for analysis.

        Args:
            days: Number of days to analyze

        Returns:
            List of error entries
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        entries = self.search(
            result='failure',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            limit=1000
        )

        errors = []
        for entry in entries:
            errors.append({
                'timestamp': entry.timestamp,
                'action_id': entry.action_id,
                'action_type': entry.action_type,
                'target': entry.target,
                'error': entry.error,
                'retry_count': entry.retry_count,
            })

        return errors

    def generate_compliance_report(self, start_date: str, end_date: str) -> str:
        """
        Generate a compliance report.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Markdown formatted compliance report
        """
        entries = self.search(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )

        report = f"""# Compliance Report

## Period
{start_date} to {end_date}

## Summary
- Total Actions: {len(entries)}
- Unique Action Types: {len(set(e.action_type for e in entries))}
- Errors: {sum(1 for e in entries if e.result == 'failure')}
- Approvals Required: {sum(1 for e in entries if e.approval_required)}

## Actions by Category
"""

        # Group by category
        by_category = {}
        for entry in entries:
            if entry.category not in by_category:
                by_category[entry.category] = 0
            by_category[entry.category] += 1

        for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
            report += f"- {category}: {count}\n"

        report += f"""
## Approval Summary
- Required: {sum(1 for e in entries if e.approval_required)}
- Approved: {sum(1 for e in entries if e.approval_status == 'approved')}
- Rejected: {sum(1 for e in entries if e.approval_status == 'rejected')}
- Pending: {sum(1 for e in entries if e.approval_required and not e.approval_status)}

## Error Summary
"""

        # Group errors by type
        errors_by_type = {}
        for entry in entries:
            if entry.result == 'failure' and entry.error:
                if entry.action_type not in errors_by_type:
                    errors_by_type[entry.action_type] = []
                errors_by_type[entry.action_type].append(entry.error)

        for action_type, errors in errors_by_type.items():
            report += f"\n### {action_type}\n"
            for error in errors[:5]:  # Show first 5 errors
                report += f"- {error}\n"

        report += f"""
## Audit Trail
All actions logged with:
- Timestamp
- Action ID
- Actor
- Target
- Result
- Details

Log files location: `{self.audit_dir}`
"""

        return report


# Global logger instance
_logger: Optional[AuditLogger] = None


def get_audit_logger(vault_path: str) -> AuditLogger:
    """Get or create the global audit logger."""
    global _logger
    if _logger is None or _logger.vault_path != Path(vault_path):
        _logger = AuditLogger(vault_path)
    return _logger


if __name__ == '__main__':
    import sys

    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    logger = AuditLogger(vault_path)

    # Demo: Log some actions
    logger.log_action(
        action_type='email_send',
        details={'to': 'client@example.com', 'subject': 'Invoice'},
        result='success',
        category='email',
        actor='ai_employee',
        target='client@example.com',
        duration_ms=1250,
    )

    logger.log_action(
        action_type='payment',
        details={'amount': 500, 'recipient': 'Vendor A'},
        result='success',
        category='payment',
        actor='ai_employee',
        target='Vendor A',
        approval_required=True,
        approval_status='approved',
        approved_by='human',
        duration_ms=3500,
    )

    # Get statistics
    stats = logger.get_statistics(days=7)
    print(f"Audit Statistics (7 days):")
    print(f"  Total actions: {stats['total_actions']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Avg duration: {stats['avg_duration_ms']:.0f}ms")
