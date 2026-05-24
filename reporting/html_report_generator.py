


# import pandas as pd
# from datetime import datetime

# def generate_html_report(
#     schedule_date,
#     metrics_df,
#     validation_report_1,
#     crew_ac_stats,
#     Schedule_check,
#     unassigned_flights_crew,
#     Standby_crew,
#     leaves_working,
#     crew_mistake_1,
#     crew_mistake_11,
#     crew_mistake_2,
#     crew_mistake_3,
#     aircraft_issue,
#     Block_hour_issue_1,
#     Block_hour_issue_2,
#     duty_hour_issue,
#     sector_issue_1,
#     sector_issue_2,
#     output_crew_stats,
#     swaps_issue,
#     get_short_time_diffs_df,
#     pairings_issue_1,
#     LTC_check,
#     training_issue,
#     aircraft_kpi,
#     flight_kpi,
#     sectors_kpi,
#     aircraft_starting_on_kpi,
#     aircraft_ending_on_kpi,
#     utilized_captain,
#     utilized_first_officer,
#     utilized_flight_attendant,
#     Standyby_captain,
#     Standyby_first_officer,
#     Standyby_flight_attendant,
#     aircraft_input_kpi,
#     flight_input_kpi,
#     sectors_input_kpi,
#     available_captain,
#     available_first_officer,
#     available_flight_attendant,
#     df_validation=None,
#     df_validation_captain=None,
#     df_validation_FO=None,
#     df_validation_FA=None
# ):
#     """
#     Generate a comprehensive HTML report for TMA Crew Scheduler validation with collapsible sections
#     """
    
#     # Calculate summary metrics
#     schedule_issues = len(Schedule_check) + len(unassigned_flights_crew)
#     block_hour_issues = len(Block_hour_issue_1) + len(Block_hour_issue_2)
#     duty_hour_issues = len(duty_hour_issue)
#     sector_issues = len(output_crew_stats[output_crew_stats["Total sectors"] > 14]) + len(sector_issue_1) + len(sector_issue_2)
#     pairing_issues = len(pairings_issue_1) + len(LTC_check) + len(training_issue)
#     unavailable_issues = len(leaves_working) + len(crew_mistake_1) + len(crew_mistake_11)
#     overnight_issues = len(crew_mistake_2) + len(crew_mistake_3)
#     aircraft_issues = len(aircraft_issue) + len(swaps_issue)
    
#     total_crew = utilized_captain + utilized_first_officer + utilized_flight_attendant
#     total_standby = Standyby_captain + Standyby_first_officer + Standyby_flight_attendant
#     total_available = available_captain + available_first_officer + available_flight_attendant
    
#     # Helper function to create status badge
#     def get_status_badge(count):
#         if count == 0:
#             return '<span class="status-badge status-success">✓ No Issues</span>'
#         else:
#             return f'<span class="status-badge status-error">⚠ {count} Issues</span>'
    
#     # Helper function to safely convert DataFrame to HTML
#     def df_to_html_safe(df, table_id=""):
#         if df.empty:
#             return '<p class="no-data">No data to display</p>'
#         return df.to_html(index=False, classes='data-table', table_id=table_id, border=0)
    
#     # Helper function to create distribution charts
#     def create_distribution_chart(df, column, title, chart_id):
#         if df is None or df.empty:
#             return ""
        
#         # Get top 300 performers
#         top_performers = df.nlargest(300, column) if len(df) > 300 else df
        
#         # Create data for chart
#         crews = top_performers['Crew code'].tolist()
#         values = top_performers[column].tolist()
        
#         return f"""
#         <div class="chart-container">
#             <canvas id="{chart_id}"></canvas>
#         </div>
#         <script>
#             new Chart(document.getElementById('{chart_id}'), {{
#                 type: 'bar',
#                 data: {{
#                     labels: {crews},
#                     datasets: [{{
#                         label: '{title}',
#                         data: {values},
#                         backgroundColor: 'rgba(102, 126, 234, 0.8)',
#                         borderColor: 'rgba(102, 126, 234, 1)',
#                         borderWidth: 1
#                     }}]
#                 }},
#                 options: {{
#                     responsive: true,
#                     maintainAspectRatio: false,
#                     scales: {{
#                         y: {{
#                             beginAtZero: true,
#                             title: {{
#                                 display: true,
#                                 text: '{title}'
#                             }}
#                         }},
#                         x: {{
#                             title: {{
#                                 display: true,
#                                 text: 'Crew Code'
#                             }},
#                             ticks: {{
#                                 maxRotation: 90,
#                                 minRotation: 45
#                             }}
#                         }}
#                     }},
#                     plugins: {{
#                         legend: {{
#                             display: true,
#                             position: 'top'
#                         }},
#                         title: {{
#                             display: true,
#                             text: '{title}'
#                         }}
#                     }}
#                 }}
#             }});
#         </script>
#         """
    
#     # Helper function to create pie charts for swaps
#     def create_swaps_pie_chart(df, title, chart_id):
#         if df is None or df.empty:
#             return ""
        
#         # Count crew by number of swaps
#         swaps_count = df['No. of swaps'].value_counts().sort_index()
#         labels = [f"{int(k)} Swaps" for k in swaps_count.index]
#         values = swaps_count.values.tolist()
        
#         # Color scheme
#         colors = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
        
#         return f"""
#         <div class="chart-container-pie">
#             <canvas id="{chart_id}"></canvas>
#         </div>
#         <script>
#             new Chart(document.getElementById('{chart_id}'), {{
#                 type: 'pie',
#                 data: {{
#                     labels: {labels},
#                     datasets: [{{
#                         data: {values},
#                         backgroundColor: {colors},
#                         borderWidth: 2,
#                         borderColor: '#ffffff'
#                     }}]
#                 }},
#                 options: {{
#                     responsive: true,
#                     maintainAspectRatio: false,
#                     plugins: {{
#                         legend: {{
#                             position: 'right'
#                         }},
#                         title: {{
#                             display: true,
#                             text: '{title}',
#                             font: {{
#                                 size: 16,
#                                 weight: 'bold'
#                             }}
#                         }}
#                     }}
#                 }}
#             }});
#         </script>
#         """
    
#     # Build HTML in parts
#     html_header = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>TMA Validation Report - {schedule_date}</title>
#     <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
#     <style>
#         * {{ margin: 0; padding: 0; box-sizing: border-box; }}
#         body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: #1e293b; line-height: 1.6; }}
#         .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
#         .report-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
#         .report-header h1 {{ font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }}
#         .report-header .subtitle {{ font-size: 1.2rem; opacity: 0.9; }}
#         .report-date {{ margin-top: 15px; font-size: 1rem; background: rgba(255,255,255,0.2); display: inline-block; padding: 8px 20px; border-radius: 20px; }}
#         .content {{ padding: 40px; }}
#         .section {{ margin-bottom: 50px; }}
#         .section-header {{ font-size: 1.8rem; font-weight: 700; color: #1e293b; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 3px solid #667eea; }}
#         .subsection-header {{ font-size: 1.4rem; font-weight: 600; color: #334155; margin: 30px 0 15px 0; }}
        
#         /* Accordion Styles */
#         .accordion {{ margin-bottom: 15px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
#         .accordion-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 18px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s ease; user-select: none; }}
#         .accordion-header:hover {{ background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%); transform: translateY(-1px); }}
#         .accordion-header.active {{ background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%); }}
#         .accordion-title {{ font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 10px; }}
#         .accordion-icon {{ font-size: 1.2rem; transition: transform 0.3s ease; }}
#         .accordion-header.active .accordion-icon {{ transform: rotate(180deg); }}
#         .accordion-content {{ max-height: 0; overflow: hidden; transition: max-height 0.4s ease; background: white; }}
#         .accordion-content.active {{ max-height: 10000px; }}
#         .accordion-body {{ padding: 20px; }}
        
#         /* Subsection Accordion */
#         .sub-accordion {{ margin: 15px 0; border: 1px solid #e2e8f0; border-radius: 6px; }}
#         .sub-accordion-header {{ background: #f8fafc; color: #334155; padding: 12px 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s ease; font-weight: 500; }}
#         .sub-accordion-header:hover {{ background: #f1f5f9; }}
#         .sub-accordion-header.active {{ background: #e0e7ff; color: #667eea; }}
#         .sub-accordion-content {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }}
#         .sub-accordion-content.active {{ max-height: 5000px; }}
#         .sub-accordion-body {{ padding: 15px; background: #fafafa; }}
        
#         /* Chart Styles */
#         .chart-container {{ margin: 20px 0; height: 400px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
#         .chart-container-pie {{ margin: 20px 0; height: 350px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
#         .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
#         .charts-grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
        
#         .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
#         .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 25px; color: white; text-align: center; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3); }}
#         .metric-card.success {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); }}
#         .metric-card.warning {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }}
#         .metric-card.error {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }}
#         .metric-label {{ font-size: 0.875rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
#         .metric-value {{ font-size: 2.5rem; font-weight: 700; margin-top: 10px; }}
#         .status-badge {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; margin: 5px; }}
#         .status-success {{ background: #d1fae5; color: #065f46; }}
#         .status-error {{ background: #fee2e2; color: #991b1b; }}
#         .table-container {{ overflow-x: auto; margin: 20px 0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
#         .data-table {{ width: 100%; border-collapse: collapse; background: white; font-size: 0.9rem; }}
#         .data-table thead {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
#         .data-table th {{ padding: 15px; text-align: left; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }}
#         .data-table td {{ padding: 12px 15px; border-bottom: 1px solid #e2e8f0; }}
#         .data-table tbody tr:hover {{ background: #f8fafc; }}
#         .no-data {{ text-align: center; padding: 40px; color: #64748b; font-style: italic; background: #f8fafc; border-radius: 8px; margin: 20px 0; }}
#         .success-box {{ background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left: 4px solid #10b981; border-radius: 8px; padding: 20px; margin: 20px 0; color: #065f46; }}
#         .error-box {{ background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-left: 4px solid #ef4444; border-radius: 8px; padding: 20px; margin: 20px 0; color: #991b1b; }}
#         .info-box {{ background: linear-gradient(135deg, #e0e7ff 0%, #ddd6fe 100%); border-left: 4px solid #667eea; border-radius: 8px; padding: 20px; margin: 20px 0; }}
#         .report-footer {{ background: #f8fafc; padding: 30px; text-align: center; color: #64748b; border-top: 2px solid #e2e8f0; }}
        
#         /* Expand/Collapse All Button */
#         .control-buttons {{ margin-bottom: 20px; display: flex; gap: 10px; }}
#         .control-btn {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.3s ease; }}
#         .control-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }}
        
#         @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; }} .accordion-content {{ max-height: none !important; }} .control-buttons {{ display: none; }} }}
#         @media (max-width: 768px) {{ .content {{ padding: 20px; }} .metrics-grid {{ grid-template-columns: 1fr; }} .report-header h1 {{ font-size: 1.8rem; }} .charts-grid {{ grid-template-columns: 1fr; }} }}
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="report-header">
#             <h1>✈️ TMA Crew Scheduler</h1>
#             <div class="subtitle">Constraints Validation Report</div>
#             <div class="report-date">📅 Schedule Date: {schedule_date}</div>
#             <div class="report-date">🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
#         </div>
#         <div class="content">
#             <div class="control-buttons">
#                 <button class="control-btn" onclick="expandAll()">📂 Expand All</button>
#                 <button class="control-btn" onclick="collapseAll()">📁 Collapse All</button>
#             </div>"""
    
#     html_summary = f"""
#             <div class="section">
#                 <div class="section-header">📊 Executive Summary</div>
#                 <div class="metrics-grid">
#                     <div class="metric-card {'success' if schedule_issues == 0 else 'error'}">
#                         <div class="metric-label">Schedule Issues</div>
#                         <div class="metric-value">{schedule_issues}</div>
#                     </div>
#                     <div class="metric-card {'success' if block_hour_issues == 0 else 'error'}">
#                         <div class="metric-label">BH Violations</div>
#                         <div class="metric-value">{block_hour_issues}</div>
#                     </div>
#                     <div class="metric-card {'success' if duty_hour_issues == 0 else 'error'}">
#                         <div class="metric-label">DH Violations</div>
#                         <div class="metric-value">{duty_hour_issues}</div>
#                     </div>
#                     <div class="metric-card {'success' if sector_issues == 0 else 'error'}">
#                         <div class="metric-label">Sector Violations</div>
#                         <div class="metric-value">{sector_issues}</div>
#                     </div>
#                     <div class="metric-card {'success' if pairing_issues == 0 else 'error'}">
#                         <div class="metric-label">Pairing Issues</div>
#                         <div class="metric-value">{pairing_issues}</div>
#                     </div>
#                     <div class="metric-card {'success' if unavailable_issues == 0 else 'error'}">
#                         <div class="metric-label">Status Issues</div>
#                         <div class="metric-value">{unavailable_issues}</div>
#                     </div>
#                     <div class="metric-card {'success' if overnight_issues == 0 else 'error'}">
#                         <div class="metric-label">Overnight Issues</div>
#                         <div class="metric-value">{overnight_issues}</div>
#                     </div>
#                     <div class="metric-card {'success' if aircraft_issues == 0 else 'error'}">
#                         <div class="metric-label">Aircraft Issues</div>
#                         <div class="metric-value">{aircraft_issues}</div>
#                     </div>
#                 </div>
#             </div>"""
    
#     html_kpi = f"""
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>📈 Key Performance Indicators</span>
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="subsection-header">Available Aircraft and Crew</div>
#                         <div class="metrics-grid">
#                             <div class="metric-card"><div class="metric-label">Total Aircraft</div><div class="metric-value">{aircraft_input_kpi}</div></div>
#                             <div class="metric-card"><div class="metric-label">Total Flights</div><div class="metric-value">{flight_input_kpi}</div></div>
#                             <div class="metric-card"><div class="metric-label">Total Sectors</div><div class="metric-value">{sectors_input_kpi}</div></div>
#                             <div class="metric-card success"><div class="metric-label">Available Crew</div><div class="metric-value">{total_available}</div></div>
#                             <div class="metric-card success"><div class="metric-label">Captains</div><div class="metric-value">{available_captain}</div></div>
#                             <div class="metric-card success"><div class="metric-label">First Officers</div><div class="metric-value">{available_first_officer}</div></div>
#                             <div class="metric-card success"><div class="metric-label">Cabin Crew</div><div class="metric-value">{available_flight_attendant}</div></div>
#                         </div>
#                         <div class="subsection-header">Scheduled Aircraft and Crew</div>
#                         <div class="metrics-grid">
#                             <div class="metric-card"><div class="metric-label">AC Scheduled</div><div class="metric-value">{aircraft_kpi}</div></div>
#                             <div class="metric-card"><div class="metric-label">AC Starting ON</div><div class="metric-value">{aircraft_starting_on_kpi}</div></div>
#                             <div class="metric-card"><div class="metric-label">AC Ending ON</div><div class="metric-value">{aircraft_ending_on_kpi}</div></div>
#                             <div class="metric-card"><div class="metric-label">Flights</div><div class="metric-value">{flight_kpi}</div></div>
#                             <div class="metric-card"><div class="metric-label">Sectors</div><div class="metric-value">{sectors_kpi}</div></div>
#                             <div class="metric-card success"><div class="metric-label">Utilized Crew</div><div class="metric-value">{total_crew}</div></div>
#                             <div class="metric-card success"><div class="metric-label">Captains</div><div class="metric-value">{utilized_captain}</div></div>
#                             <div class="metric-card success"><div class="metric-label">First Officers</div><div class="metric-value">{utilized_first_officer}</div></div>
#                             <div class="metric-card success"><div class="metric-label">Cabin Crew</div><div class="metric-value">{utilized_flight_attendant}</div></div>
#                             <div class="metric-card warning"><div class="metric-label">Standby Crew</div><div class="metric-value">{total_standby}</div></div>
#                             <div class="metric-card warning"><div class="metric-label">Captains</div><div class="metric-value">{Standyby_captain}</div></div>
#                             <div class="metric-card warning"><div class="metric-label">First Officers</div><div class="metric-value">{Standyby_first_officer}</div></div>
#                             <div class="metric-card warning"><div class="metric-label">Cabin Crew</div><div class="metric-value">{Standyby_flight_attendant}</div></div>
#                         </div>
#                     </div>
#                 </div>
#             </div>"""
    
#     html_metrics_table = f"""
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>📊 Detailed Utilization Metrics</span>
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="table-container">{df_to_html_safe(metrics_df, 'metrics-table')}</div>
#                     </div>
#                 </div>
#             </div>"""
    
#     # Add Charts Section
#     html_charts = ""
#     if df_validation is not None:
#         html_charts = f"""
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>📊 Crew Performance Analytics</span>
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="subsection-header">🔄 Aircraft Swaps Distribution</div>
#                         <div class="charts-grid-2">
#                             <div>{create_swaps_pie_chart(df_validation, 'All Crew Swaps', 'chart_swaps_all')}</div>
#                             <div>{create_swaps_pie_chart(df_validation_captain, 'Captain Swaps', 'chart_swaps_captain')}</div>
#                             <div>{create_swaps_pie_chart(df_validation_FO, 'First Officer Swaps', 'chart_swaps_fo')}</div>
#                             <div>{create_swaps_pie_chart(df_validation_FA, 'Flight Attendant Swaps', 'chart_swaps_fa')}</div>
#                         </div>
                        
#                         <div class="subsection-header">⏰ Top Performers - Block Hours</div>
#                         <div class="charts-grid">
#                             <div>{create_distribution_chart(df_validation, 'Block hours', 'All Crew - Block Hours', 'chart_bh_all')}</div>
#                             <div>{create_distribution_chart(df_validation_captain, 'Block hours', 'Captains - Block Hours', 'chart_bh_captain')}</div>
#                         </div>
#                         <div class="charts-grid">
#                             <div>{create_distribution_chart(df_validation_FO, 'Block hours', 'First Officers - Block Hours', 'chart_bh_fo')}</div>
#                             <div>{create_distribution_chart(df_validation_FA, 'Block hours', 'Flight Attendants - Block Hours', 'chart_bh_fa')}</div>
#                         </div>
                        
#                         <div class="subsection-header">✈️ Top Performers - Total Sectors</div>
#                         <div class="charts-grid">
#                             <div>{create_distribution_chart(df_validation, 'Total sectors', 'All Crew - Total Sectors', 'chart_sectors_all')}</div>
#                             <div>{create_distribution_chart(df_validation_captain, 'Total sectors', 'Captains - Total Sectors', 'chart_sectors_captain')}</div>
#                         </div>
#                         <div class="charts-grid">
#                             <div>{create_distribution_chart(df_validation_FO, 'Total sectors', 'First Officers - Total Sectors', 'chart_sectors_fo')}</div>
#                             <div>{create_distribution_chart(df_validation_FA, 'Total sectors', 'Flight Attendants - Total Sectors', 'chart_sectors_fa')}</div>
#                         </div>
#                     </div>
#                 </div>
#             </div>"""
    
#     html_validations = f"""
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>🕐 Standby Crew Analysis</span>
#                         {get_status_badge(len(Standby_crew))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ All crew have been utilized</div>' if Standby_crew.empty else f'<div class="info-box">Following {len(Standby_crew)} crew members have been kept on standby</div>'}
#                         <div class="table-container">{df_to_html_safe(Standby_crew)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>✈️ Unassigned Flights</span>
#                         {get_status_badge(len(unassigned_flights_crew))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ All flights have been assigned</div>' if unassigned_flights_crew.empty else f'<div class="error-box">⚠️ {len(unassigned_flights_crew)} flights have missing crew</div>'}
#                         <div class="table-container">{df_to_html_safe(unassigned_flights_crew)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>📋 Schedule Modifications</span>
#                         {get_status_badge(len(Schedule_check))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ No errors in schedule</div>' if Schedule_check.empty else f'<div class="error-box">⚠️ {len(Schedule_check)} modifications detected</div>'}
#                         <div class="table-container">{df_to_html_safe(Schedule_check)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>⚠️ Non-Available Crew Check</span>
#                         {get_status_badge(len(leaves_working))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ No crew on leave is scheduled</div>' if leaves_working.empty else f'<div class="error-box">❌ {len(leaves_working)} crew on leave allocated to flights</div>'}
#                         <div class="table-container">{df_to_html_safe(leaves_working[["Crew code", "Schedule Day", "Working Status"]] if not leaves_working.empty else leaves_working)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>🎓 Crew on Training Errors</span>
#                         {get_status_badge(len(crew_mistake_1) + len(crew_mistake_11))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Training at Base {get_status_badge(len(crew_mistake_1))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     {'<div class="success-box">✅ No errors</div>' if crew_mistake_1.empty else f'<div class="error-box">❌ {len(crew_mistake_1)} crew on training scheduled</div>'}
#                                     <div class="table-container">{df_to_html_safe(crew_mistake_1)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Training at Outstation {get_status_badge(len(crew_mistake_11))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     {'<div class="success-box">✅ No errors</div>' if crew_mistake_11.empty else f'<div class="error-box">❌ {len(crew_mistake_11)} crew missing exact 1 flight</div>'}
#                                     <div class="table-container">{df_to_html_safe(crew_mistake_11)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>📍 Starting Point Errors</span>
#                         {get_status_badge(len(crew_mistake_2))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ No errors</div>' if crew_mistake_2.empty else f'<div class="error-box">❌ {len(crew_mistake_2)} mismatched starting points</div>'}
#                         <div class="table-container">{df_to_html_safe(crew_mistake_2)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>🌙 Overnight Assignment Errors</span>
#                         {get_status_badge(len(crew_mistake_3))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ No errors</div>' if crew_mistake_3.empty else f'<div class="error-box">❌ {len(crew_mistake_3)} incorrect overnight assignments</div>'}
#                         <div class="table-container">{df_to_html_safe(crew_mistake_3)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>✈️ Aircraft Eligibility Errors</span>
#                         {get_status_badge(len(aircraft_issue))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ No errors</div>' if aircraft_issue.empty else f'<div class="error-box">❌ {len(aircraft_issue)} ineligible assignments</div>'}
#                         <div class="table-container">{df_to_html_safe(aircraft_issue)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>⏰ Block Hour Violations</span>
#                         {get_status_badge(len(Block_hour_issue_1) + len(Block_hour_issue_2))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Crew Ending at MLE {get_status_badge(len(Block_hour_issue_1))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     {'<div class="success-box">✅ No violations</div>' if Block_hour_issue_1.empty else f'<div class="error-box">❌ {len(Block_hour_issue_1)} violations</div>'}
#                                     <div class="table-container">{df_to_html_safe(Block_hour_issue_1)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Crew Ending at Outstation {get_status_badge(len(Block_hour_issue_2))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     {'<div class="success-box">✅ No violations</div>' if Block_hour_issue_2.empty else f'<div class="error-box">❌ {len(Block_hour_issue_2)} violations</div>'}
#                                     <div class="table-container">{df_to_html_safe(Block_hour_issue_2)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>📅 Monthly Duty Hour Violations</span>
#                         {get_status_badge(len(duty_hour_issue))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ No violations</div>' if duty_hour_issue.empty else f'<div class="error-box">❌ {len(duty_hour_issue)} violations</div>'}
#                         <div class="table-container">{df_to_html_safe(duty_hour_issue)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>🔢 Sector Violations</span>
#                         {get_status_badge(sector_issues)}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Daily (>14) {get_status_badge(len(output_crew_stats[output_crew_stats["Total sectors"] > 14]))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     <div class="table-container">{df_to_html_safe(output_crew_stats[output_crew_stats["Total sectors"] > 14])}</div>
#                                 </div>
#                             </div>
#                         </div>
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Weekly (>48) {get_status_badge(len(sector_issue_1))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     <div class="table-container">{df_to_html_safe(sector_issue_1)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>More than 12 Sectors Rule {get_status_badge(len(sector_issue_2))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     <div class="table-container">{df_to_html_safe(sector_issue_2)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>🔄 Aircraft Swap Violations</span>
#                         {get_status_badge(len(swaps_issue) + len(get_short_time_diffs_df))}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         {'<div class="success-box">✅ No swap violations</div>' if swaps_issue.empty else f'<div class="error-box">❌ {len(swaps_issue)} violations</div>'}
#                         <div class="table-container">{df_to_html_safe(swaps_issue)}</div>
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Swaps with Short Time Gaps {get_status_badge(len(get_short_time_diffs_df))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     <div class="table-container">{df_to_html_safe(get_short_time_diffs_df)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>👥 Pairing Rule Violations</span>
#                         {get_status_badge(pairing_issues)}
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Senior-Junior Pairing {get_status_badge(len(pairings_issue_1))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     <div class="table-container">{df_to_html_safe(pairings_issue_1)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>LTC Pairing {get_status_badge(len(LTC_check))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     <div class="table-container">{df_to_html_safe(LTC_check)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                         <div class="sub-accordion">
#                             <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
#                                 <span>Training Pairing {get_status_badge(len(training_issue))}</span>
#                                 <span class="accordion-icon">▼</span>
#                             </div>
#                             <div class="sub-accordion-content">
#                                 <div class="sub-accordion-body">
#                                     <div class="table-container">{df_to_html_safe(training_issue)}</div>
#                                 </div>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>📋 Crew Working Report</span>
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="table-container">{df_to_html_safe(validation_report_1)}</div>
#                     </div>
#                 </div>
#             </div>
            
#             <div class="accordion">
#                 <div class="accordion-header" onclick="toggleAccordion(this)">
#                     <div class="accordion-title">
#                         <span>✈️ Crew Aircraft Statistics</span>
#                     </div>
#                     <span class="accordion-icon">▼</span>
#                 </div>
#                 <div class="accordion-content">
#                     <div class="accordion-body">
#                         <div class="table-container">{df_to_html_safe(crew_ac_stats)}</div>
#                     </div>
#                 </div>
#             </div>"""
    
#     html_footer = """
#         </div>
#         <div class="report-footer">
#             <p><strong>TMA Crew Scheduler</strong> - Automated Validation Report</p>
#             <p>This report was generated automatically. Please verify critical data before making decisions.</p>
#         </div>
#     </div>
    
#     <script>
#         function toggleAccordion(element) {
#             const content = element.nextElementSibling;
#             const isActive = element.classList.contains('active');
            
#             element.classList.toggle('active');
#             content.classList.toggle('active');
#         }
        
#         function toggleSubAccordion(element) {
#             const content = element.nextElementSibling;
#             element.classList.toggle('active');
#             content.classList.toggle('active');
#         }
        
#         function expandAll() {
#             document.querySelectorAll('.accordion-header').forEach(header => {
#                 header.classList.add('active');
#                 header.nextElementSibling.classList.add('active');
#             });
#             document.querySelectorAll('.sub-accordion-header').forEach(header => {
#                 header.classList.add('active');
#                 header.nextElementSibling.classList.add('active');
#             });
#         }
        
#         function collapseAll() {
#             document.querySelectorAll('.accordion-header').forEach(header => {
#                 header.classList.remove('active');
#                 header.nextElementSibling.classList.remove('active');
#             });
#             document.querySelectorAll('.sub-accordion-header').forEach(header => {
#                 header.classList.remove('active');
#                 header.nextElementSibling.classList.remove('active');
#             });
#         }
#     </script>
# </body>
# </html>"""
    
#     # Combine all parts
#     html_content = html_header + html_summary + html_kpi + html_metrics_table + html_charts + html_validations + html_footer
    
#     return html_content


import pandas as pd
from datetime import datetime

def generate_html_report(
    schedule_date,
    metrics_df,
    validation_report_1,
    crew_ac_stats,
    Schedule_check,
    unassigned_flights_crew,
    Standby_crew,
    leaves_working,
    crew_mistake_1,
    crew_mistake_11,
    crew_mistake_2,
    crew_mistake_3,
    aircraft_issue,
    Block_hour_issue_1,
    Block_hour_issue_2,
    duty_hour_issue,
    sector_issue_1,
    sector_issue_2,
    output_crew_stats,
    swaps_issue,
    get_short_time_diffs_df,
    pairings_issue_1,
    LTC_check,
    training_issue,
    aircraft_kpi,
    flight_kpi,
    sectors_kpi,
    aircraft_starting_on_kpi,
    aircraft_ending_on_kpi,
    utilized_captain,
    utilized_first_officer,
    utilized_flight_attendant,
    Standyby_captain,
    Standyby_first_officer,
    Standyby_flight_attendant,
    aircraft_input_kpi,
    flight_input_kpi,
    sectors_input_kpi,
    available_captain,
    available_first_officer,
    available_flight_attendant,
    df_validation=None,
    df_validation_captain=None,
    df_validation_FO=None,
    df_validation_FA=None
):
    """
    Generate a comprehensive HTML report for TMA Crew Scheduler validation with collapsible sections
    """
    
    # Calculate summary metrics
    schedule_issues = len(Schedule_check) + len(unassigned_flights_crew)
    block_hour_issues = len(Block_hour_issue_1) + len(Block_hour_issue_2)
    duty_hour_issues = len(duty_hour_issue)
    sector_issues = len(output_crew_stats[output_crew_stats["Total sectors"] > 14]) + len(sector_issue_1) + len(sector_issue_2)
    pairing_issues = len(pairings_issue_1) + len(LTC_check) + len(training_issue)
    unavailable_issues = len(leaves_working) + len(crew_mistake_1) + len(crew_mistake_11)
    overnight_issues = len(crew_mistake_2) + len(crew_mistake_3)
    aircraft_issues = len(aircraft_issue) + len(swaps_issue)
    
    total_crew = utilized_captain + utilized_first_officer + utilized_flight_attendant
    total_standby = Standyby_captain + Standyby_first_officer + Standyby_flight_attendant
    total_available = available_captain + available_first_officer + available_flight_attendant
    
    # Helper function to create status badge
    def get_status_badge(count):
        if count == 0:
            return '<span class="status-badge status-success">✓ No Issues</span>'
        else:
            return f'<span class="status-badge status-error">⚠ {count} Issues</span>'
    
    # Helper function to safely convert DataFrame to HTML
    def df_to_html_safe(df, table_id=""):
        if df.empty:
            return '<p class="no-data">No data to display</p>'
        return df.to_html(index=False, classes='data-table', table_id=table_id, border=0)
    
    # Helper function to create distribution charts
    def create_distribution_chart(df, column, title, chart_id):
        if df is None or df.empty:
            return ""
        
        # Get top 300 performers and sort from high to low
        top_performers = df.nlargest(300, column) if len(df) > 300 else df.copy()
        top_performers = top_performers.sort_values(by=column, ascending=False)
        
        # Create data for chart
        crews = top_performers['Crew code'].tolist()
        values = top_performers[column].tolist()
        
        return f"""
        <div class="chart-container">
            <canvas id="{chart_id}"></canvas>
        </div>
        <script>
            new Chart(document.getElementById('{chart_id}'), {{
                type: 'bar',
                data: {{
                    labels: {crews},
                    datasets: [{{
                        label: '{title}',
                        data: {values},
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '{title}'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Crew Code'
                            }},
                            ticks: {{
                                maxRotation: 90,
                                minRotation: 45
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }},
                        title: {{
                            display: true,
                            text: '{title}'
                        }}
                    }}
                }}
            }});
        </script>
        """
    
    # Helper function to create pie charts for swaps
    def create_swaps_pie_chart(df, title, chart_id):
        if df is None or df.empty:
            return ""
        
        # Count crew by number of swaps
        swaps_count = df['No. of swaps'].value_counts().sort_index()
        total_crew = len(df)
        labels = [f"{int(k)} Swaps" for k in swaps_count.index]
        values = swaps_count.values.tolist()
        
        # Calculate percentages
        percentages = [(v / total_crew * 100) for v in values]
        
        # Color scheme
        colors = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
        
        return f"""
        <div class="chart-container-pie">
            <canvas id="{chart_id}"></canvas>
        </div>
        <script>
            new Chart(document.getElementById('{chart_id}'), {{
                type: 'pie',
                data: {{
                    labels: {labels},
                    datasets: [{{
                        data: {percentages},
                        backgroundColor: {colors},
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right'
                        }},
                        title: {{
                            display: true,
                            text: '{title}',
                            font: {{
                                size: 16,
                                weight: 'bold'
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.label + ': ' + context.parsed.toFixed(1) + '%';
                                }}
                            }}
                        }},
                        datalabels: {{
                            formatter: function(value, context) {{
                                return value.toFixed(1) + '%';
                            }},
                            color: '#fff',
                            font: {{
                                weight: 'bold',
                                size: 12
                            }}
                        }}
                    }}
                }}
            }});
        </script>
        """
    
    # Build HTML in parts
    html_header = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TMA Validation Report - {schedule_date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: #1e293b; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
        .report-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .report-header h1 {{ font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }}
        .report-header .subtitle {{ font-size: 1.2rem; opacity: 0.9; }}
        .report-date {{ margin-top: 15px; font-size: 1rem; background: rgba(255,255,255,0.2); display: inline-block; padding: 8px 20px; border-radius: 20px; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 50px; }}
        .section-header {{ font-size: 1.8rem; font-weight: 700; color: #1e293b; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 3px solid #667eea; }}
        .subsection-header {{ font-size: 1.4rem; font-weight: 600; color: #334155; margin: 30px 0 15px 0; }}
        
        /* Accordion Styles */
        .accordion {{ margin-bottom: 15px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .accordion-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 18px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s ease; user-select: none; }}
        .accordion-header:hover {{ background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%); transform: translateY(-1px); }}
        .accordion-header.active {{ background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%); }}
        .accordion-title {{ font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 10px; }}
        .accordion-icon {{ font-size: 1.2rem; transition: transform 0.3s ease; }}
        .accordion-header.active .accordion-icon {{ transform: rotate(180deg); }}
        .accordion-content {{ max-height: 0; overflow: hidden; transition: max-height 0.4s ease; background: white; }}
        .accordion-content.active {{ max-height: 10000px; }}
        .accordion-body {{ padding: 20px; }}
        
        /* Subsection Accordion */
        .sub-accordion {{ margin: 15px 0; border: 1px solid #e2e8f0; border-radius: 6px; }}
        .sub-accordion-header {{ background: #f8fafc; color: #334155; padding: 12px 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s ease; font-weight: 500; }}
        .sub-accordion-header:hover {{ background: #f1f5f9; }}
        .sub-accordion-header.active {{ background: #e0e7ff; color: #667eea; }}
        .sub-accordion-content {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }}
        .sub-accordion-content.active {{ max-height: 5000px; }}
        .sub-accordion-body {{ padding: 15px; background: #fafafa; }}
        
        /* Chart Styles */
        .chart-container {{ margin: 20px 0; height: 400px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .chart-container-pie {{ margin: 20px 0; height: 350px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
        .charts-grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 25px; color: white; text-align: center; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3); }}
        .metric-card.success {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); }}
        .metric-card.warning {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }}
        .metric-card.error {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }}
        .metric-label {{ font-size: 0.875rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
        .metric-value {{ font-size: 2.5rem; font-weight: 700; margin-top: 10px; }}
        .status-badge {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; margin: 5px; }}
        .status-success {{ background: #d1fae5; color: #065f46; }}
        .status-error {{ background: #fee2e2; color: #991b1b; }}
        .table-container {{ overflow-x: auto; margin: 20px 0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .data-table {{ width: 100%; border-collapse: collapse; background: white; font-size: 0.9rem; }}
        .data-table thead {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .data-table th {{ padding: 15px; text-align: left; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }}
        .data-table td {{ padding: 12px 15px; border-bottom: 1px solid #e2e8f0; }}
        .data-table tbody tr:hover {{ background: #f8fafc; }}
        .no-data {{ text-align: center; padding: 40px; color: #64748b; font-style: italic; background: #f8fafc; border-radius: 8px; margin: 20px 0; }}
        .success-box {{ background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left: 4px solid #10b981; border-radius: 8px; padding: 20px; margin: 20px 0; color: #065f46; }}
        .error-box {{ background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-left: 4px solid #ef4444; border-radius: 8px; padding: 20px; margin: 20px 0; color: #991b1b; }}
        .info-box {{ background: linear-gradient(135deg, #e0e7ff 0%, #ddd6fe 100%); border-left: 4px solid #667eea; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .report-footer {{ background: #f8fafc; padding: 30px; text-align: center; color: #64748b; border-top: 2px solid #e2e8f0; }}
        
        /* Expand/Collapse All Button */
        .control-buttons {{ margin-bottom: 20px; display: flex; gap: 10px; }}
        .control-btn {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.3s ease; }}
        .control-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }}
        
        @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; }} .accordion-content {{ max-height: none !important; }} .control-buttons {{ display: none; }} }}
        @media (max-width: 768px) {{ .content {{ padding: 20px; }} .metrics-grid {{ grid-template-columns: 1fr; }} .report-header h1 {{ font-size: 1.8rem; }} .charts-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>✈️ TMA Crew Scheduler</h1>
            <div class="subtitle">Constraints Validation Report</div>
            <div class="report-date">📅 Schedule Date: {schedule_date}</div>
            <div class="report-date">🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        <div class="content">
            <div class="control-buttons">
                <button class="control-btn" onclick="expandAll()">📂 Expand All</button>
                <button class="control-btn" onclick="collapseAll()">📁 Collapse All</button>
            </div>"""
    
    html_summary = f"""
            <div class="section">
                <div class="section-header">📊 Executive Summary</div>
                <div class="metrics-grid">
                    <div class="metric-card {'success' if schedule_issues == 0 else 'error'}">
                        <div class="metric-label">Schedule Issues</div>
                        <div class="metric-value">{schedule_issues}</div>
                    </div>
                    <div class="metric-card {'success' if block_hour_issues == 0 else 'error'}">
                        <div class="metric-label">BH Violations</div>
                        <div class="metric-value">{block_hour_issues}</div>
                    </div>
                    <div class="metric-card {'success' if duty_hour_issues == 0 else 'error'}">
                        <div class="metric-label">DH Violations</div>
                        <div class="metric-value">{duty_hour_issues}</div>
                    </div>
                    <div class="metric-card {'success' if sector_issues == 0 else 'error'}">
                        <div class="metric-label">Sector Violations</div>
                        <div class="metric-value">{sector_issues}</div>
                    </div>
                    <div class="metric-card {'success' if pairing_issues == 0 else 'error'}">
                        <div class="metric-label">Pairing Issues</div>
                        <div class="metric-value">{pairing_issues}</div>
                    </div>
                    <div class="metric-card {'success' if unavailable_issues == 0 else 'error'}">
                        <div class="metric-label">Status Issues</div>
                        <div class="metric-value">{unavailable_issues}</div>
                    </div>
                    <div class="metric-card {'success' if overnight_issues == 0 else 'error'}">
                        <div class="metric-label">Overnight Issues</div>
                        <div class="metric-value">{overnight_issues}</div>
                    </div>
                    <div class="metric-card {'success' if aircraft_issues == 0 else 'error'}">
                        <div class="metric-label">Aircraft Issues</div>
                        <div class="metric-value">{aircraft_issues}</div>
                    </div>
                </div>
            </div>"""
    
    html_kpi = f"""
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>📈 Key Performance Indicators</span>
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="subsection-header">Available Aircraft and Crew</div>
                        <div class="metrics-grid">
                            <div class="metric-card"><div class="metric-label">Total Aircraft</div><div class="metric-value">{aircraft_input_kpi}</div></div>
                            <div class="metric-card"><div class="metric-label">Total Flights</div><div class="metric-value">{flight_input_kpi}</div></div>
                            <div class="metric-card"><div class="metric-label">Total Sectors</div><div class="metric-value">{sectors_input_kpi}</div></div>
                            <div class="metric-card success"><div class="metric-label">Available Crew</div><div class="metric-value">{total_available}</div></div>
                            <div class="metric-card success"><div class="metric-label">Captains</div><div class="metric-value">{available_captain}</div></div>
                            <div class="metric-card success"><div class="metric-label">First Officers</div><div class="metric-value">{available_first_officer}</div></div>
                            <div class="metric-card success"><div class="metric-label">Cabin Crew</div><div class="metric-value">{available_flight_attendant}</div></div>
                        </div>
                        <div class="subsection-header">Scheduled Aircraft and Crew</div>
                        <div class="metrics-grid">
                            <div class="metric-card"><div class="metric-label">AC Scheduled</div><div class="metric-value">{aircraft_kpi}</div></div>
                            <div class="metric-card"><div class="metric-label">AC Starting ON</div><div class="metric-value">{aircraft_starting_on_kpi}</div></div>
                            <div class="metric-card"><div class="metric-label">AC Ending ON</div><div class="metric-value">{aircraft_ending_on_kpi}</div></div>
                            <div class="metric-card"><div class="metric-label">Flights</div><div class="metric-value">{flight_kpi}</div></div>
                            <div class="metric-card"><div class="metric-label">Sectors</div><div class="metric-value">{sectors_kpi}</div></div>
                            <div class="metric-card success"><div class="metric-label">Utilized Crew</div><div class="metric-value">{total_crew}</div></div>
                            <div class="metric-card success"><div class="metric-label">Captains</div><div class="metric-value">{utilized_captain}</div></div>
                            <div class="metric-card success"><div class="metric-label">First Officers</div><div class="metric-value">{utilized_first_officer}</div></div>
                            <div class="metric-card success"><div class="metric-label">Cabin Crew</div><div class="metric-value">{utilized_flight_attendant}</div></div>
                            <div class="metric-card warning"><div class="metric-label">Standby Crew</div><div class="metric-value">{total_standby}</div></div>
                            <div class="metric-card warning"><div class="metric-label">Captains</div><div class="metric-value">{Standyby_captain}</div></div>
                            <div class="metric-card warning"><div class="metric-label">First Officers</div><div class="metric-value">{Standyby_first_officer}</div></div>
                            <div class="metric-card warning"><div class="metric-label">Cabin Crew</div><div class="metric-value">{Standyby_flight_attendant}</div></div>
                        </div>
                    </div>
                </div>
            </div>"""
    
    html_metrics_table = f"""
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>📊 Detailed Utilization Metrics</span>
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="table-container">{df_to_html_safe(metrics_df, 'metrics-table')}</div>
                    </div>
                </div>
            </div>"""
    
    # Add Charts Section
    html_charts = ""
    if df_validation is not None:
        html_charts = f"""
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>📊 Crew Performance Analytics</span>
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="subsection-header">🔄 Aircraft Swaps Distribution</div>
                        <div class="charts-grid-2">
                            <div>{create_swaps_pie_chart(df_validation, 'All Crew Swaps', 'chart_swaps_all')}</div>
                            <div>{create_swaps_pie_chart(df_validation_captain, 'Captain Swaps', 'chart_swaps_captain')}</div>
                            <div>{create_swaps_pie_chart(df_validation_FO, 'First Officer Swaps', 'chart_swaps_fo')}</div>
                            <div>{create_swaps_pie_chart(df_validation_FA, 'Flight Attendant Swaps', 'chart_swaps_fa')}</div>
                        </div>
                        
                        <div class="subsection-header">⏰ Top Performers - Block Hours</div>
                        <div class="charts-grid">
                            <div>{create_distribution_chart(df_validation, 'Block hours', 'All Crew - Block Hours', 'chart_bh_all')}</div>
                            <div>{create_distribution_chart(df_validation_captain, 'Block hours', 'Captains - Block Hours', 'chart_bh_captain')}</div>
                        </div>
                        <div class="charts-grid">
                            <div>{create_distribution_chart(df_validation_FO, 'Block hours', 'First Officers - Block Hours', 'chart_bh_fo')}</div>
                            <div>{create_distribution_chart(df_validation_FA, 'Block hours', 'Flight Attendants - Block Hours', 'chart_bh_fa')}</div>
                        </div>
                        
                        <div class="subsection-header">✈️ Top Performers - Total Sectors</div>
                        <div class="charts-grid">
                            <div>{create_distribution_chart(df_validation, 'Total sectors', 'All Crew - Total Sectors', 'chart_sectors_all')}</div>
                            <div>{create_distribution_chart(df_validation_captain, 'Total sectors', 'Captains - Total Sectors', 'chart_sectors_captain')}</div>
                        </div>
                        <div class="charts-grid">
                            <div>{create_distribution_chart(df_validation_FO, 'Total sectors', 'First Officers - Total Sectors', 'chart_sectors_fo')}</div>
                            <div>{create_distribution_chart(df_validation_FA, 'Total sectors', 'Flight Attendants - Total Sectors', 'chart_sectors_fa')}</div>
                        </div>
                    </div>
                </div>
            </div>"""
    
    html_validations = f"""
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>🕐 Standby Crew Analysis</span>
                        {get_status_badge(len(Standby_crew))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ All crew have been utilized</div>' if Standby_crew.empty else f'<div class="info-box">Following {len(Standby_crew)} crew members have been kept on standby</div>'}
                        <div class="table-container">{df_to_html_safe(Standby_crew)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>✈️ Unassigned Flights</span>
                        {get_status_badge(len(unassigned_flights_crew))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ All flights have been assigned</div>' if unassigned_flights_crew.empty else f'<div class="error-box">⚠️ {len(unassigned_flights_crew)} flights have missing crew</div>'}
                        <div class="table-container">{df_to_html_safe(unassigned_flights_crew)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>📋 Schedule Modifications</span>
                        {get_status_badge(len(Schedule_check))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ No errors in schedule</div>' if Schedule_check.empty else f'<div class="error-box">⚠️ {len(Schedule_check)} modifications detected</div>'}
                        <div class="table-container">{df_to_html_safe(Schedule_check)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>⚠️ Non-Available Crew Check</span>
                        {get_status_badge(len(leaves_working))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ No crew on leave is scheduled</div>' if leaves_working.empty else f'<div class="error-box">❌ {len(leaves_working)} crew on leave allocated to flights</div>'}
                        <div class="table-container">{df_to_html_safe(leaves_working[["Crew code", "Schedule Day", "Working Status"]] if not leaves_working.empty else leaves_working)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>🎓 Crew on Training Errors</span>
                        {get_status_badge(len(crew_mistake_1) + len(crew_mistake_11))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Training at Base {get_status_badge(len(crew_mistake_1))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    {'<div class="success-box">✅ No errors</div>' if crew_mistake_1.empty else f'<div class="error-box">❌ {len(crew_mistake_1)} crew on training scheduled</div>'}
                                    <div class="table-container">{df_to_html_safe(crew_mistake_1)}</div>
                                </div>
                            </div>
                        </div>
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Training at Outstation {get_status_badge(len(crew_mistake_11))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    {'<div class="success-box">✅ No errors</div>' if crew_mistake_11.empty else f'<div class="error-box">❌ {len(crew_mistake_11)} crew missing exact 1 flight</div>'}
                                    <div class="table-container">{df_to_html_safe(crew_mistake_11)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>📍 Starting Point Errors</span>
                        {get_status_badge(len(crew_mistake_2))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ No errors</div>' if crew_mistake_2.empty else f'<div class="error-box">❌ {len(crew_mistake_2)} mismatched starting points</div>'}
                        <div class="table-container">{df_to_html_safe(crew_mistake_2)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>🌙 Overnight Assignment Errors</span>
                        {get_status_badge(len(crew_mistake_3))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ No errors</div>' if crew_mistake_3.empty else f'<div class="error-box">❌ {len(crew_mistake_3)} incorrect overnight assignments</div>'}
                        <div class="table-container">{df_to_html_safe(crew_mistake_3)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>✈️ Aircraft Eligibility Errors</span>
                        {get_status_badge(len(aircraft_issue))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ No errors</div>' if aircraft_issue.empty else f'<div class="error-box">❌ {len(aircraft_issue)} ineligible assignments</div>'}
                        <div class="table-container">{df_to_html_safe(aircraft_issue)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>⏰ Block Hour Violations</span>
                        {get_status_badge(len(Block_hour_issue_1) + len(Block_hour_issue_2))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Crew Ending at MLE {get_status_badge(len(Block_hour_issue_1))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    {'<div class="success-box">✅ No violations</div>' if Block_hour_issue_1.empty else f'<div class="error-box">❌ {len(Block_hour_issue_1)} violations</div>'}
                                    <div class="table-container">{df_to_html_safe(Block_hour_issue_1)}</div>
                                </div>
                            </div>
                        </div>
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Crew Ending at Outstation {get_status_badge(len(Block_hour_issue_2))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    {'<div class="success-box">✅ No violations</div>' if Block_hour_issue_2.empty else f'<div class="error-box">❌ {len(Block_hour_issue_2)} violations</div>'}
                                    <div class="table-container">{df_to_html_safe(Block_hour_issue_2)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>📅 Monthly Duty Hour Violations</span>
                        {get_status_badge(len(duty_hour_issue))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ No violations</div>' if duty_hour_issue.empty else f'<div class="error-box">❌ {len(duty_hour_issue)} violations</div>'}
                        <div class="table-container">{df_to_html_safe(duty_hour_issue)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>🔢 Sector Violations</span>
                        {get_status_badge(sector_issues)}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Daily (>14) {get_status_badge(len(output_crew_stats[output_crew_stats["Total sectors"] > 14]))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    <div class="table-container">{df_to_html_safe(output_crew_stats[output_crew_stats["Total sectors"] > 14])}</div>
                                </div>
                            </div>
                        </div>
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Weekly (>48) {get_status_badge(len(sector_issue_1))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    <div class="table-container">{df_to_html_safe(sector_issue_1)}</div>
                                </div>
                            </div>
                        </div>
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>More than 12 Sectors Rule {get_status_badge(len(sector_issue_2))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    <div class="table-container">{df_to_html_safe(sector_issue_2)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>🔄 Aircraft Swap Violations</span>
                        {get_status_badge(len(swaps_issue) + len(get_short_time_diffs_df))}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        {'<div class="success-box">✅ No swap violations</div>' if swaps_issue.empty else f'<div class="error-box">❌ {len(swaps_issue)} violations</div>'}
                        <div class="table-container">{df_to_html_safe(swaps_issue)}</div>
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Swaps with Short Time Gaps {get_status_badge(len(get_short_time_diffs_df))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    <div class="table-container">{df_to_html_safe(get_short_time_diffs_df)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>👥 Pairing Rule Violations</span>
                        {get_status_badge(pairing_issues)}
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Senior-Junior Pairing {get_status_badge(len(pairings_issue_1))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    <div class="table-container">{df_to_html_safe(pairings_issue_1)}</div>
                                </div>
                            </div>
                        </div>
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>LTC Pairing {get_status_badge(len(LTC_check))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    <div class="table-container">{df_to_html_safe(LTC_check)}</div>
                                </div>
                            </div>
                        </div>
                        <div class="sub-accordion">
                            <div class="sub-accordion-header" onclick="toggleSubAccordion(this)">
                                <span>Training Pairing {get_status_badge(len(training_issue))}</span>
                                <span class="accordion-icon">▼</span>
                            </div>
                            <div class="sub-accordion-content">
                                <div class="sub-accordion-body">
                                    <div class="table-container">{df_to_html_safe(training_issue)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>📋 Crew Working Report</span>
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="table-container">{df_to_html_safe(validation_report_1)}</div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    <div class="accordion-title">
                        <span>✈️ Crew Aircraft Statistics</span>
                    </div>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <div class="accordion-body">
                        <div class="table-container">{df_to_html_safe(crew_ac_stats)}</div>
                    </div>
                </div>
            </div>"""
    
    html_footer = """
        </div>
        <div class="report-footer">
            <p><strong>TMA Crew Scheduler</strong> - Automated Validation Report</p>
            <p>This report was generated automatically. Please verify critical data before making decisions.</p>
        </div>
    </div>
    
    <script>
        function toggleAccordion(element) {
            const content = element.nextElementSibling;
            const isActive = element.classList.contains('active');
            
            element.classList.toggle('active');
            content.classList.toggle('active');
        }
        
        function toggleSubAccordion(element) {
            const content = element.nextElementSibling;
            element.classList.toggle('active');
            content.classList.toggle('active');
        }
        
        function expandAll() {
            document.querySelectorAll('.accordion-header').forEach(header => {
                header.classList.add('active');
                header.nextElementSibling.classList.add('active');
            });
            document.querySelectorAll('.sub-accordion-header').forEach(header => {
                header.classList.add('active');
                header.nextElementSibling.classList.add('active');
            });
        }
        
        function collapseAll() {
            document.querySelectorAll('.accordion-header').forEach(header => {
                header.classList.remove('active');
                header.nextElementSibling.classList.remove('active');
            });
            document.querySelectorAll('.sub-accordion-header').forEach(header => {
                header.classList.remove('active');
                header.nextElementSibling.classList.remove('active');
            });
        }
    </script>
</body>
</html>"""
    
    # Combine all parts
    html_content = html_header + html_summary + html_kpi + html_metrics_table + html_charts + html_validations + html_footer
    
    return html_content