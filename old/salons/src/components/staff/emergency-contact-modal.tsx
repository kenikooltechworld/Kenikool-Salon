import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useEmergencyContacts } from "@/lib/api/hooks/useEmergencyContacts";
import { useToast } from "@/hooks/use-toast";

interface EmergencyContact {
  name: string;
  relationship: string;
  phone: string;
  email?: string;
  is_primary: boolean;
}

interface MedicalInfo {
  allergies?: string;
  conditions?: string;
  insurance_provider?: string;
  insurance_policy_number?: string;
}

interface EmergencyContactModalProps {
  isOpen: boolean;
  onClose: () => void;
  staffId: string;
  staffName: string;
  userRole: string;
  onUpdate?: () => Promise<void>;
}

const XIcon = () => (
  <svg
    className="w-4 h-4"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M6 18L18 6M6 6l12 12"
    />
  </svg>
);

const PlusIcon = () => (
  <svg
    className="w-4 h-4"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 4v16m8-8H4"
    />
  </svg>
);

const TrashIcon = () => (
  <svg
    className="w-4 h-4 text-red-500"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
    />
  </svg>
);

const AlertIcon = () => (
  <svg
    className="w-4 h-4"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 9v2m0 4v2m0-10a9 9 0 110 18 9 9 0 010-18z"
    />
  </svg>
);

const HeartIcon = () => (
  <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
);

export const EmergencyContactModal: React.FC<EmergencyContactModalProps> = ({
  isOpen,
  onClose,
  staffId,
  staffName,
  userRole,
  onUpdate,
}) => {
  const { showToast } = useToast();
  const {
    contacts,
    medicalInfo,
    loading,
    error,
    fetchContacts,
    fetchMedicalInfo,
    addContact,
    deleteContact,
    updateMedicalInfo,
  } = useEmergencyContacts(staffId);

  const [isAddingContact, setIsAddingContact] = useState(false);
  const [isEditingMedical, setIsEditingMedical] = useState(false);

  // Form state
  const [contactName, setContactName] = useState("");
  const [relationship, setRelationship] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [isPrimary, setIsPrimary] = useState(false);

  const [allergies, setAllergies] = useState("");
  const [conditions, setConditions] = useState("");
  const [insuranceProvider, setInsuranceProvider] = useState("");
  const [insurancePolicyNumber, setInsurancePolicyNumber] = useState("");

  useEffect(() => {
    if (isOpen) {
      fetchContacts();
      if (userRole !== "stylist") {
        fetchMedicalInfo();
      }
    }
  }, [isOpen, staffId, userRole, fetchContacts, fetchMedicalInfo]);

  useEffect(() => {
    if (medicalInfo) {
      setAllergies(medicalInfo.allergies || "");
      setConditions(medicalInfo.conditions || "");
      setInsuranceProvider(medicalInfo.insurance_provider || "");
      setInsurancePolicyNumber(medicalInfo.insurance_policy_number || "");
    }
  }, [medicalInfo]);

  const handleAddContact = async () => {
    if (!contactName || !relationship || !phone) {
      showToast({
        title: "Validation Error",
        description: "Please fill in required fields",
        variant: "destructive",
      });
      return;
    }

    const success = await addContact({
      name: contactName,
      relationship,
      phone,
      email: email || undefined,
      is_primary: isPrimary,
    });

    if (success) {
      setContactName("");
      setRelationship("");
      setPhone("");
      setEmail("");
      setIsPrimary(false);
      setIsAddingContact(false);
      if (onUpdate) await onUpdate();
    }
  };

  const handleDeleteContact = async (index: number) => {
    if (!window.confirm("Delete this contact?")) return;

    const success = await deleteContact(index);
    if (success && onUpdate) {
      await onUpdate();
    }
  };

  const handleSaveMedicalInfo = async () => {
    if (userRole === "stylist") {
      showToast({
        title: "Permission Denied",
        description: "Only managers can update medical information",
        variant: "destructive",
      });
      return;
    }

    const success = await updateMedicalInfo({
      allergies: allergies || undefined,
      conditions: conditions || undefined,
      insurance_provider: insuranceProvider || undefined,
      insurance_policy_number: insurancePolicyNumber || undefined,
    });

    if (success) {
      setIsEditingMedical(false);
      if (onUpdate) await onUpdate();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <CardTitle className="flex items-center gap-2">
            <HeartIcon />
            Emergency Information - {staffName}
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <XIcon />
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4 space-y-6">
          {loading ? (
            <p className="text-center text-slate-500">Loading...</p>
          ) : (
            <>
              {/* Emergency Contacts Section */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Emergency Contacts</h3>
                  <Button
                    onClick={() => setIsAddingContact(true)}
                    variant="outline"
                    size="sm"
                  >
                    <PlusIcon />
                    Add Contact
                  </Button>
                </div>

                {isAddingContact && (
                  <div className="border rounded-lg p-3 space-y-2 bg-slate-50">
                    <Input
                      placeholder="Name *"
                      value={contactName}
                      onChange={(e) => setContactName(e.target.value)}
                    />
                    <Input
                      placeholder="Relationship *"
                      value={relationship}
                      onChange={(e) => setRelationship(e.target.value)}
                    />
                    <Input
                      placeholder="Phone *"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                    />
                    <Input
                      placeholder="Email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={isPrimary}
                        onChange={(e) => setIsPrimary(e.target.checked)}
                      />
                      <span className="text-sm">Set as primary contact</span>
                    </label>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleAddContact}
                        className="flex-1"
                        size="sm"
                      >
                        Save
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setIsAddingContact(false)}
                        className="flex-1"
                        size="sm"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  {contacts.length === 0 ? (
                    <p className="text-sm text-slate-500">
                      No emergency contacts added
                    </p>
                  ) : (
                    contacts.map((contact, idx) => (
                      <div
                        key={idx}
                        className="border rounded-lg p-3 flex items-start justify-between"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-sm">
                              {contact.name}
                            </p>
                            {contact.is_primary && (
                              <Badge className="text-xs">Primary</Badge>
                            )}
                          </div>
                          <p className="text-xs text-slate-600 mt-1">
                            {contact.relationship}
                          </p>
                          <p className="text-xs text-slate-600">
                            {contact.phone}
                          </p>
                          {contact.email && (
                            <p className="text-xs text-slate-600">
                              {contact.email}
                            </p>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteContact(idx)}
                        >
                          <TrashIcon />
                        </Button>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Medical Information Section */}
              {userRole !== "stylist" && (
                <div className="space-y-3 border-t pt-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold flex items-center gap-2">
                      <AlertIcon />
                      Medical Information
                    </h3>
                    {!isEditingMedical && (
                      <Button
                        onClick={() => setIsEditingMedical(true)}
                        variant="outline"
                        size="sm"
                      >
                        Edit
                      </Button>
                    )}
                  </div>

                  {isEditingMedical ? (
                    <div className="space-y-2 bg-slate-50 p-3 rounded-lg">
                      <Textarea
                        placeholder="Allergies"
                        value={allergies}
                        onChange={(e) => setAllergies(e.target.value)}
                        rows={2}
                      />
                      <Textarea
                        placeholder="Medical conditions"
                        value={conditions}
                        onChange={(e) => setConditions(e.target.value)}
                        rows={2}
                      />
                      <Input
                        placeholder="Insurance provider"
                        value={insuranceProvider}
                        onChange={(e) => setInsuranceProvider(e.target.value)}
                      />
                      <Input
                        placeholder="Insurance policy number"
                        value={insurancePolicyNumber}
                        onChange={(e) =>
                          setInsurancePolicyNumber(e.target.value)
                        }
                      />
                      <div className="flex gap-2">
                        <Button
                          onClick={handleSaveMedicalInfo}
                          className="flex-1"
                          size="sm"
                        >
                          Save
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => setIsEditingMedical(false)}
                          className="flex-1"
                          size="sm"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-slate-50 p-3 rounded-lg space-y-2 text-sm">
                      {medicalInfo?.allergies && (
                        <div>
                          <p className="font-medium text-slate-700">
                            Allergies:
                          </p>
                          <p className="text-slate-600">
                            {medicalInfo.allergies}
                          </p>
                        </div>
                      )}
                      {medicalInfo?.conditions && (
                        <div>
                          <p className="font-medium text-slate-700">
                            Conditions:
                          </p>
                          <p className="text-slate-600">
                            {medicalInfo.conditions}
                          </p>
                        </div>
                      )}
                      {medicalInfo?.insurance_provider && (
                        <div>
                          <p className="font-medium text-slate-700">
                            Insurance:
                          </p>
                          <p className="text-slate-600">
                            {medicalInfo.insurance_provider}
                            {medicalInfo.insurance_policy_number &&
                              ` - ${medicalInfo.insurance_policy_number}`}
                          </p>
                        </div>
                      )}
                      {!medicalInfo?.allergies &&
                        !medicalInfo?.conditions &&
                        !medicalInfo?.insurance_provider && (
                          <p className="text-slate-500">
                            No medical information added
                          </p>
                        )}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
