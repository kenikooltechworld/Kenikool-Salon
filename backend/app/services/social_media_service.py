"""Service for social media feed integration."""

from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime
import requests

from app.models.social_media_feed import SocialMediaFeed


class SocialMediaService:
    """Service for managing social media feeds"""
    
    @staticmethod
    def sync_instagram_feed(
        tenant_id: ObjectId,
        access_token: str,
        user_id: str,
        limit: int = 12
    ) -> List[SocialMediaFeed]:
        """
        Sync Instagram feed using Instagram Basic Display API
        
        Args:
            tenant_id: Tenant ID
            access_token: Instagram access token
            user_id: Instagram user ID
            limit: Number of posts to fetch
            
        Returns:
            List of synced SocialMediaFeed records
        """
        # Instagram Basic Display API endpoint
        url = f"https://graph.instagram.com/{user_id}/media"
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp',
            'access_token': access_token,
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            synced_feeds = []
            
            for post in data.get('data', []):
                # Check if post already exists
                existing = SocialMediaFeed.objects(
                    tenant_id=tenant_id,
                    platform='instagram',
                    post_id=post['id']
                ).first()
                
                if existing:
                    # Update existing post
                    existing.caption = post.get('caption', '')
                    existing.updated_at = datetime.utcnow()
                    existing.save()
                    synced_feeds.append(existing)
                else:
                    # Create new post
                    media_url = post.get('media_url')
                    if post.get('media_type') == 'VIDEO':
                        media_url = post.get('thumbnail_url', media_url)
                    
                    feed = SocialMediaFeed(
                        tenant_id=tenant_id,
                        platform='instagram',
                        post_id=post['id'],
                        media_url=media_url,
                        media_type='video' if post.get('media_type') == 'VIDEO' else 'image',
                        caption=post.get('caption', ''),
                        permalink=post.get('permalink'),
                        published_at=datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')),
                        is_active=True
                    )
                    feed.save()
                    synced_feeds.append(feed)
            
            return synced_feeds
            
        except requests.RequestException as e:
            print(f"Error syncing Instagram feed: {e}")
            return []
    
    @staticmethod
    def get_feed_posts(
        tenant_id: ObjectId,
        platform: Optional[str] = None,
        limit: int = 12
    ) -> List[SocialMediaFeed]:
        """
        Get social media feed posts
        
        Args:
            tenant_id: Tenant ID
            platform: Filter by platform (instagram, facebook, twitter)
            limit: Maximum number of posts to return
            
        Returns:
            List of SocialMediaFeed records
        """
        query = {
            'tenant_id': tenant_id,
            'is_active': True
        }
        
        if platform:
            query['platform'] = platform
        
        feeds = SocialMediaFeed.objects(**query).order_by('-published_at').limit(limit)
        
        return list(feeds)
    
    @staticmethod
    def toggle_post_visibility(
        post_id: ObjectId,
        is_active: bool
    ) -> Optional[SocialMediaFeed]:
        """
        Toggle visibility of a social media post
        
        Args:
            post_id: Post ID
            is_active: New active status
            
        Returns:
            Updated SocialMediaFeed or None
        """
        feed = SocialMediaFeed.objects(id=post_id).first()
        
        if not feed:
            return None
        
        feed.is_active = is_active
        feed.updated_at = datetime.utcnow()
        feed.save()
        
        return feed
    
    @staticmethod
    def delete_post(post_id: ObjectId) -> bool:
        """
        Delete a social media post
        
        Args:
            post_id: Post ID
            
        Returns:
            True if deleted, False otherwise
        """
        feed = SocialMediaFeed.objects(id=post_id).first()
        
        if not feed:
            return False
        
        feed.delete()
        return True
