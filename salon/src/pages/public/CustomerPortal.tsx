import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui";
import BookingHistory from "@/components/public/BookingHistory";
import CustomerProfile from "@/components/public/CustomerProfile";
import {
  useCustomerProfile,
  useCustomerLogout,
  useIsCustomerAuthenticated,
} from "@/hooks/useCustomerAuth";
import {
  CalendarIcon,
  UserIcon,
  LogOutIcon,
  HomeIcon,
} from "@/components/icons";

export default function CustomerPortal() {
  const navigate = useNavigate();
  const isAuthenticated = useIsCustomerAuthenticated();
  const { data: profile } = useCustomerProfile();
  const logout = useCustomerLogout();
  const [activeTab, setActiveTab] = useState("bookings");

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    navigate("/public/login");
    return null;
  }

  const handleLogout = async () => {
    await logout.mutateAsync();
    navigate("/public/booking");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">My Account</h1>
              {profile && (
                <p className="text-sm text-gray-600">
                  Welcome back, {profile.first_name}!
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => navigate("/public/booking")}
              >
                <HomeIcon size={16} className="mr-2" />
                Back to Booking
              </Button>
              <Button variant="outline" onClick={handleLogout}>
                <LogOutIcon size={16} className="mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          defaultValue="bookings"
        >
          <TabsList className="mb-6">
            <TabsTrigger value="bookings">
              <CalendarIcon size={16} className="mr-2" />
              My Bookings
            </TabsTrigger>
            <TabsTrigger value="profile">
              <UserIcon size={16} className="mr-2" />
              Profile
            </TabsTrigger>
          </TabsList>

          <TabsContent value="bookings">
            <div>
              <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">My Bookings</h2>
                <p className="text-gray-600">
                  View and manage your appointment history
                </p>
              </div>
              <BookingHistory />
            </div>
          </TabsContent>

          <TabsContent value="profile">
            <div>
              <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">My Profile</h2>
                <p className="text-gray-600">
                  Manage your personal information and preferences
                </p>
              </div>
              <CustomerProfile />
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
