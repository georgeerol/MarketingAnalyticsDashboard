/**
 * Export dialog component for MMM insights
 */

'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@workspace/ui/components/dialog'
import { Button } from '@workspace/ui/components/button'
import { Card, CardContent } from '@workspace/ui/components/card'
import { Download, FileText, FileSpreadsheet, FileJson, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { exportInsights, ExportFormat, getFormatInfo } from '@/lib/export'

interface ExportDialogProps {
  children: React.ReactNode
}

export function ExportDialog({ children }: ExportDialogProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [exportStatus, setExportStatus] = useState<{
    type: 'success' | 'error' | null
    message: string
  }>({ type: null, message: '' })

  const exportFormats: ExportFormat[] = ['txt', 'csv', 'json']

  const getFormatIcon = (format: ExportFormat) => {
    switch (format) {
      case 'txt': return <FileText className="h-6 w-6" />
      case 'csv': return <FileSpreadsheet className="h-6 w-6" />
      case 'json': return <FileJson className="h-6 w-6" />
    }
  }

  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true)
    setExportStatus({ type: null, message: '' })

    try {
      await exportInsights({ format })
      setExportStatus({
        type: 'success',
        message: `Successfully exported insights as ${format.toUpperCase()}`
      })
      
      // Auto-close dialog after successful export
      setTimeout(() => {
        setIsOpen(false)
        setExportStatus({ type: null, message: '' })
      }, 2000)
      
    } catch (error) {
      setExportStatus({
        type: 'error',
        message: error instanceof Error ? error.message : 'Export failed'
      })
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Export Recommendations
          </DialogTitle>
          <DialogDescription>
            Download your MMM insights and recommendations in your preferred format.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Export Status */}
          {exportStatus.type && (
            <div className={`p-3 rounded-lg flex items-center gap-2 ${
              exportStatus.type === 'success' 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {exportStatus.type === 'success' ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <span className="text-sm">{exportStatus.message}</span>
            </div>
          )}

          {/* Format Options */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-900">Choose Export Format:</h4>
            
            {exportFormats.map((format) => {
              const formatInfo = getFormatInfo(format)
              return (
                <Card key={format} className="cursor-pointer hover:shadow-sm transition-shadow">
                  <CardContent className="p-4">
                    <Button
                      variant="ghost"
                      className="w-full justify-start h-auto p-0"
                      onClick={() => handleExport(format)}
                      disabled={isExporting}
                    >
                      <div className="flex items-center gap-3 w-full">
                        <div className="text-blue-600">
                          {getFormatIcon(format)}
                        </div>
                        <div className="flex-1 text-left">
                          <div className="font-medium text-gray-900">
                            {formatInfo.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatInfo.description}
                          </div>
                        </div>
                        {isExporting ? (
                          <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                        ) : (
                          <Download className="h-4 w-4 text-gray-400" />
                        )}
                      </div>
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Export Info */}
          <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
            <p className="font-medium mb-1">What's included in the export:</p>
            <ul className="space-y-1">
              <li>• Channel performance metrics and efficiency scores</li>
              <li>• Key insights and recommendations</li>
              <li>• Saturation points and optimization opportunities</li>
              <li>• Model metadata and analysis period</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
