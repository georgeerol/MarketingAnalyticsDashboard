'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card'
import { useMMMData } from '@/hooks/use-mmm-data'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Loader2, TrendingUp, DollarSign } from 'lucide-react'

interface ChannelData {
  name: string
  contribution: number
  share: number
  efficiency: number
  color: string
}

const COLORS = [
  '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
  '#82CA9D', '#FFC658', '#FF7C7C', '#8DD1E1', '#D084D0'
]

export function ContributionChart() {
  const { getChannelSummary, loading, error } = useMMMData()
  const [data, setData] = useState<ChannelData[]>([])
  const [viewType, setViewType] = useState<'bar' | 'pie'>('bar')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const summary = await getChannelSummary()
        const chartData = Object.entries(summary).map(([channel, data], index) => ({
          name: channel.replace(/_/g, ' '),
          contribution: Math.round(data.total_contribution),
          share: Math.round(data.contribution_share * 100),
          efficiency: Math.round(data.efficiency * 100) / 100,
          color: COLORS[index % COLORS.length]
        }))
        
        // Sort by contribution descending
        chartData.sort((a, b) => b.contribution - a.contribution)
        setData(chartData)
      } catch (err) {
        console.error('Failed to fetch contribution data:', err)
      }
    }

    fetchData()
  }, [getChannelSummary])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Channel Performance</CardTitle>
          <CardDescription>Loading contribution data...</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Channel Performance</CardTitle>
          <CardDescription>Error loading data</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-red-500">{error}</p>
        </CardContent>
      </Card>
    )
  }

  const totalContribution = data.reduce((sum, item) => sum + item.contribution, 0)
  const topChannel = data[0]

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Channel Performance
            </CardTitle>
            <CardDescription>Media channel contribution analysis</CardDescription>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewType('bar')}
              className={`px-3 py-1 rounded text-sm ${
                viewType === 'bar' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Bar Chart
            </button>
            <button
              onClick={() => setViewType('pie')}
              className={`px-3 py-1 rounded text-sm ${
                viewType === 'pie' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Pie Chart
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {totalContribution.toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Total Contribution</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {topChannel?.name || 'N/A'}
            </div>
            <div className="text-sm text-gray-500">Top Channel</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {data.length}
            </div>
            <div className="text-sm text-gray-500">Active Channels</div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            {viewType === 'bar' ? (
              <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    typeof value === 'number' ? value.toLocaleString() : value,
                    name === 'contribution' ? 'Contribution' : name
                  ]}
                  labelFormatter={(label) => `Channel: ${label}`}
                />
                <Bar 
                  dataKey="contribution" 
                  fill="#0088FE"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            ) : (
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, share }) => `${name}: ${share}%`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="contribution"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [
                    typeof value === 'number' ? value.toLocaleString() : value,
                    'Contribution'
                  ]}
                />
              </PieChart>
            )}
          </ResponsiveContainer>
        </div>

        {/* Channel Details */}
        <div className="mt-6">
          <h4 className="font-semibold mb-3">Channel Details</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            {data.slice(0, 6).map((channel, index) => (
              <div key={channel.name} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded"
                    style={{ backgroundColor: channel.color }}
                  />
                  <span className="font-medium">{channel.name}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{channel.contribution.toLocaleString()}</div>
                  <div className="text-gray-500">{channel.share}% share</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
