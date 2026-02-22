import React from 'react';
import { Checkbox, Card, Space, Tag, Row, Col } from 'antd';
import { PhoneOutlined, MailOutlined, MessageOutlined } from '@ant-design/icons';

interface ChannelInfo {
  channel: string;
  icon: React.ReactNode;
  label: string;
  description: string;
  cost: number;
}

interface ChannelSelectorProps {
  selectedChannels: string[];
  onChannelsChange: (channels: string[]) => void;
  estimatedCost?: number;
}

const CHANNEL_INFO: ChannelInfo[] = [
  {
    channel: 'sms',
    icon: <PhoneOutlined />,
    label: 'SMS',
    description: 'Text message delivery',
    cost: 0.05
  },
  {
    channel: 'whatsapp',
    icon: <MessageOutlined />,
    label: 'WhatsApp',
    description: 'WhatsApp Business messaging',
    cost: 0.08
  },
  {
    channel: 'email',
    icon: <MailOutlined />,
    label: 'Email',
    description: 'Email delivery',
    cost: 0.01
  }
];

export const ChannelSelector: React.FC<ChannelSelectorProps> = ({
  selectedChannels,
  onChannelsChange,
  estimatedCost = 0
}) => {
  const handleChannelChange = (channel: string, checked: boolean) => {
    if (checked) {
      onChannelsChange([...selectedChannels, channel]);
    } else {
      onChannelsChange(selectedChannels.filter(c => c !== channel));
    }
  };

  return (
    <Card title="Select Channels" className="mb-4">
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Row gutter={[16, 16]}>
          {CHANNEL_INFO.map(info => (
            <Col xs={24} sm={12} md={8} key={info.channel}>
              <Card
                hoverable
                className={`channel-card ${selectedChannels.includes(info.channel) ? 'selected' : ''}`}
                style={{
                  border: selectedChannels.includes(info.channel) ? '2px solid #1890ff' : '1px solid #d9d9d9',
                  cursor: 'pointer'
                }}
                onClick={() => handleChannelChange(info.channel, !selectedChannels.includes(info.channel))}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Checkbox
                    checked={selectedChannels.includes(info.channel)}
                    onChange={(e) => handleChannelChange(info.channel, e.target.checked)}
                  >
                    <Space>
                      {info.icon}
                      <strong>{info.label}</strong>
                    </Space>
                  </Checkbox>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {info.description}
                  </div>
                  <Tag color="blue">${info.cost} per message</Tag>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>

        {selectedChannels.length > 0 && (
          <div style={{ padding: '12px', backgroundColor: '#f0f2f5', borderRadius: '4px' }}>
            <strong>Selected Channels:</strong>
            <Space style={{ marginLeft: '8px' }}>
              {selectedChannels.map(channel => (
                <Tag key={channel} color="blue">
                  {CHANNEL_INFO.find(c => c.channel === channel)?.label}
                </Tag>
              ))}
            </Space>
          </div>
        )}

        {estimatedCost > 0 && (
          <div style={{ padding: '12px', backgroundColor: '#e6f7ff', borderRadius: '4px' }}>
            <strong>Estimated Cost:</strong> ${estimatedCost.toFixed(2)}
          </div>
        )}
      </Space>
    </Card>
  );
};

export default ChannelSelector;
