"""
Sales Forecasting Tools using Facebook Prophet
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json


def forecast_sales_data(csv_content, forecast_days=30, simulation_factor=1.0):
    """
    Analyze CSV sales data and generate forecasts using Prophet
    
    Args:
        csv_content (str): CSV content as string
        forecast_days (int): Number of days to forecast
        simulation_factor (float): Multiplier for simulation scenarios
    
    Returns:
        dict: Forecast results and analysis
    """
    try:
        from prophet import Prophet
    except ImportError:
        return {
            "error": "Prophet library not installed. Please install facebook-prophet.",
            "success": False
        }
    
    try:
        # Parse CSV data
        from io import StringIO
        df = pd.read_csv(StringIO(csv_content))
        
        # Validate required columns - support multiple languages and terms
        date_keywords = ['date', 'data', 'fecha', 'datum', 'time', 'timestamp', 'day', 'dia']
        sales_keywords = ['sales', 'revenue', 'amount', 'value', 'units_sold', 'sold', 'quantity', 'qty', 'venda', 'vendas', 'receita', 'ingresos', 'ventas', 'umsatz', 'verkauf', 'unidades', 'cantidad']
        
        date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in date_keywords)]
        sales_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in sales_keywords)]
        
        # Fallback: Try to auto-detect columns by data type
        if not date_columns:
            # Look for columns that can be converted to datetime
            for col in df.columns:
                try:
                    pd.to_datetime(df[col].head(), errors='raise')
                    date_columns.append(col)
                    break
                except:
                    continue
        
        if not sales_columns:
            # Look for numeric columns (excluding the date column if found)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if date_columns and date_columns[0] in numeric_cols:
                numeric_cols.remove(date_columns[0])
            if numeric_cols:
                sales_columns = [numeric_cols[0]]  # Use first numeric column
        
        if not date_columns or not sales_columns:
            return {
                "error": f"Could not identify date and sales columns. Found columns: {list(df.columns)}. Please ensure you have a date column and a numeric sales/quantity column.",
                "success": False
            }
        
        # Use first available columns
        date_col = date_columns[0]
        sales_col = sales_columns[0]
        
        # Prepare data for Prophet with robust date parsing
        try:
            # Try different date parsing methods
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
            
            # If that fails, try other common formats
            if df[date_col].isna().all():
                df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce')
            if df[date_col].isna().all():
                df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d', errors='coerce')
            if df[date_col].isna().all():
                df[date_col] = pd.to_datetime(df[date_col], format='%m/%d/%Y', errors='coerce')
                
        except Exception as e:
            return {
                "error": f"Could not parse dates in column '{date_col}'. Please ensure dates are in a recognizable format (YYYY-MM-DD, DD/MM/YYYY, etc.)",
                "success": False
            }
        
        print(f"DEBUG: Using date column: '{date_col}', sales column: '{sales_col}'")
        
        df_prophet = df[[date_col, sales_col]].rename(columns={
            date_col: 'ds',
            sales_col: 'y'
        })
        
        # Remove any null values
        df_prophet = df_prophet.dropna()
        
        # Apply simulation factor
        df_prophet['y'] = df_prophet['y'] * simulation_factor
        
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95
        )
        
        # Fit the model
        model.fit(df_prophet)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_days)
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Extract results
        forecast_results = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)
        
        # Calculate statistics
        historical_avg = df_prophet['y'].mean()
        forecast_avg = forecast_results['yhat'].mean()
        growth_rate = ((forecast_avg - historical_avg) / historical_avg) * 100
        
        # Get last actual value for comparison
        last_actual = df_prophet['y'].iloc[-1]
        first_forecast = forecast_results['yhat'].iloc[0]
        immediate_change = ((first_forecast - last_actual) / last_actual) * 100
        
        return {
            "success": True,
            "data_info": {
                "total_records": len(df_prophet),
                "date_range": f"{df_prophet['ds'].min().strftime('%Y-%m-%d')} to {df_prophet['ds'].max().strftime('%Y-%m-%d')}",
                "historical_average": round(historical_avg, 2),
                "last_actual_value": round(last_actual, 2)
            },
            "forecast_summary": {
                "forecast_days": forecast_days,
                "forecast_average": round(forecast_avg, 2),
                "expected_growth_rate": round(growth_rate, 2),
                "immediate_change": round(immediate_change, 2),
                "simulation_factor": simulation_factor
            },
            "forecast_data": [
                {
                    "date": row['ds'].strftime('%Y-%m-%d'),
                    "predicted_value": round(row['yhat'], 2),
                    "lower_bound": round(row['yhat_lower'], 2),
                    "upper_bound": round(row['yhat_upper'], 2)
                }
                for _, row in forecast_results.iterrows()
            ],
            "insights": generate_forecast_insights(df_prophet, forecast_results, growth_rate, simulation_factor)
        }
        
    except Exception as e:
        return {
            "error": f"Forecasting error: {str(e)}",
            "success": False
        }


def generate_forecast_insights(historical_data, forecast_data, growth_rate, simulation_factor):
    """Generate business insights from forecast results"""
    insights = []
    
    # Growth analysis
    if growth_rate > 10:
        insights.append("📈 Strong growth expected - consider scaling operations")
    elif growth_rate > 5:
        insights.append("📊 Moderate growth projected - maintain current strategy")
    elif growth_rate > 0:
        insights.append("📉 Slow growth anticipated - explore growth opportunities")
    else:
        insights.append("⚠️ Declining trend detected - immediate action required")
    
    # Seasonality insights
    if len(historical_data) > 30:  # Enough data for seasonality analysis
        insights.append("📅 Seasonal patterns detected - plan inventory accordingly")
    
    # Simulation insights
    if simulation_factor > 1.0:
        insights.append(f"🚀 Optimistic scenario (+{((simulation_factor-1)*100):.1f}%) - potential upside captured")
    elif simulation_factor < 1.0:
        insights.append(f"📉 Conservative scenario ({((simulation_factor-1)*100):.1f}%) - risk mitigation considered")
    
    # Volatility insights
    forecast_std = forecast_data['yhat'].std()
    historical_std = historical_data['y'].std()
    
    if forecast_std > historical_std * 1.2:
        insights.append("⚡ High forecast uncertainty - monitor closely and adjust plans")
    else:
        insights.append("✅ Stable forecast pattern - reliable for planning")
    
    return insights


def create_scenario_analysis(csv_content, forecast_days=30):
    """
    Generate multiple forecast scenarios (optimistic, realistic, pessimistic)
    """
    scenarios = {
        "pessimistic": forecast_sales_data(csv_content, forecast_days, 0.8),
        "realistic": forecast_sales_data(csv_content, forecast_days, 1.0),
        "optimistic": forecast_sales_data(csv_content, forecast_days, 1.2)
    }
    
    return scenarios


def generate_forecast_chart_data(forecast_result):
    """
    Convert forecast results to chart-friendly format
    """
    if not forecast_result.get("success"):
        return None
    
    forecast_data = forecast_result["forecast_data"]
    
    return {
        "type": "line",
        "title": "Sales Forecast",
        "labels": [item["date"] for item in forecast_data],
        "datasets": [
            {
                "label": "Predicted Sales",
                "data": [item["predicted_value"] for item in forecast_data],
                "borderColor": "#007bff",
                "backgroundColor": "rgba(0, 123, 255, 0.1)",
                "borderWidth": 3,
                "fill": False
            },
            {
                "label": "Upper Bound",
                "data": [item["upper_bound"] for item in forecast_data],
                "borderColor": "#22c55e",
                "backgroundColor": "rgba(34, 197, 94, 0.1)",
                "borderWidth": 1,
                "borderDash": [5, 5],
                "fill": False
            },
            {
                "label": "Lower Bound",
                "data": [item["lower_bound"] for item in forecast_data],
                "borderColor": "#ef4444",
                "backgroundColor": "rgba(239, 68, 68, 0.1)",
                "borderWidth": 1,
                "borderDash": [5, 5],
                "fill": False
            }
        ]
    }


def sales_data_from_path(csv_path="sales_data.csv", forecast_days=30):
    """
    Generate sales forecast using Prophet from a file path
    
    Args:
        csv_path (str): Path to CSV file
        forecast_days (int): Number of days to forecast
    
    Returns:
        dict: Forecast results
    """
    try:
        # Load CSV file content
        with open(csv_path, 'r') as file:
            csv_content = file.read()
        
        # Use existing forecast function
        return forecast_sales_data(csv_content, forecast_days)
        
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {csv_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def intelligent_recommendations(forecast_result, current_inventory=500, avg_price=20, 
                                production_cost_per_unit=10, salary_per_employee=300):
    """
    Generate intelligent recommendations from forecast results.
    
    Args:
        forecast_result (dict): Forecast output from Prophet agent
        current_inventory (int): Units in stock
        avg_price (float): Selling price per unit
        production_cost_per_unit (float): Cost to produce one unit
        salary_per_employee (float): Monthly cost of one employee
    
    Returns:
        dict: Actionable recommendations
    """
    if not forecast_result.get("success"):
        return {"error": "Forecast data missing", "success": False}
    
    forecast_data = pd.DataFrame(forecast_result["forecast_data"])
    total_forecast_demand = forecast_data["predicted_value"].sum()
    
    # 1. Inventory check
    restock_alert = bool(total_forecast_demand > current_inventory)
    
    # 2. Production volumes (with +10% buffer)
    production_plan = float(total_forecast_demand * 1.1)
    
    # 3. Hiring recommendations (1 staff per 500 units forecast)
    employees_needed = int(total_forecast_demand // 500) + 1
    
    # 4. Cashflow projection
    revenue = total_forecast_demand * avg_price
    production_cost = total_forecast_demand * production_cost_per_unit
    salary_cost = employees_needed * salary_per_employee
    profit = revenue - (production_cost + salary_cost)
    
    return {
        "success": True,
        "inventory": {
            "current_inventory": current_inventory,
            "forecasted_demand": round(total_forecast_demand, 2),
            "restock_needed": restock_alert
        },
        "production": {
            "recommended_volume": round(production_plan, 2),
            "note": "Includes +10% buffer"
        },
        "hiring": {
            "employees_needed": employees_needed,
            "roles": ["Sales Associate", "Production Worker"],
            "salary_estimate_per_employee": salary_per_employee,
            "total_salary_cost": salary_cost
        },
        "cashflow": {
            "expected_revenue": round(revenue, 2),
            "expected_costs": round(production_cost + salary_cost, 2),
            "expected_profit": round(profit, 2)
        },
        "insights": [
            "📦 Restock inventory to meet forecasted demand" if restock_alert else "✅ Current stock is sufficient",
            f"👩‍💻 Hire {employees_needed} staff to handle workload",
            "💵 Maintain profit margin by balancing production and salary costs"
        ]
    }


def comprehensive_business_analysis(csv_content, forecast_days=30, current_inventory=500, 
                                   avg_price=20, production_cost_per_unit=10, salary_per_employee=300):
    """
    Complete business analysis combining forecasting and intelligent recommendations
    
    Args:
        csv_content (str): CSV content as string
        forecast_days (int): Number of days to forecast
        current_inventory (int): Units in stock
        avg_price (float): Selling price per unit
        production_cost_per_unit (float): Cost to produce one unit
        salary_per_employee (float): Monthly cost of one employee
    
    Returns:
        dict: Complete analysis with forecast and recommendations
    """
    # Step 1: Generate forecast
    forecast_result = forecast_sales_data(csv_content, forecast_days)
    
    if not forecast_result.get("success"):
        return forecast_result
    
    # Step 2: Generate recommendations
    recommendations = intelligent_recommendations(
        forecast_result, current_inventory, avg_price, 
        production_cost_per_unit, salary_per_employee
    )
    
    # Step 3: Generate scenario analysis
    scenarios = create_scenario_analysis(csv_content, forecast_days)
    
    # Step 4: Generate chart data
    chart_data = generate_forecast_chart_data(forecast_result)
    
    return {
        "success": True,
        "forecast": forecast_result,
        "recommendations": recommendations,
        "scenarios": scenarios,
        "chart_data": chart_data,
        "analysis_type": "comprehensive_business_analysis"
    }