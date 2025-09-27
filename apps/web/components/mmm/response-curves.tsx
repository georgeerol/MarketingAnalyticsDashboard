'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card'
import { useMMMData } from '@/hooks/use-mmm-data'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { Loader2, TrendingDown, Target, Zap, BarChart3 } from 'lucide-react'
import { formatChannelName } from '@/lib/format-channel'

interface CurveData {
  spend: number
  response: number
}

interface ChannelCurve {
  channel: string
  data: CurveData[]
  saturation_point: number
  efficiency: number
  adstock_rate: number
}

export function ResponseCurves() {
  const { getResponseCurves, getChannels, loading, error } = useMMMData()
  const [curves, setCurves] = useState<ChannelCurve[]>([])
  const [selectedChannel, setSelectedChannel] = useState<string>('')
  const [channels, setChannels] = useState<string[]>([])

  useEffect(() => {
    let isMounted = true
    
    const fetchData = async () => {
      try {
        // Get all channels first
        const channelList = await getChannels()
        
        if (!isMounted) return
        
        setChannels(channelList)
        setSelectedChannel(channelList[0] || '')

        // Get response curves for all channels
        const allCurves = await getResponseCurves() as { curves: Record<string, any> }
        
        if (!isMounted) return
        
        const curveData = Object.entries(allCurves.curves).map(([channel, data]) => ({
          channel: formatChannelName(channel),
          data: data.spend.map((spend: number, index: number) => ({
            spend: Math.round(spend),
            response: Math.round(data.response[index])
          })),
          saturation_point: data.saturation_point,
          efficiency: data.efficiency,
          adstock_rate: data.adstock_rate
        }))

        setCurves(curveData)
      } catch (err) {
        console.error('Failed to fetch response curves:', err)
      }
    }

    fetchData()
    
    return () => {
      isMounted = false
    }
  }, []) // Remove dependencies to prevent infinite loop

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Response Curves</CardTitle>
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

  const selectedCurve = curves.find(c => c.channel === formatChannelName(selectedChannel))
  const maxResponse = selectedCurve ? Math.max(...selectedCurve.data.map(d => d.response)) : 0

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5" />
              Response Curves
            </CardTitle>
            <CardDescription>Analyze diminishing returns and saturation points</CardDescription>
          </div>
          <select
            value={selectedChannel}
            onChange={(e) => setSelectedChannel(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
        {selectedCurve && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-orange-600 mb-1">
                  <Target className="h-4 w-4" />
                </div>
                <div className="text-2xl font-bold text-orange-600">
                  ${Math.round(selectedCurve.saturation_point).toLocaleString()}
                </div>
                <div className="text-sm text-gray-500">Saturation Point</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-green-600 mb-1">
                  <Zap className="h-4 w-4" />
                </div>
                <div className="text-2xl font-bold text-green-600">
                  {selectedCurve.efficiency.toFixed(2)}
                </div>
                <div className="text-sm text-gray-500">Efficiency</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-purple-600 mb-1">
                  <TrendingDown className="h-4 w-4" />
                </div>
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(selectedCurve.adstock_rate * 100)}%
                </div>
                <div className="text-sm text-gray-500">Adstock Rate</div>
              </div>
            </div>

            {/* Response Curve Chart */}
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={selectedCurve.data}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="spend"
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
                  />
                  <YAxis 
                    tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                  />
                  <Tooltip 
                    formatter={(value, name) => [
                      `$${typeof value === 'number' ? value.toLocaleString() : value}`,
                      name === 'response' ? 'Response' : name
                    ]}
                    labelFormatter={(label) => `Spend: $${typeof label === 'number' ? label.toLocaleString() : label}`}
                  />
                  <ReferenceLine 
                    x={selectedCurve.saturation_point} 
                    stroke="#ff7300" 
                    strokeDasharray="5 5"
                    label={{ value: "Saturation", position: "top" }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="response" 
                    stroke="#0088FE" 
                    strokeWidth={3}
                    dot={{ fill: '#0088FE', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Insights */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Key Insights
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="font-medium">Optimal Spend Range:</span>
                  <span className="ml-2 text-gray-700">
                    $0 - ${Math.round(selectedCurve.saturation_point * 0.8).toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Diminishing Returns:</span>
                  <span className="ml-2 text-gray-700">
                    Beyond ${Math.round(selectedCurve.saturation_point).toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Peak Response:</span>
                  <span className="ml-2 text-gray-700">
                    ${maxResponse.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Carryover Effect:</span>
                  <span className="ml-2 text-gray-700">
                    {Math.round(selectedCurve.adstock_rate * 100)}% retention
                  </span>
                </div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
