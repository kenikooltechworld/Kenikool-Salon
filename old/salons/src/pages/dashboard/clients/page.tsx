import { useState, lazy, Suspense } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  PlusIcon,
  SearchIcon,
  UsersIcon,
  AlertTriangleIcon,
  EditIcon,
  TrashIcon,
  CalendarIcon,
  DollarIcon,
  FilterIcon,
} from "@/components/icons";
import { useClients } from "@/lib/api/hooks/useClients";
import { Client, ClientFilter } from "@/lib/api/types";
import { useConfirmation } from "@/hooks/use-confirmation";

// Lazy load modal and filter panel
const ClientFormModal = lazy(() =>
  import("@/components/clients").then((mod) => ({
    default: mod.ClientFormModal,
  }))
);

const ClientFilterPanel = lazy(() =>
  import("@/components/clients/client-filter-panel").then((mod) => ({
    default: mod.ClientFilterPanel,
  }))
);

export default function ClientsPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client>();
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<
    Omit<ClientFilter, "offset" | "limit">
  >({});
  const pageSize = 20;

  const { confirm, ConfirmationDialog } = useConfirmation();

  // Fetch clients
  const { data, isLoading, error, refetch } = useClients({
    search: searchQuery || undefined,
    ...filters,
    limit: pageSize,
    offset: (currentPage - 1) * pageSize,
  });

  const clients = data?.items || [];
  const pageInfo = data?.page_info;

  const handleOpenModal = (client?: Client) => {
    setEditingClient(client);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setEditingClient(undefined);
    setIsModalOpen(false);
  };

  const handleDelete = async (id: string) => {
    const confirmed = await confirm({
      title: "Delete Client",
      message:
        "Are you sure you want to delete this client? This action cannot be undone.",
      confirmText: "Delete",
      cancelText: "Cancel",
      variant: "danger",
    });

    if (!confirmed) return;

    // TODO: Implement delete client functionality
    console.log("Delete client:", id);
  };

  const handleViewProfile = (clientId: string) => {
    navigate(`/dashboard/clients/${clientId}`);
  };

  const handleFilterChange = (
    newFilters: Omit<ClientFilter, "offset" | "limit">
  ) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const getSegmentColor = (segment: string) => {
    switch (segment) {
      case "vip":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200";
      case "regular":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "inactive":
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
      case "new":
      default:
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    }
  };

  if (error) {
    return (
      <div className="space-y-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading clients</h3>
            <p className="text-sm">{error.message}</p>
          </div>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Clients</h1>
          <p className="text-muted-foreground">
            Manage your client database and relationships
          </p>
        </div>
        <Button onClick={() => handleOpenModal()}>
          <PlusIcon size={20} />
          Add Client
        </Button>
      </div>

      {/* Search and Filters */}
      <Card className="p-4">
        <div className="space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <SearchIcon
                size={20}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              />
              <Input
                placeholder="Search by name, phone, or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <FilterIcon size={20} />
              Filters
            </Button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <Suspense fallback={<Spinner />}>
              <ClientFilterPanel
                filters={filters}
                onFilterChange={handleFilterChange}
              />
            </Suspense>
          )}
        </div>
      </Card>

      {/* Clients Table */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : clients.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <UsersIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No clients found
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery
                ? "Try adjusting your search"
                : "Get started by adding your first client"}
            </p>
            {!searchQuery && (
              <Button onClick={() => handleOpenModal()}>
                <PlusIcon size={20} />
                Add Client
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <>
          {/* Desktop Table View */}
          <Card className="hidden md:block overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted">
                  <tr>
                    <th className="text-left p-4 font-semibold text-foreground">
                      Name
                    </th>
                    <th className="text-left p-4 font-semibold text-foreground">
                      Contact
                    </th>
                    <th className="text-left p-4 font-semibold text-foreground">
                      Visits
                    </th>
                    <th className="text-left p-4 font-semibold text-foreground">
                      Total Spent
                    </th>
                    <th className="text-left p-4 font-semibold text-foreground">
                      Last Visit
                    </th>
                    <th className="text-right p-4 font-semibold text-foreground">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client) => (
                    <tr
                      key={client.id}
                      className="border-t border-border hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => handleViewProfile(client.id)}
                    >
                      <td className="p-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-foreground">
                              {client.name}
                            </p>
                            <Badge className={getSegmentColor(client.segment)}>
                              {client.segment}
                            </Badge>
                          </div>
                          {client.email && (
                            <p className="text-sm text-muted-foreground">
                              {client.email}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <div>
                          <p className="text-sm text-foreground">
                            {client.phone}
                          </p>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <CalendarIcon
                            size={16}
                            className="text-muted-foreground"
                          />
                          <span className="text-foreground">
                            {client.total_visits}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <DollarIcon
                            size={16}
                            className="text-muted-foreground"
                          />
                          <span className="font-medium text-foreground">
                            ₦{client.total_spent.toLocaleString()}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className="text-sm text-muted-foreground">
                          {client.last_visit_date
                            ? new Date(
                                client.last_visit_date
                              ).toLocaleDateString()
                            : "Never"}
                        </span>
                      </td>
                      <td className="p-4">
                        <div
                          className="flex items-center justify-end gap-2"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleOpenModal(client)}
                          >
                            <EditIcon size={16} />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(client.id)}
                          >
                            <TrashIcon size={16} />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Mobile Card View */}
          <div className="md:hidden space-y-4">
            {clients.map((client) => (
              <Card
                key={client.id}
                className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => handleViewProfile(client.id)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-foreground">
                        {client.name}
                      </h3>
                      <Badge className={getSegmentColor(client.segment)}>
                        {client.segment}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {client.phone}
                    </p>
                    {client.email && (
                      <p className="text-sm text-muted-foreground">
                        {client.email}
                      </p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Visits</p>
                    <p className="font-medium text-foreground">
                      {client.total_visits}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">
                      Total Spent
                    </p>
                    <p className="font-medium text-foreground">
                      ₦{client.total_spent.toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-border">
                  <span className="text-xs text-muted-foreground">
                    Last visit:{" "}
                    {client.last_visit_date
                      ? new Date(client.last_visit_date).toLocaleDateString()
                      : "Never"}
                  </span>
                  <div
                    className="flex items-center gap-2"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleOpenModal(client)}
                    >
                      <EditIcon size={16} />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(client.id)}
                    >
                      <TrashIcon size={16} />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {pageInfo &&
            (pageInfo.has_next_page || pageInfo.has_previous_page) && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  disabled={!pageInfo.has_previous_page}
                  onClick={() => setCurrentPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {currentPage}
                </span>
                <Button
                  variant="outline"
                  disabled={!pageInfo.has_next_page}
                  onClick={() => setCurrentPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            )}
        </>
      )}

      {/* Client Form Modal */}
      <Suspense fallback={null}>
        <ClientFormModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onSuccess={refetch}
          client={editingClient}
        />
      </Suspense>

      {/* Confirmation Dialog */}
      <ConfirmationDialog />
    </div>
  );
}
