import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function GuestBookingFlow() {
    const [step, setStep] = useState(1);
    const [guestData, setGuestData] = useState({
        name: '',
        email: '',
        phone: '',
        serviceId: '',
        stylistId: '',
        bookingDate: '',
        notes: ''
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setGuestData(prev => ({ ...prev, [name]: value }));
    };

    const handleNext = () => {
        if (step < 4) setStep(step + 1);
    };

    const handleBack = () => {
        if (step > 1) setStep(step - 1);
    };

    const handleSubmit = async () => {
        try {
            const response = await fetch('/api/guest-bookings/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(guestData)
            });
            if (response.ok) {
                alert('Booking created successfully!');
            }
        } catch (error) {
            console.error('Booking error:', error);
        }
    };

    return (
        <Card className="w-full max-w-2xl">
            <CardHeader>
                <CardTitle>Book Your Appointment</CardTitle>
            </CardHeader>
            <CardContent>
                {step === 1 && (
                    <div className="space-y-4">
                        <div>
                            <Label>Full Name</Label>
                            <Input
                                name="name"
                                value={guestData.name}
                                onChange={handleInputChange}
                                placeholder="Your name"
                            />
                        </div>
                        <div>
                            <Label>Email</Label>
                            <Input
                                name="email"
                                type="email"
                                value={guestData.email}
                                onChange={handleInputChange}
                                placeholder="your@email.com"
                            />
                        </div>
                        <div>
                            <Label>Phone</Label>
                            <Input
                                name="phone"
                                value={guestData.phone}
                                onChange={handleInputChange}
                                placeholder="+1234567890"
                            />
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-4">
                        <div>
                            <Label>Select Service</Label>
                            <Input
                                name="serviceId"
                                value={guestData.serviceId}
                                onChange={handleInputChange}
                                placeholder="Service ID"
                            />
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="space-y-4">
                        <div>
                            <Label>Select Stylist</Label>
                            <Input
                                name="stylistId"
                                value={guestData.stylistId}
                                onChange={handleInputChange}
                                placeholder="Stylist ID"
                            />
                        </div>
                    </div>
                )}

                {step === 4 && (
                    <div className="space-y-4">
                        <div>
                            <Label>Booking Date & Time</Label>
                            <Input
                                name="bookingDate"
                                type="datetime-local"
                                value={guestData.bookingDate}
                                onChange={handleInputChange}
                            />
                        </div>
                        <div>
                            <Label>Special Requests</Label>
                            <textarea
                                name="notes"
                                value={guestData.notes}
                                onChange={handleInputChange}
                                placeholder="Any special requests?"
                                className="w-full p-2 border rounded"
                            />
                        </div>
                    </div>
                )}

                <div className="flex justify-between mt-6">
                    <Button onClick={handleBack} disabled={step === 1} variant="outline">
                        Back
                    </Button>
                    {step < 4 ? (
                        <Button onClick={handleNext}>Next</Button>
                    ) : (
                        <Button onClick={handleSubmit}>Complete Booking</Button>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
