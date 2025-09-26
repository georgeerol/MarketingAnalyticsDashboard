'use client';

import React, { useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@workspace/ui/components/tabs';
import { mockMeridianData, calculateBudgetAllocation, getTopPerformers } from '../lib/meridian-data';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

export function ContributionCharts() {
  const [selectedMetric, setSelectedMetric] = useState<'spend' | 'contribution' | 'roi'>('spend');

  // Prepare data for different chart types
  const budgetAllocation = calculateBudgetAllocation(mockMeridianData.channels);
  const topPerformers = getTopPerformers(mockMeridianData.channels, 'roi');

  // Prepare pie chart data
  const pieData = mockMeridianData.channels.map((channel, index) => ({
    name: channel.name,
    value: channel.spend.reduce((a, b) => a + b, 0),
    roi: channel.roi,
    contribution: channel.contribution.reduce((a, b) => a + b, 0),
    fill: COLORS[index % COLORS.length]
  }));

  // Prepare bar chart data
  const barData = mockMeridianData.channels.map(channel => ({
    name: channel.name,
    spend: channel.spend.reduce((a, b) => a + b, 0),
    contribution: channel.contribution.reduce((a, b) => a + b, 0),
    roi: channel.roi
  }));

  // Prepare time series data
  const timeSeriesData = mockMeridianData.channels.map(channel => ({
    name: channel.name,
    data: channel.spend.map((spend, index) => ({
      period: index,
      spend,
      contribution: channel.contribution[index],
      roi: channel.roi
    }))
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded shadow-lg">
          <p className="font-semibold">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value?.toLocaleString()}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Media Spend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${mockMeridianData.kpi.total_spend[0]?.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average ROI</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((mockMeridianData.kpi.roi_m.reduce((a, b) => a + b, 0) / mockMeridianData.kpi.roi_m.length) * 100).toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Channels</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockMeridianData.model_info.media_channels_count}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="allocation" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="allocation">Budget Allocation</TabsTrigger>
          <TabsTrigger value="performance">Channel Performance</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="allocation">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Budget Allocation by Channel</CardTitle>
                <CardDescription>Distribution of media spend across channels</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`$${value.toLocaleString()}`, 'Spend']} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Performers by ROI</CardTitle>
                <CardDescription>Highest return on investment channels</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topPerformers}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                    <Tooltip
                      formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'ROI']}
                      labelFormatter={(label) => `Channel: ${label}`}
                    />
                    <Bar dataKey="roi" fill="#00C49F" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Contribution vs Spend</CardTitle>
                <CardDescription>Channel efficiency comparison</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip
                      formatter={(value: number, name: string) => [
                        name === 'spend' ? `$${value.toLocaleString()}` : `$${value.toLocaleString()}`,
                        name === 'spend' ? 'Media Spend' : 'Revenue Contribution'
                      ]}
                    />
                    <Legend />
                    <Bar dataKey="spend" fill="#8884d8" name="Media Spend" />
                    <Bar dataKey="contribution" fill="#82ca9d" name="Revenue Contribution" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>ROI by Channel</CardTitle>
                <CardDescription>Return on investment across all channels</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                    <YAxis dataKey="name" type="category" width={100} />
                    <Tooltip
                      formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'ROI']}
                    />
                    <Bar dataKey="roi" fill="#ffc658" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends">
          <Card>
            <CardHeader>
              <CardTitle>Channel Performance Over Time</CardTitle>
              <CardDescription>Spend and contribution trends</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={timeSeriesData[0].data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      name === 'spend' ? `$${value.toLocaleString()}` : `$${value.toLocaleString()}`,
                      name === 'spend' ? 'Media Spend' : 'Revenue Contribution'
                    ]}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="spend" stroke="#8884d8" strokeWidth={2} name="Media Spend" />
                  <Line type="monotone" dataKey="contribution" stroke="#82ca9d" strokeWidth={2} name="Revenue Contribution" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
