/**
 * MMM insights and recommendations component
 */

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card'
import { useMMMData } from '@/hooks/use-mmm-data'
import { Loader2, Lightbulb, TrendingUp, AlertTriangle, CheckCircle, ArrowRight, Search, Target } from 'lucide-react'
import { formatChannelName } from '@/lib/format-channel'

interface Insight {
  type: 'success' | 'warning' | 'info'
  title: string
  description: string
  action?: string
  icon: React.ReactNode
}

interface ChannelRecommendation {
  channel: string
  action: 'increase' | 'decrease' | 'maintain'
  reason: string
  impact: 'high' | 'medium' | 'low'
}

/**
 * Main insights component with recommendations
 * 
 * Analyzes channel performance and shows insights like
 * "Google Search is your top performer" with action items.
 */
export function MMMInsights() {
  const { getChannelSummary, getMMMInfo, loading, error } = useMMMData()
  const [insights, setInsights] = useState<Insight[]>([])
  const [recommendations, setRecommendations] = useState<ChannelRecommendation[]>([])
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

        // Generate insights based on data
        const generatedInsights: Insight[] = []
        const generatedRecommendations: ChannelRecommendation[] = []

        const channels = Object.entries(summary)
        const totalContribution = channels.reduce((sum, [_, data]) => sum + data.total_contribution, 0)
        
        // Sort channels by efficiency
        const sortedByEfficiency = channels.sort(([,a], [,b]) => b.efficiency - a.efficiency)
        const topPerformer = sortedByEfficiency[0]
        const underPerformer = sortedByEfficiency[sortedByEfficiency.length - 1]

        // Top performer insight
        if (topPerformer) {
          generatedInsights.push({
            type: 'success',
            title: `${formatChannelName(topPerformer[0])} is your top performer`,
            description: `With an efficiency of ${topPerformer[1].efficiency.toFixed(2)}, this channel delivers the highest ROI.`,
            action: 'Consider increasing investment',
            icon: <CheckCircle className="h-5 w-5" />
          })

          generatedRecommendations.push({
            channel: formatChannelName(topPerformer[0]),
            action: 'increase',
            reason: 'Highest efficiency and strong performance',
            impact: 'high'
          })
        }

        // Under-performer insight
        if (underPerformer && underPerformer[1].efficiency < 0.5) {
          generatedInsights.push({
            type: 'warning',
            title: `${formatChannelName(underPerformer[0])} needs optimization`,
            description: `Low efficiency of ${underPerformer[1].efficiency.toFixed(2)} suggests room for improvement.`,
            action: 'Review targeting and creative',
            icon: <AlertTriangle className="h-5 w-5" />
          })

          generatedRecommendations.push({
            channel: formatChannelName(underPerformer[0]),
            action: 'decrease',
            reason: 'Below average efficiency, needs optimization',
            impact: 'medium'
          })
        }

        // Budget distribution insight
        const topChannels = sortedByEfficiency.slice(0, 3)
        const topChannelsShare = topChannels.reduce((sum, [_, data]) => sum + data.contribution_share, 0)
        
        if (topChannelsShare < 0.6) {
          generatedInsights.push({
            type: 'info',
            title: 'Budget distribution opportunity',
            description: `Your top 3 channels account for ${Math.round(topChannelsShare * 100)}% of contribution. Consider reallocating budget.`,
            action: 'Optimize budget allocation',
            icon: <TrendingUp className="h-5 w-5" />
          })
        }

        // Model data quality insight
        generatedInsights.push({
          type: 'info',
          title: 'Model Coverage',
          description: `Analysis covers ${info.total_weeks} weeks across ${info.channels.length} channels with ${info.data_frequency} data.`,
          icon: <Lightbulb className="h-5 w-5" />
        })

        // Add recommendations for middle performers
        const middlePerformers = sortedByEfficiency.slice(1, -1)
        middlePerformers.forEach(([channel, data]) => {
          if (data.contribution_share > 0.1) { // Significant channels
            generatedRecommendations.push({
              channel: formatChannelName(channel),
              action: 'maintain',
              reason: 'Solid performance with growth potential',
              impact: 'medium'
            })
          }
        })

        if (!isMounted) return
        
        setInsights(generatedInsights)
        setRecommendations(generatedRecommendations.slice(0, 6)) // Limit to 6 recommendations
      } catch (err) {
        console.error('Failed to generate insights:', err)
      }
    }

    generateInsights()
    
    return () => {
      isMounted = false
    }
  }, []) // Remove dependencies to prevent infinite loop

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>MMM Insights</CardTitle>
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

  const getActionColor = (action: string) => {
    switch (action) {
      case 'increase': return 'text-green-600 bg-green-50'
      case 'decrease': return 'text-red-600 bg-red-50'
      case 'maintain': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getImpactBadge = (impact: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[impact as keyof typeof colors] || colors.low
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
        {/* Model Info */}
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

        {/* Key Insights */}
        <div className="space-y-4 mb-6">
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
                  {insight.icon}
                </div>
                <div className="flex-1">
                  <h5 className="font-medium mb-1">{insight.title}</h5>
                  <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                  {insight.action && (
                    <div className="flex items-center gap-1 text-sm font-medium text-blue-600">
                      <ArrowRight className="h-3 w-3" />
                      {insight.action}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Channel Recommendations */}
        <div>
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Target className="h-5 w-5" />
            Channel Recommendations
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recommendations.map((rec, index) => (
              <div key={index} className="p-3 border rounded-lg hover:shadow-sm transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{rec.channel}</span>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getActionColor(rec.action)}`}>
                      {rec.action.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getImpactBadge(rec.impact)}`}>
                      {rec.impact}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{rec.reason}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Next Steps
          </h4>
          <p className="text-sm text-gray-700 mb-3">
            Based on your MMM analysis, focus on optimizing your top-performing channels while 
            improving efficiency in underperforming areas.
          </p>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
            Export Recommendations
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
