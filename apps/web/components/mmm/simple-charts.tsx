/**
 * Simple chart components for the MMM dashboard
 */

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card'
import { useMMMData } from '@/hooks/use-mmm-data'
import { useAuth } from '@/lib/auth'
import { formatChannelName } from '@/lib/format-channel'
import { Loader2, TrendingUp, TrendingDown, Target, Zap, Lightbulb, CheckCircle, AlertTriangle, ArrowRight, Rocket, BarChart3, Search, BarChart2 } from 'lucide-react'

/**
 * Data structure for insights shown to users
 */
interface Insight {
  /** success, warning, or info - affects styling */
  type: 'success' | 'warning' | 'info'
  /** Insight title */
  title: string
  /** Insight description */
  description: string
  /** Icon to show */
  icon?: React.ReactNode
}

/**
 * Bar chart with optional performance badges
 * 
 * Shows horizontal bars for each data item. If showPerformance is true,
 * adds badges like "High Performer" based on efficiency vs average.
 */
function SimpleBarChart({ data, title, showPerformance = false }: { 
  data: Array<{name: string, value: number, color: string, efficiency?: number}>, 
  title: string,
  showPerformance?: boolean 
}) {
  const maxValue = Math.max(...data.map(d => d.value))
  
  // Calculate performance tiers for efficiency indicators
  const efficiencies = data.map(d => d.efficiency || 0).filter(e => e > 0)
  const avgEfficiency = efficiencies.length > 0 ? efficiencies.reduce((a, b) => a + b, 0) / efficiencies.length : 1
  
  const getPerformanceIndicator = (efficiency?: number) => {
    if (!efficiency || !showPerformance) return null
    if (efficiency > avgEfficiency * 1.2) return { icon: <Rocket className="h-4 w-4" />, label: 'High Performer', color: 'text-green-600' }
    if (efficiency < avgEfficiency * 0.8) return { icon: <AlertTriangle className="h-4 w-4" />, label: 'Underperformer', color: 'text-red-600' }
    return { icon: <BarChart3 className="h-4 w-4" />, label: 'Average', color: 'text-blue-600' }
  }
  
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h4 className="font-medium text-sm text-gray-600">{title}</h4>
        {showPerformance && (
          <div className="text-xs text-gray-500">
            Avg ROI: {avgEfficiency.toFixed(2)}
          </div>
        )}
      </div>
      {data.map((item, index) => {
        const performance = getPerformanceIndicator(item.efficiency)
        return (
          <div key={index} className="space-y-1">
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center gap-2">
                <span className="font-medium">{item.name}</span>
                {performance && (
                  <span className={`text-xs ${performance.color} flex items-center gap-1`}>
                    {performance.icon} {performance.label}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {item.efficiency && showPerformance && (
                  <span className="text-xs text-gray-500">
                    ROI: {item.efficiency.toFixed(2)}
                  </span>
                )}
                <span className="text-gray-600">{item.value.toLocaleString()}</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="h-3 rounded-full transition-all duration-500 relative"
                style={{
                  width: `${(item.value / maxValue) * 100}%`,
                  backgroundColor: item.color
                }}
              >
                {/* Performance gradient overlay */}
                {performance && (
                  <div 
                    className="absolute inset-0 rounded-full opacity-20"
                    style={{
                      background: performance.color.includes('green') ? 'linear-gradient(90deg, transparent, #10b981)' :
                                 performance.color.includes('red') ? 'linear-gradient(90deg, transparent, #ef4444)' :
                                 'linear-gradient(90deg, transparent, #3b82f6)'
                    }}
                  />
                )}
              </div>
            </div>
          </div>
        )
      })}
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

/**
 * Shows channel contributions in a bar chart
 * 
 * Fetches channel data and displays it with performance indicators.
 */
export function SimpleContributionChart() {
  const { getChannelSummary, getResponseCurves, loading, error } = useMMMData()
  const { token } = useAuth()
  const [data, setData] = useState<Array<{name: string, value: number, color: string, efficiency?: number}>>([])

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  useEffect(() => {
    if (!token) return // Don't fetch data if not authenticated
    
    let isMounted = true
    
    const fetchData = async () => {
      try {
        // Fetch both contribution and efficiency data
        const [summary, responseCurves] = await Promise.all([
          getChannelSummary(),
          getResponseCurves()
        ])
        
        if (!isMounted) return
        
        const chartData = Object.entries(summary).map(([channel, data], index) => {
          // Get efficiency from response curves
          const efficiency = responseCurves.curves && typeof responseCurves.curves === 'object' && 
                            responseCurves.curves[channel as keyof typeof responseCurves.curves]?.efficiency || 0
          
          return {
            name: formatChannelName(channel),
            value: Math.round(data.total_contribution),
            color: COLORS[index % COLORS.length] || '#8884D8',
            efficiency: efficiency
          }
        })
        
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
  }, [token])

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
        <CardDescription>Top performing media channels with ROI insights</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 mb-6">
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
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {data.length > 0 ? (data.reduce((sum, item) => sum + (item.efficiency || 0), 0) / data.length).toFixed(2) : '0.00'}
            </div>
            <div className="text-sm text-gray-500">Avg ROI</div>
          </div>
        </div>

        <SimpleBarChart data={data} title="Channel Contributions" showPerformance={true} />
        
        {data.length > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center gap-2 text-sm text-blue-800">
              <Lightbulb className="h-4 w-4" />
              <span className="font-medium">Performance Insight:</span>
            </div>
            <p className="text-sm text-blue-700 mt-1">
              {data.find(d => d.efficiency && d.efficiency > 1.4) ? 
                `${data.find(d => d.efficiency && d.efficiency > 1.4)?.name} shows exceptional ROI (${data.find(d => d.efficiency && d.efficiency > 1.4)?.efficiency?.toFixed(2)}). Consider increasing investment.` :
                `Top performer: ${data[0]?.name} with ${data[0]?.efficiency?.toFixed(2) || 'N/A'} ROI. Monitor for optimization opportunities.`
              }
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Interactive response curves chart
 * 
 * Shows spend vs response curves for each channel. User can pick
 * which channel to view from a dropdown.
 */
export function SimpleResponseCurves() {
  const { getResponseCurves, getChannels, loading, error } = useMMMData()
  const { token } = useAuth()
  const [selectedChannel, setSelectedChannel] = useState<string>('')
  const [channels, setChannels] = useState<string[]>([])
  const [curveData, setCurveData] = useState<Array<{x: number, y: number}>>([])
  const [saturationPoint, setSaturationPoint] = useState<number>(0)
  const [efficiency, setEfficiency] = useState<number>(0)
  const [allCurvesData, setAllCurvesData] = useState<Record<string, any>>({})

  // Initial data fetch
  useEffect(() => {
    if (!token) return // Don't fetch data if not authenticated
    
    let isMounted = true
    
    const fetchData = async () => {
      try {
        const channelList = await getChannels()
        
        if (!isMounted) return
        
        setChannels(channelList)
        setSelectedChannel(channelList[0] || '')

        const allCurves = await getResponseCurves() as { curves: Record<string, any> }
        
        if (!isMounted) return
        
        setAllCurvesData(allCurves.curves)
        
        // Set initial data for first channel
        const firstChannel = channelList[0]
        if (firstChannel && allCurves.curves[firstChannel]) {
          updateChannelData(firstChannel, allCurves.curves)
        }
      } catch (err) {
        console.error('Failed to fetch response curves:', err)
      }
    }

    fetchData()
    
    return () => {
      isMounted = false
    }
  }, [token])

  // Update data when selected channel changes
  useEffect(() => {
    if (selectedChannel && allCurvesData[selectedChannel]) {
      updateChannelData(selectedChannel, allCurvesData)
    }
  }, [selectedChannel, allCurvesData])

  const updateChannelData = (channel: string, curvesData: Record<string, any>) => {
    const data = curvesData[channel]
    if (data) {
      const points = data.spend.slice(0, 20).map((spend: number, index: number) => ({
        x: spend,
        y: data.response[index]
      }))
      setCurveData(points)
      setSaturationPoint(data.saturation_point)
      setEfficiency(data.efficiency)
    }
  }

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
                {formatChannelName(channel)}
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

/**
 * Generates insights from MMM data
 * 
 * Looks at channel performance and creates recommendations like
 * "increase spend on Google Search" or "Facebook is underperforming".
 */
export function SimpleMMInsights() {
  const { getChannelSummary, getMMMInfo, getResponseCurves, loading, error } = useMMMData()
  const { token } = useAuth()
  const [insights, setInsights] = useState<Insight[]>([])
  const [modelInfo, setModelInfo] = useState<any>(null)

  useEffect(() => {
    if (!token) return // Don't fetch data if not authenticated
    
    let isMounted = true
    
    const generateInsights = async () => {
      try {
        const [summary, info, curves] = await Promise.all([
          getChannelSummary(),
          getMMMInfo(),
          getResponseCurves()
        ])
        
        if (!isMounted) return
        
        setModelInfo(info)

        const channels = Object.entries(summary)
        const sortedByEfficiency = channels.sort(([,a], [,b]) => (b as any).efficiency - (a as any).efficiency)
        const topPerformer = sortedByEfficiency[0]
        const underPerformer = sortedByEfficiency[sortedByEfficiency.length - 1]

        const generatedInsights: Insight[] = []
        
        // Calculate efficiency statistics
        const efficiencies = Object.values(curves.curves || {}).map((c: any) => c?.efficiency || 0).filter(e => e > 0)
        const avgEfficiency = efficiencies.length > 0 ? efficiencies.reduce((a, b) => a + b, 0) / efficiencies.length : 1
        const maxEfficiency = efficiencies.length > 0 ? Math.max(...efficiencies) : 1
        const minEfficiency = efficiencies.length > 0 ? Math.min(...efficiencies) : 1
        
        if (topPerformer) {
          const topEfficiency = (topPerformer[1] as any).efficiency
          const topChannelCurve = (curves.curves as any)?.[topPerformer[0]]
          const saturationPoint = topChannelCurve?.saturation_point || 50000
          
          generatedInsights.push({
            type: 'success',
            title: `${topPerformer[0].replace(/_/g, ' ')} is your top performer`,
            icon: <Rocket className="h-5 w-5" />,
            description: `ROI: ${topEfficiency.toFixed(2)} (${((topEfficiency - avgEfficiency) / avgEfficiency * 100).toFixed(0)}% above average). Saturation at $${saturationPoint.toLocaleString()}. Consider increasing spend up to this threshold.`
          })
        }
        
        if (underPerformer && underPerformer !== topPerformer) {
          const underEfficiency = (underPerformer[1] as any).efficiency
          const potentialGain = ((avgEfficiency - underEfficiency) / underEfficiency * 100).toFixed(0)
          
          generatedInsights.push({
            type: 'warning',
            title: `${underPerformer[0].replace(/_/g, ' ')} underperforming`,
            icon: <AlertTriangle className="h-5 w-5" />,
            description: `ROI: ${underEfficiency.toFixed(2)} (${potentialGain}% below average). Optimize targeting, creative, or reduce spend and reallocate to higher-performing channels.`
          })
        }
        
        // Budget reallocation recommendation
        if (topPerformer && underPerformer && topPerformer !== underPerformer) {
          const efficiencyGap = (topPerformer[1] as any).efficiency - (underPerformer[1] as any).efficiency
          generatedInsights.push({
            type: 'info',
            title: `Budget Optimization Opportunity`,
            icon: <Lightbulb className="h-5 w-5" />,
            description: `Shifting budget from ${underPerformer[0].replace(/_/g, ' ')} to ${topPerformer[0].replace(/_/g, ' ')} could improve ROI by ${efficiencyGap.toFixed(2)}x per dollar spent.`
          })
        }
        
        // Saturation warnings
        const nearSaturation = Object.entries(curves.curves || {}).filter(([_, data]: [string, any]) => {
          // Assume current spend is 70% of saturation point for this example
          return data?.saturation_point && data.saturation_point < 50000 // Low saturation threshold
        })
        
        if (nearSaturation.length > 0) {
          generatedInsights.push({
            type: 'warning',
            title: `Saturation Alert`,
            icon: <BarChart2 className="h-5 w-5" />,
            description: `${nearSaturation.map(([name]) => name.replace(/_/g, ' ')).join(', ')} ${nearSaturation.length === 1 ? 'has' : 'have'} low saturation points. Monitor spend levels to avoid diminishing returns.`
          })
        }
        
        generatedInsights.push({
          type: 'info',
          title: 'Portfolio Performance',
          icon: <TrendingUp className="h-5 w-5" />,
          description: `Average ROI: ${avgEfficiency.toFixed(2)} | Best: ${maxEfficiency.toFixed(2)} | Worst: ${minEfficiency.toFixed(2)} | ${info.total_weeks} weeks analyzed across ${info.channels.length} channels.`
        })

        setInsights(generatedInsights)
      } catch (err) {
        console.error('Failed to generate insights:', err)
      }
    }

    generateInsights()
    
    return () => {
      isMounted = false
    }
  }, [token])

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
          <h4 className="font-semibold flex items-center gap-2">
            <Search className="h-5 w-5" />
            Key Insights
          </h4>
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
                  {insight.icon || (insight.type === 'success' ? <CheckCircle className="h-5 w-5" /> :
                   insight.type === 'warning' ? <AlertTriangle className="h-5 w-5" /> :
                   <Lightbulb className="h-5 w-5" />)}
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
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Next Steps
          </h4>
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
