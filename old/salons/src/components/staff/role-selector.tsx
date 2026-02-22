"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface RoleSelectorProps {
  staffId: string;
  staffName: string;
  currentRole: string;
  isOpen: boolean;
  onClose: () => void;
  onRoleUpdated?: () => void;
}

interface Role {
  role: string;
  permissions: string[];
  permission_count: number;
}

export function RoleSelector({
  staffId,
  staffName,
  currentRole,
  isOpen,
  onClose,
  onRoleUpdated,
}: RoleSelectorProps) {
  const [selectedRole, setSelectedRole] = useState(currentRole);

  // Fetch available roles
  const { data: rolesData } = useQuery({
    queryKey: ["staff-roles"],
    queryFn: async () => {
      const res = await fetch("/api/staff/roles");
      if (!res.ok) throw new Error("Failed to fetch roles");
      return res.json();
    },
  });

  const roles: Role[] = rolesData?.data || [];

  // Update role mutation
  const updateRoleMutation = useMutation({
    mutationFn: async (newRole: string) => {
      const res = await fetch(`/api/staff/roles/${staffId}/role`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: newRole }),
      });
      if (!res.ok) throw new Error("Failed to update role");
      return res.json();
    },
    onSuccess: () => {
      toast.success(`Role updated to ${selectedRole}`);
      onRoleUpdated?.();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to update role");
    },
  });

  const selectedRoleData = roles.find((r) => r.role === selectedRole);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Update Staff Role - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Current Role */}
          <div>
            <label className="text-sm font-medium">Current Role</label>
            <Badge className="mt-2" variant="secondary">
              {currentRole}
            </Badge>
          </div>

          {/* Role Selection */}
          <div>
            <label htmlFor="role-select" className="text-sm font-medium">
              Select New Role
            </label>
            <Select value={selectedRole} onValueChange={setSelectedRole}>
              <SelectTrigger id="role-select" className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {roles.map((role) => (
                  <SelectItem key={role.role} value={role.role}>
                    <div className="flex items-center gap-2">
                      <span className="capitalize">{role.role}</span>
                      <span className="text-xs text-muted-foreground">
                        ({role.permission_count} permissions)
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Role Permissions */}
          {selectedRoleData && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  Permissions for {selectedRole}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {selectedRoleData.permissions.map((permission) => (
                    <div
                      key={permission}
                      className="text-xs bg-muted p-2 rounded flex items-center gap-2"
                    >
                      <span className="w-1.5 h-1.5 bg-primary rounded-full" />
                      {permission}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Warning if changing role */}
          {selectedRole !== currentRole && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
              ⚠️ Changing the role will update permissions immediately. The
              staff member will have access to new features on their next login.
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => updateRoleMutation.mutate(selectedRole)}
            disabled={
              selectedRole === currentRole || updateRoleMutation.isPending
            }
          >
            {updateRoleMutation.isPending ? "Updating..." : "Update Role"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
