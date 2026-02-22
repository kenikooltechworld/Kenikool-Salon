import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface OrganizationMember {
    name: string;
    email: string;
    phone: string;
    position: string;
}

interface OrganizationAccountRegistrationProps {
    onSuccess?: (organizationId: string) => void;
    onCancel?: () => void;
}

export function OrganizationAccountRegistration({
    onSuccess,
    onCancel,
}: OrganizationAccountRegistrationProps) {
    const { toast } = useToast();
    const [step, setStep] = useState<"info" | "members" | "review">("info");
    const [companyName, setCompanyName] = useState("");
    const [companyEmail, setCompanyEmail] = useState("");
    const [companyPhone, setCompanyPhone] = useState("");
    const [companyAddress, setCompanyAddress] = useState("");
    const [members, setMembers] = useState<OrganizationMember[]>([]);
    const [currentMember, setCurrentMember] = useState<OrganizationMember>({
        name: "",
        email: "",
        phone: "",
        position: "",
    });

    const createOrgMutation = useMutation({
        mutationFn: async () => {
            const response = await apiClient.post("/api/organization-accounts", {
                company_name: companyName,
                company_email: companyEmail,
                company_phone: companyPhone,
                company_address: companyAddress,
                employees: members,
            });
            return response.data;
        },
        onSuccess: (data) => {
            toast("Organization account created successfully!", "success");
            onSuccess?.(data.organization_id);
        },
        onError: (error: any) => {
            toast(
                error.response?.data?.detail || "Failed to create organization account",
                "error"
            );
        },
    });

    const handleAddMember = () => {
        if (!currentMember.name || !currentMember.email || !currentMember.position) {
            toast("Please fill in all member fields", "error");
            return;
        }

        setMembers([...members, currentMember]);
        setCurrentMember({ name: "", email: "", phone: "", position: "" });
    };

    const handleRemoveMember = (index: number) => {
        setMembers(members.filter((_, i) => i !== index));
    };

    const handleSubmit = async () => {
        if (!companyName || !companyEmail) {
            toast("Please fill in company information", "error");
            return;
        }

        if (members.length === 0) {
            toast("Please add at least one employee", "error");
            return;
        }

        await createOrgMutation.mutateAsync();
    };

    return (
        <div className="space-y-6">
            {/* Step Indicator */}
            <div className="flex gap-2">
                {["info", "members", "review"].map((s, idx) => (
                    <div key={s} className="flex items-center">
                        <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step === s
                                    ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                                    : ["info", "members", "review"].indexOf(step) > idx
                                        ? "bg-[var(--accent)] text-[var(--accent-foreground)]"
                                        : "bg-[var(--muted)] text-[var(--muted-foreground)]"
                                }`}
                        >
                            {idx + 1}
                        </div>
                        {idx < 2 && (
                            <div
                                className={`w-8 h-1 mx-1 ${["info", "members", "review"].indexOf(step) > idx
                                        ? "bg-[var(--accent)]"
                                        : "bg-[var(--muted)]"
                                    }`}
                            />
                        )}
                    </div>
                ))}
            </div>

            {/* Company Information */}
            {step === "info" && (
                <Card>
                    <CardHeader>
                        <CardTitle>Company Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium text-[var(--foreground)]">
                                Company Name *
                            </label>
                            <Input
                                value={companyName}
                                onChange={(e) => setCompanyName(e.target.value)}
                                placeholder="Enter company name"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-[var(--foreground)]">
                                Company Email *
                            </label>
                            <Input
                                type="email"
                                value={companyEmail}
                                onChange={(e) => setCompanyEmail(e.target.value)}
                                placeholder="Enter company email"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-[var(--foreground)]">
                                Company Phone
                            </label>
                            <Input
                                type="tel"
                                value={companyPhone}
                                onChange={(e) => setCompanyPhone(e.target.value)}
                                placeholder="Enter company phone"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-[var(--foreground)]">
                                Company Address
                            </label>
                            <Input
                                value={companyAddress}
                                onChange={(e) => setCompanyAddress(e.target.value)}
                                placeholder="Enter company address"
                                className="mt-1"
                            />
                        </div>
                        <Button
                            onClick={() => setStep("members")}
                            className="w-full"
                            disabled={!companyName || !companyEmail}
                        >
                            Next: Add Employees
                        </Button>
                    </CardContent>
                </Card>
            )}

            {/* Add Employees */}
            {step === "members" && (
                <Card>
                    <CardHeader>
                        <CardTitle>Add Employees</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-3">
                            <div>
                                <label className="text-sm font-medium text-[var(--foreground)]">
                                    Employee Name *
                                </label>
                                <Input
                                    value={currentMember.name}
                                    onChange={(e) =>
                                        setCurrentMember({ ...currentMember, name: e.target.value })
                                    }
                                    placeholder="Enter employee name"
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium text-[var(--foreground)]">
                                    Email *
                                </label>
                                <Input
                                    type="email"
                                    value={currentMember.email}
                                    onChange={(e) =>
                                        setCurrentMember({ ...currentMember, email: e.target.value })
                                    }
                                    placeholder="Enter employee email"
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium text-[var(--foreground)]">
                                    Phone
                                </label>
                                <Input
                                    type="tel"
                                    value={currentMember.phone}
                                    onChange={(e) =>
                                        setCurrentMember({ ...currentMember, phone: e.target.value })
                                    }
                                    placeholder="Enter employee phone"
                                    className="mt-1"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium text-[var(--foreground)]">
                                    Position *
                                </label>
                                <Input
                                    value={currentMember.position}
                                    onChange={(e) =>
                                        setCurrentMember({
                                            ...currentMember,
                                            position: e.target.value,
                                        })
                                    }
                                    placeholder="Enter position"
                                    className="mt-1"
                                />
                            </div>
                            <Button
                                onClick={handleAddMember}
                                variant="secondary"
                                className="w-full"
                            >
                                Add Employee
                            </Button>
                        </div>

                        {/* Added Members List */}
                        {members.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-[var(--foreground)]">
                                    Added Employees ({members.length})
                                </h4>
                                <div className="space-y-2">
                                    {members.map((member, idx) => (
                                        <div
                                            key={idx}
                                            className="flex items-center justify-between p-3 bg-[var(--muted)] rounded-lg"
                                        >
                                            <div>
                                                <p className="font-medium text-[var(--foreground)]">
                                                    {member.name}
                                                </p>
                                                <p className="text-sm text-[var(--muted-foreground)]">
                                                    {member.position} • {member.email}
                                                </p>
                                            </div>
                                            <button
                                                onClick={() => handleRemoveMember(idx)}
                                                className="text-[var(--destructive)] hover:bg-[var(--destructive)]/10 p-1 rounded"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="flex gap-2">
                            <Button
                                onClick={() => setStep("info")}
                                variant="outline"
                                className="flex-1"
                            >
                                Back
                            </Button>
                            <Button
                                onClick={() => setStep("review")}
                                className="flex-1"
                                disabled={members.length === 0}
                            >
                                Review
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Review */}
            {step === "review" && (
                <Card>
                    <CardHeader>
                        <CardTitle>Review Organization Details</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm text-[var(--muted-foreground)]">
                                    Company Name
                                </p>
                                <p className="font-medium text-[var(--foreground)]">
                                    {companyName}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-[var(--muted-foreground)]">
                                    Company Email
                                </p>
                                <p className="font-medium text-[var(--foreground)]">
                                    {companyEmail}
                                </p>
                            </div>
                            {companyPhone && (
                                <div>
                                    <p className="text-sm text-[var(--muted-foreground)]">
                                        Company Phone
                                    </p>
                                    <p className="font-medium text-[var(--foreground)]">
                                        {companyPhone}
                                    </p>
                                </div>
                            )}
                            {companyAddress && (
                                <div>
                                    <p className="text-sm text-[var(--muted-foreground)]">
                                        Company Address
                                    </p>
                                    <p className="font-medium text-[var(--foreground)]">
                                        {companyAddress}
                                    </p>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-[var(--border)] pt-4">
                            <p className="text-sm font-medium text-[var(--foreground)] mb-2">
                                Employees ({members.length})
                            </p>
                            <div className="space-y-2">
                                {members.map((member, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-center justify-between p-2 bg-[var(--muted)] rounded"
                                    >
                                        <div>
                                            <p className="text-sm font-medium text-[var(--foreground)]">
                                                {member.name}
                                            </p>
                                            <p className="text-xs text-[var(--muted-foreground)]">
                                                {member.position}
                                            </p>
                                        </div>
                                        <Badge variant="secondary">{member.email}</Badge>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <Button
                                onClick={() => setStep("members")}
                                variant="outline"
                                className="flex-1"
                            >
                                Back
                            </Button>
                            <Button
                                onClick={handleSubmit}
                                className="flex-1"
                                disabled={createOrgMutation.isPending}
                            >
                                {createOrgMutation.isPending ? "Creating..." : "Create Account"}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Cancel Button */}
            {onCancel && (
                <Button onClick={onCancel} variant="ghost" className="w-full">
                    Cancel
                </Button>
            )}
        </div>
    );
}
