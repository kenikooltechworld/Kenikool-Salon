import { useEffect, useState } from "react";
import { InstagramIcon, ExternalLinkIcon } from "@/components/icons";
import { apiClient } from "@/lib/utils/api";

interface InstagramPost {
  id: string;
  platform: string;
  media_url: string;
  media_type: string;
  caption?: string;
  permalink?: string;
  likes_count: number;
  comments_count: number;
  published_at: string;
}

interface InstagramFeedProps {
  limit?: number;
}

export function InstagramFeed({ limit = 6 }: InstagramFeedProps) {
  const [posts, setPosts] = useState<InstagramPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState<InstagramPost | null>(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const { data } = await apiClient.get<InstagramPost[]>(
          `/social-proof/social-feed?platform=instagram&limit=${limit}`,
        );
        setPosts(data);
      } catch (error) {
        console.error("Error fetching Instagram feed:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPosts();
  }, [limit]);

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: limit }).map((_, i) => (
          <div
            key={i}
            className="aspect-square bg-gray-200 animate-pulse rounded-lg"
          />
        ))}
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="text-center py-12">
        <InstagramIcon size={48} className="mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600">No Instagram posts available</p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {posts.map((post) => (
          <button
            key={post.id}
            onClick={() => setSelectedPost(post)}
            className="relative aspect-square rounded-lg overflow-hidden group cursor-pointer"
          >
            <img
              src={post.media_url}
              alt={post.caption || "Instagram post"}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
            />

            {/* Overlay on hover */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 flex items-center justify-center">
              <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-white text-center">
                <InstagramIcon size={32} className="mx-auto mb-2" />
                <p className="text-sm">View on Instagram</p>
              </div>
            </div>

            {/* Video indicator */}
            {post.media_type === "video" && (
              <div className="absolute top-2 right-2 bg-black bg-opacity-70 rounded-full p-2">
                <svg
                  className="w-4 h-4 text-white"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                </svg>
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Modal for selected post */}
      {selectedPost && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedPost(null)}
        >
          <div
            className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative">
              <img
                src={selectedPost.media_url}
                alt={selectedPost.caption || "Instagram post"}
                className="w-full"
              />
              <button
                onClick={() => setSelectedPost(null)}
                className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:bg-gray-100 transition"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <div className="p-6">
              {selectedPost.caption && (
                <p className="text-gray-700 mb-4">{selectedPost.caption}</p>
              )}

              <div className="flex items-center justify-between text-sm text-gray-600">
                <div className="flex items-center gap-4">
                  <span>❤️ {selectedPost.likes_count}</span>
                  <span>💬 {selectedPost.comments_count}</span>
                </div>

                {selectedPost.permalink && (
                  <a
                    href={selectedPost.permalink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition"
                  >
                    View on Instagram
                    <ExternalLinkIcon size={16} />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
