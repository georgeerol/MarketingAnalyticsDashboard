"""
Export API endpoints for MMM insights and recommendations.
"""

from datetime import datetime
from typing import Dict, Any
import json
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.mmm_service import MMMService

router = APIRouter()


def generate_insights_data(mmm_service: MMMService) -> Dict[str, Any]:
    """Generate insights data for export"""
    try:
        # Get all the data we need
        channel_summary = mmm_service.get_channel_summary()
        model_info = mmm_service.get_model_info()
        response_curves = mmm_service.get_response_curves()
        
        # Calculate insights similar to frontend
        channels = list(channel_summary.items())
        total_contribution = sum(data.total_contribution for _, data in channels)
        
        # Sort channels by efficiency
        sorted_by_efficiency = sorted(channels, key=lambda x: x[1].efficiency, reverse=True)
        top_performer = sorted_by_efficiency[0] if sorted_by_efficiency else None
        under_performer = sorted_by_efficiency[-1] if sorted_by_efficiency else None
        
        # Generate insights
        insights = []
        recommendations = []
        
        # Top performer insight
        if top_performer:
            insights.append({
                "type": "success",
                "title": f"{top_performer[0]} is your top performer",
                "description": f"With an efficiency of {top_performer[1].efficiency:.2f}, this channel delivers the highest ROI.",
                "action": "Consider increasing investment",
                "channel": top_performer[0],
                "efficiency": top_performer[1].efficiency,
                "saturation_point": response_curves['curves'][top_performer[0]]['saturation_point']
            })
            
            recommendations.append({
                "channel": top_performer[0],
                "action": "increase",
                "reason": "Highest efficiency and strong performance",
                "impact": "high",
                "current_efficiency": top_performer[1].efficiency,
                "saturation_point": response_curves['curves'][top_performer[0]]['saturation_point']
            })
        
        # Under-performer insight
        if under_performer and under_performer[1].efficiency < 1.0:
            insights.append({
                "type": "warning",
                "title": f"{under_performer[0]} needs optimization",
                "description": f"Efficiency of {under_performer[1].efficiency:.2f} suggests room for improvement.",
                "action": "Review targeting and creative",
                "channel": under_performer[0],
                "efficiency": under_performer[1].efficiency,
                "saturation_point": response_curves['curves'][under_performer[0]]['saturation_point']
            })
            
            recommendations.append({
                "channel": under_performer[0],
                "action": "optimize",
                "reason": "Below average efficiency, needs optimization",
                "impact": "medium",
                "current_efficiency": under_performer[1].efficiency,
                "saturation_point": response_curves['curves'][under_performer[0]]['saturation_point']
            })
        
        # Budget optimization insights
        avg_efficiency = sum(data.efficiency for _, data in channels) / len(channels)
        high_performers = [ch for ch, data in channels if data.efficiency > avg_efficiency * 1.2]
        
        if len(high_performers) >= 2:
            insights.append({
                "type": "info",
                "title": "Budget reallocation opportunity",
                "description": f"Consider shifting budget to {', '.join(high_performers[:2])} for improved ROI.",
                "action": "Optimize budget allocation"
            })
        
        # Add recommendations for all channels
        for channel, data in channels:
            if channel not in [r['channel'] for r in recommendations]:
                if data.efficiency > avg_efficiency:
                    recommendations.append({
                        "channel": channel,
                        "action": "maintain" if data.efficiency < avg_efficiency * 1.3 else "increase",
                        "reason": "Good performance with growth potential",
                        "impact": "medium",
                        "current_efficiency": data.efficiency,
                        "saturation_point": response_curves['curves'][channel]['saturation_point']
                    })
        
        return {
            "export_metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_type": model_info.model_type,
                "training_period": model_info.training_period,
                "data_source": model_info.data_source,
                "total_weeks": model_info.total_weeks,
                "channels_analyzed": len(model_info.channels)
            },
            "model_info": {
                "model_type": model_info.model_type,
                "version": model_info.version,
                "training_period": model_info.training_period,
                "channels": model_info.channels,
                "data_frequency": model_info.data_frequency,
                "total_weeks": model_info.total_weeks,
                "data_source": model_info.data_source
            },
            "channel_performance": {
                channel: {
                    "efficiency": data.efficiency,
                    "total_contribution": data.total_contribution,
                    "contribution_share": data.contribution_share,
                    "saturation_point": response_curves['curves'][channel]['saturation_point'],
                    "adstock_rate": response_curves['curves'][channel]['adstock_rate']
                }
                for channel, data in channels
            },
            "insights": insights,
            "recommendations": recommendations,
            "summary_statistics": {
                "total_channels": len(channels),
                "average_efficiency": avg_efficiency,
                "best_performer": top_performer[0] if top_performer else None,
                "best_efficiency": top_performer[1].efficiency if top_performer else None,
                "total_contribution": total_contribution,
                "high_performers": high_performers
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights data: {str(e)}")


def format_as_csv(data: Dict[str, Any]) -> str:
    """Format data as CSV"""
    output = io.StringIO()
    
    # Write metadata
    writer = csv.writer(output)
    writer.writerow(["MMM INSIGHTS EXPORT"])
    writer.writerow(["Generated:", data['export_metadata']['generated_at']])
    writer.writerow(["Model:", data['export_metadata']['model_type']])
    writer.writerow(["Period:", data['model_info']['training_period']])
    writer.writerow([])
    
    # Channel Performance
    writer.writerow(["CHANNEL PERFORMANCE"])
    writer.writerow(["Channel", "Efficiency", "Total Contribution", "Contribution Share", "Saturation Point", "Adstock Rate"])
    
    for channel, perf in data['channel_performance'].items():
        writer.writerow([
            channel,
            f"{perf['efficiency']:.3f}",
            f"{perf['total_contribution']:,.0f}",
            f"{perf['contribution_share']:.1%}",
            f"${perf['saturation_point']:,.0f}",
            f"{perf['adstock_rate']:.3f}"
        ])
    
    writer.writerow([])
    
    # Insights
    writer.writerow(["KEY INSIGHTS"])
    writer.writerow(["Type", "Title", "Description", "Action"])
    
    for insight in data['insights']:
        writer.writerow([
            insight['type'],
            insight['title'],
            insight['description'],
            insight.get('action', '')
        ])
    
    writer.writerow([])
    
    # Recommendations
    writer.writerow(["RECOMMENDATIONS"])
    writer.writerow(["Channel", "Action", "Reason", "Impact", "Current Efficiency", "Saturation Point"])
    
    for rec in data['recommendations']:
        writer.writerow([
            rec['channel'],
            rec['action'],
            rec['reason'],
            rec['impact'],
            f"{rec['current_efficiency']:.3f}",
            f"${rec['saturation_point']:,.0f}"
        ])
    
    return output.getvalue()


def format_as_json(data: Dict[str, Any]) -> str:
    """Format data as JSON"""
    return json.dumps(data, indent=2, default=str)


def format_as_text(data: Dict[str, Any]) -> str:
    """Format data as text report"""
    lines = []
    lines.append("=" * 80)
    lines.append("MMM INSIGHTS & RECOMMENDATIONS REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {data['export_metadata']['generated_at']}")
    lines.append(f"Model: {data['export_metadata']['model_type']}")
    lines.append(f"Analysis Period: {data['model_info']['training_period']}")
    lines.append(f"Data Coverage: {data['export_metadata']['total_weeks']} weeks, {data['export_metadata']['channels_analyzed']} channels")
    lines.append("")
    
    # Executive Summary
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 40)
    summary = data['summary_statistics']
    lines.append(f"• Total Channels Analyzed: {summary['total_channels']}")
    lines.append(f"• Average Efficiency: {summary['average_efficiency']:.3f}")
    lines.append(f"• Best Performer: {summary['best_performer']} (Efficiency: {summary['best_efficiency']:.3f})")
    lines.append(f"• Total Contribution: {summary['total_contribution']:,.0f}")
    lines.append("")
    
    # Channel Performance
    lines.append("CHANNEL PERFORMANCE")
    lines.append("-" * 40)
    for channel, perf in data['channel_performance'].items():
        lines.append(f"\n{channel}:")
        lines.append(f"  • Efficiency: {perf['efficiency']:.3f}")
        lines.append(f"  • Total Contribution: {perf['total_contribution']:,.0f}")
        lines.append(f"  • Market Share: {perf['contribution_share']:.1%}")
        lines.append(f"  • Saturation Point: ${perf['saturation_point']:,.0f}")
        lines.append(f"  • Adstock Rate: {perf['adstock_rate']:.3f}")
    
    lines.append("")
    
    # Key Insights
    lines.append("KEY INSIGHTS")
    lines.append("-" * 40)
    for i, insight in enumerate(data['insights'], 1):
        icon = "[SUCCESS]" if insight['type'] == 'success' else "[WARNING]" if insight['type'] == 'warning' else "[INFO]"
        lines.append(f"\n{i}. {icon} {insight['title']}")
        lines.append(f"   {insight['description']}")
        if insight.get('action'):
            lines.append(f"   → Action: {insight['action']}")
    
    lines.append("")
    
    # Recommendations
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 40)
    for i, rec in enumerate(data['recommendations'], 1):
        action_icon = "[INCREASE]" if rec['action'] == 'increase' else "[OPTIMIZE]" if rec['action'] == 'optimize' else "[ANALYZE]"
        impact_text = rec['impact'].upper()
        lines.append(f"\n{i}. {action_icon} {rec['channel']} - {rec['action'].upper()} ({impact_text} IMPACT)")
        lines.append(f"   Reason: {rec['reason']}")
        lines.append(f"   Current Efficiency: {rec['current_efficiency']:.3f}")
        lines.append(f"   Saturation Point: ${rec['saturation_point']:,.0f}")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


@router.get("/insights")
async def export_insights(
    format: str = Query("json", pattern="^(json|csv|txt)$"),
    current_user: User = Depends(get_current_user)
):
    """Export MMM insights"""
    try:
        mmm_service = MMMService()
        insights_data = generate_insights_data(mmm_service)
        
        # Format based on requested type
        if format == "csv":
            content = format_as_csv(insights_data)
            media_type = "text/csv"
            filename = f"mmm_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        elif format == "txt":
            content = format_as_text(insights_data)
            media_type = "text/plain"
            filename = f"mmm_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:  # json
            content = format_as_json(insights_data)
            media_type = "application/json"
            filename = f"mmm_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Return as streaming response for download
        return StreamingResponse(
            io.StringIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

