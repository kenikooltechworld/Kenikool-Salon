"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { useState } from "react";
import { ChevronDown, ChevronUp, RotateCcw, Eye } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export interface BrandingVersion {
  version_id: string;
  created_at: string;
  created_by: string;
  change_description?: string;
  config: Record<string, any>;
}

interface VersionHistoryProps {
  versions: BrandingVersion[];
  currentVersion?: BrandingVersion;
  onRollback: (versionId: string) => Promise<void>;
  onViewDiff?: (versionId: string) => void;
  useHooks?: boolean;
}

export function VersionHistory({
  versions,
  currentVersion,
  onRollback,
  onViewDiff,
  useHooks = false,
}: VersionHistoryProps) {
  const { showToast } = useToast();
  const [expandedVersion, setExpandedVersion] = useState<string | null>(null);
  const [rollbackLoading, setRollbackLoading] = useState<string | null>(null);
  const [showDiffModal, setShowDiffModal] = useState(false);
  const [selectedVersionForDiff, setSelectedVersionForDiff] =
    useState<BrandingVersion | null>(null);

  const handleRollback = async (versionId: string) => {
    if (!confirm("Are you sure you want to rollback to this version?")) return;

    try {
      setRollbackLoading(versionId);
      await onRollback(versionId);
      showToast({
        title: "Success",
        description: "Successfully rolled back to this version",
      });
    } catch (error) {
      console.error("Rollback failed:", error);
      showToast({
        title: "Error",
        description: "Failed to rollback. Please try again.",
        variant: "destructive",
      });
    } finally {
      setRollbackLoading(null);
    }
  };

  const handleViewDiff = (version: BrandingVersion) => {
    setSelectedVersionForDiff(version);
    setShowDiffModal(true);
    onViewDiff?.(version.version_id);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getChangeSummary = (version: BrandingVersion) => {
    const changes = [];
    if (version.config.company_name) changes.push("Company name");
    if (version.config.primary_color) changes.push("Primary color");
    if (version.config.secondary_color) changes.push("Secondary color");
    if (version.config.logo_url) changes.push("Logo");
    if (version.config.font_family) changes.push("Font");
    return changes.length > 0 ? changes.join(", ") : "No changes";
  };

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">Version History</h3>

        {versions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No versions yet. Changes will be saved here.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {versions.map((version, index) => {
              const isCurrentVersion =
                currentVersion?.version_id === version.version_id;
              const isExpanded = expandedVersion === version.version_id;

              return (
                <div
                  key={version.version_id}
                  className="border rounded-lg overflow-hidden"
                >
                  {/* Version Header */}
                  <button
                    onClick={() =>
                      setExpandedVersion(isExpanded ? null : version.version_id)
                    }
                    className={`w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors ${
                      isCurrentVersion ? "bg-blue-50" : ""
                    }`}
                  >
                    <div className="flex items-center gap-3 flex-1 text-left">
                      <div>
                        {isExpanded ? (
                          <ChevronUp className="h-5 w-5 text-gray-400" />
                        ) : (
                          <ChevronDown className="h-5 w-5 text-gray-400" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">
                            Version {versions.length - index}
                          </span>
                          {isCurrentVersion && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              Current
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {formatDate(version.created_at)} by{" "}
                          {version.created_by}
                        </div>
                        {version.change_description && (
                          <div className="text-sm text-gray-700 mt-1">
                            {version.change_description}
                          </div>
                        )}
                      </div>
                    </div>
                  </button>

                  {/* Version Details */}
                  {isExpanded && (
                    <div className="border-t bg-gray-50 p-4 space-y-3">
                      {/* Changes Summary */}
                      <div>
                        <h4 className="text-sm font-semibold mb-2">Changes</h4>
                        <p className="text-sm text-gray-600">
                          {getChangeSummary(version)}
                        </p>
                      </div>

                      {/* Configuration Preview */}
                      <div>
                        <h4 className="text-sm font-semibold mb-2">
                          Configuration
                        </h4>
                        <div className="bg-white p-3 rounded text-sm space-y-1 font-mono text-xs">
                          {version.config.company_name && (
                            <div>
                              <span className="text-gray-600">Company:</span>{" "}
                              {version.config.company_name}
                            </div>
                          )}
                          {version.config.primary_color && (
                            <div className="flex items-center gap-2">
                              <span className="text-gray-600">Primary:</span>
                              <div
                                className="w-6 h-6 rounded border"
                                style={{
                                  backgroundColor: version.config.primary_color,
                                }}
                              />
                              {version.config.primary_color}
                            </div>
                          )}
                          {version.config.secondary_color && (
                            <div className="flex items-center gap-2">
                              <span className="text-gray-600">Secondary:</span>
                              <div
                                className="w-6 h-6 rounded border"
                                style={{
                                  backgroundColor:
                                    version.config.secondary_color,
                                }}
                              />
                              {version.config.secondary_color}
                            </div>
                          )}
                          {version.config.font_family && (
                            <div>
                              <span className="text-gray-600">Font:</span>{" "}
                              {version.config.font_family}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2 pt-2">
                        {!isCurrentVersion && (
                          <Button
                            size="sm"
                            onClick={() => handleRollback(version.version_id)}
                            disabled={rollbackLoading === version.version_id}
                            className="gap-2"
                          >
                            <RotateCcw className="h-4 w-4" />
                            {rollbackLoading === version.version_id
                              ? "Rolling back..."
                              : "Rollback"}
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleViewDiff(version)}
                          className="gap-2"
                        >
                          <Eye className="h-4 w-4" />
                          View Diff
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Diff Modal */}
      {showDiffModal && selectedVersionForDiff && (
        <Modal
          isOpen={showDiffModal}
          onClose={() => {
            setShowDiffModal(false);
            setSelectedVersionForDiff(null);
          }}
          size="lg"
        >
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Version Comparison</h2>

            <div className="grid grid-cols-2 gap-4">
              {/* Current Version */}
              <div>
                <h3 className="font-semibold text-sm mb-2">Current Version</h3>
                <div className="bg-gray-50 p-3 rounded text-sm space-y-1 font-mono text-xs max-h-96 overflow-y-auto">
                  {currentVersion ? (
                    <>
                      {currentVersion.config.company_name && (
                        <div>
                          <span className="text-gray-600">Company:</span>{" "}
                          {currentVersion.config.company_name}
                        </div>
                      )}
                      {currentVersion.config.primary_color && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-600">Primary:</span>
                          <div
                            className="w-4 h-4 rounded border"
                            style={{
                              backgroundColor:
                                currentVersion.config.primary_color,
                            }}
                          />
                          {currentVersion.config.primary_color}
                        </div>
                      )}
                      {currentVersion.config.secondary_color && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-600">Secondary:</span>
                          <div
                            className="w-4 h-4 rounded border"
                            style={{
                              backgroundColor:
                                currentVersion.config.secondary_color,
                            }}
                          />
                          {currentVersion.config.secondary_color}
                        </div>
                      )}
                      {currentVersion.config.font_family && (
                        <div>
                          <span className="text-gray-600">Font:</span>{" "}
                          {currentVersion.config.font_family}
                        </div>
                      )}
                    </>
                  ) : (
                    <p className="text-gray-500">No current version</p>
                  )}
                </div>
              </div>

              {/* Selected Version */}
              <div>
                <h3 className="font-semibold text-sm mb-2">
                  Selected Version (
                  {formatDate(selectedVersionForDiff.created_at)})
                </h3>
                <div className="bg-gray-50 p-3 rounded text-sm space-y-1 font-mono text-xs max-h-96 overflow-y-auto">
                  {selectedVersionForDiff.config.company_name && (
                    <div>
                      <span className="text-gray-600">Company:</span>{" "}
                      {selectedVersionForDiff.config.company_name}
                    </div>
                  )}
                  {selectedVersionForDiff.config.primary_color && (
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">Primary:</span>
                      <div
                        className="w-4 h-4 rounded border"
                        style={{
                          backgroundColor:
                            selectedVersionForDiff.config.primary_color,
                        }}
                      />
                      {selectedVersionForDiff.config.primary_color}
                    </div>
                  )}
                  {selectedVersionForDiff.config.secondary_color && (
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">Secondary:</span>
                      <div
                        className="w-4 h-4 rounded border"
                        style={{
                          backgroundColor:
                            selectedVersionForDiff.config.secondary_color,
                        }}
                      />
                      {selectedVersionForDiff.config.secondary_color}
                    </div>
                  )}
                  {selectedVersionForDiff.config.font_family && (
                    <div>
                      <span className="text-gray-600">Font:</span>{" "}
                      {selectedVersionForDiff.config.font_family}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Close Button */}
            <div className="flex justify-end gap-2 pt-4 border-t">
              <Button
                variant="outline"
                onClick={() => {
                  setShowDiffModal(false);
                  setSelectedVersionForDiff(null);
                }}
              >
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
