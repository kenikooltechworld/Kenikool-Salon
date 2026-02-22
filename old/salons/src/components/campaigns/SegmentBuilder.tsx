import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Select, Slider, Space, Tag, Empty, Spin, message } from 'antd';
import { PlusOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';

interface SegmentCriteria {
  visit_frequency?: { operator: string; value: number | [number, number] };
  last_visit?: { operator: string; days: number };
  total_spending?: { operator: string; amount: number | [number, number] };
  service_preferences?: string[];
  loyalty_tier?: string[];
  demographics?: { age_range?: [number, number]; gender?: string };
  tags?: string[];
}

interface SegmentBuilderProps {
  onSave?: (criteria: SegmentCriteria) => void;
  onPreview?: (criteria: SegmentCriteria) => void;
  initialCriteria?: SegmentCriteria;
}

export const SegmentBuilder: React.FC<SegmentBuilderProps> = ({
  onSave,
  onPreview,
  initialCriteria = {}
}) => {
  const [criteria, setCriteria] = useState<SegmentCriteria>(initialCriteria);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);

  const handleAddVisitFrequency = () => {
    setCriteria({
      ...criteria,
      visit_frequency: { operator: 'gt', value: 5 }
    });
  };

  const handleAddLastVisit = () => {
    setCriteria({
      ...criteria,
      last_visit: { operator: 'within', days: 30 }
    });
  };

  const handleAddSpending = () => {
    setCriteria({
      ...criteria,
      total_spending: { operator: 'gt', amount: 100 }
    });
  };

  const handleAddDemographics = () => {
    setCriteria({
      ...criteria,
      demographics: { age_range: [18, 65], gender: 'all' }
    });
  };

  const handleRemoveCriteria = (key: keyof SegmentCriteria) => {
    const newCriteria = { ...criteria };
    delete newCriteria[key];
    setCriteria(newCriteria);
  };

  const handlePreview = async () => {
    setPreviewLoading(true);
    try {
      if (onPreview) {
        await onPreview(criteria);
      }
      message.success('Preview loaded');
    } catch (error) {
      message.error('Failed to preview segment');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleSave = () => {
    if (onSave) {
      onSave(criteria);
      message.success('Segment saved');
    }
  };

  return (
    <div className="segment-builder">
      <Card title="Segment Builder" className="mb-4">
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* Visit Frequency */}
          {criteria.visit_frequency ? (
            <Card size="small" title="Visit Frequency">
              <Space>
                <Select
                  value={criteria.visit_frequency.operator}
                  onChange={(val) =>
                    setCriteria({
                      ...criteria,
                      visit_frequency: { ...criteria.visit_frequency!, operator: val }
                    })
                  }
                  options={[
                    { label: 'Greater than', value: 'gt' },
                    { label: 'Less than', value: 'lt' },
                    { label: 'Equal to', value: 'eq' },
                    { label: 'Between', value: 'between' }
                  ]}
                />
                <Input
                  type="number"
                  value={
                    Array.isArray(criteria.visit_frequency.value)
                      ? criteria.visit_frequency.value[0]
                      : criteria.visit_frequency.value
                  }
                  onChange={(e) =>
                    setCriteria({
                      ...criteria,
                      visit_frequency: {
                        ...criteria.visit_frequency!,
                        value: parseInt(e.target.value) || 0
                      }
                    })
                  }
                  placeholder="Value"
                />
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleRemoveCriteria('visit_frequency')}
                />
              </Space>
            </Card>
          ) : (
            <Button onClick={handleAddVisitFrequency}>+ Add Visit Frequency</Button>
          )}

          {/* Last Visit */}
          {criteria.last_visit ? (
            <Card size="small" title="Last Visit">
              <Space>
                <Select
                  value={criteria.last_visit.operator}
                  onChange={(val) =>
                    setCriteria({
                      ...criteria,
                      last_visit: { ...criteria.last_visit!, operator: val }
                    })
                  }
                  options={[
                    { label: 'Within', value: 'within' },
                    { label: 'Before', value: 'before' },
                    { label: 'After', value: 'after' }
                  ]}
                />
                <Input
                  type="number"
                  value={criteria.last_visit.days}
                  onChange={(e) =>
                    setCriteria({
                      ...criteria,
                      last_visit: {
                        ...criteria.last_visit!,
                        days: parseInt(e.target.value) || 0
                      }
                    })
                  }
                  placeholder="Days"
                  suffix="days"
                />
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleRemoveCriteria('last_visit')}
                />
              </Space>
            </Card>
          ) : (
            <Button onClick={handleAddLastVisit}>+ Add Last Visit</Button>
          )}

          {/* Total Spending */}
          {criteria.total_spending ? (
            <Card size="small" title="Total Spending">
              <Space>
                <Select
                  value={criteria.total_spending.operator}
                  onChange={(val) =>
                    setCriteria({
                      ...criteria,
                      total_spending: { ...criteria.total_spending!, operator: val }
                    })
                  }
                  options={[
                    { label: 'Greater than', value: 'gt' },
                    { label: 'Less than', value: 'lt' },
                    { label: 'Equal to', value: 'eq' },
                    { label: 'Between', value: 'between' }
                  ]}
                />
                <Input
                  type="number"
                  value={
                    Array.isArray(criteria.total_spending.amount)
                      ? criteria.total_spending.amount[0]
                      : criteria.total_spending.amount
                  }
                  onChange={(e) =>
                    setCriteria({
                      ...criteria,
                      total_spending: {
                        ...criteria.total_spending!,
                        amount: parseFloat(e.target.value) || 0
                      }
                    })
                  }
                  placeholder="Amount"
                  prefix="$"
                />
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleRemoveCriteria('total_spending')}
                />
              </Space>
            </Card>
          ) : (
            <Button onClick={handleAddSpending}>+ Add Total Spending</Button>
          )}

          {/* Demographics */}
          {criteria.demographics ? (
            <Card size="small" title="Demographics">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <span>Age Range:</span>
                  <Input
                    type="number"
                    value={criteria.demographics.age_range?.[0] || 18}
                    onChange={(e) =>
                      setCriteria({
                        ...criteria,
                        demographics: {
                          ...criteria.demographics!,
                          age_range: [parseInt(e.target.value) || 18, criteria.demographics.age_range?.[1] || 65]
                        }
                      })
                    }
                    placeholder="Min age"
                    style={{ width: 100 }}
                  />
                  <span>to</span>
                  <Input
                    type="number"
                    value={criteria.demographics.age_range?.[1] || 65}
                    onChange={(e) =>
                      setCriteria({
                        ...criteria,
                        demographics: {
                          ...criteria.demographics!,
                          age_range: [criteria.demographics.age_range?.[0] || 18, parseInt(e.target.value) || 65]
                        }
                      })
                    }
                    placeholder="Max age"
                    style={{ width: 100 }}
                  />
                </Space>
                <Space>
                  <span>Gender:</span>
                  <Select
                    value={criteria.demographics.gender || 'all'}
                    onChange={(val) =>
                      setCriteria({
                        ...criteria,
                        demographics: { ...criteria.demographics!, gender: val }
                      })
                    }
                    options={[
                      { label: 'All', value: 'all' },
                      { label: 'Male', value: 'male' },
                      { label: 'Female', value: 'female' }
                    ]}
                    style={{ width: 120 }}
                  />
                </Space>
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleRemoveCriteria('demographics')}
                />
              </Space>
            </Card>
          ) : (
            <Button onClick={handleAddDemographics}>+ Add Demographics</Button>
          )}

          {/* Action Buttons */}
          <Space>
            <Button
              type="primary"
              icon={<EyeOutlined />}
              onClick={handlePreview}
              loading={previewLoading}
            >
              Preview
            </Button>
            <Button type="primary" onClick={handleSave}>
              Save Segment
            </Button>
          </Space>
        </Space>
      </Card>

      {/* Preview Results */}
      {previewData && (
        <Card title="Preview Results" className="mt-4">
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <strong>Matching Clients:</strong> {previewData.client_count}
            </div>
            {previewData.sample_clients && previewData.sample_clients.length > 0 && (
              <div>
                <strong>Sample Clients:</strong>
                <div className="mt-2">
                  {previewData.sample_clients.map((client: any) => (
                    <Tag key={client._id}>{client.name}</Tag>
                  ))}
                </div>
              </div>
            )}
          </Space>
        </Card>
      )}
    </div>
  );
};

export default SegmentBuilder;
