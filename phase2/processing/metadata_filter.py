"""
Phase 2 - Metadata Filtering
Filter search results by category, tags, and freshness
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta


class MetadataFilter:
    """
    Filter documents by metadata criteria

    Supported filters:
    - category: Document type (architecture, devops, testing, etc.)
    - tags: Document tags
    - freshness: Document age (newer/older than N days)
    - confidence: Quality score (0.0-1.0)
    - sources: Specific document sources
    """

    def __init__(self):
        """Initialize metadata filter"""
        self.valid_categories = {
            'architecture', 'devops', 'testing', 'security',
            'performance', 'data-pipeline', 'integration'
        }

    def filter_by_category(
        self,
        documents: List[Dict],
        categories: List[str]
    ) -> List[Dict]:
        """Filter documents by category"""
        if not categories:
            return documents

        return [
            doc for doc in documents
            if doc.get('category') in categories
        ]

    def filter_by_tags(
        self,
        documents: List[Dict],
        tags: List[str],
        match_all: bool = False
    ) -> List[Dict]:
        """
        Filter documents by tags

        Args:
            documents: List of documents
            tags: List of tags to match
            match_all: If True, doc must have all tags. If False, any tag matches.

        Returns:
            Filtered documents
        """
        if not tags:
            return documents

        filtered = []
        for doc in documents:
            doc_tags = set(doc.get('tags', []))
            query_tags = set(tags)

            if match_all:
                # All query tags must be in doc
                if query_tags.issubset(doc_tags):
                    filtered.append(doc)
            else:
                # Any query tag in doc
                if doc_tags & query_tags:
                    filtered.append(doc)

        return filtered

    def filter_by_freshness(
        self,
        documents: List[Dict],
        days_old_max: Optional[int] = None,
        days_old_min: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter by document age

        Args:
            documents: List of documents
            days_old_max: Only include docs updated in last N days
            days_old_min: Only include docs not updated in last N days

        Returns:
            Filtered documents
        """
        if not days_old_max and not days_old_min:
            return documents

        filtered = []
        now = datetime.now()

        for doc in documents:
            # Get update timestamp (default: today if not provided)
            update_str = doc.get('updated_at', datetime.now().isoformat())

            try:
                updated_at = datetime.fromisoformat(update_str)
            except:
                updated_at = now

            days_old = (now - updated_at).days

            # Check constraints
            if days_old_max and days_old > days_old_max:
                continue
            if days_old_min and days_old < days_old_min:
                continue

            filtered.append(doc)

        return filtered

    def filter_by_confidence(
        self,
        documents: List[Dict],
        min_confidence: float = 0.0
    ) -> List[Dict]:
        """Filter by confidence/quality score"""
        if min_confidence <= 0.0:
            return documents

        return [
            doc for doc in documents
            if doc.get('confidence', 1.0) >= min_confidence
        ]

    def apply_filters(
        self,
        documents: List[Dict],
        filters: Dict
    ) -> List[Dict]:
        """
        Apply multiple filters at once

        Args:
            documents: List of documents
            filters: Dictionary with filter criteria
                {
                    'categories': ['architecture', 'devops'],
                    'tags': ['microservices', 'docker'],
                    'tags_match_all': False,
                    'days_fresh': 30,
                    'min_confidence': 0.8
                }

        Returns:
            Filtered documents
        """
        result = documents

        if 'categories' in filters:
            result = self.filter_by_category(result, filters['categories'])

        if 'tags' in filters:
            match_all = filters.get('tags_match_all', False)
            result = self.filter_by_tags(result, filters['tags'], match_all=match_all)

        if 'days_fresh' in filters:
            result = self.filter_by_freshness(result, days_old_max=filters['days_fresh'])

        if 'min_confidence' in filters:
            result = self.filter_by_confidence(result, filters['min_confidence'])

        return result
