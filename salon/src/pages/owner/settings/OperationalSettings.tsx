import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
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
import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  Loader2Icon,
  PlusIcon,
  Trash2Icon,
} from "@/components/icons";

interface ResourceCapacity {
  id: string;
  name: string;
  type: string;
  capacity: number;
  available: number;
}

interface InventoryThreshold {
  id: string;
  itemName: string;
  lowThreshold: number;
  criticalThreshold: number;
  reorderQuantity: number;
}

interface OperationalConfig {
  resources: ResourceCapacity[];
  inventory: InventoryThreshold[];
  waitingRoom: {
    maxQueueSize: number;
    estimatedWaitTime: number;
  };
}

export function OperationalSettings() {
  const [config, setConfig] = useState<OperationalConfig>({
    resources: [],
    inventory: [],
    waitingRoom: {
      maxQueueSize: 50,
      estimatedWaitTime: 15,
    },
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch("/api/v1/settings/operational");
      const data = await response.json();
      setConfig((prev) => ({
        ...prev,
        ...data,
        waitingRoom: {
          maxQueueSize: data.waiting_room_max_capacity ?? prev.waitingRoom.maxQueueSize,
          estimatedWaitTime: data.waiting_room_estimated_wait_time ?? prev.waitingRoom.estimatedWaitTime,
        },
        resources: data.resources ?? prev.resources,
        inventory: data.inventory ?? prev.inventory,
      }));
    } catch (error) {
      setMessage({
        type: "error",
        text: "Failed to load operational settings",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch("/api/v1/settings/operational", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...config,
          waiting_room_max_capacity: config.waitingRoom.maxQueueSize,
          waiting_room_estimated_wait_time: config.waitingRoom.estimatedWaitTime,
        }),
      });
      setMessage({ type: "success", text: "Operational settings saved" });
    } catch (error) {
      setMessage({ type: "error", text: "Failed to save settings" });
    } finally {
      setSaving(false);
    }
  };

  const addResource = () => {
    setConfig({
      ...config,
      resources: [
        ...config.resources,
        {
          id: Date.now().toString(),
          name: "New Resource",
          type: "",
          capacity: 0,
          available: 0,
        },
      ],
    });
  };

  const removeResource = (id: string) => {
    setConfig({
      ...config,
      resources: config.resources.filter((r) => r.id !== id),
    });
  };

  const updateResource = (id: string, updates: Partial<ResourceCapacity>) => {
    setConfig({
      ...config,
      resources: config.resources.map((r) =>
        r.id === id ? { ...r, ...updates } : r,
      ),
    });
  };

  const addInventoryThreshold = () => {
    setConfig({
      ...config,
      inventory: [
        ...config.inventory,
        {
          id: Date.now().toString(),
          itemName: "New Item",
          lowThreshold: 0,
          criticalThreshold: 0,
          reorderQuantity: 0,
        },
      ],
    });
  };

  const removeInventoryThreshold = (id: string) => {
    setConfig({
      ...config,
      inventory: config.inventory.filter((i) => i.id !== id),
    });
  };

  const updateInventoryThreshold = (
    id: string,
    updates: Partial<InventoryThreshold>,
  ) => {
    setConfig({
      ...config,
      inventory: config.inventory.map((i) =>
        i.id === id ? { ...i, ...updates } : i,
      ),
    });
  };

  if (loading)
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-5 w-72" />
        </div>
        <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
          <Skeleton className="h-6 w-40" />
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="border rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1 space-y-3">
                    <Skeleton className="h-4 w-32" />
                    <div className="grid grid-cols-2 gap-3">
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-10 w-full" />
                    </div>
                  </div>
                  <Skeleton className="h-9 w-9 ml-4" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate("/settings")}
        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        ← Back to Settings
      </button>

      {message && (
        <div
          className={`flex items-center gap-2 p-4 rounded-lg ${message.type === "success" ? "bg-green-50 text-green-900" : "bg-red-50 text-red-900"}`}
        >
          {message.type === "success" ? (
            <CheckCircle2Icon className="w-5 h-5" />
          ) : (
            <AlertCircleIcon className="w-5 h-5" />
          )}
          {message.text}
        </div>
      )}

      <Tabs defaultValue="resources" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="inventory">Inventory</TabsTrigger>
          <TabsTrigger value="waiting-room">Waiting Room</TabsTrigger>
        </TabsList>

        <TabsContent value="resources" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Resource Management</CardTitle>
                <CardDescription>
                  Configure rooms, equipment, and capacity
                </CardDescription>
              </div>
              <Button onClick={addResource} size="sm">
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Resource
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {config.resources.map((resource) => (
                <div
                  key={resource.id}
                  className="border rounded-lg p-4 space-y-3"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label>Resource Name</Label>
                          <Input
                            value={resource.name}
                            onChange={(e) =>
                              updateResource(resource.id, {
                                name: e.target.value,
                              })
                            }
                          />
                        </div>
                        <div>
                          <Label>Type</Label>
                          <Input
                            value={resource.type}
                            onChange={(e) =>
                              updateResource(resource.id, {
                                type: e.target.value,
                              })
                            }
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label>Total Capacity</Label>
                          <Input
                            type="number"
                            value={resource.capacity}
                            onChange={(e) =>
                              updateResource(resource.id, {
                                capacity: parseInt(e.target.value),
                              })
                            }
                          />
                        </div>
                        <div>
                          <Label>Currently Available</Label>
                          <Input
                            type="number"
                            value={resource.available}
                            onChange={(e) =>
                              updateResource(resource.id, {
                                available: parseInt(e.target.value),
                              })
                            }
                          />
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => removeResource(resource.id)}
                      className="ml-4"
                    >
                      <Trash2Icon className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="inventory" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Inventory Thresholds</CardTitle>
                <CardDescription>
                  Set stock level alerts and reorder points
                </CardDescription>
              </div>
              <Button onClick={addInventoryThreshold} size="sm">
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Item
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {config.inventory.map((item) => (
                <div key={item.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex-1 space-y-3">
                      <div>
                        <Label>Item Name</Label>
                        <Input
                          value={item.itemName}
                          onChange={(e) =>
                            updateInventoryThreshold(item.id, {
                              itemName: e.target.value,
                            })
                          }
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <Label>Low Threshold</Label>
                          <Input
                            type="number"
                            value={item.lowThreshold}
                            onChange={(e) =>
                              updateInventoryThreshold(item.id, {
                                lowThreshold: parseInt(e.target.value),
                              })
                            }
                          />
                        </div>
                        <div>
                          <Label>Critical Threshold</Label>
                          <Input
                            type="number"
                            value={item.criticalThreshold}
                            onChange={(e) =>
                              updateInventoryThreshold(item.id, {
                                criticalThreshold: parseInt(e.target.value),
                              })
                            }
                          />
                        </div>
                        <div>
                          <Label>Reorder Quantity</Label>
                          <Input
                            type="number"
                            value={item.reorderQuantity}
                            onChange={(e) =>
                              updateInventoryThreshold(item.id, {
                                reorderQuantity: parseInt(e.target.value),
                              })
                            }
                          />
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => removeInventoryThreshold(item.id)}
                      className="ml-4"
                    >
                      <Trash2Icon className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="waiting-room" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Waiting Room Configuration</CardTitle>
              <CardDescription>
                Manage queue and wait time settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Maximum Queue Size</Label>
                <Input
                  type="number"
                  value={config.waitingRoom.maxQueueSize}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      waitingRoom: {
                        ...config.waitingRoom,
                        maxQueueSize: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label>Estimated Wait Time (minutes)</Label>
                <Input
                  type="number"
                  value={config.waitingRoom.estimatedWaitTime}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      waitingRoom: {
                        ...config.waitingRoom,
                        estimatedWaitTime: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Button onClick={handleSave} disabled={saving} className="w-full">
        {saving ? <Loader2Icon className="animate-spin mr-2 w-4 h-4" /> : null}
        Save Operational Settings
      </Button>
    </div>
  );
}
