'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Gift, Search, Send, FileText } from 'lucide-react';

export default function GiftCardsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center gap-3 mb-2">
            <Gift className="w-8 h-8 text-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900">Gift Cards</h1>
          </div>
          <p className="text-gray-600">Manage your gift cards, check balances, and more</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {/* Check Balance */}
          <Link href="/gift-cards/balance">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Check Balance</CardTitle>
                  <Search className="w-5 h-5 text-purple-600" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Check your gift card balance and expiration date
                </p>
              </CardContent>
            </Card>
          </Link>

          {/* Purchase */}
          <Link href="/gift-cards/purchase">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Purchase</CardTitle>
                  <Gift className="w-5 h-5 text-green-600" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Buy a gift card for yourself or someone special
                </p>
              </CardContent>
            </Card>
          </Link>

          {/* Transfer */}
          <Link href="/gift-cards/transfer">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Transfer</CardTitle>
                  <Send className="w-5 h-5 text-blue-600" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Transfer balance to another gift card
                </p>
              </CardContent>
            </Card>
          </Link>

          {/* Terms */}
          <Link href="/gift-cards/terms">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Terms</CardTitle>
                  <FileText className="w-5 h-5 text-orange-600" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Read our gift card terms and conditions
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Info Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* How It Works */}
          <Card>
            <CardHeader>
              <CardTitle>How It Works</CardTitle>
              <CardDescription>Get started with our gift cards</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-8 w-8 rounded-md bg-purple-600 text-white text-sm font-semibold">
                    1
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Purchase a Card</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Choose an amount and purchase a digital or physical gift card
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-8 w-8 rounded-md bg-purple-600 text-white text-sm font-semibold">
                    2
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Receive or Send</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Digital cards are sent instantly via email. Physical cards can be picked up or mailed
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-8 w-8 rounded-md bg-purple-600 text-white text-sm font-semibold">
                    3
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">Use Anytime</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Redeem your gift card at any of our locations or online
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Features */}
          <Card>
            <CardHeader>
              <CardTitle>Features</CardTitle>
              <CardDescription>What you can do with gift cards</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="text-green-600 mt-1">✓</div>
                <div>
                  <p className="font-medium text-gray-900">Check Balance Anytime</p>
                  <p className="text-sm text-gray-600">No login required</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="text-green-600 mt-1">✓</div>
                <div>
                  <p className="font-medium text-gray-900">Transfer Balance</p>
                  <p className="text-sm text-gray-600">Move funds to another card</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="text-green-600 mt-1">✓</div>
                <div>
                  <p className="font-medium text-gray-900">Secure PIN Protection</p>
                  <p className="text-sm text-gray-600">Optional PIN for added security</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="text-green-600 mt-1">✓</div>
                <div>
                  <p className="font-medium text-gray-900">Valid for 12 Months</p>
                  <p className="text-sm text-gray-600">Plenty of time to use your card</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="text-green-600 mt-1">✓</div>
                <div>
                  <p className="font-medium text-gray-900">Personalized Messages</p>
                  <p className="text-sm text-gray-600">Add a special message for recipients</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
