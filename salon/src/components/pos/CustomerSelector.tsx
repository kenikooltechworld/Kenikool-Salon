import { useState } from "react";
import { useCustomers } from "@/hooks/useCustomers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Modal } from "@/components/ui/modal";
import { SearchIcon, XIcon } from "@/components/icons";

interface CustomerSelectorProps {
  onSelect: (customerId: string, customerName: string) => void;
  selectedCustomerId?: string;
  selectedCustomerName?: string;
}

export default function CustomerSelector({
  onSelect,
  selectedCustomerId,
  selectedCustomerName,
}: CustomerSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const { data: customersData, isLoading } = useCustomers({
    pageSize: 50,
  });

  const customers = customersData?.customers || [];
  const filtered = customers.filter(
    (c) =>
      c.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.phone?.includes(searchTerm),
  );

  const handleSelect = (customerId: string, customerName: string) => {
    onSelect(customerId, customerName);
    setIsOpen(false);
    setSearchTerm("");
  };

  const handleClear = () => {
    onSelect("", "");
  };

  return (
    <>
      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={() => setIsOpen(true)}
          className="flex-1 justify-start text-left"
        >
          <SearchIcon size={16} className="mr-2" />
          {selectedCustomerName || "Select Customer"}
        </Button>
        {selectedCustomerId && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="text-destructive hover:text-destructive"
          >
            <XIcon size={16} />
          </Button>
        )}
      </div>

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Select Customer</h2>

          <Input
            placeholder="Search by name, email, or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            autoFocus
          />

          <div className="max-h-96 overflow-y-auto space-y-2">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : filtered.length === 0 ? (
              <Card className="p-4 text-center text-muted-foreground">
                No customers found
              </Card>
            ) : (
              filtered.map((customer) => (
                <Card
                  key={customer.id}
                  className="p-3 cursor-pointer hover:bg-muted transition"
                  onClick={() => handleSelect(customer.id, customer.name)}
                >
                  <p className="font-medium text-foreground">{customer.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {customer.email}
                  </p>
                  {customer.phone && (
                    <p className="text-sm text-muted-foreground">
                      {customer.phone}
                    </p>
                  )}
                </Card>
              ))
            )}
          </div>

          <Button
            variant="outline"
            onClick={() => setIsOpen(false)}
            className="w-full"
          >
            Close
          </Button>
        </div>
      </Modal>
    </>
  );
}
