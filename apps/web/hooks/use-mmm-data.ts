import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'

interface MMMChannel {
  name: string
  total_spend: number
  total_contribution: number
  contribution_share: number
  efficiency: number
  avg_weekly_spend: number
  avg_weekly_contribution: number
}

interface MMMContribution {
  channel: string
  data: number[]
  summary: {
    mean: number
    total: number
    max: number
    min: number
  }
}

interface MMMResponseCurve {
  channel: string
  curves: {
    spend: number[]
    response: number[]
    saturation_point: number
    efficiency: number
    adstock_rate: number
  }
}

interface MMMInfo {
  model_type: string
  version: string
  training_period: string
  channels: string[]
  data_frequency: string
  total_weeks: number
  data_source: string
}

export function useMMMData() {
  const { token } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWithAuth = async (url: string) => {
    if (!token) throw new Error('No authentication token')
    
    const response = await fetch(`http://localhost:8000${url}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }

  const getMMMInfo = async (): Promise<MMMInfo> => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchWithAuth('/mmm/info')
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch MMM info')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getChannels = async (): Promise<string[]> => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchWithAuth('/mmm/channels')
      return data.channels
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch channels')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getContribution = async (channel?: string): Promise<MMMContribution | { channels: string[], data: any[], summary: Record<string, any> }> => {
    setLoading(true)
    setError(null)
    try {
      const url = channel ? `/mmm/contribution?channel=${channel}` : '/mmm/contribution'
      const data = await fetchWithAuth(url)
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch contribution data')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getResponseCurves = async (channel?: string): Promise<MMMResponseCurve | { curves: Record<string, any> }> => {
    setLoading(true)
    setError(null)
    try {
      const url = channel ? `/mmm/response-curves?channel=${channel}` : '/mmm/response-curves'
      const data = await fetchWithAuth(url)
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch response curves')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getChannelSummary = async (): Promise<Record<string, MMMChannel>> => {
    setLoading(true)
    setError(null)
    try {
      // Get both contribution and response curves data to build accurate channel summary
      const [contributionData, responseCurvesData] = await Promise.all([
        fetchWithAuth('/mmm/contribution') as Promise<{ summary: Record<string, any> }>,
        fetchWithAuth('/mmm/response-curves') as Promise<{ curves: Record<string, any> }>
      ])
      const channels = await getChannels()
      
      const summary: Record<string, MMMChannel> = {}
      
      channels.forEach(channel => {
        const channelData = contributionData.summary[channel]
        const curveData = responseCurvesData.curves[channel]
        if (channelData && curveData) {
          summary[channel] = {
            name: channel,
            total_spend: channelData.total * 0.5, // Mock spend calculation
            total_contribution: channelData.total,
            contribution_share: channelData.total / Object.values(contributionData.summary).reduce((sum: number, ch: any) => sum + ch.total, 0),
            efficiency: curveData.efficiency, // Use real efficiency from response curves
            avg_weekly_spend: channelData.mean * 0.5,
            avg_weekly_contribution: channelData.mean
          }
        }
      })
      
      return summary
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch channel summary')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    error,
    getMMMInfo,
    getChannels,
    getContribution,
    getResponseCurves,
    getChannelSummary,
  }
}
