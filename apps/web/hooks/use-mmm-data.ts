/**
 * @fileoverview MMM Data Hook
 * 
 * Custom React hook for fetching and managing Media Mix Modeling (MMM) data.
 * Provides a centralized interface for accessing MMM API endpoints with
 * authentication, loading states, and error handling.
 * 
 * @author MMM Dashboard Team
 * @version 1.0.0
 */

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'

/**
 * MMM Channel data structure containing performance metrics
 * @interface MMMChannel
 */
interface MMMChannel {
  /** Channel name (e.g., 'Google Search', 'Facebook') */
  name: string
  /** Total spend amount for the channel */
  total_spend: number
  /** Total contribution value generated */
  total_contribution: number
  /** Share of total contribution (0-1) */
  contribution_share: number
  /** Channel efficiency (ROI metric) */
  efficiency: number
  /** Average weekly spend */
  avg_weekly_spend: number
  /** Average weekly contribution */
  avg_weekly_contribution: number
}

/**
 * MMM Contribution data for a specific channel
 * @interface MMMContribution
 */
interface MMMContribution {
  /** Channel name */
  channel: string
  /** Time series contribution data */
  data: number[]
  /** Statistical summary of contribution data */
  summary: {
    /** Mean contribution value */
    mean: number
    /** Total contribution */
    total: number
    /** Maximum contribution value */
    max: number
    /** Minimum contribution value */
    min: number
  }
}

/**
 * MMM Response Curve data showing spend vs response relationship
 * @interface MMMResponseCurve
 */
interface MMMResponseCurve {
  /** Channel name */
  channel: string
  /** Response curve data points */
  curves: {
    /** Spend values (x-axis) */
    spend: number[]
    /** Response values (y-axis) */
    response: number[]
    /** Saturation point where diminishing returns begin */
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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

/**
 * MMM Data Hook
 * 
 * Custom React hook that provides a comprehensive interface for fetching and managing
 * Media Mix Modeling data from the backend API. Handles authentication, loading states,
 * error management, and provides methods for accessing all MMM endpoints.
 * 
 * Features:
 * - Automatic authentication token handling
 * - Centralized loading and error state management
 * - Type-safe API responses
 * - Consistent error handling across all endpoints
 * - Support for both summary and detailed MMM data
 * 
 * Available Methods:
 * - getChannels(): Get list of available marketing channels
 * - getChannelSummary(): Get performance summary for all channels
 * - getContributionData(): Get contribution time series data
 * - getResponseCurves(): Get response curve data for optimization
 * - getMMMInfo(): Get model metadata and information
 * - getMMMStatus(): Get current model status
 * 
 * @returns {Object} Hook interface with data fetching methods and state
 * 
 * @example
 * ```tsx
 * function MMMDashboard() {
 *   const { getChannelSummary, getResponseCurves, loading, error } = useMMMData()
 *   const [channels, setChannels] = useState([])
 *   
 *   useEffect(() => {
 *     const fetchData = async () => {
 *       try {
 *         const summary = await getChannelSummary()
 *         setChannels(Object.entries(summary))
 *       } catch (err) {
 *         console.error('Failed to fetch channel data:', err)
 *       }
 *     }
 *     
 *     fetchData()
 *   }, [])
 *   
 *   if (loading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error}</div>
 *   
 *   return <ChannelChart data={channels} />
 * }
 * ```
 * 
 * @see {@link useAuth} for authentication state
 * @see {@link MMMChannel} for channel data structure
 * @see {@link MMMContribution} for contribution data structure
 * @see {@link MMMResponseCurve} for response curve data structure
 */
export function useMMMData() {
  const { token } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWithAuth = async (url: string) => {
    if (!token) throw new Error('No authentication token')
    
    const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}${url}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.')
      }
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
