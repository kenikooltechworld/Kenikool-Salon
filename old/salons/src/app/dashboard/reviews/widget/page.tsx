"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Copy, Check } from "lucide-react";
import { ReviewWidget } from "@/components/reviews/review-widget";

interface WidgetConfig {
  colors: {
    primary: string;
    background: string;
    text: string;
  };
  layout: "grid" | "list";
  maxReviews: number;
}

export default function WidgetConfigurationPage() {
  const [config, setConfig] = useState<WidgetConfig>({
    colors: {
      primary: "#3b82f6",
      background: "#ffffff",
      text: "#1f2937",
    },
    layout: "grid",
    maxReviews: 5,
  });

  const [copied, setCopied] = useState(false);
  const [tenantId, setTenantId] = useState("");

  useEffect(() => {
    // Get tenant ID from user context or API
    const fetchTenantId = async () => {
      try {
        const response = await fetch("/api/user/profile");
        const data = await response.json();
        setTenantId(data.tenant_id);
      } catch (error) {
        console.error("Error fetching tenant ID:", error);
      }
    };

    fetchTenantId();
  }, []);

  const handleColorChange = (
    colorKey: keyof typeof config.colors,
    value: string,
  ) => {
    setConfig((prev) => ({
      ...prev,
      colors: {
        ...prev.colors,
        [colorKey]: value,
      },
    }));
  };

  const handleLayoutChange = (layout: "grid" | "list") => {
    setConfig((prev) => ({
      ...prev,
      layout,
    }));
  };

  const handleMaxReviewsChange = (value: number) => {
    setConfig((prev) => ({
      ...prev,
      maxReviews: Math.max(1, Math.min(20, value)),
    }));
  };

  const generateEmbedCode = () => {
    const apiUrl = import.meta.env.VITE_API_URL || "https://api.yourdomain.com";
    const widgetUrl =
      import.meta.env.VITE_WIDGET_URL || "https://yourdomain.com/widget.js";

    return `<!-- Salon Reviews Widget -->
<div id="salon-reviews-widget"></div>
<script>
  (function () {
    var script = document.createElement("script");
    script.src = "${widgetUrl}";
    script.setAttribute("data-tenant-id", "${tenantId}");
    script.setAttribute("data-max-reviews", "${config.maxReviews}");
    script.setAttribute("data-layout", "${config.layout}");
    script.setAttribute("data-primary-color", "${config.colors.primary}");
    script.setAttribute("data-background-color", "${config.colors.background}");
    script.setAttribute("data-text-color", "${config.colors.text}");
    script.setAttribute("data-api-url", "${apiUrl}");
    document.body.appendChild(script);
  })();
</script>`;
  };

  const copyToClipboard = () => {
    const code = generateEmbedCode();
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Review Widget</h1>
        <p className="text-gray-600 mt-2">
          Customize and embed your salon reviews on external websites
        </p>
      </div>

      <Tabs defaultValue="preview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="preview">Preview</TabsTrigger>
          <TabsTrigger value="customize">Customize</TabsTrigger>
          <TabsTrigger value="embed">Embed Code</TabsTrigger>
        </TabsList>

        {/* Preview Tab */}
        <TabsContent value="preview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Widget Preview</CardTitle>
              <CardDescription>
                This is how your widget will appear on external websites
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-w-md">
                {tenantId && (
                  <ReviewWidget tenantId={tenantId} config={config} />
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Customize Tab */}
        <TabsContent value="customize" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>
                Customize the look and feel of your widget
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Colors Section */}
              <div className="space-y-4">
                <h3 className="font-semibold">Colors</h3>

                <div className="space-y-2">
                  <Label htmlFor="primary-color">Primary Color</Label>
                  <div className="flex gap-2">
                    <input
                      id="primary-color"
                      type="color"
                      value={config.colors.primary}
                      onChange={(e) =>
                        handleColorChange("primary", e.target.value)
                      }
                      className="w-12 h-10 rounded cursor-pointer"
                    />
                    <Input
                      type="text"
                      value={config.colors.primary}
                      onChange={(e) =>
                        handleColorChange("primary", e.target.value)
                      }
                      placeholder="#3b82f6"
                      className="flex-1"
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    Used for headers, borders, and links
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="background-color">Background Color</Label>
                  <div className="flex gap-2">
                    <input
                      id="background-color"
                      type="color"
                      value={config.colors.background}
                      onChange={(e) =>
                        handleColorChange("background", e.target.value)
                      }
                      className="w-12 h-10 rounded cursor-pointer"
                    />
                    <Input
                      type="text"
                      value={config.colors.background}
                      onChange={(e) =>
                        handleColorChange("background", e.target.value)
                      }
                      placeholder="#ffffff"
                      className="flex-1"
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    Widget background color
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="text-color">Text Color</Label>
                  <div className="flex gap-2">
                    <input
                      id="text-color"
                      type="color"
                      value={config.colors.text}
                      onChange={(e) =>
                        handleColorChange("text", e.target.value)
                      }
                      className="w-12 h-10 rounded cursor-pointer"
                    />
                    <Input
                      type="text"
                      value={config.colors.text}
                      onChange={(e) =>
                        handleColorChange("text", e.target.value)
                      }
                      placeholder="#1f2937"
                      className="flex-1"
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    Text and content color
                  </p>
                </div>
              </div>

              {/* Layout Section */}
              <div className="space-y-4">
                <h3 className="font-semibold">Layout</h3>

                <div className="space-y-2">
                  <Label>Display Layout</Label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="layout"
                        value="grid"
                        checked={config.layout === "grid"}
                        onChange={() => handleLayoutChange("grid")}
                        className="w-4 h-4"
                      />
                      <span className="text-sm">Grid (Stacked)</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="layout"
                        value="list"
                        checked={config.layout === "list"}
                        onChange={() => handleLayoutChange("list")}
                        className="w-4 h-4"
                      />
                      <span className="text-sm">List</span>
                    </label>
                  </div>
                </div>
              </div>

              {/* Max Reviews Section */}
              <div className="space-y-4">
                <h3 className="font-semibold">Content</h3>

                <div className="space-y-2">
                  <Label htmlFor="max-reviews">
                    Maximum Reviews to Display: {config.maxReviews}
                  </Label>
                  <input
                    id="max-reviews"
                    type="range"
                    min="1"
                    max="20"
                    value={config.maxReviews}
                    onChange={(e) =>
                      handleMaxReviewsChange(parseInt(e.target.value))
                    }
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500">
                    Shows the {config.maxReviews} most recent approved reviews
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Embed Code Tab */}
        <TabsContent value="embed" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Embed Code</CardTitle>
              <CardDescription>
                Copy this code and paste it into your website's HTML
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="embed-code">HTML Code</Label>
                <div className="relative">
                  <textarea
                    id="embed-code"
                    value={generateEmbedCode()}
                    readOnly
                    className="w-full h-64 p-3 font-mono text-sm border rounded-lg bg-gray-50 text-gray-900"
                  />
                  <Button
                    onClick={copyToClipboard}
                    size="sm"
                    className="absolute top-2 right-2"
                    variant="outline"
                  >
                    {copied ? (
                      <>
                        <Check size={16} className="mr-1" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy size={16} className="mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                <h4 className="font-semibold text-sm text-blue-900">
                  Installation Instructions
                </h4>
                <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                  <li>Copy the code above</li>
                  <li>Go to your website's HTML editor or theme settings</li>
                  <li>Paste the code where you want the reviews to appear</li>
                  <li>Save and publish your changes</li>
                  <li>
                    The widget will automatically load your latest reviews
                  </li>
                </ol>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-2">
                <h4 className="font-semibold text-sm text-amber-900">
                  Important Notes
                </h4>
                <ul className="text-sm text-amber-800 space-y-1 list-disc list-inside">
                  <li>Only approved reviews will be displayed</li>
                  <li>The widget updates automatically every hour</li>
                  <li>Ensure your website allows external scripts</li>
                  <li>The widget is responsive and works on mobile devices</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
