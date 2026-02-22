import React, { useState, useMemo } from 'react';
import { Card, Tabs, Input, Button, Space, Alert, Tag, Tooltip } from 'antd';
import { CopyOutlined, InsertRowBelowOutlined } from '@ant-design/icons';

interface MessageComposerProps {
  channels: string[];
  messages: Record<string, string>;
  emailSubject?: string;
  onMessagesChange: (messages: Record<string, string>) => void;
  onEmailSubjectChange?: (subject: string) => void;
}

const CHANNEL_LIMITS = {
  sms: 160,
  whatsapp: 4096,
  email: null
};

const PERSONALIZATION_TOKENS = [
  { token: '{{client_name}}', description: 'Client name' },
  { token: '{{salon_name}}', description: 'Salon name' },
  { token: '{{discount_code}}', description: 'Discount code' },
  { token: '{{booking_url}}', description: 'Booking URL' },
  { token: '{{expiry_date}}', description: 'Expiry date' }
];

export const MessageComposer: React.FC<MessageComposerProps> = ({
  channels,
  messages,
  emailSubject = '',
  onMessagesChange,
  onEmailSubjectChange
}) => {
  const [selectedChannel, setSelectedChannel] = useState<string>(channels[0] || 'sms');

  const currentMessage = messages[selectedChannel] || '';
  const charLimit = CHANNEL_LIMITS[selectedChannel as keyof typeof CHANNEL_LIMITS];
  const charCount = currentMessage.length;
  const charPercentage = charLimit ? (charCount / charLimit) * 100 : 0;

  const handleMessageChange = (value: string) => {
    const limit = CHANNEL_LIMITS[selectedChannel as keyof typeof CHANNEL_LIMITS];
    if (limit && value.length > limit) {
      return;
    }
    onMessagesChange({
      ...messages,
      [selectedChannel]: value
    });
  };

  const handleInsertToken = (token: string) => {
    const textarea = document.querySelector(`textarea[data-channel="${selectedChannel}"]`) as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newValue = currentMessage.slice(0, start) + token + currentMessage.slice(end);
      handleMessageChange(newValue);
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + token.length;
        textarea.focus();
      }, 0);
    }
  };

  const tabItems = channels.map(channel => ({
    key: channel,
    label: channel.toUpperCase(),
    children: (
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {channel === 'email' && (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Email Subject
            </label>
            <Input
              placeholder="Enter email subject"
              value={emailSubject}
              onChange={(e) => onEmailSubjectChange?.(e.target.value)}
              maxLength={100}
            />
            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              {emailSubject.length}/100 characters
            </div>
          </div>
        )}

        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Message Content
          </label>
          <Input.TextArea
            data-channel={channel}
            value={currentMessage}
            onChange={(e) => handleMessageChange(e.target.value)}
            placeholder={`Enter your ${channel} message...`}
            rows={6}
            maxLength={charLimit || undefined}
          />
          <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'space-between' }}>
            <div>
              {charLimit ? (
                <span style={{ color: charPercentage > 80 ? '#ff4d4f' : '#666' }}>
                  {charCount}/{charLimit} characters
                </span>
              ) : (
                <span style={{ color: '#666' }}>
                  {charCount} characters
                </span>
              )}
            </div>
            {charLimit && (
              <div style={{
                width: '100px',
                height: '4px',
                backgroundColor: '#f0f0f0',
                borderRadius: '2px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${Math.min(charPercentage, 100)}%`,
                  height: '100%',
                  backgroundColor: charPercentage > 80 ? '#ff4d4f' : '#1890ff',
                  transition: 'width 0.3s'
                }} />
              </div>
            )}
          </div>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Personalization Tokens
          </label>
          <Space wrap>
            {PERSONALIZATION_TOKENS.map(({ token, description }) => (
              <Tooltip key={token} title={description}>
                <Button
                  size="small"
                  icon={<InsertRowBelowOutlined />}
                  onClick={() => handleInsertToken(token)}
                >
                  {token}
                </Button>
              </Tooltip>
            ))}
          </Space>
        </div>

        {channel === 'sms' && charCount > 160 && (
          <Alert
            message="Message exceeds SMS limit"
            description="Your message will be split into multiple SMS messages"
            type="warning"
            showIcon
          />
        )}
      </Space>
    )
  }));

  return (
    <Card title="Compose Messages" className="mb-4">
      <Tabs
        activeKey={selectedChannel}
        onChange={setSelectedChannel}
        items={tabItems}
      />
    </Card>
  );
};

export default MessageComposer;
