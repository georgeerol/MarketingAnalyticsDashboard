'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card'
import { useMMMData } from '@/hooks/use-mmm-data'
import { Loader2, TrendingUp, TrendingDown, Target, Zap, Lightbulb, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react'

// Simple bar chart component without external dependencies
function SimpleBarChart({ data, title }: { data: Array<{name: string, value: number, color: string}>, title: string }) {
  const maxValue = Math.max(...data.map(d => d.value))
  
  return (
    <div className="space-y-3">
      <h4 className="font-medium text-sm text-gray-600">{title}</h4>
      {data.map((item, index) => (
        <div key={index} className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="font-medium">{item.name}</span>
            <span className="text-gray-600">{item.value.toLocaleString()}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all duration-500"
              style={{
                width: `${(item.value / maxValue) * 100}%`,
                backgroundColor: item.color
              }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

// Simple line chart component
function SimpleLineChart({ data, title }: { data: Array<{x: number, y: number}>, title: string, saturationPoint?: number }) {
  const maxX = Math.max(...data.map(d => d.x))
  const maxY = Math.max(...data.map(d => d.y))
  
  return (
    <div className="space-y-3">
      <h4 className="font-medium text-sm text-gray-600">{title}</h4>
      <div className="relative h-32 bg-gray-50 rounded-lg p-4">
        <svg className="w-full h-full" viewBox="0 0 300 100">
          {/* Grid lines */}
          <defs>
            <pattern id="grid" width="30" height="20" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Line */}
          <polyline
            fill="none"
            stroke="#0088FE"
            strokeWidth="2"
            points={data.map((d, i) => 
              `${(d.x / maxX) * 280 + 10},${90 - (d.y / maxY) * 80}`
            ).join(' ')}
          />
          
          {/* Points */}
          {data.map((d, i) => (
            <circle
              key={i}
              cx={(d.x / maxX) * 280 + 10}
              cy={90 - (d.y / maxY) * 80}
              r="2"
              fill="#0088FE"
            />
          ))}
        </svg>
      </div>
    </div>
  )
}

export function SimpleContributionChart() {
  const { getChannelSummary, loading, error } = useMMMData()
  const [data, setData] = useState<Array<{name: string, value: number, color: string}>>([])

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  useEffect(() => {
    let isMounted = true
    
    const fetchData = async () => {
      try {
        const summary = await getChannelSummary()
        
        if (!isMounted) return
        
        const chartData = Object.entries(summary).map(([channel, data], index) => ({
          name: channel.replace(/_/g, ' '),
          value: Math.round(data.total_contribution),
          color: COLORS[index % COLORS.length]
        }))
        
        chartData.sort((a, b) => b.value - a.value)
        setData(chartData.slice(0, 6)) // Show top 6 channels
      } catch (err) {
        console.error('Failed to fetch contribution data:', err)
      }
    }

    fetchData()
    
    return () => {
      isMounted = false
    }
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Channel Performance
          </CardTitle>
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

  const totalContribution = data.reduce((sum, item) => sum + item.value, 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Channel Performance
        </CardTitle>
        <CardDescription>Top performing media channels</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {totalContribution.toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Total Contribution</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {data[0]?.name || 'N/A'}
            </div>
            <div className="text-sm text-gray-500">Top Channel</div>
          </div>
        </div>

        <SimpleBarChart data={data} title="Channel Contributions" />
      </CardContent>
    </Card>
  )
}

export function SimpleResponseCurves() {
  const { getResponseCurves, getChannels, loading, error } = useMMMData()
  const [selectedChannel, setSelectedChannel] = useState<string>('')
  const [channels, setChannels] = useState<string[]>([])
  const [curveData, setCurveData] = useState<Array<{x: number, y: number}>>([])
  const [saturationPoint, setSaturationPoint] = useState<number>(0)
  const [efficiency, setEfficiency] = useState<number>(0)

  useEffect(() => {
    let isMounted = true
    
    const fetchData = async () => {
      try {
        const channelList = await getChannels()
        
        if (!isMounted) return
        
        setChannels(channelList)
        setSelectedChannel(channelList[0] || '')

        const allCurves = await getResponseCurves() as { curves: Record<string, any> }
        
        if (!isMounted) return
        
        const firstChannel = channelList[0]
        if (firstChannel && allCurves.curves[firstChannel]) {
          const data = allCurves.curves[firstChannel]
          const points = data.spend.slice(0, 20).map((spend: number, index: number) => ({
            x: spend,
            y: data.response[index]
          }))
          setCurveData(points)
          setSaturationPoint(data.saturation_point)
          setEfficiency(data.efficiency)
        }
      } catch (err) {
        console.error('Failed to fetch response curves:', err)
      }
    }

    fetchData()
    
    return () => {
      isMounted = false
    }
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="h-5 w-5" />
            Response Curves
          </CardTitle>
          <CardDescription>Loading response curve data...</CardDescription>
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
          <CardTitle>Response Curves</CardTitle>
          <CardDescription>Error loading data</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-red-500">{error}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5" />
              Response Curves
            </CardTitle>
            <CardDescription>Diminishing returns analysis</CardDescription>
          </div>
          <select
            value={selectedChannel}
            onChange={(e) => setSelectedChannel(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            {channels.map(channel => (
              <option key={channel} value={channel}>
                {channel.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-orange-600 mb-1">
              <Target className="h-4 w-4" />
            </div>
            <div className="text-2xl font-bold text-orange-600">
              ${Math.round(saturationPoint).toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Saturation Point</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-green-600 mb-1">
              <Zap className="h-4 w-4" />
            </div>
            <div className="text-2xl font-bold text-green-600">
              {efficiency.toFixed(2)}
            </div>
            <div className="text-sm text-gray-500">Efficiency</div>
          </div>
        </div>

        <SimpleLineChart data={curveData} title={`${selectedChannel.replace(/_/g, ' ')} Response Curve`} />
        
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Insight:</strong> Optimal spend range is $0 - ${Math.round(saturationPoint * 0.8).toLocaleString()}. 
            Beyond ${Math.round(saturationPoint).toLocaleString()}, diminishing returns occur.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

export function SimpleMMInsights() {
  const { getChannelSummary, getMMMInfo, loading, error } = useMMMData()
  const [insights, setInsights] = useState<Array<{type: string, title: string, description: string}>>([])
  const [modelInfo, setModelInfo] = useState<any>(null)

  useEffect(() => {
    let isMounted = true
    
    const generateInsights = async () => {
      try {
        const [summary, info] = await Promise.all([
          getChannelSummary(),
          getMMMInfo()
        ])
        
        if (!isMounted) return
        
        setModelInfo(info)

        const channels = Object.entries(summary)
        const sortedByEfficiency = channels.sort(([,a], [,b]) => b.efficiency - a.efficiency)
        const topPerformer = sortedByEfficiency[0]
        const underPerformer = sortedByEfficiency[sortedByEfficiency.length - 1]

        const generatedInsights = [
          {
            type: 'success',
            title: `${topPerformer[0].replace(/_/g, ' ')} is your top performer`,
            description: `With an efficiency of ${topPerformer[1].efficiency.toFixed(2)}, this channel delivers the highest ROI.`
          },
          {
            type: 'warning',
            title: `${underPerformer[0].replace(/_/g, ' ')} needs optimization`,
            description: `Low efficiency of ${underPerformer[1].efficiency.toFixed(2)} suggests room for improvement.`
          },
          {
            type: 'info',
            title: 'Model Coverage',
            description: `Analysis covers ${info.total_weeks} weeks across ${info.channels.length} channels.`
          }
        ]

        setInsights(generatedInsights)
      } catch (err) {
        console.error('Failed to generate insights:', err)
      }
    }

    generateInsights()
    
    return () => {
      isMounted = false
    }
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            MMM Insights
          </CardTitle>
          <CardDescription>Generating recommendations...</CardDescription>
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
          <CardTitle>MMM Insights</CardTitle>
          <CardDescription>Error loading insights</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-red-500">{error}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5" />
          MMM Insights
        </CardTitle>
        <CardDescription>AI-powered recommendations for media optimization</CardDescription>
      </CardHeader>
      <CardContent>
        {modelInfo && (
          <div className="mb-6 p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">
              <strong>Model:</strong> {modelInfo.model_type} ({modelInfo.data_source})
              <br />
              <strong>Period:</strong> {modelInfo.training_period}
              <br />
              <strong>Data:</strong> {modelInfo.total_weeks} weeks, {modelInfo.channels.length} channels
            </div>
          </div>
        )}

        <div className="space-y-4">
          <h4 className="font-semibold">🔍 Key Insights</h4>
          {insights.map((insight, index) => (
            <div key={index} className={`p-4 rounded-lg border-l-4 ${
              insight.type === 'success' ? 'border-green-500 bg-green-50' :
              insight.type === 'warning' ? 'border-yellow-500 bg-yellow-50' :
              'border-blue-500 bg-blue-50'
            }`}>
              <div className="flex items-start gap-3">
                <div className={`${
                  insight.type === 'success' ? 'text-green-600' :
                  insight.type === 'warning' ? 'text-yellow-600' :
                  'text-blue-600'
                }`}>
                  {insight.type === 'success' ? <CheckCircle className="h-5 w-5" /> :
                   insight.type === 'warning' ? <AlertTriangle className="h-5 w-5" /> :
                   <Lightbulb className="h-5 w-5" />}
                </div>
                <div className="flex-1">
                  <h5 className="font-medium mb-1">{insight.title}</h5>
                  <p className="text-sm text-gray-600">{insight.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">📈 Next Steps</h4>
          <p className="text-sm text-gray-700 mb-3">
            Focus on optimizing your top-performing channels while improving efficiency in underperforming areas.
          </p>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
            Export Recommendations
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
