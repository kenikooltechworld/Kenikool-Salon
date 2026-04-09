/**
 * Social Proof Management Page
 * Owner interface for managing social proof features
 */

import { useState } from "react";
import {
  Card,
  Button,
  Input,
  Spinner,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui";
import { useToast } from "@/components/ui/toast";
import {
  useSocialFeed,
  useSyncInstagram,
  useTogglePostVisibility,
  useDeleteSocialPost,
  useVideoTestimonials,
} from "@/hooks/useSocialProof";
import {
  TrashIcon,
  RefreshIcon,
  EyeIcon,
  EyeOffIcon,
} from "@/components/icons";

export default function SocialProof() {
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState("instagram");
  const [instagramToken, setInstagramToken] = useState("");
  const [instagramUserId, setInstagramUserId] = useState("");

  const { data: instagramFeed, isLoading: instagramLoading } = useSocialFeed(
    "instagram",
    20,
  );
  const { data: videoTestimonials, isLoading: testimonialsLoading } =
    useVideoTestimonials(20);
  const syncInstagram = useSyncInstagram();
  const toggleVisibility = useTogglePostVisibility();
  const deletePost = useDeleteSocialPost();

  const handleSyncInstagram = async () => {
    if (!instagramToken || !instagramUserId) {
      addToast({
        title: "Error",
        description: "Please provide Instagram access token and user ID",
        variant: "error",
      });
      return;
    }

    try {
      await syncInstagram.mutateAsync({
        access_token: instagramToken,
        user_id: instagramUserId,
        limit: 20,
      });

      addToast({
        title: "Success",
        description: "Instagram feed synced successfully",
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to sync Instagram feed",
        variant: "error",
      });
    }
  };

  const handleToggleVisibility = async (
    postId: string,
    currentStatus: boolean,
  ) => {
    try {
      await toggleVisibility.mutateAsync({
        postId,
        isActive: !currentStatus,
      });

      addToast({
        title: "Success",
        description: "Post visibility updated",
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to update post visibility",
        variant: "error",
      });
    }
  };

  const handleDeletePost = async (postId: string) => {
    if (!confirm("Are you sure you want to delete this post?")) {
      return;
    }

    try {
      await deletePost.mutateAsync(postId);

      addToast({
        title: "Success",
        description: "Post deleted successfully",
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to delete post",
        variant: "error",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Social Proof Management</h1>
        <p className="text-gray-600 mt-2">
          Manage your social media feeds and video testimonials
        </p>
      </div>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="instagram"
      >
        <TabsList>
          <TabsTrigger value="instagram">Instagram Feed</TabsTrigger>
          <TabsTrigger value="testimonials">Video Testimonials</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Instagram Feed Tab */}
        <TabsContent value="instagram">
          <Card className="p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-4">Instagram Feed</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <Input
                  placeholder="Instagram Access Token"
                  value={instagramToken}
                  onChange={(e) => setInstagramToken(e.target.value)}
                />
                <Input
                  placeholder="Instagram User ID"
                  value={instagramUserId}
                  onChange={(e) => setInstagramUserId(e.target.value)}
                />
                <Button
                  onClick={handleSyncInstagram}
                  disabled={syncInstagram.isPending}
                >
                  <RefreshIcon size={16} className="mr-2" />
                  Sync Feed
                </Button>
              </div>

              <p className="text-sm text-gray-600">
                Get your Instagram access token from the{" "}
                <a
                  href="https://developers.facebook.com/apps/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  Facebook Developer Portal
                </a>
              </p>
            </div>

            {instagramLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : instagramFeed && instagramFeed.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {instagramFeed.map((post: any) => (
                  <div key={post.id} className="relative group">
                    <img
                      src={post.media_url}
                      alt={post.caption || "Instagram post"}
                      className="w-full aspect-square object-cover rounded-lg"
                    />

                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() =>
                          handleToggleVisibility(post.id, post.is_active)
                        }
                      >
                        {post.is_active ? (
                          <EyeOffIcon size={16} />
                        ) : (
                          <EyeIcon size={16} />
                        )}
                      </Button>

                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeletePost(post.id)}
                      >
                        <TrashIcon size={16} />
                      </Button>
                    </div>

                    {!post.is_active && (
                      <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
                        Hidden
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No Instagram posts found. Sync your feed to get started.
              </div>
            )}
          </Card>
        </TabsContent>

        {/* Video Testimonials Tab */}
        <TabsContent value="testimonials">
          <Card className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Video Testimonials</h2>
              <Button>Add Testimonial</Button>
            </div>

            {testimonialsLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : videoTestimonials && videoTestimonials.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {videoTestimonials.map((testimonial: any) => (
                  <div key={testimonial.id} className="relative group">
                    <div className="aspect-video bg-gray-200 rounded-lg overflow-hidden">
                      {testimonial.thumbnail_url ? (
                        <img
                          src={testimonial.thumbnail_url}
                          alt={testimonial.customer_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-blue-500 text-white">
                          Video
                        </div>
                      )}
                    </div>

                    <div className="mt-2">
                      <h3 className="font-semibold">
                        {testimonial.customer_name}
                      </h3>
                      {testimonial.testimonial_text && (
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {testimonial.testimonial_text}
                        </p>
                      )}
                    </div>

                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition">
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => {
                          // Handle delete testimonial
                        }}
                      >
                        <TrashIcon size={16} />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No video testimonials found. Add your first testimonial to get
                started.
              </div>
            )}
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              Social Proof Settings
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Live Booking Notifications
                </label>
                <p className="text-sm text-gray-600 mb-2">
                  Show recent booking notifications to visitors
                </p>
                <Button variant="outline">Configure</Button>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Instagram Feed Display
                </label>
                <p className="text-sm text-gray-600 mb-2">
                  Control how Instagram posts are displayed on your booking page
                </p>
                <Button variant="outline">Configure</Button>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Video Testimonials Display
                </label>
                <p className="text-sm text-gray-600 mb-2">
                  Control how video testimonials are displayed
                </p>
                <Button variant="outline">Configure</Button>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
