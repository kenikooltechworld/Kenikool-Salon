import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CampaignManager } from "@/components/campaigns/campaign-manager";
import { SMSCreditsManager } from "@/components/campaigns/sms-credits-manager";
import { CampaignTemplates } from "@/components/campaigns/campaign-templates";

export default function CampaignsPage() {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Campaigns</h1>
          <p className="text-muted-foreground mt-2">
            Create and manage SMS, WhatsApp, and Email campaigns
          </p>
        </div>

        <Tabs defaultValue="campaigns" className="w-full">
          <TabsList>
            <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
            <TabsTrigger value="templates">Templates</TabsTrigger>
            <TabsTrigger value="credits">SMS Credits</TabsTrigger>
          </TabsList>

          <TabsContent value="campaigns" className="mt-6">
            <CampaignManager />
          </TabsContent>

          <TabsContent value="templates" className="mt-6">
            <CampaignTemplates />
          </TabsContent>

          <TabsContent value="credits" className="mt-6">
            <SMSCreditsManager />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
