"""
Django Views for Market Trend Analysis System
Handles all API endpoints and renders templates
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
import json
import traceback

from .models import Stock, HistoricalData, Prediction, VolatilityAnalysis, MarketReport
from .ml_utils import (
    DataProcessor, VolatilityAnalyzer, PredictionEngine,
    ReportGenerator, fetch_stock_data_yfinance, generate_dummy_data
)


# ============== Template Views ==============

def dashboard(request):
    """
    Render the main dashboard
    """
    # Get available stocks
    stocks = Stock.objects.filter(is_active=True)

    context = {
        'stocks': stocks,
        'page_title': 'AI-Powered Market Trend Analysis'
    }
    return render(request, 'dashboard.html', context)


# ============== API: Stock Management ==============

@require_http_methods(["GET"])
def api_stocks_list(request):
    """
    Get list of all available stocks
    """
    try:
        stocks = Stock.objects.filter(is_active=True).values(
            'id', 'symbol', 'company_name', 'exchange', 'sector'
        )
        return JsonResponse({
            'success': True,
            'stocks': list(stocks)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_stock_detail(request, stock_id):
    """
    Get detailed information about a specific stock
    """
    try:
        stock = Stock.objects.get(id=stock_id)

        # Get latest historical data
        latest_data = stock.historical_data.order_by('-date')[:30]

        data_points = []
        for point in latest_data:
            data_points.append({
                'date': point.date.isoformat(),
                'open': float(point.open_price),
                'high': float(point.high),
                'low': float(point.low),
                'close': float(point.close),
                'volume': point.volume
            })

        return JsonResponse({
            'success': True,
            'stock': {
                'id': stock.id,
                'symbol': stock.symbol,
                'company_name': stock.company_name,
                'exchange': stock.exchange,
                'sector': stock.sector,
                'latest_price': float(stock.latest_price) if stock.latest_price else None,
                'data_points_count': stock.data_points_count
            },
            'historical_data': data_points
        })
    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Stock not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============== API: Data Ingestion ==============

@csrf_exempt
@require_http_methods(["POST"])
def api_fetch_stock_data(request):
    """
    Fetch stock data from yfinance or generate dummy data
    """
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol', '').upper().strip()

        if not symbol:
            return JsonResponse({
                'success': False,
                'error': 'Symbol is required'
            }, status=400)

        # Try to fetch from yfinance
        df = fetch_stock_data_yfinance(symbol)

        # If yfinance fails, generate dummy data
        if df is None:
            df = generate_dummy_data(symbol)

        # Engineer features
        df = DataProcessor.engineer_features(df)

        # Get or create stock
        stock, created = Stock.objects.get_or_create(
            symbol=symbol,
            defaults={
                'company_name': f'{symbol} Corporation',
                'exchange': 'NYSE',
                'sector': 'Technology'
            }
        )

        # Store historical data
        records_created = 0
        records_updated = 0

        for _, row in df.iterrows():
            historical_data, created = HistoricalData.objects.update_or_create(
                stock=stock,
                date=row['date'],
                defaults={
                    'open_price': round(float(row.get('open_price', row.get('open', 0))), 4),
                    'high': round(float(row.get('high', 0)), 4),
                    'low': round(float(row.get('low', 0)), 4),
                    'close': round(float(row.get('close', 0)), 4),
                    'volume': int(row.get('volume', 0)),
                    'adjusted_close': round(float(row.get('adjusted_close', row.get('close', 0))), 4),
                    'moving_average_5': round(float(row.get('ma_5', 0)), 4) if pd_notna(row.get('ma_5')) else None,
                    'moving_average_10': round(float(row.get('ma_10', 0)), 4) if pd_notna(row.get('ma_10')) else None,
                    'moving_average_20': round(float(row.get('ma_20', 0)), 4) if pd_notna(row.get('ma_20')) else None,
                    'moving_average_50': round(float(row.get('ma_50', 0)), 4) if pd_notna(row.get('ma_50')) else None,
                    'rsi': round(float(row.get('rsi', 0)), 2) if pd_notna(row.get('rsi')) else None,
                }
            )

            if created:
                records_created += 1
            else:
                records_updated += 1

        return JsonResponse({
            'success': True,
            'message': f'Successfully fetched data for {symbol}',
            'stock_id': stock.id,
            'records_created': records_created,
            'records_updated': records_updated,
            'total_records': stock.historical_data.count()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# ============== API: Prediction Engine ==============

@csrf_exempt
@require_http_methods(["POST"])
def api_train_and_predict(request):
    """
    Train ML model and generate predictions
    """
    try:
        data = json.loads(request.body)
        stock_id = data.get('stock_id')
        model_type = data.get('model_type', 'RandomForest')

        if not stock_id:
            return JsonResponse({
                'success': False,
                'error': 'stock_id is required'
            }, status=400)

        # Get stock
        stock = Stock.objects.get(id=stock_id)

        # Get historical data
        historical_qs = stock.historical_data.order_by('date')
        historical_data = list(historical_qs.values())

        if len(historical_data) < 50:
            return JsonResponse({
                'success': False,
                'error': f'Insufficient data. Need at least 50 data points, got {len(historical_data)}'
            }, status=400)

        # Convert to DataFrame
        import pandas as pd
        historical_data = convert_decimal_to_float(historical_data)
        df = pd.DataFrame(historical_data)

        # Rename columns for ML utils
        column_map = {
            'open_price': 'open',
            'date': 'date'
        }
        df = df.rename(columns=column_map)

        # Initialize prediction engine
        engine = PredictionEngine(model_type=model_type)

        # Train model
        training_results = engine.train(df)

        if 'error' in training_results:
            return JsonResponse({
                'success': False,
                'error': training_results['error']
            }, status=500)

        # Make prediction
        predicted_price = engine.predict(df)
        current_price = float(df['close'].iloc[-1])

        # Generate signal
        signal_result = engine.generate_signal(current_price, predicted_price)

        # Calculate target date (next trading day)
        prediction_date = timezone.now().date()
        target_date = prediction_date + timedelta(days=1)

        # Save prediction to database
        prediction, created = Prediction.objects.update_or_create(
            stock=stock,
            prediction_date=prediction_date,
            defaults={
                'target_date': target_date,
                'predicted_price': round(predicted_price, 4),
                'model_type': model_type,
                'mse': training_results['mse'],
                'rmse': training_results['rmse'],
                'r2_score': training_results['r2_score'],
                'mae': training_results['mae'],
                'feature_importance': training_results['feature_importance'],
                'signal': signal_result['signal'],
                'confidence': signal_result['confidence']
            }
        )

        return JsonResponse({
            'success': True,
            'prediction': {
                'id': prediction.id,
                'stock_symbol': stock.symbol,
                'prediction_date': prediction.prediction_date.isoformat(),
                'target_date': prediction.target_date.isoformat(),
                'predicted_price': float(prediction.predicted_price),
                'current_price': current_price,
                'signal': prediction.signal,
                'confidence': float(prediction.confidence),
                'model_type': model_type,
                'metrics': {
                    'mse': training_results['mse'],
                    'rmse': training_results['rmse'],
                    'r2_score': training_results['r2_score'],
                    'mae': training_results['mae']
                },
                'feature_importance': training_results['feature_importance']
            }
        })

    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Stock not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@require_http_methods(["GET"])
def api_get_predictions(request, stock_id):
    """
    Get recent predictions for a stock
    """
    try:
        stock = Stock.objects.get(id=stock_id)
        predictions = stock.predictions.order_by('-prediction_date')[:10]

        predictions_data = []
        for pred in predictions:
            predictions_data.append({
                'id': pred.id,
                'prediction_date': pred.prediction_date.isoformat(),
                'target_date': pred.target_date.isoformat(),
                'predicted_price': float(pred.predicted_price),
                'actual_price': float(pred.actual_price) if pred.actual_price else None,
                'signal': pred.signal,
                'confidence': float(pred.confidence) if pred.confidence else None,
                'model_type': pred.model_type,
                'r2_score': pred.r2_score,
                'rmse': pred.rmse
            })

        return JsonResponse({
            'success': True,
            'predictions': predictions_data
        })

    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Stock not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============== API: Volatility and Risk Analysis ==============

@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_volatility(request):
    """
    Calculate volatility and risk metrics for a stock
    """
    try:
        data = json.loads(request.body)
        stock_id = data.get('stock_id')
        period_days = data.get('period_days', 30)

        if not stock_id:
            return JsonResponse({
                'success': False,
                'error': 'stock_id is required'
            }, status=400)

        # Get stock
        stock = Stock.objects.get(id=stock_id)

        # Get historical data
        historical_qs = stock.historical_data.order_by('-date')[:period_days]
        historical_data = list(historical_qs.values())

        if len(historical_data) < 10:
            return JsonResponse({
                'success': False,
                'error': f'Insufficient data. Need at least 10 data points, got {len(historical_data)}'
            }, status=400)

        # Convert to DataFrame
        import pandas as pd
        historical_data = convert_decimal_to_float(historical_data)
        df = pd.DataFrame(historical_data)
        df = df.sort_values('date')

        # Rename columns
        column_map = {
            'open_price': 'open',
            'date': 'date'
        }
        df = df.rename(columns=column_map)

        # Calculate metrics
        volatility_metrics = VolatilityAnalyzer.calculate_volatility(df, period_days)
        var_95 = VolatilityAnalyzer.calculate_var(df, 0.95)
        var_99 = VolatilityAnalyzer.calculate_var(df, 0.99)
        sharpe_ratio = VolatilityAnalyzer.calculate_sharpe_ratio(df)
        max_drawdown = VolatilityAnalyzer.calculate_max_drawdown(df)

        # Classify risk level
        risk_level = VolatilityAnalyzer.classify_risk_level(volatility_metrics['daily_volatility'])

        # Save to database
        analysis_date = timezone.now().date()
        volatility_analysis, created = VolatilityAnalysis.objects.update_or_create(
            stock=stock,
            analysis_date=analysis_date,
            defaults={
                'daily_volatility': volatility_metrics['daily_volatility'],
                'annualized_volatility': volatility_metrics['annualized_volatility'],
                'var_95': var_95.get('var_95'),
                'var_99': var_99.get('var_99'),
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'risk_level': risk_level,
                'period_days': period_days
            }
        )

        return JsonResponse({
            'success': True,
            'analysis': {
                'id': volatility_analysis.id,
                'analysis_date': volatility_analysis.analysis_date.isoformat(),
                'daily_volatility': volatility_analysis.daily_volatility,
                'annualized_volatility': volatility_analysis.annualized_volatility,
                'var_95': volatility_analysis.var_95,
                'var_99': volatility_analysis.var_99,
                'sharpe_ratio': volatility_analysis.sharpe_ratio,
                'max_drawdown': volatility_analysis.max_drawdown,
                'risk_level': volatility_analysis.risk_level,
                'period_days': period_days
            }
        })

    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Stock not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# ============== API: Market Report Generation ==============

@csrf_exempt
@require_http_methods(["POST"])
def api_generate_report(request):
    """
    Generate a comprehensive market analysis report
    """
    try:
        data = json.loads(request.body)
        stock_id = data.get('stock_id')

        if not stock_id:
            return JsonResponse({
                'success': False,
                'error': 'stock_id is required'
            }, status=400)

        # Get stock
        stock = Stock.objects.get(id=stock_id)

        # Get historical data
        historical_qs = stock.historical_data.order_by('-date')[:90]
        historical_data = list(historical_qs.values())

        if len(historical_data) < 10:
            return JsonResponse({
                'success': False,
                'error': f'Insufficient data. Need at least 10 data points, got {len(historical_data)}'
            }, status=400)

        # Convert to DataFrame
        import pandas as pd
        historical_data = convert_decimal_to_float(historical_data)
        df = pd.DataFrame(historical_data)
        df = df.sort_values('date')

        # Rename columns
        column_map = {
            'open_price': 'open',
            'date': 'date'
        }
        df = df.rename(columns=column_map)

        # Calculate volatility
        volatility = VolatilityAnalyzer.calculate_volatility(df)

        # Get latest prediction
        latest_prediction = stock.predictions.order_by('-prediction_date').first()
        prediction_dict = {
            'signal': latest_prediction.signal if latest_prediction else 'HOLD',
            'confidence': float(latest_prediction.confidence) if latest_prediction and latest_prediction.confidence else 50,
            'predicted_price': float(latest_prediction.predicted_price) if latest_prediction else float(df['close'].iloc[-1]),
            'price_change_percent': 0
        }

        # Generate summary
        summary = ReportGenerator.generate_summary(df, volatility, prediction_dict)

        # Save report (create new report each time - no unique constraint)
        report_date = timezone.now().date()
        report = MarketReport.objects.create(
            stock=stock,
            report_date=report_date,
            title=f"{stock.symbol} Market Analysis Report",
            summary=f"Market trend for {stock.symbol} is {summary['trend']}. Current price: ${summary['current_price']:.2f}, Change: {summary['price_change_percent']:+.2f}%",
            trend=summary['trend'],
            key_findings=summary['key_findings'],
            recommendation=summary['recommendation'],
            data={
                'current_price': summary['current_price'],
                'price_change_percent': summary['price_change_percent'],
                'volatility': volatility
            }
        )

        return JsonResponse({
            'success': True,
            'report': {
                'id': report.id,
                'title': report.title,
                'report_date': report.report_date.isoformat(),
                'trend': report.trend,
                'summary': report.summary,
                'key_findings': report.key_findings,
                'recommendation': report.recommendation,
                'data': report.data
            }
        })

    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Stock not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@require_http_methods(["GET"])
def api_get_reports(request, stock_id):
    """
    Get recent reports for a stock
    """
    try:
        stock = Stock.objects.get(id=stock_id)
        reports = stock.market_reports.order_by('-report_date')[:5]

        reports_data = []
        for report in reports:
            reports_data.append({
                'id': report.id,
                'title': report.title,
                'report_date': report.report_date.isoformat(),
                'trend': report.trend,
                'summary': report.summary,
                'key_findings': report.key_findings,
                'recommendation': report.recommendation
            })

        return JsonResponse({
            'success': True,
            'reports': reports_data
        })

    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Stock not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============== API: Dashboard Data ==============

@require_http_methods(["GET"])
def api_dashboard_data(request, stock_id):
    """
    Get comprehensive dashboard data for a stock
    """
    try:
        stock = Stock.objects.get(id=stock_id)

        # Get historical data
        historical_qs = stock.historical_data.order_by('-date')[:90]
        historical_data = list(historical_qs.values())

        # Convert to DataFrame
        import pandas as pd
        historical_data = convert_decimal_to_float(historical_data)
        df = pd.DataFrame(historical_data)
        df = df.sort_values('date')

        # Prepare chart data
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                'date': row['date'].isoformat() if hasattr(row['date'], 'isoformat') else str(row['date']),
                'open': float(row.get('open_price', 0)),
                'high': float(row.get('high', 0)),
                'low': float(row.get('low', 0)),
                'close': float(row.get('close', 0)),
                'volume': int(row.get('volume', 0)),
                'ma_5': float(row.get('moving_average_5', 0)) if pd_notna(row.get('moving_average_5')) else None,
                'ma_20': float(row.get('moving_average_20', 0)) if pd_notna(row.get('moving_average_20')) else None,
            })

        # Get latest prediction
        latest_prediction = stock.predictions.order_by('-prediction_date').first()
        prediction_data = None
        if latest_prediction:
            prediction_data = {
                'predicted_price': float(latest_prediction.predicted_price),
                'signal': latest_prediction.signal,
                'confidence': float(latest_prediction.confidence) if latest_prediction.confidence else None,
                'r2_score': latest_prediction.r2_score,
                'rmse': latest_prediction.rmse
            }

        # Get latest volatility analysis
        latest_volatility = stock.volatility_analyses.order_by('-analysis_date').first()
        volatility_data = None
        if latest_volatility:
            volatility_data = {
                'daily_volatility': latest_volatility.daily_volatility,
                'annualized_volatility': latest_volatility.annualized_volatility,
                'risk_level': latest_volatility.risk_level,
                'var_95': latest_volatility.var_95,
                'sharpe_ratio': latest_volatility.sharpe_ratio
            }

        return JsonResponse({
            'success': True,
            'stock': {
                'symbol': stock.symbol,
                'company_name': stock.company_name,
                'latest_price': float(stock.latest_price) if stock.latest_price else None
            },
            'chart_data': chart_data,
            'prediction': prediction_data,
            'volatility': volatility_data
        })

    except Stock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Stock not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


# ============== Helper Functions ==============

def pd_notna(value):
    """
    Check if pandas value is not null/NaN
    """
    import pandas as pd
    return pd.notna(value) and value is not None


def convert_decimal_to_float(data_list):
    """
    Convert Django Decimal objects to float for pandas compatibility
    """
    from decimal import Decimal
    converted_data = []
    for item in data_list:
        converted_item = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                converted_item[key] = float(value)
            else:
                converted_item[key] = value
        converted_data.append(converted_item)
    return converted_data


# ============== Error Handlers ==============

def api_error_handler(request, exception=None):
    """
    Global API error handler
    """
    return JsonResponse({
        'success': False,
        'error': 'Internal server error',
        'message': str(exception) if exception else 'An unexpected error occurred'
    }, status=500)
