import { useState } from "react";
import {
  useGiftCards,
  useCancelGiftCard,
  useGiftCard,
  useGiftCardTransactions,
} from "@/hooks/useGiftCards";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  CreditCardIcon as CreditCard,
  SearchIcon as Search,
  X,
  EyeIcon as Eye,
  Ban,
} from "@/components/icons";
import { format } from "date-fns";

export default function GiftCards() {
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGiftCardId, setSelectedGiftCardId] = useState<string | null>(
    null,
  );
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState("");

  const { data: giftCardsData, isLoading } = useGiftCards(
    statusFilter || undefined,
  );
  const { data: selectedGiftCard } = useGiftCard(selectedGiftCardId);
  const { data: transactions } = useGiftCardTransactions(selectedGiftCardId);
  const cancelGiftCard = useCancelGiftCard();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "redeemed":
        return "bg-gray-100 text-gray-800";
      case "expired":
        return "bg-red-100 text-red-800";
      case "cancelled":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const filteredGiftCards = giftCardsData?.gift_cards.filter((gc) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      gc.code.toLowerCase().includes(query) ||
      gc.purchased_by_name?.toLowerCase().includes(query) ||
      gc.purchased_by_email?.toLowerCase().includes(query) ||
      gc.recipient_name?.toLowerCase().includes(query) ||
      gc.recipient_email?.toLowerCase().includes(query)
    );
  });

  const handleCancelGiftCard = async () => {
    if (!selectedGiftCardId || !cancelReason.trim()) return;

    try {
      await cancelGiftCard.mutateAsync({
        giftCardId: selectedGiftCardId,
        reason: cancelReason,
      });
      setCancelDialogOpen(false);
      setCancelReason("");
      setSelectedGiftCardId(null);
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to cancel gift card");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gift Cards</h1>
          <p className="text-gray-600">
            Manage gift cards and track redemptions
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by code, purchaser, or recipient..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="redeemed">Redeemed</SelectItem>
                <SelectItem value="expired">Expired</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Gift Cards Table */}
      <Card>
        <CardHeader>
          <CardTitle>Gift Cards ({giftCardsData?.total || 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">Loading...</div>
          ) : filteredGiftCards && filteredGiftCards.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Balance</TableHead>
                  <TableHead>Purchaser</TableHead>
                  <TableHead>Recipient</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Purchase Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredGiftCards.map((giftCard) => (
                  <TableRow key={giftCard.id}>
                    <TableCell className="font-mono">{giftCard.code}</TableCell>
                    <TableCell>
                      ₦{giftCard.initial_amount.toLocaleString()}
                    </TableCell>
                    <TableCell className="font-semibold">
                      ₦{giftCard.current_balance.toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">
                          {giftCard.purchased_by_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {giftCard.purchased_by_email}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {giftCard.recipient_name ? (
                        <div>
                          <div className="font-medium">
                            {giftCard.recipient_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {giftCard.recipient_email}
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(giftCard.status)}>
                        {giftCard.status.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {format(new Date(giftCard.purchase_date), "PP")}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedGiftCardId(giftCard.id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        {giftCard.status === "active" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedGiftCardId(giftCard.id);
                              setCancelDialogOpen(true);
                            }}
                          >
                            <Ban className="h-4 w-4 text-red-600" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No gift cards found
            </div>
          )}
        </CardContent>
      </Card>

      {/* Gift Card Details Dialog */}
      <Dialog
        open={!!selectedGiftCardId && !cancelDialogOpen}
        onOpenChange={() => setSelectedGiftCardId(null)}
      >
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Gift Card Details</DialogTitle>
          </DialogHeader>
          {selectedGiftCard && (
            <Tabs defaultValue="details">
              <TabsList>
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="transactions">Transactions</TabsTrigger>
              </TabsList>

              <TabsContent value="details" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm text-gray-600">Code</Label>
                    <p className="font-mono font-semibold">
                      {selectedGiftCard.code}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm text-gray-600">Status</Label>
                    <Badge className={getStatusColor(selectedGiftCard.status)}>
                      {selectedGiftCard.status.toUpperCase()}
                    </Badge>
                  </div>
                  <div>
                    <Label className="text-sm text-gray-600">
                      Initial Amount
                    </Label>
                    <p className="font-semibold">
                      ₦{selectedGiftCard.initial_amount.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm text-gray-600">
                      Current Balance
                    </Label>
                    <p className="font-semibold text-blue-600">
                      ₦{selectedGiftCard.current_balance.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm text-gray-600">
                      Purchase Date
                    </Label>
                    <p>
                      {format(new Date(selectedGiftCard.purchase_date), "PPP")}
                    </p>
                  </div>
                  {selectedGiftCard.expiry_date && (
                    <div>
                      <Label className="text-sm text-gray-600">
                        Expiry Date
                      </Label>
                      <p>
                        {format(new Date(selectedGiftCard.expiry_date), "PPP")}
                      </p>
                    </div>
                  )}
                  <div>
                    <Label className="text-sm text-gray-600">Purchaser</Label>
                    <p className="font-medium">
                      {selectedGiftCard.purchased_by_name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {selectedGiftCard.purchased_by_email}
                    </p>
                  </div>
                  {selectedGiftCard.recipient_name && (
                    <div>
                      <Label className="text-sm text-gray-600">Recipient</Label>
                      <p className="font-medium">
                        {selectedGiftCard.recipient_name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {selectedGiftCard.recipient_email}
                      </p>
                    </div>
                  )}
                  <div>
                    <Label className="text-sm text-gray-600">
                      Delivery Method
                    </Label>
                    <p className="capitalize">
                      {selectedGiftCard.delivery_method}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm text-gray-600">Delivered</Label>
                    <p>{selectedGiftCard.is_delivered ? "Yes" : "No"}</p>
                  </div>
                </div>
                {selectedGiftCard.personal_message && (
                  <div>
                    <Label className="text-sm text-gray-600">
                      Personal Message
                    </Label>
                    <p className="mt-1 p-3 bg-gray-50 rounded-md">
                      {selectedGiftCard.personal_message}
                    </p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="transactions">
                {transactions && transactions.length > 0 ? (
                  <div className="space-y-2">
                    {transactions.map((transaction) => (
                      <Card key={transaction.id}>
                        <CardContent className="pt-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium capitalize">
                                {transaction.transaction_type}
                              </p>
                              <p className="text-sm text-gray-600">
                                {transaction.description}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">
                                {format(
                                  new Date(transaction.created_at),
                                  "PPP p",
                                )}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold">
                                ₦{transaction.amount.toLocaleString()}
                              </p>
                              <p className="text-sm text-gray-600">
                                Balance: ₦
                                {transaction.balance_after.toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No transactions yet
                  </div>
                )}
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>

      {/* Cancel Gift Card Dialog */}
      <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Gift Card</DialogTitle>
            <DialogDescription>
              Please provide a reason for cancelling this gift card.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="cancelReason">Reason *</Label>
              <Input
                id="cancelReason"
                placeholder="Enter cancellation reason..."
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                minLength={10}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setCancelDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleCancelGiftCard}
                disabled={cancelGiftCard.isPending || cancelReason.length < 10}
              >
                {cancelGiftCard.isPending
                  ? "Cancelling..."
                  : "Cancel Gift Card"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function Label({ children, className, ...props }: any) {
  return (
    <label
      className={`block text-sm font-medium ${className || ""}`}
      {...props}
    >
      {children}
    </label>
  );
}
