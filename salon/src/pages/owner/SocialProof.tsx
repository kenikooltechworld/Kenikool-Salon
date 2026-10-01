/**
 * Social Proof Management Page
 * Owner interface for managing social proof features
 */

import { useState } from "react";
import {
  Card,
  Button,
  Input,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Label,
  Textarea,
  Select,
  Skeleton,
} from "@/components/ui";
import { useToast } from "@/components/ui/toast";
import {
  useSocialFeed,
  useSyncInstagram,
  useTogglePostVisibility,
  useDeleteSocialPost,
  useVideoTestimonials,
  useCreateVideoTestimonial,
  useDeleteVideoTestimonial,
} from "@/hooks/useSocialProof";
import {
  TrashIcon,
  RefreshIcon,
  EyeIcon,
  EyeOffIcon,
  PlusIcon,
  SettingsIcon,
} from "@/components/icons";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

export default function SocialProof() {
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState("instagram");
  const [instagramToken, setInstagramToken] = useState("");
  const [instagramUserId, setInstagramUserId] = useState("");
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [settings, setSettings] = useState({
    liveNotifications: true,
    instagramDisplay: true,
    videoTestimonialsDisplay: true,
  });

  const { data: instagramFeed, isLoading: instagramLoading } = useSocialFeed(
    "instagram",
    20,
  );
  const { data: videoTestimonials, isLoading: testimonialsLoading } =
    useVideoTestimonials(20);
  const syncInstagram = useSyncInstagram();
  const toggleVisibility = useTogglePostVisibility();
  const deletePost = useDeleteSocialPost();
  const createTestimonial = useCreateVideoTestimonial();
  const deleteTestimonial = useDeleteVideoTestimonial();

  const [formData, setFormData] = useState({
    customer_name: "",
    video_url: "",
    thumbnail_url: "",
    testimonial_text: "",
    rating: "5",
    display_order: "0",
  });

  const handleCreateTestimonial = async () => {
    if (!formData.customer_name || !formData.video_url) {
      addToast({
        title: "Error",
        description: "Customer name and video URL are required",
        variant: "error",
      });
      return;
    }

    try {
      await createTestimonial.mutateAsync({
        customer_name: formData.customer_name,
        video_url: formData.video_url,
        thumbnail_url: formData.thumbnail_url || undefined,
        testimonial_text: formData.testimonial_text || undefined,
        rating: parseInt(formData.rating, 10),
        display_order: parseInt(formData.display_order, 10),
      });

      addToast({
        title: "Success",
        description: "Video testimonial added successfully",
        variant: "success",
      });
      setIsAddModalOpen(false);
      setFormData({
        customer_name: "",
        video_url: "",
        thumbnail_url: "",
        testimonial_text: "",
        rating: "5",
        display_order: "0",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to add testimonial",
        variant: "error",
      });
    }
  };

  const handleDeleteTestimonial = async (testimonialId: string) => {
    if (!confirm("Are you sure you want to delete this testimonial?")) {
      return;
    }

    try {
      await deleteTestimonial.mutateAsync(testimonialId);
      addToast({
        title: "Success",
        description: "Testimonial deleted successfully",
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to delete testimonial",
        variant: "error",
      });
    }
  };

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
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {[...Array(8)].map((_, i) => (
                  <Skeleton key={i} className="aspect-square rounded-lg" />
                ))}
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
              <Button className="gap-2" onClick={() => setIsAddModalOpen(true)}>
                <PlusIcon size={16} />
                Add Testimonial
              </Button>
            </div>

            {testimonialsLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <Skeleton key={i} className="aspect-video rounded-lg" />
                ))}
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
                        onClick={() => handleDeleteTestimonial(testimonial.id)}
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

          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Video Testimonial</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Customer Name</Label>
                  <Input
                    value={formData.customer_name}
                    onChange={(e) =>
                      setFormData({ ...formData, customer_name: e.target.value })
                    }
                    placeholder="Enter customer name"
                  />
                </div>
                <div>
                  <Label>Video URL</Label>
                  <Input
                    value={formData.video_url}
                    onChange={(e) =>
                      setFormData({ ...formData, video_url: e.target.value })
                    }
                    placeholder="https://example.com/video.mp4"
                  />
                </div>
                <div>
                  <Label>Thumbnail URL</Label>
                  <Input
                    value={formData.thumbnail_url}
                    onChange={(e) =>
                      setFormData({ ...formData, thumbnail_url: e.target.value })
                    }
                    placeholder="https://example.com/thumbnail.jpg"
                  />
                </div>
                <div>
                  <Label>Testimonial Text</Label>
                  <Textarea
                    value={formData.testimonial_text}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        testimonial_text: e.target.value,
                      })
                    }
                    placeholder="What did the customer say?"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Rating</Label>
                    <Select
                      value={formData.rating}
                      onValueChange={(value) =>
                        setFormData({ ...formData, rating: value })
                      }
                    >
                      <option value="5">5 Stars</option>
                      <option value="4">4 Stars</option>
                      <option value="3">3 Stars</option>
                      <option value="2">2 Stars</option>
                      <option value="1">1 Star</option>
                    </Select>
                  </div>
                  <div>
                    <Label>Display Order</Label>
                    <Input
                      type="number"
                      value={formData.display_order}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          display_order: e.target.value,
                        })
                      }
                    />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setIsAddModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateTestimonial}
                  disabled={createTestimonial.isPending}
                >
                  {createTestimonial.isPending ? "Adding..." : "Add Testimonial"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              Social Proof Settings
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <label className="block text-sm font-medium">
                    Live Booking Notifications
                  </label>
                  <p className="text-sm text-gray-600">
                    Show recent booking notifications to visitors
                  </p>
                </div>
                <Button
                  variant={settings.liveNotifications ? "primary" : "outline"}
                  onClick={() =>
                    setSettings({
                      ...settings,
                      liveNotifications: !settings.liveNotifications,
                    })
                  }
                >
                  {settings.liveNotifications ? "Enabled" : "Disabled"}
                </Button>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <label className="block text-sm font-medium">
                    Instagram Feed Display
                  </label>
                  <p className="text-sm text-gray-600">
                    Control how Instagram posts are displayed on your booking page
                  </p>
                </div>
                <Button
                  variant={settings.instagramDisplay ? "primary" : "outline"}
                  onClick={() =>
                    setSettings({
                      ...settings,
                      instagramDisplay: !settings.instagramDisplay,
                    })
                  }
                >
                  {settings.instagramDisplay ? "Enabled" : "Disabled"}
                </Button>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <label className="block text-sm font-medium">
                    Video Testimonials Display
                  </label>
                  <p className="text-sm text-gray-600">
                    Control how video testimonials are displayed
                  </p>
                </div>
                <Button
                  variant={settings.videoTestimonialsDisplay ? "primary" : "outline"}
                  onClick={() =>
                    setSettings({
                      ...settings,
                      videoTestimonialsDisplay: !settings.videoTestimonialsDisplay,
                    })
                  }
                >
                  {settings.videoTestimonialsDisplay ? "Enabled" : "Disabled"}
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
