import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Calendar,
  Download,
  Eye,
  MessageSquare,
  Send,
  Clock,
  AlertTriangle,
  TrendingUp,
  Users,
  DollarSign,
  FileText,
  Mail,
  Phone,
  Edit,
  Trash2,
  Plus,
  RefreshCw,
  Filter,
  Settings
} from 'lucide-react';
import { 
  useGetDetailedARAgingReport,
  useGetClientAgingDetails,
  useExportAgingReport,
  useGetCollectionNotes,
  useAddCollectionNote,
  useUpdateCollectionNote,
  useDeleteCollectionNote,
  useGetReminderConfiguration,
  useSetupAutomatedReminders,
  useSendPaymentReminder,
  useGetReminderHistory
} from '@/lib/api/hooks/useAccounting';
import { toast } from 'sonner';

const NOTE_TYPES = [
  { value: 'general', label: 'General', icon: MessageSquare },
  { value: 'phone_call', label: 'Phone Call', icon: Phone },
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'payment_plan', label: 'Payment Plan', icon: Calendar },
  { value: 'legal_action', label: 'Legal Action', icon: AlertTriangle }
];

const REMINDER_METHODS = [
  { value: 'email', label: 'Email' },
  { value: 'sms', label: 'SMS' },
  { value: 'phone', label: 'Phone Call' }
];

export default function AgingReportsPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedClient, setSelectedClient] = useState<any>(null);
  const [showClientDetails, setShowClientDetails] = useState(false);
  const [showNoteDialog, setShowNoteDialog] = useState(false);
  const [showReminderDialog, setShowReminderDialog] = useState(false);
  const [showReminderConfig, setShowReminderConfig] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    as_of_date: new Date().toISOString().split('T')[0],
    client_id: '',
    include_zero_balances: false,
    min_amount: '',
    max_amount: ''
  });
  
  // Form states
  const [noteForm, setNoteForm] = useState({
    client_id: '',
    invoice_id: '',
    note_text: '',
    note_type: 'general'
  });
  
  const [reminderForm, setReminderForm] = useState({
    invoice_id: '',
    reminder_type: 'email',
    custom_message: ''
  });
  
  const [reminderConfig, setReminderConfig] = useState({
    reminder_schedule: [
      { days_overdue: 7, method: 'email' },
      { days_overdue: 30, method: 'email' },
      { days_overdue: 60, method: 'phone' }
    ],
    email_template: '',
    sms_template: '',
    enabled: true
  });

  // Queries and mutations
  const { data: agingReport, refetch: refetchAging } = useGetDetailedARAgingReport(filters);
  const { data: clientDetails } = useGetClientAgingDetails(selectedClient?.client_id || '', filters.as_of_date);
  const { data: collectionNotes } = useGetCollectionNotes({
    client_id: selectedClient?.client_id
  });
  const { data: reminderConfiguration } = useGetReminderConfiguration();
  const { data: reminderHistory } = useGetReminderHistory({
    client_id: selectedClient?.client_id
  });
  
  const exportReport = useExportAgingReport();
  const addNote = useAddCollectionNote();
  const updateNote = useUpdateCollectionNote();
  const deleteNote = useDeleteCollectionNote();
  const setupReminders = useSetupAutomatedReminders();
  const sendReminder = useSendPaymentReminder();

  const handleExportReport = async (format: string) => {
    try {
      await exportReport.mutateAsync({
        format_type: format,
        ...filters
      });
      toast.success(`Aging report exported as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handleAddNote = async () => {
    try {
      await addNote.mutateAsync(noteForm);
      setShowNoteDialog(false);
      setNoteForm({
        client_id: '',
        invoice_id: '',
        note_text: '',
        note_type: 'general'
      });
      toast.success('Collection note added successfully');
    } catch (error) {
      console.error('Error adding note:', error);
    }
  };

  const handleSendReminder = async () => {
    try {
      await sendReminder.mutateAsync(reminderForm);
      setShowReminderDialog(false);
      setReminderForm({
        invoice_id: '',
        reminder_type: 'email',
        custom_message: ''
      });
      toast.success('Payment reminder sent successfully');
    } catch (error) {
      console.error('Error sending reminder:', error);
    }
  };

  const handleSetupReminders = async () => {
    try {
      await setupReminders.mutateAsync(reminderConfig);
      setShowReminderConfig(false);
      toast.success('Reminder configuration updated successfully');
    } catch (error) {
      console.error('Error setting up reminders:', error);
    }
  };

  const openClientDetails = (clientName: string, clientData: any) => {
    setSelectedClient({
      client_name: clientName,
      client_id: clientData.client_id,
      ...clientData
    });
    setShowClientDetails(true);
  };

  const getBucketVariant = (bucketKey: string) => {
    const variants = {
      current: 'success',
      '30_days': 'warning',
      '60_days': 'warning',
      '90_plus': 'destructive'
    };
    return variants[bucketKey as keyof typeof variants] || 'secondary';
  };

  const renderAgingOverview = () => {
    if (!agingReport) return null;

    return (
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-8 w-8" />
                <div>
                  <p className="text-sm text-muted-foreground">Total Outstanding</p>
                  <p className="text-2xl font-bold">${agingReport.total_outstanding.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-8 w-8" />
                <div>
                  <p className="text-sm text-muted-foreground">Total Invoices</p>
                  <p className="text-2xl font-bold">{agingReport.summary.total_invoices}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-8 w-8" />
                <div>
                  <p className="text-sm text-muted-foreground">Total Clients</p>
                  <p className="text-2xl font-bold">{agingReport.summary.total_clients}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-8 w-8" />
                <div>
                  <p className="text-sm text-muted-foreground">Avg Days Outstanding</p>
                  <p className="text-2xl font-bold">{agingReport.summary.average_days_outstanding.toFixed(0)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Aging Buckets */}
        <Card>
          <CardHeader>
            <CardTitle>Aging Buckets</CardTitle>
            <CardDescription>
              Outstanding amounts grouped by age
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {Object.entries(agingReport.buckets).map(([key, bucket]: [string, any]) => (
                <div key={key} className="border rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <Badge variant={getBucketVariant(key)}>
                      {bucket.label}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {bucket.count} invoices
                    </span>
                  </div>
                  <p className="text-2xl font-bold">${bucket.amount.toLocaleString()}</p>
                  <p className="text-sm text-muted-foreground">
                    {((bucket.amount / agingReport.total_outstanding) * 100).toFixed(1)}% of total
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Client Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Client Breakdown</CardTitle>
            <CardDescription>
              Outstanding amounts by client
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(agingReport.clients).map(([clientName, clientData]: [string, any]) => (
                <div key={clientName} className="border rounded-lg p-4 hover:bg-muted cursor-pointer"
                     onClick={() => openClientDetails(clientName, clientData)}>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-semibold">{clientName}</h4>
                        <Badge variant="outline">
                          {clientData.invoice_count} invoices
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Current</p>
                          <p className="font-medium">${clientData.buckets.current.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">31-60 days</p>
                          <p className="font-medium">${clientData.buckets['30_days'].toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">61-90 days</p>
                          <p className="font-medium">${clientData.buckets['60_days'].toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">90+ days</p>
                          <p className="font-medium">${clientData.buckets['90_plus'].toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-lg font-bold">${clientData.total_outstanding.toLocaleString()}</p>
                      <p className="text-sm text-muted-foreground">
                        Avg: {clientData.average_days_outstanding.toFixed(0)} days
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderCollectionNotes = () => {
    return (
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Collection Notes</CardTitle>
              <CardDescription>
                Track collection activities and client communications
              </CardDescription>
            </div>
            <Button onClick={() => setShowNoteDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Note
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {collectionNotes && collectionNotes.length > 0 ? (
              collectionNotes.map((note: any) => {
                const noteType = NOTE_TYPES.find(type => type.value === note.note_type);
                const IconComponent = noteType?.icon || MessageSquare;
                
                return (
                  <div key={note.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center space-x-2">
                        <IconComponent className="h-4 w-4 text-muted-foreground" />
                        <Badge variant="outline">
                          {noteType?.label || note.note_type}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {new Date(note.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setNoteForm({
                              ...note,
                              client_id: note.client_id || '',
                              invoice_id: note.invoice_id || ''
                            });
                            setShowNoteDialog(true);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteNote.mutate(note.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <p className="text-sm">{note.note_text}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      By: {note.created_by}
                    </p>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No collection notes found</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderReminderHistory = () => {
    return (
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Payment Reminders</CardTitle>
              <CardDescription>
                History of payment reminders sent to clients
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" onClick={() => setShowReminderConfig(true)}>
                <Settings className="h-4 w-4 mr-2" />
                Configure
              </Button>
              <Button onClick={() => setShowReminderDialog(true)}>
                <Send className="h-4 w-4 mr-2" />
                Send Reminder
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {reminderHistory && reminderHistory.length > 0 ? (
              reminderHistory.map((reminder: any) => (
                <div key={reminder.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <Badge variant="outline">
                          {reminder.reminder_type}
                        </Badge>
                        <span className="font-medium">
                          {reminder.client_name}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Invoice: {reminder.invoice_number} - ${reminder.invoice_amount?.toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {new Date(reminder.sent_at).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        To: {reminder.sent_to}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm">{reminder.message}</p>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Send className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No reminders sent yet</p>
              </div>
            )}
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
            <h1 className="text-3xl font-bold">Enhanced Aging Reports</h1>
            <p className="text-muted-foreground">
              Detailed aging analysis with client drill-down, collection notes, and automated reminders.
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => handleExportReport('excel')}>
              <Download className="h-4 w-4 mr-2" />
              Export Excel
            </Button>
            <Button variant="outline" onClick={() => handleExportReport('csv')}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="space-y-2">
              <Label htmlFor="as_of_date">As of Date</Label>
              <Input
                id="as_of_date"
                type="date"
                value={filters.as_of_date}
                onChange={(e) => setFilters(prev => ({ ...prev, as_of_date: e.target.value }))}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="min_amount">Min Amount</Label>
              <Input
                id="min_amount"
                type="number"
                step="0.01"
                value={filters.min_amount}
                onChange={(e) => setFilters(prev => ({ ...prev, min_amount: e.target.value }))}
                placeholder="0.00"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="max_amount">Max Amount</Label>
              <Input
                id="max_amount"
                type="number"
                step="0.01"
                value={filters.max_amount}
                onChange={(e) => setFilters(prev => ({ ...prev, max_amount: e.target.value }))}
                placeholder="No limit"
              />
            </div>
            
            <div className="flex items-center space-x-2 pt-8">
              <Checkbox
                id="include_zero_balances"
                checked={filters.include_zero_balances}
                onCheckedChange={(checked) => 
                  setFilters(prev => ({ ...prev, include_zero_balances: checked as boolean }))
                }
              />
              <Label htmlFor="include_zero_balances">Include zero balances</Label>
            </div>
            
            <div className="pt-6">
              <Button onClick={() => refetchAging()} className="w-full">
                <RefreshCw className="h-4 w-4 mr-2" />
                Apply Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Aging Overview</TabsTrigger>
          <TabsTrigger value="notes">Collection Notes</TabsTrigger>
          <TabsTrigger value="reminders">Payment Reminders</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          {renderAgingOverview()}
        </TabsContent>

        <TabsContent value="notes">
          {renderCollectionNotes()}
        </TabsContent>

        <TabsContent value="reminders">
          {renderReminderHistory()}
        </TabsContent>
      </Tabs>

      {/* Client Details Dialog */}
      <Dialog open={showClientDetails} onOpenChange={setShowClientDetails}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Client Aging Details - {selectedClient?.client_name}</DialogTitle>
            <DialogDescription>
              Detailed aging information and collection history for this client.
            </DialogDescription>
          </DialogHeader>
          
          {clientDetails && (
            <div className="space-y-6">
              {/* Client Information */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Client Name</Label>
                  <p className="font-medium">{clientDetails.client.name}</p>
                </div>
                <div>
                  <Label>Email</Label>
                  <p className="font-medium">{clientDetails.client.email || 'N/A'}</p>
                </div>
                <div>
                  <Label>Phone</Label>
                  <p className="font-medium">{clientDetails.client.phone || 'N/A'}</p>
                </div>
                <div>
                  <Label>Total Outstanding</Label>
                  <p className="font-medium text-lg">${clientDetails.aging_summary.total_outstanding?.toLocaleString()}</p>
                </div>
              </div>

              {/* Outstanding Invoices */}
              <div>
                <Label className="text-base font-semibold">Outstanding Invoices</Label>
                <div className="mt-2 border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted">
                      <tr>
                        <th className="px-4 py-2 text-left">Invoice #</th>
                        <th className="px-4 py-2 text-left">Date</th>
                        <th className="px-4 py-2 text-left">Due Date</th>
                        <th className="px-4 py-2 text-right">Amount Due</th>
                        <th className="px-4 py-2 text-right">Days Outstanding</th>
                        <th className="px-4 py-2 text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {clientDetails.aging_summary.invoices?.map((invoice: any) => (
                        <tr key={invoice.id} className="border-t">
                          <td className="px-4 py-2">{invoice.invoice_number}</td>
                          <td className="px-4 py-2">{invoice.invoice_date}</td>
                          <td className="px-4 py-2">{invoice.due_date}</td>
                          <td className="px-4 py-2 text-right">${invoice.amount_due.toLocaleString()}</td>
                          <td className="px-4 py-2 text-right">
                            <Badge variant={
                              invoice.days_outstanding <= 30 ? 'success' :
                              invoice.days_outstanding <= 60 ? 'warning' :
                              invoice.days_outstanding <= 90 ? 'warning' :
                              'destructive'
                            }>
                              {invoice.days_outstanding} days
                            </Badge>
                          </td>
                          <td className="px-4 py-2 text-center">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setReminderForm(prev => ({ ...prev, invoice_id: invoice.id }));
                                setShowReminderDialog(true);
                              }}
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Recent Payment History */}
              {clientDetails.payment_history && clientDetails.payment_history.length > 0 && (
                <div>
                  <Label className="text-base font-semibold">Recent Payments</Label>
                  <div className="mt-2 space-y-2">
                    {clientDetails.payment_history.map((payment: any) => (
                      <div key={payment.id} className="flex justify-between items-center p-2 border rounded">
                        <div>
                          <span className="font-medium">Invoice {payment.invoice_number}</span>
                          <span className="text-sm text-muted-foreground ml-2">
                            {payment.payment_date}
                          </span>
                        </div>
                        <span className="font-medium">${payment.amount.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Add/Edit Collection Note Dialog */}
      <Dialog open={showNoteDialog} onOpenChange={setShowNoteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {noteForm.id ? 'Edit Collection Note' : 'Add Collection Note'}
            </DialogTitle>
            <DialogDescription>
              Record collection activities and client communications.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="note_type">Note Type</Label>
              <Select
                value={noteForm.note_type}
                onValueChange={(value) => setNoteForm(prev => ({ ...prev, note_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {NOTE_TYPES.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="note_text">Note</Label>
              <Textarea
                id="note_text"
                value={noteForm.note_text}
                onChange={(e) => setNoteForm(prev => ({ ...prev, note_text: e.target.value }))}
                placeholder="Enter collection note details..."
                rows={4}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowNoteDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleAddNote}
                disabled={!noteForm.note_text || addNote.isPending}
              >
                {addNote.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  noteForm.id ? 'Update Note' : 'Add Note'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Send Reminder Dialog */}
      <Dialog open={showReminderDialog} onOpenChange={setShowReminderDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send Payment Reminder</DialogTitle>
            <DialogDescription>
              Send a payment reminder to the client for an overdue invoice.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="reminder_type">Reminder Method</Label>
              <Select
                value={reminderForm.reminder_type}
                onValueChange={(value) => setReminderForm(prev => ({ ...prev, reminder_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {REMINDER_METHODS.map(method => (
                    <SelectItem key={method.value} value={method.value}>
                      {method.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="custom_message">Custom Message (Optional)</Label>
              <Textarea
                id="custom_message"
                value={reminderForm.custom_message}
                onChange={(e) => setReminderForm(prev => ({ ...prev, custom_message: e.target.value }))}
                placeholder="Enter custom reminder message..."
                rows={3}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowReminderDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleSendReminder}
                disabled={!reminderForm.invoice_id || sendReminder.isPending}
              >
                {sendReminder.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Send Reminder
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Reminder Configuration Dialog */}
      <Dialog open={showReminderConfig} onOpenChange={setShowReminderConfig}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Automated Reminder Configuration</DialogTitle>
            <DialogDescription>
              Set up automated payment reminders based on days overdue.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="reminders_enabled"
                checked={reminderConfig.enabled}
                onCheckedChange={(checked) => 
                  setReminderConfig(prev => ({ ...prev, enabled: checked as boolean }))
                }
              />
              <Label htmlFor="reminders_enabled">Enable automated reminders</Label>
            </div>

            <div className="space-y-2">
              <Label>Reminder Schedule</Label>
              <div className="space-y-2">
                {reminderConfig.reminder_schedule.map((schedule, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Input
                      type="number"
                      value={schedule.days_overdue}
                      onChange={(e) => {
                        const newSchedule = [...reminderConfig.reminder_schedule];
                        newSchedule[index].days_overdue = parseInt(e.target.value) || 0;
                        setReminderConfig(prev => ({ ...prev, reminder_schedule: newSchedule }));
                      }}
                      className="w-20"
                    />
                    <span className="text-sm">days overdue</span>
                    <Select
                      value={schedule.method}
                      onValueChange={(value) => {
                        const newSchedule = [...reminderConfig.reminder_schedule];
                        newSchedule[index].method = value;
                        setReminderConfig(prev => ({ ...prev, reminder_schedule: newSchedule }));
                      }}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {REMINDER_METHODS.map(method => (
                          <SelectItem key={method.value} value={method.value}>
                            {method.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email_template">Email Template</Label>
              <Textarea
                id="email_template"
                value={reminderConfig.email_template}
                onChange={(e) => setReminderConfig(prev => ({ ...prev, email_template: e.target.value }))}
                placeholder="Dear {client_name}, your invoice {invoice_number} is overdue..."
                rows={3}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowReminderConfig(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleSetupReminders}
                disabled={setupReminders.isPending}
              >
                {setupReminders.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Configuration'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}