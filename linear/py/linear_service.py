"""Linear API service for task management."""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    """Linear issue."""
    id: str
    title: str
    description: str
    status: str
    priority: str
    assignee: Optional[str] = None
    project: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LinearService:
    """Service for Linear API integration."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Linear service.
        
        Args:
            api_key: Linear API key
        """
        self.api_key = api_key
        self.base_url = "https://api.linear.app/graphql"
        self.issues: Dict[str, Issue] = {}
        logger.info("Initialized Linear service")

    async def create_issue(
        self,
        title: str,
        description: str,
        project_id: str,
        priority: str = "medium",
        assignee: Optional[str] = None,
    ) -> Issue:
        """Create a new issue.
        
        Args:
            title: Issue title
            description: Issue description
            project_id: Project ID
            priority: Priority level
            assignee: Assignee user ID
            
        Returns:
            Created issue
        """
        issue = Issue(
            id=f"issue-{len(self.issues) + 1}",
            title=title,
            description=description,
            status="backlog",
            priority=priority,
            assignee=assignee,
            project=project_id,
        )
        
        self.issues[issue.id] = issue
        logger.debug(f"Created issue: {issue.id}")
        
        return issue

    async def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue by ID.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Issue or None if not found
        """
        return self.issues.get(issue_id)

    async def update_issue(
        self,
        issue_id: str,
        **kwargs
    ) -> Optional[Issue]:
        """Update issue.
        
        Args:
            issue_id: Issue ID
            **kwargs: Fields to update
            
        Returns:
            Updated issue or None
        """
        issue = self.issues.get(issue_id)
        if not issue:
            logger.warning(f"Issue not found: {issue_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(issue, key):
                setattr(issue, key, value)
        
        logger.debug(f"Updated issue: {issue_id}")
        return issue

    async def delete_issue(self, issue_id: str) -> bool:
        """Delete issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            True if deleted, False if not found
        """
        if issue_id in self.issues:
            del self.issues[issue_id]
            logger.debug(f"Deleted issue: {issue_id}")
            return True
        return False

    async def list_issues(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> List[Issue]:
        """List issues with optional filters.
        
        Args:
            project_id: Filter by project
            status: Filter by status
            assignee: Filter by assignee
            
        Returns:
            List of issues
        """
        issues = list(self.issues.values())
        
        if project_id:
            issues = [i for i in issues if i.project == project_id]
        if status:
            issues = [i for i in issues if i.status == status]
        if assignee:
            issues = [i for i in issues if i.assignee == assignee]
        
        logger.debug(f"Listed {len(issues)} issues")
        return issues

    async def change_status(
        self,
        issue_id: str,
        status: str,
    ) -> Optional[Issue]:
        """Change issue status.
        
        Args:
            issue_id: Issue ID
            status: New status
            
        Returns:
            Updated issue
        """
        return await self.update_issue(issue_id, status=status)

    async def assign_issue(
        self,
        issue_id: str,
        assignee: str,
    ) -> Optional[Issue]:
        """Assign issue to user.
        
        Args:
            issue_id: Issue ID
            assignee: Assignee user ID
            
        Returns:
            Updated issue
        """
        return await self.update_issue(issue_id, assignee=assignee)
