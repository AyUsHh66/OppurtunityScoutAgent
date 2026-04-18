"""
Enhanced Explainable AI (XAI) module for transparent decision-making
Provides standardized reasoning traces, factor analysis, and confidence scoring
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

from core_engine.logging_config import get_logger

logger = get_logger(__name__)


class FactorType(str, Enum):
    """Types of decision factors"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class DecisionFactor:
    """Represents a single factor in decision-making"""
    type: FactorType
    description: str
    weight: float = 1.0  # Impact weight
    source_quote: Optional[str] = None  # Supporting quote from data
    confidence: float = 1.0  # 0-1 confidence in this factor


@dataclass
class ReasoningTrace:
    """Step-by-step reasoning trace"""
    step_number: int
    description: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExplainableDecision:
    """Standardized explainable decision structure"""
    decision_id: str
    decision_type: str  # e.g., "lead_qualification", "job_match"
    decision: str  # The actual decision made
    confidence_score: float  # 0-1 confidence
    
    # XAI Components
    reasoning_traces: List[ReasoningTrace] = field(default_factory=list)
    positive_factors: List[DecisionFactor] = field(default_factory=list)
    negative_factors: List[DecisionFactor] = field(default_factory=list)
    neutral_factors: List[DecisionFactor] = field(default_factory=list)
    
    # Metadata
    model_used: str = "phi"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processing_time_ms: float = 0.0
    
    def calculate_confidence_level(self) -> str:
        """Calculate confidence level based on factors and score"""
        if self.confidence_score >= 0.8:
            return "HIGH"
        elif self.confidence_score >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_summary(self) -> str:
        """Generate summary of decision"""
        positive_count = len(self.positive_factors)
        negative_count = len(self.negative_factors)
        
        summary = f"Decision: {self.decision}\n"
        summary += f"Confidence: {self.confidence_score:.2%} ({self.calculate_confidence_level()})\n"
        summary += f"Positive Factors: {positive_count}\n"
        summary += f"Negative Factors: {negative_count}\n"
        
        return summary
    
    def get_detailed_reasoning(self) -> str:
        """Generate detailed reasoning explanation"""
        report = "=" * 80 + "\n"
        report += f"EXPLAINABLE AI DECISION REPORT\n"
        report += f"Decision Type: {self.decision_type}\n"
        report += f"Decision: {self.decision}\n"
        report += f"Confidence: {self.confidence_score:.2%} ({self.calculate_confidence_level()})\n"
        report += f"Model: {self.model_used}\n"
        report += "=" * 80 + "\n\n"
        
        # Reasoning traces
        if self.reasoning_traces:
            report += "REASONING PROCESS:\n"
            report += "-" * 80 + "\n"
            for trace in self.reasoning_traces:
                report += f"Step {trace.step_number}: {trace.description}\n"
            report += "\n"
        
        # Positive factors
        if self.positive_factors:
            report += "POSITIVE FACTORS (Supporting the decision):\n"
            report += "-" * 80 + "\n"
            for i, factor in enumerate(self.positive_factors, 1):
                report += f"  {i}. {factor.description}\n"
                if factor.source_quote:
                    report += f"     Source: \"{factor.source_quote}\"\n"
                if factor.weight != 1.0 or factor.confidence != 1.0:
                    report += f"     Weight: {factor.weight:.2f} | Confidence: {factor.confidence:.2%}\n"
            report += "\n"
        
        # Negative factors
        if self.negative_factors:
            report += "NEGATIVE FACTORS (Against the decision):\n"
            report += "-" * 80 + "\n"
            for i, factor in enumerate(self.negative_factors, 1):
                report += f"  {i}. {factor.description}\n"
                if factor.source_quote:
                    report += f"     Source: \"{factor.source_quote}\"\n"
                if factor.weight != 1.0 or factor.confidence != 1.0:
                    report += f"     Weight: {factor.weight:.2f} | Confidence: {factor.confidence:.2%}\n"
            report += "\n"
        
        # Neutral factors
        if self.neutral_factors:
            report += "NEUTRAL FACTORS (Informational):\n"
            report += "-" * 80 + "\n"
            for i, factor in enumerate(self.neutral_factors, 1):
                report += f"  {i}. {factor.description}\n"
            report += "\n"
        
        report += "=" * 80 + "\n"
        report += f"Processing Time: {self.processing_time_ms:.2f}ms\n"
        
        return report
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'decision_id': self.decision_id,
            'decision_type': self.decision_type,
            'decision': self.decision,
            'confidence_score': self.confidence_score,
            'confidence_level': self.calculate_confidence_level(),
            'reasoning_traces': [
                {
                    'step': t.step_number,
                    'description': t.description,
                }
                for t in self.reasoning_traces
            ],
            'positive_factors': len(self.positive_factors),
            'negative_factors': len(self.negative_factors),
            'neutral_factors': len(self.neutral_factors),
            'model_used': self.model_used,
            'created_at': self.created_at,
            'processing_time_ms': self.processing_time_ms,
        }


class ExplainableAIFactory:
    """Factory for creating explainable AI decisions"""
    
    @staticmethod
    def create_lead_qualification_decision(
        decision_id: str,
        company_name: str,
        qualification_score: float,
        positive_factors: List[str],
        negative_factors: List[str],
        source_quotes: List[str],
        confidence: float = 0.7,
        model: str = "phi"
    ) -> ExplainableDecision:
        """Create an explainable decision for lead qualification"""
        
        decision = ExplainableDecision(
            decision_id=decision_id,
            decision_type="lead_qualification",
            decision=f"Lead '{company_name}' qualified with score {qualification_score}/10",
            confidence_score=confidence,
            model_used=model,
        )
        
        # Add positive factors
        for i, factor_text in enumerate(positive_factors):
            decision.positive_factors.append(
                DecisionFactor(
                    type=FactorType.POSITIVE,
                    description=factor_text,
                    source_quote=source_quotes[i] if i < len(source_quotes) else None,
                    weight=1.0,
                    confidence=confidence,
                )
            )
        
        # Add negative factors
        for i, factor_text in enumerate(negative_factors):
            decision.negative_factors.append(
                DecisionFactor(
                    type=FactorType.NEGATIVE,
                    description=factor_text,
                    weight=0.8,  # Negative factors slightly less impactful
                    confidence=confidence,
                )
            )
        
        return decision
    
    @staticmethod
    def create_job_match_decision(
        decision_id: str,
        job_title: str,
        match_score: float,
        matching_skills: List[str],
        missing_skills: List[str],
        match_factors: List[str],
        confidence: float = 0.75
    ) -> ExplainableDecision:
        """Create an explainable decision for job matching"""
        
        decision = ExplainableDecision(
            decision_id=decision_id,
            decision_type="job_match",
            decision=f"Job '{job_title}' is a {match_score:.0%} match",
            confidence_score=confidence,
        )
        
        # Add matching skills as positive factors
        for skill in matching_skills:
            decision.positive_factors.append(
                DecisionFactor(
                    type=FactorType.POSITIVE,
                    description=f"You have the required skill: {skill}",
                    weight=1.2,
                )
            )
        
        # Add missing skills as negative factors
        for skill in missing_skills:
            decision.negative_factors.append(
                DecisionFactor(
                    type=FactorType.NEGATIVE,
                    description=f"Missing important skill: {skill}",
                    weight=0.9,
                )
            )
        
        # Add match factors
        for factor in match_factors:
            decision.positive_factors.append(
                DecisionFactor(
                    type=FactorType.POSITIVE,
                    description=factor,
                    weight=1.0,
                )
            )
        
        return decision
    
    @staticmethod
    def create_reasoning_trace(
        step_number: int,
        description: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None
    ) -> ReasoningTrace:
        """Create a reasoning trace step"""
        return ReasoningTrace(
            step_number=step_number,
            description=description,
            input_data=input_data or {},
            output_data=output_data or {},
        )


class ExplainabilityFormatter:
    """Formats explainable decisions for different outputs"""
    
    @staticmethod
    def format_for_terminal(decision: ExplainableDecision) -> str:
        """Format for terminal output with colors"""
        output = decision.get_detailed_reasoning()
        return output
    
    @staticmethod
    def format_for_json(decision: ExplainableDecision) -> Dict[str, Any]:
        """Format for JSON output"""
        return decision.to_dict()
    
    @staticmethod
    def format_for_discord(decision: ExplainableDecision) -> Dict[str, Any]:
        """Format as Discord embed"""
        confidence_level = decision.calculate_confidence_level()
        color_map = {
            'HIGH': 3066993,    # Blue
            'MEDIUM': 16776960,  # Yellow
            'LOW': 16711680,     # Red
        }
        
        embed = {
            "title": f"{decision.decision_type.upper()} Decision",
            "description": decision.decision,
            "color": color_map.get(confidence_level, 3066993),
            "fields": [
                {
                    "name": "Confidence",
                    "value": f"{decision.confidence_score:.1%} ({confidence_level})",
                    "inline": True
                },
                {
                    "name": "Positive Factors",
                    "value": str(len(decision.positive_factors)),
                    "inline": True
                },
                {
                    "name": "Negative Factors",
                    "value": str(len(decision.negative_factors)),
                    "inline": True
                }
            ]
        }
        
        # Add factor summaries
        if decision.positive_factors:
            factors_text = "\n".join([f.description for f in decision.positive_factors[:3]])
            embed["fields"].append({
                "name": "Key Positive Factors",
                "value": factors_text,
                "inline": False
            })
        
        if decision.negative_factors:
            factors_text = "\n".join([f.description for f in decision.negative_factors[:3]])
            embed["fields"].append({
                "name": "Key Negative Factors",
                "value": factors_text,
                "inline": False
            })
        
        return embed
