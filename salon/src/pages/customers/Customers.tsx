import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import {
  PlusIcon,
  SearchIcon,
  TrashIcon,
  EditIcon,
  AlertCircleIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCustomers,
  useDeleteCustomer,
  type Customer,
} from "@/hooks/useCustomers";
import { CreateCustomerModal } from "@/components/customers/CreateCustomerModal";
import { EditCustomerModal } from "@/components/customers/EditCustomerModal";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function Customers() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(
    null,
  );
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [expandedTable, setExpandedTable] = useState(false);

  const filters = useMemo(
    () => ({
      search: searchTerm || undefined,
      status: statusFilter !== "all" ? statusFilter : undefined,
      page: currentPage,
      page_size: pageSize,
    }),
    [searchTerm, statusFilter, currentPage, pageSize],
  );

  const { data, isLoading, error } = useCustomers(filters);
  const deleteMutation = useDeleteCustomer();

  const handleEdit = (customerId: string) => {
    setSelectedCustomerId(customerId);
    setEditModalOpen(true);
  };

  const handleDelete = async (customerId: string) => {
    try {
      await deleteMutation.mutateAsync(customerId);
      showToast({
        variant: "success",
        title: "Success",
        description: "Customer has been deleted successfully",
      });
      setDeleteConfirm(null);
    } catch (error) {
      showToast({
        variant: "error",
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete customer",
      });
    }
  };

  const handleRefresh = () => {
    setCurrentPage(1);
  };

  const customers = data?.customers || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="w-full min-h-screen space-y-4 sm:space-y-5 md:space-y-6 p-3 sm:p-4 md:p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl sm:text-2xl md:text-3xl font-bold text-foreground truncate">
            Customers
          </h2>
          <p className="text-sm sm:text-sm md:text-base text-muted-foreground mt-2 truncate">
            Manage your salon customers ({total} total)
          </p>
        </div>
        <Button
          onClick={() => setCreateModalOpen(true)}
          className="gap-2 w-full sm:w-auto cursor-pointer flex-shrink-0"
          size="sm"
        >
          <PlusIcon size={16} />
          <span className="hidden xs:inline">Add Customer</span>
          <span className="xs:hidden">Add</span>
        </Button>
      </div>

      {/* Error State */}
      {error && (
        <div className="flex items-start gap-2 xs:gap-3 p-2 xs:p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircleIcon className="w-4 h-4 xs:w-5 xs:h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="min-w-0 flex-1">
            <p className="text-xs xs:text-sm font-medium text-red-800">
              Failed to load customers
            </p>
            <p className="text-xs text-red-700 break-words">
              {error instanceof Error ? error.message : "Please try again"}
            </p>
          </div>
        </div>
      )}

      {/* Search & Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 xs:gap-4 sm:gap-4">
        <div className="relative w-full">
          <SearchIcon
            size={18}
            className="absolute left-3 xs:left-3 top-1/2 -translate-y-1/2 text-muted-foreground flex-shrink-0"
          />
          <input
            type="text"
            placeholder="Search by name or phone..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full pl-10 xs:pl-10 pr-4 xs:pr-4 py-3 xs:py-3 text-sm xs:text-base border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <Select
          value={statusFilter}
          onValueChange={(value) => {
            setStatusFilter(value);
            setCurrentPage(1);
          }}
        >
          <SelectTrigger className="w-full text-sm xs:text-base py-3 h-auto">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Customers Table - Responsive */}
      <div className="bg-card border border-border rounded-lg overflow-hidden shadow-sm">
        {/* Mobile Expand Button */}
        <div className="sm:hidden flex items-center justify-between p-4 border-b border-border bg-muted/50">
          <span className="text-sm font-medium text-foreground">
            {expandedTable ? "Full Table View" : "Compact View"}
          </span>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setExpandedTable(!expandedTable)}
            className="text-xs h-8"
          >
            {expandedTable ? "Collapse" : "Expand"}
          </Button>
        </div>

        {/* Desktop Table View & Expanded Mobile View */}
        <div
          className={`${expandedTable ? "block" : "hidden sm:block"} overflow-x-auto`}
        >
          <table className="w-full text-sm sm:text-base">
            <thead className="bg-muted border-b border-border">
              <tr>
                <th className="px-4 sm:px-6 py-3 sm:py-4 text-left font-semibold text-foreground whitespace-nowrap">
                  Name
                </th>
                <th className="px-4 sm:px-6 py-3 sm:py-4 text-left font-semibold text-foreground whitespace-nowrap">
                  Email
                </th>
                <th className="px-4 sm:px-6 py-3 sm:py-4 text-left font-semibold text-foreground whitespace-nowrap">
                  Phone
                </th>
                <th className="px-4 sm:px-6 py-3 sm:py-4 text-left font-semibold text-foreground whitespace-nowrap">
                  Status
                </th>
                <th className="px-4 sm:px-6 py-3 sm:py-4 text-left font-semibold text-foreground whitespace-nowrap">
                  Created
                </th>
                <th className="px-4 sm:px-6 py-3 sm:py-4 text-right font-semibold text-foreground whitespace-nowrap">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="hover:bg-muted/50 transition">
                    <td className="px-4 sm:px-6 py-4 sm:py-5">
                      <Skeleton className="h-5 w-40" />
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5">
                      <Skeleton className="h-5 w-48" />
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5">
                      <Skeleton className="h-5 w-36" />
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5">
                      <Skeleton className="h-5 w-20" />
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5">
                      <Skeleton className="h-5 w-32" />
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5">
                      <Skeleton className="h-9 w-20" />
                    </td>
                  </tr>
                ))
              ) : customers.length > 0 ? (
                customers.map((customer: Customer) => (
                  <tr
                    key={customer.id}
                    className="hover:bg-muted/50 transition cursor-pointer"
                    onClick={() => navigate(`/customers/${customer.id}`)}
                  >
                    <td className="px-4 sm:px-6 py-4 sm:py-5 text-foreground whitespace-nowrap">
                      <p className="font-semibold text-sm sm:text-base">
                        {customer.firstName} {customer.lastName}
                      </p>
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5 text-muted-foreground text-sm sm:text-base truncate">
                      {customer.email}
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5 text-muted-foreground text-sm sm:text-base whitespace-nowrap">
                      {customer.phone}
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5 whitespace-nowrap">
                      <span
                        className={`px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium ${
                          customer.status === "active"
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {customer.status === "active" ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5 text-muted-foreground text-sm sm:text-base whitespace-nowrap">
                      {new Date(customer.createdAt).toLocaleDateString()}
                    </td>
                    <td className="px-4 sm:px-6 py-4 sm:py-5 text-right">
                      <div className="flex items-center justify-end gap-2 sm:gap-3 whitespace-nowrap">
                        <button
                          onClick={() => handleEdit(customer.id)}
                          className="p-2 sm:p-2.5 hover:bg-muted rounded-lg transition cursor-pointer"
                          title="Edit customer"
                        >
                          <EditIcon
                            size={18}
                            className="text-muted-foreground"
                          />
                        </button>
                        <div className="relative">
                          <button
                            onClick={() =>
                              setDeleteConfirm(
                                deleteConfirm === customer.id
                                  ? null
                                  : customer.id,
                              )
                            }
                            className="p-2 sm:p-2.5 hover:bg-destructive/10 rounded-lg transition cursor-pointer"
                            title="Delete customer"
                          >
                            <TrashIcon size={18} className="text-destructive" />
                          </button>

                          {deleteConfirm === customer.id && (
                            <div className="absolute right-0 top-full mt-2 sm:mt-3 bg-card border border-border rounded-lg shadow-lg p-3 sm:p-4 z-10 w-56">
                              <div className="flex items-start gap-3 mb-3 sm:mb-4">
                                <AlertTriangleIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                                <p className="text-sm sm:text-base text-foreground font-medium">
                                  Are you sure? This action cannot be undone.
                                </p>
                              </div>
                              <div className="flex gap-2 sm:gap-3">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setDeleteConfirm(null)}
                                  className="flex-1 text-sm sm:text-base h-9 sm:h-10"
                                >
                                  Cancel
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleDelete(customer.id)}
                                  disabled={deleteMutation.isPending}
                                  className="flex-1 text-sm sm:text-base h-9 sm:h-10"
                                >
                                  {deleteMutation.isPending ? "..." : "Delete"}
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 sm:px-6 py-8 sm:py-10 text-center text-muted-foreground text-sm sm:text-base font-medium"
                  >
                    No customers found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Mobile Card View */}
        <div className={`${expandedTable ? "hidden" : "sm:hidden"}`}>
          {isLoading ? (
            <div className="space-y-3 p-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="bg-muted rounded-lg p-4 space-y-3">
                  <Skeleton className="h-6 w-40" />
                  <Skeleton className="h-5 w-48" />
                  <Skeleton className="h-5 w-32" />
                  <div className="flex gap-2 justify-end pt-2">
                    <Skeleton className="h-9 w-9" />
                    <Skeleton className="h-9 w-9" />
                  </div>
                </div>
              ))}
            </div>
          ) : customers.length > 0 ? (
            <div className="space-y-3 p-4">
              {customers.map((customer: Customer) => (
                <div
                  key={customer.id}
                  className="bg-muted rounded-lg p-4 space-y-2 cursor-pointer hover:bg-muted/80 transition"
                  onClick={() => navigate(`/customers/${customer.id}`)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-base text-foreground truncate">
                        {customer.firstName} {customer.lastName}
                      </p>
                      <p className="text-sm text-muted-foreground truncate mt-1">
                        {customer.email}
                      </p>
                      <p className="text-sm text-muted-foreground truncate mt-1">
                        {customer.phone}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <button
                        onClick={() => handleEdit(customer.id)}
                        className="p-2 hover:bg-background rounded-lg transition cursor-pointer"
                        title="Edit customer"
                      >
                        <EditIcon size={18} className="text-muted-foreground" />
                      </button>
                      <div className="relative">
                        <button
                          onClick={() =>
                            setDeleteConfirm(
                              deleteConfirm === customer.id
                                ? null
                                : customer.id,
                            )
                          }
                          className="p-2 hover:bg-destructive/10 rounded-lg transition cursor-pointer"
                          title="Delete customer"
                        >
                          <TrashIcon size={18} className="text-destructive" />
                        </button>

                        {deleteConfirm === customer.id && (
                          <div className="absolute right-0 top-full mt-2 bg-card border border-border rounded-lg shadow-lg p-3 z-10 w-56">
                            <div className="flex items-start gap-3 mb-3">
                              <AlertTriangleIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                              <p className="text-sm text-foreground font-medium">
                                Are you sure? This action cannot be undone.
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setDeleteConfirm(null)}
                                className="flex-1 text-sm h-9"
                              >
                                Cancel
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => handleDelete(customer.id)}
                                disabled={deleteMutation.isPending}
                                className="flex-1 text-sm h-9"
                              >
                                {deleteMutation.isPending ? "..." : "Delete"}
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-2 border-t border-border">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap ${
                        customer.status === "active"
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {customer.status === "active" ? "Active" : "Inactive"}
                    </span>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {new Date(customer.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="px-4 py-8 text-center text-muted-foreground text-sm font-medium">
              No customers found
            </div>
          )}
        </div>
      </div>

      {/* Pagination */}
      {!isLoading && customers.length > 0 && (
        <div className="flex flex-col gap-4 xs:gap-5 sm:gap-6 p-4 xs:p-5 sm:p-6 bg-muted/50 rounded-lg border border-border">
          <div className="text-sm xs:text-base text-muted-foreground text-center sm:text-left font-medium">
            Showing {(currentPage - 1) * pageSize + 1} to{" "}
            {Math.min(currentPage * pageSize, total)} of {total} customers
          </div>

          <div className="flex flex-col xs:flex-row items-center justify-center xs:justify-between gap-3 xs:gap-4 sm:gap-5 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="text-sm xs:text-base h-9 xs:h-10 px-4 xs:px-5"
            >
              Previous
            </Button>

            <div className="flex items-center gap-2 xs:gap-3 flex-wrap justify-center">
              {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                const pageNum = i + 1;
                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "primary" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(pageNum)}
                    className="text-sm xs:text-base h-9 xs:h-10 w-9 xs:w-10 p-0"
                  >
                    {pageNum}
                  </Button>
                );
              })}
              {totalPages > 5 && (
                <span className="text-muted-foreground text-sm xs:text-base font-medium">
                  ...
                </span>
              )}
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setCurrentPage(Math.min(totalPages, currentPage + 1))
              }
              disabled={currentPage === totalPages}
              className="text-sm xs:text-base h-9 xs:h-10 px-4 xs:px-5"
            >
              Next
            </Button>

            <Select
              value={pageSize.toString()}
              onValueChange={(value) => {
                setPageSize(parseInt(value));
                setCurrentPage(1);
              }}
            >
              <SelectTrigger className="w-24 xs:w-28 text-sm xs:text-base h-9 xs:h-10">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="25">25</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      )}

      {/* Modals */}
      <CreateCustomerModal
        open={createModalOpen}
        onOpenChange={setCreateModalOpen}
        onSuccess={() => {
          handleRefresh();
          showToast({
            variant: "success",
            title: "Success",
            description: "Customer has been created successfully",
          });
        }}
      />

      <EditCustomerModal
        customerId={selectedCustomerId}
        open={editModalOpen}
        onOpenChange={setEditModalOpen}
        onSuccess={() => {
          handleRefresh();
          showToast({
            variant: "success",
            title: "Success",
            description: "Customer has been updated successfully",
          });
        }}
      />
    </div>
  );
}
