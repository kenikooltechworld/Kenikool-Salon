import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  PlusIcon,
  EditIcon,
  RefreshCcwIcon,
  ListIcon, // Using ListIcon for FileText
  TagIcon, // Using TagIcon for Paperclip
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  MailIcon, // Using MailIcon for Send
  EyeIcon,
  RefreshIcon
} from '@/components/icons';
import { 
  useGetJournalEntries,
  useGetJournalEntry,
  useUpdateJournalEntry,
  useReverseJournalEntry,
  useAddJournalEntryAttachment,
  useRemoveJournalEntryAttachment,
  useGetJournalEntryTemplates,
  useCreateJournalEntryTemplate,
  useDeleteJournalEntryTemplate,
  useSubmitJournalEntryForApproval,
  useApproveJournalEntry,
  useGetJournalEntriesForApproval,
  useGetAccounts
} from '@/lib/api/hooks/useAccounting';
import { toast } from 'sonner';

const APPROVAL_STATUSES = {
  draft: { label: 'Draft', variant: 'secondary' },
  pending: { label: 'Pending Approval', variant: 'warning' },
  approved: { label: 'Approved', variant: 'success' },
  rejected: { label: 'Rejected', variant: 'destructive' }
};

export default function JournalEntriesPage() {
  const [activeTab, setActiveTab] = useState('entries');
  const [selectedEntry, setSelectedEntry] = useState<any>(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showReverseDialog, setShowReverseDialog] = useState(false);
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false);
  
  // Form states
  const [editForm, setEditForm] = useState({
    date: '',
    description: '',
    reference: '',
    line_items: [] as any[]
  });
  
  const [reverseForm, setReverseForm] = useState({
    reversal_date: new Date().toISOString().split('T')[0],
    reversal_reason: ''
  });
  
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    line_items: [] as any[]
  });
  
  const [attachmentForm, setAttachmentForm] = useState({
    attachment_url: '',
    attachment_name: '',
    attachment_type: 'document'
  });
  
  const [approvalForm] = useState({
    approval_notes: '',
    rejection_reason: ''
  });

  // Queries and mutations
  const { data: journalEntries } = useGetJournalEntries();
  const { data: accounts } = useGetAccounts();
  const { data: templates } = useGetJournalEntryTemplates();
  const { data: pendingEntries } = useGetJournalEntriesForApproval();
  const { data: entryDetails } = useGetJournalEntry(selectedEntry?.id || '');
  
  const updateEntry = useUpdateJournalEntry();
  const reverseEntry = useReverseJournalEntry();
  const addAttachment = useAddJournalEntryAttachment();
  const removeAttachment = useRemoveJournalEntryAttachment();
  const createTemplate = useCreateJournalEntryTemplate();
  const deleteTemplate = useDeleteJournalEntryTemplate();
  const submitForApproval = useSubmitJournalEntryForApproval();
  const approveEntry = useApproveJournalEntry();

  const handleEditEntry = (entry: any) => {
    setSelectedEntry(entry);
    setEditForm({
      date: entry.date,
      description: entry.description,
      reference: entry.reference || '',
      line_items: entry.line_items || []
    });
    setShowEditDialog(true);
  };

  const handleUpdateEntry = async () => {
    if (!selectedEntry) return;

    try {
      await updateEntry.mutateAsync({
        entry_id: selectedEntry.id,
        ...editForm
      });
      setShowEditDialog(false);
      toast.success('Journal entry updated successfully');
    } catch (error) {
      console.error('Error updating entry:', error);
    }
  };

  const handleReverseEntry = async () => {
    if (!selectedEntry) return;

    try {
      await reverseEntry.mutateAsync({
        entry_id: selectedEntry.id,
        ...reverseForm
      });
      setShowReverseDialog(false);
      toast.success('Journal entry reversed successfully');
    } catch (error) {
      console.error('Error reversing entry:', error);
    }
  };

  const handleAddAttachment = async () => {
    if (!selectedEntry) return;

    try {
      await addAttachment.mutateAsync({
        entry_id: selectedEntry.id,
        ...attachmentForm
      });
      setShowAttachmentDialog(false);
      setAttachmentForm({
        attachment_url: '',
        attachment_name: '',
        attachment_type: 'document'
      });
      toast.success('Attachment added successfully');
    } catch (error) {
      console.error('Error adding attachment:', error);
    }
  };

  const handleRemoveAttachment = async (attachmentId: string) => {
    if (!selectedEntry) return;

    try {
      await removeAttachment.mutateAsync({
        entry_id: selectedEntry.id,
        attachment_id: attachmentId
      });
      toast.success('Attachment removed successfully');
    } catch (error) {
      console.error('Error removing attachment:', error);
    }
  };

  const handleCreateTemplate = async () => {
    try {
      await createTemplate.mutateAsync(templateForm);
      setShowTemplateDialog(false);
      setTemplateForm({
        name: '',
        description: '',
        line_items: []
      });
      toast.success('Template created successfully');
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  const handleSubmitForApproval = async (entryId: string) => {
    try {
      await submitForApproval.mutateAsync(entryId);
      toast.success('Journal entry submitted for approval');
    } catch (error) {
      console.error('Error submitting for approval:', error);
    }
  };

  const handleApproveEntry = async (entryId: string) => {
    try {
      await approveEntry.mutateAsync({
        entry_id: entryId,
        approval_notes: approvalForm.approval_notes
      });
      toast.success('Journal entry approved');
    } catch (error) {
      console.error('Error approving entry:', error);
    }
  };

  const addLineItem = () => {
    const newItem = {
      account_id: '',
      debit: 0,
      credit: 0,
      description: ''
    };
    setEditForm(prev => ({
      ...prev,
      line_items: [...prev.line_items, newItem]
    }));
  };

  const updateLineItem = (index: number, field: string, value: any) => {
    setEditForm(prev => ({
      ...prev,
      line_items: prev.line_items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const removeLineItem = (index: number) => {
    setEditForm(prev => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index)
    }));
  };

  const calculateTotals = () => {
    const totalDebit = editForm.line_items.reduce((sum, item) => sum + (item.debit || 0), 0);
    const totalCredit = editForm.line_items.reduce((sum, item) => sum + (item.credit || 0), 0);
    return { totalDebit, totalCredit, balanced: Math.abs(totalDebit - totalCredit) < 0.01 };
  };

  const renderJournalEntryCard = (entry: any) => {
    const status = entry.approval_status || 'draft';
    const statusConfig = APPROVAL_STATUSES[status as keyof typeof APPROVAL_STATUSES];

    return (
      <Card key={entry.id} className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold">#{entry.entry_number}</span>
                <Badge className={statusConfig.color}>
                  {statusConfig.label}
                </Badge>
                {entry.reversed && (
                  <Badge variant="destructive">Reversed</Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">{entry.date}</p>
              {entry.reference && (
                <p className="text-sm text-muted-foreground">Ref: {entry.reference}</p>
              )}
            </div>
            <div className="text-right">
              <p className="font-medium">${entry.total_debit?.toLocaleString()}</p>
              <p className="text-sm text-muted-foreground">
                {entry.balanced ? 'Balanced' : 'Unbalanced'}
              </p>
            </div>
          </div>
          
          <p className="text-sm mb-3">{entry.description}</p>
          
          {entry.attachments && entry.attachments.length > 0 && (
            <div className="flex items-center gap-1 mb-3">
              <TagIcon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {entry.attachments.length} attachment(s)
              </span>
            </div>
          )}
          
          <div className="flex justify-between items-center">
            <div className="flex space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedEntry(entry)}
                className="h-8 w-8 p-0"
              >
                <EyeIcon className="h-4 w-4" />
              </Button>
              
              {!entry.reversed && status === 'draft' && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditEntry(entry)}
                    className="h-8 w-8 p-0"
                  >
                    <EditIcon className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSubmitForApproval(entry.id)}
                    className="h-8 w-8 p-0"
                  >
                    <MailIcon className="h-4 w-4" />
                  </Button>
                </>
              )}
              
              {!entry.reversed && status === 'approved' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedEntry(entry);
                    setShowReverseDialog(true);
                  }}
                  className="h-8 w-8 p-0"
                >
                  <RefreshCcwIcon className="h-4 w-4" />
                </Button>
              )}
            </div>
            
            <span className="text-xs text-muted-foreground">
              {entry.created_by}
            </span>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">Journal Entries</h1>
            <p className="text-muted-foreground">
              Manage journal entries with editing, reversal, templates, and approval workflow.
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button onClick={() => setShowTemplateDialog(true)} variant="outline">
              <ListIcon className="h-4 w-4 mr-2" />
              Create Template
            </Button>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6" defaultValue="entries">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="entries">All Entries</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="approval">Pending Approval</TabsTrigger>
          <TabsTrigger value="details">Entry Details</TabsTrigger>
        </TabsList>

        {/* All Entries Tab */}
        <TabsContent value="entries">
          <div className="grid gap-4">
            {journalEntries && journalEntries.length > 0 ? (
              journalEntries.map(renderJournalEntryCard)
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <ListIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No journal entries found</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <Card>
            <CardHeader>
              <CardTitle>Journal Entry Templates</CardTitle>
              <CardDescription>
                Create and manage reusable journal entry templates.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {templates && templates.length > 0 ? (
                  templates.map((template: any) => (
                    <div key={template.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-semibold">{template.name}</h4>
                          <p className="text-sm text-muted-foreground">{template.description}</p>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              // TODO: Implement create from template
                              console.log('Create from template:', template.id);
                            }}
                          >
                            Use Template
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteTemplate.mutate(template.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="text-sm">
                        <p className="font-medium mb-1">Line Items:</p>
                        <div className="space-y-1">
                          {template.line_items?.map((item: any, index: number) => (
                            <div key={index} className="flex justify-between text-xs">
                              <span>{item.account_code} - {item.account_name}</span>
                              <span>
                                {item.debit > 0 ? `Dr: $${item.debit}` : `Cr: $${item.credit}`}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <ListIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No templates found</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pending Approval Tab */}
        <TabsContent value="approval">
          <Card>
            <CardHeader>
              <CardTitle>Entries Pending Approval</CardTitle>
              <CardDescription>
                Review and approve or reject journal entries.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pendingEntries && pendingEntries.length > 0 ? (
                  pendingEntries.map((entry: any) => (
                    <div key={entry.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold">#{entry.entry_number}</span>
                            <Badge variant="warning">
                              Pending Approval
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{entry.date}</p>
                          <p className="text-sm text-muted-foreground">
                            Submitted by: {entry.submitted_by}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${entry.total_debit?.toLocaleString()}</p>
                        </div>
                      </div>
                      
                      <p className="text-sm mb-3">{entry.description}</p>
                      
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedEntry(entry);
                          }}
                          className="h-8 w-8 p-0"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleApproveEntry(entry.id)}
                        >
                          <CheckCircleIcon className="h-4 w-4 mr-2" />
                          Approve
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleApproveEntry(entry.id)}
                        >
                          <XCircleIcon className="h-4 w-4 mr-2" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <ClockIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No entries pending approval</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Entry Details Tab */}
        <TabsContent value="details">
          {selectedEntry && entryDetails ? (
            <Card>
              <CardHeader>
                <CardTitle>Entry Details - #{entryDetails.entry_number}</CardTitle>
                <CardDescription>
                  Detailed view of journal entry with attachments and history.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Basic Information */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Date</Label>
                      <p className="font-medium">{entryDetails.date}</p>
                    </div>
                    <div>
                      <Label>Reference</Label>
                      <p className="font-medium">{entryDetails.reference || 'N/A'}</p>
                    </div>
                    <div>
                      <Label>Status</Label>
                      <Badge variant={APPROVAL_STATUSES[entryDetails.approval_status as keyof typeof APPROVAL_STATUSES]?.variant}>
                        {APPROVAL_STATUSES[entryDetails.approval_status as keyof typeof APPROVAL_STATUSES]?.label || 'Draft'}
                      </Badge>
                    </div>
                    <div>
                      <Label>Created By</Label>
                      <p className="font-medium">{entryDetails.created_by}</p>
                    </div>
                  </div>

                  <div>
                    <Label>Description</Label>
                    <p className="font-medium">{entryDetails.description}</p>
                  </div>

                  {/* Line Items */}
                  <div>
                    <Label className="text-base font-semibold">Line Items</Label>
                    <div className="mt-2 border rounded-lg overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-muted">
                          <tr>
                            <th className="px-4 py-2 text-left">Account</th>
                            <th className="px-4 py-2 text-left">Description</th>
                            <th className="px-4 py-2 text-right">Debit</th>
                            <th className="px-4 py-2 text-right">Credit</th>
                          </tr>
                        </thead>
                        <tbody>
                          {entryDetails.line_items?.map((item: any, index: number) => (
                            <tr key={index} className="border-t">
                              <td className="px-4 py-2">
                                {item.account_code} - {item.account_name}
                              </td>
                              <td className="px-4 py-2">{item.description}</td>
                              <td className="px-4 py-2 text-right">
                                {item.debit > 0 ? `$${item.debit.toLocaleString()}` : ''}
                              </td>
                              <td className="px-4 py-2 text-right">
                                {item.credit > 0 ? `$${item.credit.toLocaleString()}` : ''}
                              </td>
                            </tr>
                          ))}
                          <tr className="border-t bg-muted font-semibold">
                            <td className="px-4 py-2" colSpan={2}>Total</td>
                            <td className="px-4 py-2 text-right">
                              ${entryDetails.total_debit?.toLocaleString()}
                            </td>
                            <td className="px-4 py-2 text-right">
                              ${entryDetails.total_credit?.toLocaleString()}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Attachments */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <Label className="text-base font-semibold">Attachments</Label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowAttachmentDialog(true)}
                      >
                        <TagIcon className="h-4 w-4 mr-2" />
                        Add Attachment
                      </Button>
                    </div>
                    
                    {entryDetails.attachments && entryDetails.attachments.length > 0 ? (
                      <div className="space-y-2">
                        {entryDetails.attachments.map((attachment: any) => (
                          <div key={attachment.id} className="flex justify-between items-center p-2 border rounded">
                            <div>
                              <p className="font-medium">{attachment.name}</p>
                              <p className="text-sm text-muted-foreground">{attachment.type}</p>
                            </div>
                            <div className="flex space-x-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => window.open(attachment.url, '_blank')}
                              >
                                <EyeIcon className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleRemoveAttachment(attachment.id)}
                              >
                                <TrashIcon className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-muted-foreground">No attachments</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <ListIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Select an entry to view details</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Edit Entry Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Edit Journal Entry</DialogTitle>
            <DialogDescription>
              Update journal entry details. Entry must be balanced.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit_date">Date</Label>
                <Input
                  id="edit_date"
                  type="date"
                  value={editForm.date}
                  onChange={(e) => setEditForm(prev => ({ ...prev, date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit_reference">Reference</Label>
                <Input
                  id="edit_reference"
                  value={editForm.reference}
                  onChange={(e) => setEditForm(prev => ({ ...prev, reference: e.target.value }))}
                  placeholder="Optional reference"
                />
              </div>
              <div className="space-y-2">
                <Label>Balance Status</Label>
                <div className="flex items-center space-x-2 pt-2">
                  {calculateTotals().balanced ? (
                    <Badge variant="success">Balanced</Badge>
                  ) : (
                    <Badge variant="destructive">Unbalanced</Badge>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit_description">Description</Label>
              <Textarea
                id="edit_description"
                value={editForm.description}
                onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Entry description"
              />
            </div>

            {/* Line Items */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label className="text-base font-semibold">Line Items</Label>
                <Button type="button" onClick={addLineItem} size="sm">
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Add Line Item
                </Button>
              </div>
              
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-2 py-2 text-left">Account</th>
                      <th className="px-2 py-2 text-left">Description</th>
                      <th className="px-2 py-2 text-right">Debit</th>
                      <th className="px-2 py-2 text-right">Credit</th>
                      <th className="px-2 py-2"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {editForm.line_items.map((item, index) => (
                      <tr key={index} className="border-t">
                        <td className="px-2 py-2">
                          <Select
                            value={item.account_id}
                            onValueChange={(value) => updateLineItem(index, 'account_id', value)}
                          >
                            <SelectTrigger className="w-full">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {accounts && accounts.map((account: any) => (
                                <SelectItem key={account.id} value={account.id}>
                                  {account.code} - {account.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </td>
                        <td className="px-2 py-2">
                          <Input
                            value={item.description}
                            onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                            placeholder="Line description"
                          />
                        </td>
                        <td className="px-2 py-2">
                          <Input
                            type="number"
                            step="0.01"
                            value={item.debit}
                            onChange={(e) => updateLineItem(index, 'debit', parseFloat(e.target.value) || 0)}
                            placeholder="0.00"
                          />
                        </td>
                        <td className="px-2 py-2">
                          <Input
                            type="number"
                            step="0.01"
                            value={item.credit}
                            onChange={(e) => updateLineItem(index, 'credit', parseFloat(e.target.value) || 0)}
                            placeholder="0.00"
                          />
                        </td>
                        <td className="px-2 py-2">
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeLineItem(index)}
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Totals */}
              <div className="flex justify-end space-x-4 text-sm">
                <span>Total Debits: ${calculateTotals().totalDebit.toLocaleString()}</span>
                <span>Total Credits: ${calculateTotals().totalCredit.toLocaleString()}</span>
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowEditDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleUpdateEntry}
                disabled={!calculateTotals().balanced || updateEntry.isPending}
              >
                {updateEntry.isPending ? (
                  <>
                    <RefreshIcon className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : (
                  'Update Entry'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Reverse Entry Dialog */}
      <Dialog open={showReverseDialog} onOpenChange={setShowReverseDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reverse Journal Entry</DialogTitle>
            <DialogDescription>
              Create a reversal entry to cancel the effects of this journal entry.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="reversal_date">Reversal Date</Label>
              <Input
                id="reversal_date"
                type="date"
                value={reverseForm.reversal_date}
                onChange={(e) => setReverseForm(prev => ({ ...prev, reversal_date: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="reversal_reason">Reason for Reversal</Label>
              <Textarea
                id="reversal_reason"
                value={reverseForm.reversal_reason}
                onChange={(e) => setReverseForm(prev => ({ ...prev, reversal_reason: e.target.value }))}
                placeholder="Explain why this entry is being reversed"
                required
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowReverseDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleReverseEntry}
                disabled={!reverseForm.reversal_reason || reverseEntry.isPending}
                variant="destructive"
              >
                {reverseEntry.isPending ? (
                  <>
                    <RefreshIcon className="mr-2 h-4 w-4 animate-spin" />
                    Reversing...
                  </>
                ) : (
                  <>
                    <RefreshCcwIcon className="mr-2 h-4 w-4" />
                    Reverse Entry
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Attachment Dialog */}
      <Dialog open={showAttachmentDialog} onOpenChange={setShowAttachmentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Attachment</DialogTitle>
            <DialogDescription>
              Add a file attachment to this journal entry.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="attachment_name">Attachment Name</Label>
              <Input
                id="attachment_name"
                value={attachmentForm.attachment_name}
                onChange={(e) => setAttachmentForm(prev => ({ ...prev, attachment_name: e.target.value }))}
                placeholder="Enter attachment name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="attachment_url">File URL</Label>
              <Input
                id="attachment_url"
                value={attachmentForm.attachment_url}
                onChange={(e) => setAttachmentForm(prev => ({ ...prev, attachment_url: e.target.value }))}
                placeholder="Enter file URL"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="attachment_type">Attachment Type</Label>
              <Select
                value={attachmentForm.attachment_type}
                onValueChange={(value) => setAttachmentForm(prev => ({ ...prev, attachment_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="document">Document</SelectItem>
                  <SelectItem value="image">Image</SelectItem>
                  <SelectItem value="receipt">Receipt</SelectItem>
                  <SelectItem value="invoice">Invoice</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowAttachmentDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleAddAttachment}
                disabled={!attachmentForm.attachment_name || !attachmentForm.attachment_url || addAttachment.isPending}
              >
                {addAttachment.isPending ? (
                  <>
                    <RefreshIcon className="mr-2 h-4 w-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <TagIcon className="mr-2 h-4 w-4" />
                    Add Attachment
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Create Template Dialog */}
      <Dialog open={showTemplateDialog} onOpenChange={setShowTemplateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Journal Entry Template</DialogTitle>
            <DialogDescription>
              Create a reusable template for common journal entries.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="template_name">Template Name</Label>
              <Input
                id="template_name"
                value={templateForm.name}
                onChange={(e) => setTemplateForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter template name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="template_description">Description</Label>
              <Textarea
                id="template_description"
                value={templateForm.description}
                onChange={(e) => setTemplateForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe when to use this template"
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowTemplateDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleCreateTemplate}
                disabled={!templateForm.name || createTemplate.isPending}
              >
                {createTemplate.isPending ? (
                  <>
                    <RefreshIcon className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Template'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}