/**
 * Social Proof Management Page
 * Owner interface for managing social proof features
 * Mobile-first responsive design
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
    <div className="space-y-4 p-3 sm:space-y-6 sm:p-0">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground sm:text-3xl">
          Social Proof Management
        </h1>
        <p className="mt-1 text-sm text-muted-foreground sm:text-base sm:mt-2">
          Manage your social media feeds and video testimonials
        </p>
      </div>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="instagram"
      >
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="instagram" className="whitespace-nowrap">
            Instagram Feed
          </TabsTrigger>
          <TabsTrigger value="testimonials" className="whitespace-nowrap">
            Video Testimonials
          </TabsTrigger>
          <TabsTrigger value="settings" className="whitespace-nowrap">
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Instagram Feed Tab */}
        <TabsContent value="instagram" className="mt-4">
          <Card className="p-4 sm:p-6">
            <div className="mb-4 sm:mb-6">
              <h2 className="text-lg font-semibold text-foreground sm:text-xl sm:mb-4">
                Instagram Feed
              </h2>

              {/* Sync Form - stacked on mobile, grid on larger screens */}
              <div className="flex flex-col gap-3 sm:grid-cols-3 sm:gap-4 mb-3 sm:mb-4">
                <Input
                  placeholder="Instagram Access Token"
                  value={instagramToken}
                  onChange={(e) => setInstagramToken(e.target.value)}
                  className="w-full"
                />
                <Input
                  placeholder="Instagram User ID"
                  value={instagramUserId}
                  onChange={(e) => setInstagramUserId(e.target.value)}
                  className="w-full"
                />
                <Button
                  onClick={handleSyncInstagram}
                  disabled={syncInstagram.isPending}
                  className="w-full sm:w-auto"
                >
                  <RefreshIcon size={16} className="mr-2" />
                  {syncInstagram.isPending ? "Syncing..." : "Sync Feed"}
                </Button>
              </div>

              <p className="text-xs text-muted-foreground sm:text-sm">
                Get your Instagram access token from the{" "}
                <a
                  href="https://developers.facebook.com/apps/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  Facebook Developer Portal
                </a>
              </p>
            </div>

            {/* Instagram Posts Grid */}
            {instagramLoading ? (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3 xl:grid-cols-4">
                {[...Array(8)].map((_, i) => (
                  <Skeleton key={i} className="aspect-square rounded-lg" />
                ))}
              </div>
            ) : instagramFeed && instagramFeed.length > 0 ? (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3 xl:grid-cols-4">
                {instagramFeed.map((post: any) => (
                  <div key={post.id} className="relative group">
                    <div className="aspect-square overflow-hidden rounded-lg bg-muted">
                      <img
                        src={post.media_url}
                        alt={post.caption || "Instagram post"}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                    </div>

                    {/* Overlay actions - larger touch targets on mobile */}
                    <div className="absolute inset-0 flex items-center justify-center gap-2 rounded-lg bg-black/60 opacity-0 transition-opacity group-hover:opacity-100 group-active:opacity-100">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() =>
                          handleToggleVisibility(post.id, post.is_active)
                        }
                        className="h-8 w-8 p-0 sm:h-9 sm:w-9"
                        aria-label={post.is_active ? "Hide post" : "Show post"}
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
                        className="h-8 w-8 p-0 sm:h-9 sm:w-9"
                        aria-label="Delete post"
                      >
                        <TrashIcon size={16} />
                      </Button>
                    </div>

                    {!post.is_active && (
                      <div className="absolute left-2 top-2 bg-destructive text-destructive-foreground text-xs px-2 py-0.5 rounded">
                        Hidden
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <p className="text-sm text-muted-foreground">
                  No Instagram posts found. Sync your feed to get started.
                </p>
              </div>
            )}
          </Card>
        </TabsContent>

        {/* Video Testimonials Tab */}
        <TabsContent value="testimonials" className="mt-4">
          <Card className="p-4 sm:p-6">
            {/* Header with Add button */}
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-lg font-semibold text-foreground sm:text-xl">
                Video Testimonials
              </h2>
              <Button
                className="gap-2 w-full sm:w-auto"
                onClick={() => setIsAddModalOpen(true)}
              >
                <PlusIcon size={16} />
                Add Testimonial
              </Button>
            </div>

            {/* Testimonials Grid */}
            {testimonialsLoading ? (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
                {[...Array(6)].map((_, i) => (
                  <Skeleton key={i} className="aspect-video rounded-lg" />
                ))}
              </div>
            ) : videoTestimonials && videoTestimonials.length > 0 ? (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
                {videoTestimonials.map((testimonial: any) => (
                  <div
                    key={testimonial.id}
                    className="group relative rounded-lg border bg-card"
                  >
                    <div className="aspect-video overflow-hidden rounded-t-lg bg-muted">
                      {testimonial.thumbnail_url ? (
                        <img
                          src={testimonial.thumbnail_url}
                          alt={testimonial.customer_name}
                          className="h-full w-full object-cover"
                          loading="lazy"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center bg-primary/10 text-primary">
                          <div className="flex flex-col items-center gap-1">
                            <svg
                              className="h-8 w-8"
                              fill="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path d="M8 5v14l11-7z" />
                            </svg>
                            <span className="text-xs font-medium">Video</span>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="p-3 sm:p-4">
                      <h3 className="font-semibold text-sm text-foreground sm:text-base truncate">
                        {testimonial.customer_name}
                      </h3>
                      {testimonial.testimonial_text && (
                        <p className="mt-1 text-xs text-muted-foreground sm:text-sm line-clamp-2">
                          {testimonial.testimonial_text}
                        </p>
                      )}
                      {testimonial.rating && (
                        <div className="mt-2 flex items-center gap-0.5">
                          {[...Array(5)].map((_, i) => (
                            <svg
                              key={i}
                              className={`h-3.5 w-3.5 sm:h-4 sm:w-4 ${
                                i < testimonial.rating
                                  ? "text-yellow-400 fill-yellow-400"
                                  : "text-gray-300"
                              }`}
                              viewBox="0 0 24 24"
                            >
                              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                            </svg>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Delete button - touch friendly on mobile */}
                    <div className="absolute right-2 top-2 sm:top-3">
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() =>
                          handleDeleteTestimonial(testimonial.id)
                        }
                        className="h-8 w-8 p-0 sm:h-9 sm:w-9"
                        aria-label="Delete testimonial"
                      >
                        <TrashIcon size={14} className="sm:h-4 sm:w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <p className="text-sm text-muted-foreground">
                  No video testimonials found. Add your first testimonial to get
                  started.
                </p>
              </div>
            )}
          </Card>

          {/* Add Testimonial Modal */}
          <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
            <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
              <DialogHeader>
                <DialogTitle className="text-lg sm:text-xl">
                  Add Video Testimonial
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 px-4 sm:px-0">
                <div>
                  <Label className="text-sm">Customer Name</Label>
                  <Input
                    value={formData.customer_name}
                    onChange={(e) =>
                      setFormData({ ...formData, customer_name: e.target.value })
                    }
                    placeholder="Enter customer name"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label className="text-sm">Video URL</Label>
                  <Input
                    value={formData.video_url}
                    onChange={(e) =>
                      setFormData({ ...formData, video_url: e.target.value })
                    }
                    placeholder="https://example.com/video.mp4"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label className="text-sm">Thumbnail URL</Label>
                  <Input
                    value={formData.thumbnail_url}
                    onChange={(e) =>
                      setFormData({ ...formData, thumbnail_url: e.target.value })
                    }
                    placeholder="https://example.com/thumbnail.jpg"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label className="text-sm">Testimonial Text</Label>
                  <Textarea
                    value={formData.testimonial_text}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        testimonial_text: e.target.value,
                      })
                    }
                    placeholder="What did the customer say?"
                    className="mt-1"
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3 sm:gap-4">
                  <div>
                    <Label className="text-sm">Rating</Label>
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
                    <Label className="text-sm">Display Order</Label>
                    <Input
                      type="number"
                      value={formData.display_order}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          display_order: e.target.value,
                        })
                      }
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>
              <DialogFooter className="flex-col-reverse gap-2 sm:flex-row sm:gap-3">
                <Button
                  variant="outline"
                  onClick={() => setIsAddModalOpen(false)}
                  className="w-full sm:w-auto"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateTestimonial}
                  disabled={createTestimonial.isPending}
                  className="w-full sm:w-auto"
                >
                  {createTestimonial.isPending ? "Adding..." : "Add Testimonial"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="mt-4">
          <Card className="p-4 sm:p-6">
            <h2 className="mb-4 text-lg font-semibold text-foreground sm:text-xl sm:mb-6">
              Social Proof Settings
            </h2>

            <div className="space-y-3 sm:space-y-4">
              {[
                {
                  key: "liveNotifications",
                  label: "Live Booking Notifications",
                  description:
                    "Show recent booking notifications to visitors",
                },
                {
                  key: "instagramDisplay",
                  label: "Instagram Feed Display",
                  description:
                    "Control how Instagram posts are displayed on your booking page",
                },
                {
                  key: "videoTestimonialsDisplay",
                  label: "Video Testimonials Display",
                  description:
                    "Control how video testimonials are displayed",
                },
              ].map((item) => (
                <div
                  key={item.key}
                  className="flex flex-col gap-3 rounded-lg border p-3 sm:flex-row sm:items-center sm:justify-between sm:p-4"
                >
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-foreground">
                      {item.label}
                    </label>
                    <p className="mt-0.5 text-xs text-muted-foreground sm:text-sm">
                      {item.description}
                    </p>
                  </div>
                  <Button
                    variant={
                      settings[item.key as keyof typeof settings]
                        ? "default"
                        : "outline"
                    }
                    onClick={() =>
                      setSettings({
                        ...settings,
                        [item.key]: !settings[item.key as keyof typeof settings],
                      })
                    }
                    className="w-full sm:w-auto"
                  >
                    {settings[item.key as keyof typeof settings]
                      ? "Enabled"
                      : "Disabled"}
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
