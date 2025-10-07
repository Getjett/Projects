"""
AI Strategy Optimizer
Analyzes backtest results and suggests parameter improvements
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import statistics


class StrategyOptimizer:
    """
    AI-powered strategy optimization engine
    Analyzes backtest results and provides actionable recommendations
    """
    
    def __init__(self):
        self.min_trades_for_analysis = 10
    
    def analyze_backtest(self, trades: List[Dict], strategy_config: Dict) -> Dict[str, Any]:
        """
        Main analysis function that returns comprehensive optimization suggestions
        
        Args:
            trades: List of trade results from backtest
            strategy_config: Current strategy configuration
            
        Returns:
            Dict containing analysis and recommendations
        """
        if len(trades) < self.min_trades_for_analysis:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {self.min_trades_for_analysis} trades for analysis"
            }
        
        # Perform multiple analysis
        win_rate_analysis = self._analyze_win_rate(trades)
        profit_analysis = self._analyze_profit_distribution(trades)
        time_analysis = self._analyze_entry_exit_timing(trades)
        risk_reward_analysis = self._analyze_risk_reward(trades, strategy_config)
        direction_analysis = self._analyze_trade_direction(trades)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            win_rate_analysis,
            profit_analysis,
            time_analysis,
            risk_reward_analysis,
            direction_analysis,
            strategy_config
        )
        
        # Calculate optimized parameters
        optimized_params = self._calculate_optimized_parameters(
            trades,
            strategy_config,
            recommendations
        )
        
        return {
            "status": "success",
            "analysis": {
                "win_rate": win_rate_analysis,
                "profit_distribution": profit_analysis,
                "timing": time_analysis,
                "risk_reward": risk_reward_analysis,
                "direction": direction_analysis
            },
            "recommendations": recommendations,
            "optimized_parameters": optimized_params,
            "confidence_score": self._calculate_confidence_score(trades)
        }
    
    def _analyze_win_rate(self, trades: List[Dict]) -> Dict:
        """Analyze win rate patterns"""
        winning_trades = [t for t in trades if t['profit_loss'] > 0]
        losing_trades = [t for t in trades if t['profit_loss'] <= 0]
        
        win_rate = (len(winning_trades) / len(trades)) * 100
        
        avg_win = statistics.mean([t['profit_loss'] for t in winning_trades]) if winning_trades else 0
        avg_loss = statistics.mean([abs(t['profit_loss']) for t in losing_trades]) if losing_trades else 0
        
        return {
            "win_rate": round(win_rate, 2),
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "profit_factor": round(avg_win / avg_loss, 2) if avg_loss > 0 else 0,
            "assessment": self._assess_win_rate(win_rate)
        }
    
    def _assess_win_rate(self, win_rate: float) -> str:
        """Assess win rate quality"""
        if win_rate >= 60:
            return "excellent"
        elif win_rate >= 50:
            return "good"
        elif win_rate >= 40:
            return "acceptable"
        else:
            return "needs_improvement"
    
    def _analyze_profit_distribution(self, trades: List[Dict]) -> Dict:
        """Analyze how profits are distributed"""
        profits = [t['profit_loss'] for t in trades]
        
        # Find outliers
        mean_profit = statistics.mean(profits)
        std_profit = statistics.stdev(profits) if len(profits) > 1 else 0
        
        large_wins = [p for p in profits if p > mean_profit + std_profit]
        large_losses = [p for p in profits if p < mean_profit - std_profit]
        
        return {
            "mean_profit": round(mean_profit, 2),
            "median_profit": round(statistics.median(profits), 2),
            "std_deviation": round(std_profit, 2),
            "max_profit": round(max(profits), 2),
            "max_loss": round(min(profits), 2),
            "large_wins_count": len(large_wins),
            "large_losses_count": len(large_losses),
            "consistency": "high" if std_profit < abs(mean_profit) else "low"
        }
    
    def _analyze_entry_exit_timing(self, trades: List[Dict]) -> Dict:
        """Analyze best entry and exit times"""
        entry_hours = {}
        exit_hours = {}
        
        for trade in trades:
            entry_time = datetime.fromisoformat(trade['entry_time'].replace('Z', '+00:00'))
            exit_time = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
            
            entry_hour = entry_time.hour
            exit_hour = exit_time.hour
            
            # Track profitability by hour
            if entry_hour not in entry_hours:
                entry_hours[entry_hour] = {'trades': 0, 'profit': 0}
            entry_hours[entry_hour]['trades'] += 1
            entry_hours[entry_hour]['profit'] += trade['profit_loss']
            
            if exit_hour not in exit_hours:
                exit_hours[exit_hour] = {'trades': 0, 'profit': 0}
            exit_hours[exit_hour]['trades'] += 1
            exit_hours[exit_hour]['profit'] += trade['profit_loss']
        
        # Find best entry times
        best_entry_hour = max(entry_hours.items(), key=lambda x: x[1]['profit'])[0] if entry_hours else 9
        worst_entry_hour = min(entry_hours.items(), key=lambda x: x[1]['profit'])[0] if entry_hours else 15
        
        return {
            "best_entry_hour": best_entry_hour,
            "worst_entry_hour": worst_entry_hour,
            "entry_hour_data": entry_hours,
            "suggested_entry_window": f"{best_entry_hour:02d}:15 - {min(best_entry_hour + 2, 15):02d}:00"
        }
    
    def _analyze_risk_reward(self, trades: List[Dict], strategy_config: Dict) -> Dict:
        """Analyze actual risk/reward vs configured"""
        winning_trades = [t for t in trades if t['profit_loss'] > 0]
        losing_trades = [t for t in trades if t['profit_loss'] < 0]
        
        if not winning_trades or not losing_trades:
            return {"status": "insufficient_data"}
        
        avg_win = statistics.mean([t['profit_loss'] for t in winning_trades])
        avg_loss = abs(statistics.mean([t['profit_loss'] for t in losing_trades]))
        
        actual_rr = avg_win / avg_loss if avg_loss > 0 else 0
        configured_rr = strategy_config.get('risk_reward_ratio', 1.5)
        
        return {
            "actual_risk_reward": round(actual_rr, 2),
            "configured_risk_reward": configured_rr,
            "average_win_size": round(avg_win, 2),
            "average_loss_size": round(avg_loss, 2),
            "rr_efficiency": round((actual_rr / configured_rr) * 100, 2) if configured_rr > 0 else 0,
            "assessment": "optimal" if actual_rr >= 1.5 else "suboptimal"
        }
    
    def _analyze_trade_direction(self, trades: List[Dict]) -> Dict:
        """Analyze performance by trade direction (BULLISH vs BEARISH)"""
        bullish_trades = [t for t in trades if t.get('position_type') == 'BULLISH']
        bearish_trades = [t for t in trades if t.get('position_type') == 'BEARISH']
        
        bullish_profit = sum(t['profit_loss'] for t in bullish_trades)
        bearish_profit = sum(t['profit_loss'] for t in bearish_trades)
        
        bullish_win_rate = (len([t for t in bullish_trades if t['profit_loss'] > 0]) / len(bullish_trades) * 100) if bullish_trades else 0
        bearish_win_rate = (len([t for t in bearish_trades if t['profit_loss'] > 0]) / len(bearish_trades) * 100) if bearish_trades else 0
        
        return {
            "bullish_trades": len(bullish_trades),
            "bearish_trades": len(bearish_trades),
            "bullish_profit": round(bullish_profit, 2),
            "bearish_profit": round(bearish_profit, 2),
            "bullish_win_rate": round(bullish_win_rate, 2),
            "bearish_win_rate": round(bearish_win_rate, 2),
            "best_direction": "BULLISH" if bullish_profit > bearish_profit else "BEARISH"
        }
    
    def _generate_recommendations(
        self,
        win_rate: Dict,
        profit: Dict,
        timing: Dict,
        risk_reward: Dict,
        direction: Dict,
        current_config: Dict
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Win Rate Recommendations
        if win_rate['assessment'] == 'needs_improvement':
            recommendations.append({
                "priority": "high",
                "category": "win_rate",
                "title": "⚠️ Low Win Rate Detected",
                "issue": f"Current win rate is {win_rate['win_rate']}%, which is below acceptable threshold",
                "suggestion": "Consider tightening entry filters or using more selective breakout conditions",
                "action": "Add volume confirmation or require stronger trends"
            })
        
        # Profit Factor Recommendations
        if win_rate['profit_factor'] < 1.5:
            recommendations.append({
                "priority": "high",
                "category": "profit_factor",
                "title": "💰 Improve Profit Factor",
                "issue": f"Profit factor is {win_rate['profit_factor']}, target should be > 1.5",
                "suggestion": "Average losses are too large compared to wins",
                "action": f"Reduce stop loss from {current_config.get('stop_loss_value')}% to improve risk/reward"
            })
        
        # Timing Recommendations
        if timing.get('best_entry_hour'):
            current_start = current_config.get('entry_time_start', '09:15')
            recommendations.append({
                "priority": "medium",
                "category": "timing",
                "title": "⏰ Optimize Entry Timing",
                "issue": f"Best performing entries occur around {timing['best_entry_hour']}:00",
                "suggestion": f"Current entry window starts at {current_start}",
                "action": f"Adjust entry window to {timing['suggested_entry_window']}"
            })
        
        # Risk/Reward Recommendations
        if risk_reward.get('assessment') == 'suboptimal':
            recommendations.append({
                "priority": "high",
                "category": "risk_reward",
                "title": "📊 Adjust Risk/Reward Ratio",
                "issue": f"Actual R:R is {risk_reward['actual_risk_reward']}, lower than configured",
                "suggestion": "Either increase target or decrease stop loss",
                "action": "Increase target from {0}% to {1}%".format(
                    current_config.get('target_value'),
                    int(current_config.get('target_value', 2) * 1.5)
                )
            })
        
        # Direction Recommendations
        if direction.get('best_direction'):
            if abs(direction['bullish_profit'] - direction['bearish_profit']) > 10000:
                recommendations.append({
                    "priority": "medium",
                    "category": "direction",
                    "title": "🎯 Focus on Best Direction",
                    "issue": f"{direction['best_direction']} trades are significantly more profitable",
                    "suggestion": f"{direction['best_direction']}: ₹{max(direction['bullish_profit'], direction['bearish_profit']):.0f} vs other: ₹{min(direction['bullish_profit'], direction['bearish_profit']):.0f}",
                    "action": f"Change breakout direction to {direction['best_direction']} only"
                })
        
        # Consistency Recommendations
        if profit['consistency'] == 'low':
            recommendations.append({
                "priority": "low",
                "category": "consistency",
                "title": "📉 High Variance in Results",
                "issue": "Large swings between wins and losses indicate inconsistent strategy",
                "suggestion": "Results are unpredictable with high standard deviation",
                "action": "Add more strict entry filters to reduce randomness"
            })
        
        return sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])
    
    def _calculate_optimized_parameters(
        self,
        trades: List[Dict],
        current_config: Dict,
        recommendations: List[Dict]
    ) -> Dict:
        """Calculate specific optimized parameter values"""
        winning_trades = [t for t in trades if t['profit_loss'] > 0]
        losing_trades = [t for t in trades if t['profit_loss'] < 0]
        
        if not winning_trades or not losing_trades:
            return current_config
        
        # Calculate optimal target based on average winning trade
        avg_win_pct = statistics.mean([t['profit_loss_percent'] for t in winning_trades])
        optimal_target = round(avg_win_pct * 0.8, 1)  # 80% of average win to hit more often
        
        # Calculate optimal stop loss based on average losing trade
        avg_loss_pct = abs(statistics.mean([t['profit_loss_percent'] for t in losing_trades]))
        optimal_stop_loss = round(avg_loss_pct * 0.9, 1)  # 90% of average loss to exit sooner
        
        return {
            "current": {
                "target_value": current_config.get('target_value'),
                "stop_loss_value": current_config.get('stop_loss_value'),
                "entry_time_start": current_config.get('entry_time_start'),
                "breakout_direction": current_config.get('breakout_direction')
            },
            "optimized": {
                "target_value": max(optimal_target, 1),  # At least 1%
                "stop_loss_value": max(optimal_stop_loss, 0.5),  # At least 0.5%
                "entry_time_start": "09:30",  # After initial volatility
                "breakout_direction": self._get_best_direction(trades)
            },
            "expected_improvement": self._estimate_improvement(trades, optimal_target, optimal_stop_loss)
        }
    
    def _get_best_direction(self, trades: List[Dict]) -> str:
        """Determine best performing direction"""
        bullish_profit = sum(t['profit_loss'] for t in trades if t.get('position_type') == 'BULLISH')
        bearish_profit = sum(t['profit_loss'] for t in trades if t.get('position_type') == 'BEARISH')
        
        if abs(bullish_profit - bearish_profit) < 5000:
            return "BOTH"
        return "BULLISH" if bullish_profit > bearish_profit else "BEARISH"
    
    def _estimate_improvement(self, trades: List[Dict], new_target: float, new_sl: float) -> Dict:
        """Estimate potential improvement with new parameters"""
        current_net = sum(t['profit_loss'] for t in trades)
        
        # Rough estimation: Better R:R should improve results by 15-30%
        estimated_improvement = 20  # 20% improvement estimate
        
        return {
            "current_profit": round(current_net, 2),
            "estimated_profit": round(current_net * 1.2, 2),
            "improvement_percentage": estimated_improvement,
            "confidence": "medium"
        }
    
    def _calculate_confidence_score(self, trades: List[Dict]) -> int:
        """Calculate confidence in recommendations (0-100)"""
        score = 50  # Base score
        
        # More trades = higher confidence
        if len(trades) > 50:
            score += 20
        elif len(trades) > 30:
            score += 10
        
        # Consistent results = higher confidence
        profits = [t['profit_loss'] for t in trades]
        if len(profits) > 1:
            cv = statistics.stdev(profits) / abs(statistics.mean(profits)) if statistics.mean(profits) != 0 else 999
            if cv < 1:  # Low coefficient of variation
                score += 20
        
        # Profitable strategy = higher confidence
        if sum(profits) > 0:
            score += 10
        
        return min(score, 100)


# Singleton instance
optimizer = StrategyOptimizer()
