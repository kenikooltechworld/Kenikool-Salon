import { useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  AlertTriangleIcon,
  PlusIcon,
  ScissorsIcon,
  XIcon,
  UploadIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { showToast } from "@/lib/utils/toast";

interface ServiceTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  is_default: boolean;
  template_data: any;
}

interface TemplateLibraryProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function TemplateLibrary({ onClose, onSuccess }: TemplateLibraryProps) {
  const [selectedTemplate, setSelectedTemplate] =
    useState<ServiceTemplate | null>(null);
  const [serviceName, setServiceName] = useState("");
  const [customizations, setCustomizations] = useState<any>({});
  const [showCustomize, setShowCustomize] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>("");
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [uploadError, setUploadError] = useState<string>("");
  const [imageValidationError, setImageValidationError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Fetch templates
  const { data: templatesData, isLoading } = useQuery({
    queryKey: ["service-templates"],
    queryFn: async () => {
      const response = await apiClient.get("/api/services/templates");
      return response.data;
    },
  });

  const templates = templatesData?.templates || [];

  // Create from template mutation
  const createMutation = useMutation({
    mutationFn: async (data: {
      template_id: string;
      name: string;
      customizations: any;
    }) => {
      const response = await apiClient.post(
        `/api/services/templates/${data.template_id}/create-service`,
        {
          name: data.name,
          customizations: data.customizations,
        },
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      showToast("Service created successfully!", "success");
      onSuccess();
      onClose();
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || "Failed to create service",
        "error",
      );
    },
  });

  // Save as template mutation
  const saveTemplateMutation = useMutation({
    mutationFn: async (data: {
      name: string;
      description: string;
      template_data: any;
    }) => {
      const response = await apiClient.post("/api/services/templates", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-templates"] });
      showToast("Template saved successfully!", "success");
    },
  });

  const handleSelectTemplate = (template: ServiceTemplate) => {
    setSelectedTemplate(template);
    setServiceName(template.name);
    setCustomizations({});
    setShowCustomize(false);
    setImageFile(null);
    setImagePreview("");
    setUploadError("");
    setImageValidationError("");
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImageValidationError("");

    // Validate file type
    if (!file.type.startsWith("image/")) {
      const error = "Please select an image file";
      setImageValidationError(error);
      showToast(error, "error");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      const error = "Image size must be less than 5MB";
      setImageValidationError(error);
      showToast(error, "error");
      return;
    }

    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
    showToast("Image selected", "success");
  };

  const uploadImageToBackend = async (file: File): Promise<string> => {
    setIsUploadingImage(true);
    showToast("Uploading image...", "info");
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await apiClient.post("/api/services/upload", formData, {
        // DO NOT set Content-Type header - let axios/browser set it with boundary
        // Setting it manually breaks multipart/form-data
      });

      if (!response.data?.url) {
        throw new Error("Failed to get image URL from server");
      }

      showToast("Image uploaded successfully", "success");
      return response.data.url;
    } catch (error) {
      console.error("Upload error:", error);
      const errorMsg =
        error instanceof Error ? error.message : "Failed to upload image";
      showToast(errorMsg, "error");
      throw error;
    } finally {
      setIsUploadingImage(false);
    }
  };

  const handleCreateFromTemplate = async () => {
    if (!selectedTemplate || !serviceName) return;

    try {
      setUploadError("");
      let photoUrl = customizations.photo_url || "";

      // Upload image if selected
      if (imageFile) {
        photoUrl = await uploadImageToBackend(imageFile);
      }

      showToast("Creating service...", "info");
      createMutation.mutate({
        template_id: selectedTemplate.id,
        name: serviceName,
        customizations: showCustomize
          ? { ...customizations, photo_url: photoUrl }
          : { photo_url: photoUrl },
      });
    } catch (error) {
      const errorMsg =
        error instanceof Error ? error.message : "Failed to upload image";
      setUploadError(errorMsg);
      showToast(errorMsg, "error");
    }
  };

  const handleCustomizationChange = (field: string, value: any) => {
    setCustomizations((prev: any) => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <Card className="p-6 max-h-[80vh] overflow-y-auto">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Service Templates
            </h3>
            <p className="text-sm text-muted-foreground">
              Create services quickly from templates
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={onClose}>
            <XIcon size={16} />
          </Button>
        </div>

        {uploadError && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h4 className="font-semibold">Upload Error</h4>
              <p className="text-sm">{uploadError}</p>
            </div>
          </Alert>
        )}

        {imageValidationError && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h4 className="font-semibold">Image Error</h4>
              <p className="text-sm">{imageValidationError}</p>
            </div>
          </Alert>
        )}

        {isLoading ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : (
          <>
            {/* Template Selection */}
            {!selectedTemplate ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map((template: ServiceTemplate) => (
                  <Card
                    key={template.id}
                    className="p-4 cursor-pointer hover:shadow-md transition-all duration-200"
                    onClick={() => handleSelectTemplate(template)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <ScissorsIcon size={20} className="text-primary" />
                        <h4 className="font-semibold text-foreground">
                          {template.name}
                        </h4>
                      </div>
                      {template.is_default && (
                        <Badge variant="secondary" size="sm">
                          Default
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {template.description}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="secondary" size="sm">
                        {template.category}
                      </Badge>
                      <span>
                        ₦{template.template_data.price?.toLocaleString() || 0}
                      </span>
                      <span>•</span>
                      <span>
                        {template.template_data.duration_minutes || 0} mins
                      </span>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              /* Template Customization */
              <div className="space-y-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedTemplate(null)}
                >
                  ← Back to Templates
                </Button>

                <Card className="p-4 bg-muted/50">
                  <div className="flex items-center gap-2 mb-2">
                    <ScissorsIcon size={20} className="text-primary" />
                    <h4 className="font-semibold text-foreground">
                      {selectedTemplate.name}
                    </h4>
                    {selectedTemplate.is_default && (
                      <Badge variant="secondary" size="sm">
                        Default
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {selectedTemplate.description}
                  </p>
                </Card>

                {/* Service Name */}
                <div>
                  <Label htmlFor="serviceName">Service Name *</Label>
                  <Input
                    id="serviceName"
                    value={serviceName}
                    onChange={(e) => setServiceName(e.target.value)}
                    placeholder="Enter service name"
                  />
                </div>

                {/* Customize Toggle */}
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="customize"
                    checked={showCustomize}
                    onChange={(e) => setShowCustomize(e.target.checked)}
                    className="w-4 h-4 cursor-pointer"
                  />
                  <Label htmlFor="customize" className="cursor-pointer">
                    Customize template values
                  </Label>
                </div>

                {/* Customization Fields */}
                {showCustomize && (
                  <Card className="p-4 space-y-4">
                    <div>
                      <Label htmlFor="image_upload">Service Image</Label>
                      <div className="flex gap-2">
                        <Input
                          ref={fileInputRef}
                          id="image_upload"
                          type="file"
                          accept="image/*"
                          onChange={handleImageSelect}
                          className="hidden"
                        />
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => fileInputRef.current?.click()}
                          disabled={isUploadingImage}
                          className="flex-1"
                        >
                          {isUploadingImage ? (
                            <>
                              <Spinner size="sm" />
                              Uploading...
                            </>
                          ) : (
                            <>
                              <UploadIcon size={16} />
                              Choose Image
                            </>
                          )}
                        </Button>
                      </div>
                      {imagePreview && (
                        <div className="mt-2">
                          <img
                            src={imagePreview}
                            alt="Preview"
                            className="w-full h-32 object-cover rounded"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setImageFile(null);
                              setImagePreview("");
                              if (fileInputRef.current) {
                                fileInputRef.current.value = "";
                              }
                            }}
                            className="mt-1"
                          >
                            Remove Image
                          </Button>
                        </div>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        Upload image to Cloudinary via backend (max 5MB)
                      </p>
                    </div>
                    <div>
                      <Label htmlFor="price">Price (₦)</Label>
                      <Input
                        id="price"
                        type="number"
                        value={
                          customizations.price ||
                          selectedTemplate.template_data.price ||
                          ""
                        }
                        onChange={(e) =>
                          handleCustomizationChange(
                            "price",
                            parseFloat(e.target.value),
                          )
                        }
                        placeholder="Price"
                      />
                    </div>
                    <div>
                      <Label htmlFor="duration">Duration (minutes)</Label>
                      <Input
                        id="duration"
                        type="number"
                        value={
                          customizations.duration_minutes ||
                          selectedTemplate.template_data.duration_minutes ||
                          ""
                        }
                        onChange={(e) =>
                          handleCustomizationChange(
                            "duration_minutes",
                            parseInt(e.target.value),
                          )
                        }
                        placeholder="Duration"
                      />
                    </div>
                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Input
                        id="description"
                        value={
                          customizations.description ||
                          selectedTemplate.template_data.description ||
                          ""
                        }
                        onChange={(e) =>
                          handleCustomizationChange(
                            "description",
                            e.target.value,
                          )
                        }
                        placeholder="Description"
                      />
                    </div>
                    <div>
                      <Label htmlFor="category">Category</Label>
                      <select
                        id="category"
                        value={
                          customizations.category ||
                          selectedTemplate.template_data.category ||
                          ""
                        }
                        onChange={(e) =>
                          handleCustomizationChange("category", e.target.value)
                        }
                        className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground"
                      >
                        <option value="">Select a category</option>
                        <option value="Hair">Hair</option>
                        <option value="Skincare">Skincare</option>
                        <option value="Nails">Nails</option>
                        <option value="Massage">Massage</option>
                        <option value="Waxing">Waxing</option>
                        <option value="Makeup">Makeup</option>
                        <option value="Threading">Threading</option>
                        <option value="Spa">Spa</option>
                      </select>
                    </div>
                  </Card>
                )}

                {/* Template Preview */}
                <Card className="p-4 bg-muted/50">
                  <h4 className="font-medium text-foreground mb-2">Preview</h4>
                  <div className="space-y-1 text-sm">
                    <p>
                      <span className="text-muted-foreground">Name:</span>{" "}
                      <span className="font-medium">
                        {serviceName || "Not set"}
                      </span>
                    </p>
                    <p>
                      <span className="text-muted-foreground">Price:</span> ₦
                      {(
                        customizations.price ||
                        selectedTemplate.template_data.price ||
                        0
                      ).toLocaleString()}
                    </p>
                    <p>
                      <span className="text-muted-foreground">Duration:</span>{" "}
                      {customizations.duration_minutes ||
                        selectedTemplate.template_data.duration_minutes ||
                        0}{" "}
                      mins
                    </p>
                    <p>
                      <span className="text-muted-foreground">Category:</span>{" "}
                      {customizations.category ||
                        selectedTemplate.template_data.category ||
                        "Not set"}
                    </p>
                  </div>
                </Card>

                {/* Actions */}
                <div className="flex gap-3">
                  <Button
                    onClick={handleCreateFromTemplate}
                    disabled={
                      createMutation.isPending ||
                      !serviceName ||
                      isUploadingImage
                    }
                    className="flex-1"
                  >
                    {createMutation.isPending ? (
                      <>
                        <Spinner size="sm" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <PlusIcon size={16} />
                        Create Service
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setSelectedTemplate(null)}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Card>
  );
}
