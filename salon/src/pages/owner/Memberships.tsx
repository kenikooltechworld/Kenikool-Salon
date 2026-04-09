import { useState } from "react";
import {
  PlusIcon,
  EditIcon,
  TrashIcon,
  UsersIcon,
  TrendingUpIcon,
  SearchIcon,
} from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Select, SelectItem } from "@/components/ui/select";
import {
  useMembershipTiers,
  useDeleteMembershipTier,
  useAllMemberships,
  useMembershipStats,
} from "@/hooks/useMemberships";
import { formatDate } from "@/lib/utils/date";

export default function Memberships() {
  const { data: tiers, isLoading: tiersLoading } = useMembershipTiers();
  const { data: memberships, isLoading: membershipsLoading } =
    useAllMemberships();
  const { data: stats, isLoading: statsLoading } = useMembershipStats();
  const deleteTier = useDeleteMembershipTier();

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [tierFilter, setTierFilter] = useState<string>("all");

  const handleDelete = async (tierId: string) => {
    if (!confirm("Are you sure you want to delete this membership tier?"))
      return;

    try {
      await deleteTier.mutateAsync(tierId);
      alert("Membership tier deleted successfully");
    } catch (error) {
      alert("Failed to delete membership tier");
    }
  };

  // Filter memberships
  const filteredMemberships = memberships?.filter((m) => {
    if (statusFilter !== "all" && m.status !== statusFilter) return false;
    if (tierFilter !== "all" && m.tier_id !== tierFilter) return false;
    if (
      searchQuery &&
      !m.tier_name.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  if (tiersLoading || membershipsLoading || statsLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Membership Management</h1>
          <p className="text-muted-foreground">
            Manage tiers, members, and subscription analytics
          </p>
        </div>
      </div>

      <Tabs defaultValue="tiers" className="space-y-6">
        <TabsList>
          <TabsTrigger value="tiers">Membership Tiers</TabsTrigger>
          <TabsTrigger value="members">Active Members</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Membership Tiers Tab */}
        <TabsContent value="tiers" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Membership Tiers</h2>
            <Button>
              <PlusIcon size={16} className="mr-2" />
              Create Tier
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tiers?.map((tier) => (
              <Card key={tier.id} className="p-6">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-bold">{tier.name}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {tier.description}
                      </p>
                    </div>
                    <Badge variant={tier.is_active ? "default" : "secondary"}>
                      {tier.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-bold">
                        ₦{tier.monthly_price.toLocaleString()}
                      </span>
                      <span className="text-muted-foreground">/month</span>
                    </div>
                    {tier.annual_price && (
                      <div className="text-sm text-muted-foreground">
                        or ₦{tier.annual_price.toLocaleString()}/year
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Badge variant="outline">
                        {tier.discount_percentage}% discount
                      </Badge>
                      {tier.priority_booking && (
                        <Badge variant="outline">Priority booking</Badge>
                      )}
                    </div>
                    <div className="text-sm">
                      {tier.free_services_per_month} free services/month
                    </div>
                    {tier.rollover_unused && (
                      <div className="text-sm text-green-600">
                        Unused services rollover
                      </div>
                    )}
                  </div>

                  {tier.benefits.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-sm font-medium">Benefits:</div>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {tier.benefits.map((benefit, idx) => (
                          <li key={idx}>• {benefit.description}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {tier.max_members && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <UsersIcon size={16} />
                      Max {tier.max_members} members
                    </div>
                  )}

                  <div className="flex gap-2 pt-4 border-t">
                    <Button variant="outline" size="sm" className="flex-1">
                      <EditIcon size={16} className="mr-2" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(tier.id)}
                    >
                      <TrashIcon size={16} />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {(!tiers || tiers.length === 0) && (
            <Card className="p-12 text-center">
              <UsersIcon
                size={48}
                className="mx-auto text-muted-foreground mb-4"
              />
              <h3 className="text-lg font-semibold mb-2">
                No membership tiers yet
              </h3>
              <p className="text-muted-foreground mb-4">
                Create your first membership tier to start offering
                subscriptions
              </p>
              <Button>
                <PlusIcon size={16} className="mr-2" />
                Create First Tier
              </Button>
            </Card>
          )}
        </TabsContent>

        {/* Active Members Tab */}
        <TabsContent value="members" className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 flex items-center gap-4">
              <div className="relative flex-1 max-w-md">
                <SearchIcon
                  size={16}
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
                />
                <Input
                  placeholder="Search by tier name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <option value="all">All Statuses</option>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </Select>
              <Select value={tierFilter} onValueChange={setTierFilter}>
                <option value="all">All Tiers</option>
                {tiers?.map((tier) => (
                  <SelectItem key={tier.id} value={tier.id}>
                    {tier.name}
                  </SelectItem>
                ))}
              </Select>
            </div>
            <Button>
              <PlusIcon size={16} className="mr-2" />
              Assign Membership
            </Button>
          </div>

          <Card>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b">
                  <tr className="text-left">
                    <th className="p-4 font-medium">Customer ID</th>
                    <th className="p-4 font-medium">Tier</th>
                    <th className="p-4 font-medium">Status</th>
                    <th className="p-4 font-medium">Services Remaining</th>
                    <th className="p-4 font-medium">Next Billing</th>
                    <th className="p-4 font-medium">Start Date</th>
                    <th className="p-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredMemberships?.map((membership) => (
                    <tr
                      key={membership.id}
                      className="border-b hover:bg-muted/50"
                    >
                      <td className="p-4 font-mono text-sm">
                        {membership.customer_id.slice(-8)}
                      </td>
                      <td className="p-4">{membership.tier_name}</td>
                      <td className="p-4">
                        <Badge
                          variant={
                            membership.status === "active"
                              ? "default"
                              : membership.status === "paused"
                                ? "secondary"
                                : "destructive"
                          }
                        >
                          {membership.status}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">
                            {membership.services_remaining_this_cycle}
                          </span>
                          <span className="text-sm text-muted-foreground">
                            ({membership.services_used_this_cycle} used)
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        {formatDate(membership.next_billing_date)}
                      </td>
                      <td className="p-4">
                        {formatDate(membership.start_date)}
                      </td>
                      <td className="p-4">
                        <Button variant="ghost" size="sm">
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {(!filteredMemberships || filteredMemberships.length === 0) && (
              <div className="p-12 text-center">
                <UsersIcon
                  size={48}
                  className="mx-auto text-muted-foreground mb-4"
                />
                <h3 className="text-lg font-semibold mb-2">No members found</h3>
                <p className="text-muted-foreground">
                  {searchQuery || statusFilter !== "all" || tierFilter !== "all"
                    ? "Try adjusting your filters"
                    : "No active memberships yet"}
                </p>
              </div>
            )}
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <h2 className="text-xl font-semibold">Membership Analytics</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Members</p>
                  <p className="text-3xl font-bold mt-2">
                    {stats?.total_members || 0}
                  </p>
                </div>
                <UsersIcon size={32} className="text-blue-500" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">
                    Active Members
                  </p>
                  <p className="text-3xl font-bold mt-2 text-green-600">
                    {stats?.total_active || 0}
                  </p>
                </div>
                <TrendingUpIcon size={32} className="text-green-500" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">
                    Paused Members
                  </p>
                  <p className="text-3xl font-bold mt-2 text-yellow-600">
                    {stats?.total_paused || 0}
                  </p>
                </div>
                <UsersIcon size={32} className="text-yellow-500" />
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">
                    Monthly Revenue
                  </p>
                  <p className="text-3xl font-bold mt-2">
                    ₦{(stats?.monthly_revenue || 0).toLocaleString()}
                  </p>
                </div>
                <TrendingUpIcon size={32} className="text-blue-500" />
              </div>
            </Card>
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">
              Membership Distribution
            </h3>
            <div className="space-y-4">
              {tiers?.map((tier) => {
                const tierMemberships = memberships?.filter(
                  (m) => m.tier_id === tier.id && m.status === "active",
                );
                const count = tierMemberships?.length || 0;
                const percentage =
                  (stats?.total_active ?? 0) > 0
                    ? ((count / (stats?.total_active ?? 1)) * 100).toFixed(1)
                    : "0";

                return (
                  <div key={tier.id} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{tier.name}</span>
                      <span className="text-sm text-muted-foreground">
                        {count} members ({percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
