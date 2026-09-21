import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { Checkbox } from "@/components/ui/checkbox";

interface StaffOption {
  id: string;
  firstName: string;
  lastName: string;
  specialties: string[];
}

interface StaffMultiSelectProps {
  value: string[];
  onChange: (ids: string[]) => void;
}

export function StaffMultiSelect({ value, onChange }: StaffMultiSelectProps) {
  const { data: staffList, isLoading } = useQuery<StaffOption[]>({
    queryKey: ["staff-list"],
    queryFn: async () => {
      const { data } = await apiClient.get<{ staff: StaffOption[] }>("/staff", {
        params: { page_size: 100 },
      });
      return data?.staff || [];
    },
  });

  const toggle = (id: string) => {
    onChange(value.includes(id) ? value.filter((v) => v !== id) : [...value, id]);
  };

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-foreground">Assigned Staff</p>
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading staff...</p>
      ) : !staffList?.length ? (
        <p className="text-sm text-muted-foreground">No staff members found.</p>
      ) : (
        <div className="max-h-48 overflow-y-auto rounded-md border border-border divide-y">
          {staffList.map((s) => {
            const id = s.id;
            const checked = value.includes(id);
            return (
              <label
                key={id}
                className={`flex items-center gap-3 px-3 py-2 cursor-pointer transition-colors ${
                  checked ? "bg-primary/5" : "hover:bg-muted/50"
                }`}
              >
                <Checkbox
                  checked={checked}
                  onCheckedChange={() => toggle(id)}
                />
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium text-foreground truncate block">
                    {s.firstName} {s.lastName}
                  </span>
                  {s.specialties?.length > 0 && (
                    <span className="text-xs text-muted-foreground truncate block">
                      {s.specialties.join(", ")}
                    </span>
                  )}
                </div>
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
}
