import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Modal, message, Popconfirm, Tag } from 'antd';
import { EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { formatDistanceToNow } from 'date-fns';

interface Segment {
  _id: string;
  name: string;
  description?: string;
  client_count: number;
  updated_at: string;
  created_by: string;
}

interface SegmentManagerProps {
  segments: Segment[];
  loading?: boolean;
  onEdit?: (segment: Segment) => void;
  onDelete?: (segmentId: string) => void;
  onView?: (segment: Segment) => void;
}

export const SegmentManager: React.FC<SegmentManagerProps> = ({
  segments = [],
  loading = false,
  onEdit,
  onDelete,
  onView
}) => {
  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || '-'
    },
    {
      title: 'Clients',
      dataIndex: 'client_count',
      key: 'client_count',
      render: (count: number) => <Tag color="blue">{count} clients</Tag>
    },
    {
      title: 'Last Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => formatDistanceToNow(new Date(date), { addSuffix: true })
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Segment) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => onView?.(record)}
            title="View segment"
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => onEdit?.(record)}
            title="Edit segment"
          />
          <Popconfirm
            title="Delete Segment"
            description="Are you sure you want to delete this segment?"
            onConfirm={() => {
              onDelete?.(record._id);
              message.success('Segment deleted');
            }}
            okText="Yes"
            cancelText="No"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              title="Delete segment"
            />
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <Table
      columns={columns}
      dataSource={segments}
      loading={loading}
      rowKey="_id"
      pagination={{ pageSize: 10 }}
      size="small"
    />
  );
};

export default SegmentManager;
