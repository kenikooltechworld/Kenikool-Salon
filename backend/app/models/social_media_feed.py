"""Model for social media feed integration."""

from mongoengine import Document, StringField, DateTimeField, ObjectIdField, BooleanField, IntField, URLField
from datetime import datetime


class SocialMediaFeed(Document):
    """Store social media posts for display"""
    
    meta = {
        'collection': 'social_media_feeds',
        'indexes': [
            'tenant_id',
            'platform',
            {'fields': ['tenant_id', 'platform', '-published_at']},
            {'fields': ['tenant_id', 'is_active', '-published_at']},
        ]
    }
    
    tenant_id = ObjectIdField(required=True)
    platform = StringField(required=True, choices=['instagram', 'facebook', 'twitter'])
    post_id = StringField(required=True)  # External platform post ID
    media_url = URLField(required=True)
    media_type = StringField(choices=['image', 'video'], default='image')
    caption = StringField(max_length=2000)
    permalink = URLField()
    likes_count = IntField(default=0)
    comments_count = IntField(default=0)
    published_at = DateTimeField(required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': str(self.id),
            'platform': self.platform,
            'post_id': self.post_id,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'caption': self.caption,
            'permalink': self.permalink,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }
