import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

interface Employee {
    name: string;
    email: string;
    phone: string;
    department: string;
}

export function OrganizationBooking() {
    const { toast } = useToast();
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [newEmployee, setNewEmployee] = useState<Employee>({
        name: '',
        email: '',
        phone: '',
        department: ''
    });
    const [bookingData, setBookingData] = useState({
        serviceId: '',
        stylistId: '',
        bookingDate: '',
        deferredPayment: false
    });

    const createBookingMutation = useMutation({
        mutationFn: async () => {
            const response = await apiClient.post('/api/organization-accounts/bookings', {
                employee_bookings: employees.map(emp => ({
                    employee_name: emp.name,
                    employee_email: emp.email,
                    employee_phone: emp.phone,
                    department: emp.department,
                    service_id: bookingData.serviceId,
                    stylist_id: bookingData.stylistId,
                    booking_date: bookingData.bookingDate
                })),
                deferred_payment: bookingData.deferredPayment
            });
            return response.data;
        },
        onSuccess: () => {
            toast('Organization booking created successfully!', 'success');
            setEmployees([]);
            setBookingData({
                serviceId: '',
                stylistId: '',
                bookingDate: '',
                deferredPayment: false
            });
        },
        onError: (error: any) => {
            toast(
                error.response?.data?.detail || 'Failed to create organization booking',
                'error'
            );
        }
    });

    const addEmployee = () => {
        if (!newEmployee.name || !newEmployee.email) {
            toast('Please fill in name and email', 'error');
            return;
        }
        setEmployees([...employees, newEmployee]);
        setNewEmployee({ name: '', email: '', phone: '', department: '' });
    };

    const removeEmployee = (index: number) => {
        setEmployees(employees.filter((_, i) => i !== index));
    };

    const handleSubmit = async () => {
        if (!bookingData.serviceId || !bookingData.stylistId || !bookingData.bookingDate) {
            toast('Please fill in all booking details', 'error');
            return;
        }
        if (employees.length === 0) {
            toast('Please add at least one employee', 'error');
            return;
        }
        await createBookingMutation.mutateAsync();
    };

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Add Employees</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label>Name *</Label>
                            <Input
                                value={newEmployee.name}
                                onChange={(e) => setNewEmployee({ ...newEmployee, name: e.target.value })}
                                placeholder="Employee name"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <Label>Email *</Label>
                            <Input
                                type="email"
                                value={newEmployee.email}
                                onChange={(e) => setNewEmployee({ ...newEmployee, email: e.target.value })}
                                placeholder="Email"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <Label>Phone</Label>
                            <Input
                                type="tel"
                                value={newEmployee.phone}
                                onChange={(e) => setNewEmployee({ ...newEmployee, phone: e.target.value })}
                                placeholder="Phone"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <Label>Department</Label>
                            <Input
                                value={newEmployee.department}
                                onChange={(e) => setNewEmployee({ ...newEmployee, department: e.target.value })}
                                placeholder="Department"
                                className="mt-1"
                            />
                        </div>
                    </div>
                    <Button onClick={addEmployee} variant="secondary" className="w-full">
                        Add Employee
                    </Button>
                </CardContent>
            </Card>

            {employees.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Employees ({employees.length})</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {employees.map((emp, idx) => (
                                <div key={idx} className="flex justify-between items-center p-3 bg-[var(--muted)] rounded-lg">
                                    <div>
                                        <p className="font-medium text-[var(--foreground)]">{emp.name}</p>
                                        <p className="text-sm text-[var(--muted-foreground)]">{emp.email}</p>
                                        {emp.department && (
                                            <Badge variant="secondary" className="mt-1">{emp.department}</Badge>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => removeEmployee(idx)}
                                        className="text-[var(--destructive)] hover:bg-[var(--destructive)]/10 p-1 rounded"
                                    >
                                        <X size={18} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            <Card>
                <CardHeader>
                    <CardTitle>Booking Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <Label>Service ID *</Label>
                        <Input
                            value={bookingData.serviceId}
                            onChange={(e) => setBookingData({ ...bookingData, serviceId: e.target.value })}
                            placeholder="Service ID"
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Stylist ID *</Label>
                        <Input
                            value={bookingData.stylistId}
                            onChange={(e) => setBookingData({ ...bookingData, stylistId: e.target.value })}
                            placeholder="Stylist ID"
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Booking Date & Time *</Label>
                        <Input
                            type="datetime-local"
                            value={bookingData.bookingDate}
                            onChange={(e) => setBookingData({ ...bookingData, bookingDate: e.target.value })}
                            className="mt-1"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="deferred"
                            checked={bookingData.deferredPayment}
                            onChange={(e) => setBookingData({ ...bookingData, deferredPayment: e.target.checked })}
                        />
                        <Label htmlFor="deferred" className="cursor-pointer">
                            Enable Deferred Payment
                        </Label>
                    </div>
                    <Button
                        onClick={handleSubmit}
                        className="w-full"
                        disabled={createBookingMutation.isPending}
                    >
                        {createBookingMutation.isPending ? 'Creating...' : 'Create Organization Booking'}
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
