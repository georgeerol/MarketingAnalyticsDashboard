/**
 * Export utilities for downloading MMM insights and recommendations
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export type ExportFormat = 'json' | 'csv' | 'txt'

export interface ExportOptions {
  format: ExportFormat
  filename?: string
}

/**
 * Download MMM insights in the specified format
 */
export async function exportInsights(options: ExportOptions): Promise<void> {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('Authentication required')
    }

    const response = await fetch(
      `${API_BASE}/api/v1/export/insights?format=${options.format}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Export failed: ${response.status}`)
    }

    // Get the filename from the response headers or use provided/default
    const contentDisposition = response.headers.get('content-disposition')
    let filename = options.filename
    
    if (!filename && contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    if (!filename) {
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
      filename = `mmm_insights_${timestamp}.${options.format}`
    }

    // Create blob and download
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('Export failed:', error)
    throw error
  }
}

/**
 * Preview insights data (JSON format only)
 */
export async function previewInsights(): Promise<any> {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('Authentication required')
    }

    const response = await fetch(
      `${API_BASE}/api/v1/export/insights/preview`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Preview failed: ${response.status}`)
    }

    return await response.json()
    
  } catch (error) {
    console.error('Preview failed:', error)
    throw error
  }
}

/**
 * Get export format display information
 */
export function getFormatInfo(format: ExportFormat) {
  const formatInfo = {
    json: {
      name: 'JSON',
      description: 'Structured data format',
      icon: '📄',
      mimeType: 'application/json'
    },
    csv: {
      name: 'CSV',
      description: 'Spreadsheet compatible',
      icon: '📊',
      mimeType: 'text/csv'
    },
    txt: {
      name: 'Text Report',
      description: 'Human-readable report',
      icon: '📝',
      mimeType: 'text/plain'
    }
  }
  
  return formatInfo[format]
}

/**
 * Validate export format
 */
export function isValidFormat(format: string): format is ExportFormat {
  return ['json', 'csv', 'txt'].includes(format)
}
