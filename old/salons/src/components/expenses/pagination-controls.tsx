import { Button } from "@/components/ui/button";
import { Select, SelectItem } from "@/components/ui/select";
import { ChevronLeftIcon, ChevronRightIcon } from "@/components/icons";

interface PaginationControlsProps {
  currentPage: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

export function PaginationControls({
  currentPage,
  pageSize,
  total,
  onPageChange,
  onPageSizeChange,
}: PaginationControlsProps) {
  const totalPages = Math.ceil(total / pageSize);
  const hasPreviousPage = currentPage > 1;
  const hasNextPage = currentPage < totalPages;

  const handlePreviousPage = () => {
    if (hasPreviousPage) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (hasNextPage) {
      onPageChange(currentPage + 1);
    }
  };

  const handlePageSizeChange = (value: string) => {
    onPageSizeChange(parseInt(value));
    onPageChange(1);
  };

  return (
    <div className="flex items-center justify-between p-4 bg-[var(--muted)] rounded-[var(--radius-md)]">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-[var(--muted-foreground)]">
            Items per page:
          </span>
          <Select
            value={pageSize.toString()}
            onValueChange={handlePageSizeChange}
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <SelectItem key={size} value={size.toString()}>
                {size}
              </SelectItem>
            ))}
          </Select>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handlePreviousPage}
          disabled={!hasPreviousPage}
        >
          <ChevronLeftIcon size={16} />
        </Button>

        <span className="text-sm text-[var(--muted-foreground)] px-2">
          Page {currentPage} of {totalPages || 1}
        </span>

        <Button
          variant="outline"
          size="sm"
          onClick={handleNextPage}
          disabled={!hasNextPage}
        >
          <ChevronRightIcon size={16} />
        </Button>
      </div>

      <div className="text-sm text-[var(--muted-foreground)]">
        Total: {total} items
      </div>
    </div>
  );
}
