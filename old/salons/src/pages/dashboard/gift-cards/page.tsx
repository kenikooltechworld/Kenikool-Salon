import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardContent,
  CardDescription,
} from "@/components/ui/card";
import { PlusIcon, GiftIcon } from "@/components/icons";
import {
  GiftCardCreateModal,
  GiftCardRedeemModal,
  GiftCardList,
} from "@/components/gift-cards";

export default function GiftCardsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isRedeemModalOpen, setIsRedeemModalOpen] = useState(false);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--foreground)]">
            Gift Cards
          </h1>
          <p className="text-[var(--muted-foreground)] mt-1">
            Create and manage gift cards for your salon
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => setIsRedeemModalOpen(true)}>
            <GiftIcon className="w-5 h-5 mr-2" />
            Redeem Gift Card
          </Button>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <PlusIcon className="w-5 h-5 mr-2" />
            Create Gift Card
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Total Gift Cards</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--foreground)]">
              0
            </p>
          </CardContent>
        </Card>
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Active</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--success)]">0</p>
          </CardContent>
        </Card>
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Total Value</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--foreground)]">
              ₦0
            </p>
          </CardContent>
        </Card>
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Redeemed</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--info)]">0</p>
          </CardContent>
        </Card>
      </div>

      {/* Gift Cards List */}
      <GiftCardList />

      {/* Modals */}
      <GiftCardCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />

      <GiftCardRedeemModal
        isOpen={isRedeemModalOpen}
        onClose={() => setIsRedeemModalOpen(false)}
      />
    </div>
  );
}
