import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import {
  Award,
  CheckCircle2,
  XCircle,
  ArrowLeft,
  ArrowRight,
  TrendingUp,
  RotateCcw,
  Sparkles,
  HelpCircle,
  ShieldCheck,
  ChevronRight,
  BookOpen,
  FileText,
  AlertTriangle,
  Loader2,
  ExternalLink,
  Target,
  BarChart3,
  GraduationCap
} from 'lucide-react';

interface InteractiveQuizProps {
  onReturnToDashboard?: () => void;
  onViewWeeklyProgress?: () => void;
}

export const InteractiveQuiz: React.FC<InteractiveQuizProps> = ({
  onReturnToDashboard,
  onViewWeeklyProgress,
}) => {
  const {
    assessmentTopics,
    activeAssessment,
    assessmentResult,
    isAssessmentLoading,
    assessmentError,
    selectedAssessmentTopicId,
    setSelectedAssessmentTopicId,
    startDiagnosticAssessment,
    submitDiagnosticAssessment,
    resetDiagnosticAssessment,
    navigateTo,
    selectedLearnerId,
    userProfile
  } = useApp();

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [validationError, setValidationError] = useState<string | null>(null);

  // When a new assessment starts, reset local question index and answers
  useEffect(() => {
    if (activeAssessment) {
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setValidationError(null);
    }
  }, [activeAssessment?.attempt_id]);

  const handleSelectOption = (questionId: string, optionKey: string) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: optionKey,
    }));
    setValidationError(null);
  };

  const handleNext = () => {
    if (!activeAssessment) return;
    if (currentQuestionIndex < activeAssessment.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    if (!activeAssessment) return;

    // Check if all questions have been answered
    const unansweredCount = activeAssessment.questions.filter(
      (q) => !userAnswers[q.question_id]
    ).length;

    if (unansweredCount > 0) {
      setValidationError(
        `Please select an answer for all ${activeAssessment.questions.length} questions before submitting (${unansweredCount} remaining).`
      );
      return;
    }

    setValidationError(null);
    await submitDiagnosticAssessment(userAnswers);
  };

  const returnDashboard = () => {
    if (onReturnToDashboard) {
      onReturnToDashboard();
    } else {
      navigateTo('dashboard');
    }
  };

  // =========================================================================
  // VIEW 1: Assessment Result & Source Provenance Screen
  // =========================================================================
  if (assessmentResult) {
    const isMastery = assessmentResult.provisional_estimate.estimated_level >= 3;
    const isThresholdMet = assessmentResult.provisional_estimate.evidence_threshold_met;

    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        {/* Provisional Competency Score Updated Banner */}
        <div className="bg-linear-to-r from-emerald-800 via-teal-800 to-blue-900 rounded-xl p-6 text-white shadow-md relative overflow-hidden border border-emerald-600">
          <div className="flex flex-wrap items-center justify-between gap-4 relative z-10">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs uppercase tracking-wider font-extrabold px-2 py-0.5 rounded bg-emerald-400 text-slate-950 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Provisional Estimate Recorded
                </span>
                <span className="text-xs text-emerald-200">• Source-Grounded Diagnostic</span>
              </div>
              <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-amber-300" />
                {assessmentResult.competency_name}
              </h2>
              <p className="text-xs text-emerald-100 mt-1 max-w-xl">
                Diagnostic assessment graded server-side against official source documentation. Results have been recorded with full audit provenance.
              </p>
            </div>

            {/* Estimated Level & Confidence Badge */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center min-w-[200px]">
              <span className="text-xs font-semibold text-emerald-200 block uppercase tracking-wide">
                Provisional Assessment
              </span>
              <div className="flex items-center justify-center gap-2 my-1">
                <span className="text-3xl font-extrabold text-amber-300">
                  Level {assessmentResult.provisional_estimate.estimated_level}
                </span>
                <span className="text-slate-300 text-lg font-bold">/ 5</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <span className="text-[11px] font-bold text-emerald-300 bg-emerald-950/60 px-2.5 py-0.5 rounded-full inline-block">
                  {Math.round(assessmentResult.provisional_estimate.confidence * 100)}% Confidence
                </span>
                <span className="text-[11px] font-semibold text-slate-200">
                  ({assessmentResult.score_percentage}% Score)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Prototype Methodology & Evidence Sufficiency Alert */}
        <div className="bg-amber-50 rounded-xl border border-amber-200 p-4 text-xs text-amber-900 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-bold">
              <span>Prototype Diagnostic Estimator</span>
              <span className="px-1.5 py-0.2 bg-amber-200 text-amber-900 rounded font-semibold text-[10px]">
                {isThresholdMet ? 'Evidence Threshold Met (≥3 questions)' : 'Insufficient Evidence (<3 questions)'}
              </span>
            </div>
            <p className="text-amber-800">
              {assessmentResult.provisional_estimate.methodology_note}
            </p>
            <p className="text-amber-700 font-medium italic">
              {assessmentResult.provisional_estimate.limitations_disclaimer}
            </p>
          </div>
        </div>

        {/* Performance Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 bg-white rounded-xl border border-slate-200 text-center shadow-2xs">
            <span className="text-xs text-slate-500 font-medium block">Raw Score</span>
            <span className="text-3xl font-extrabold text-slate-900">
              {assessmentResult.correct_count} / {assessmentResult.total_questions}
            </span>
            <span className="text-[11px] text-slate-500 block mt-1">Questions answered correctly</span>
          </div>

          <div className="p-4 bg-white rounded-xl border border-slate-200 text-center shadow-2xs">
            <span className="text-xs text-blue-700 font-medium block">Scoring Percentage</span>
            <span className="text-3xl font-extrabold text-blue-900">
              {assessmentResult.score_percentage}%
            </span>
            <span className="text-[11px] font-semibold text-emerald-700 block mt-1">
              {isMastery ? 'Level benchmark satisfied' : 'Foundation level assigned'}
            </span>
          </div>

          <div className="p-4 bg-white rounded-xl border border-slate-200 text-center shadow-2xs">
            <span className="text-xs text-emerald-700 font-medium block">Officer Profile Sync</span>
            <span className="text-2xl font-extrabold text-emerald-800">
              {userProfile.employeeId}
            </span>
            <span className="text-[11px] text-slate-600 block mt-1">
              Skill gap dynamically updated
            </span>
          </div>
        </div>

        {/* Question Review & Grounded Citations */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Detailed Question Review & Source Provenance
              </h3>
              <p className="text-xs text-slate-500">
                Every question is verified against official Ministry documentation with exact page citations and verbatim excerpts.
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md">
              {assessmentResult.feedback.length} Verified Items
            </span>
          </div>

          <div className="space-y-5">
            {assessmentResult.feedback.map((fb, idx) => {
              const isCorrect = fb.is_correct;

              return (
                <div
                  key={fb.question_id}
                  className={`p-5 rounded-xl border transition-all ${
                    isCorrect
                      ? 'border-emerald-200 bg-emerald-50/20'
                      : 'border-rose-200 bg-rose-50/20'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-slate-500">
                          Q{idx + 1} ({fb.question_id})
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-slate-900 leading-snug">
                        {fb.question_text}
                      </h4>
                    </div>
                    <span
                      className={`text-[11px] font-bold px-2.5 py-1 rounded flex items-center gap-1 shrink-0 ${
                        isCorrect
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {isCorrect ? (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5" /> Correct
                        </>
                      ) : (
                        <>
                          <XCircle className="w-3.5 h-3.5" /> Incorrect
                        </>
                      )}
                    </span>
                  </div>

                  {/* Answer Summary */}
                  <div className="flex flex-wrap gap-4 text-xs my-3 bg-white/70 p-3 rounded-lg border border-slate-200/60">
                    <div>
                      <span className="text-slate-500 font-medium">Your Submitted Answer: </span>
                      <strong className={isCorrect ? 'text-emerald-700' : 'text-rose-700'}>
                        Option {fb.selected_answer || 'None'}
                      </strong>
                    </div>
                    <div>
                      <span className="text-slate-500 font-medium">Official Correct Answer: </span>
                      <strong className="text-emerald-700">Option {fb.correct_answer}</strong>
                    </div>
                  </div>

                  {/* Grounded Source Citation Box */}
                  <div className="p-3.5 bg-blue-50/60 rounded-lg border border-blue-200/80 mb-3 space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-bold text-blue-900">
                      <span className="flex items-center gap-1.5">
                        <BookOpen className="w-3.5 h-3.5 text-blue-700" />
                        Source Reference: {fb.source_title}
                      </span>
                      <span className="px-2 py-0.5 bg-blue-200/80 text-blue-950 rounded text-[11px] font-mono">
                        Page {fb.page_reference}
                      </span>
                    </div>
                    <blockquote className="text-xs text-blue-950/90 italic pl-3 border-l-2 border-blue-400 my-1 font-serif leading-relaxed">
                      &ldquo;{fb.verbatim_excerpt}&rdquo;
                    </blockquote>
                    <span className="text-[10px] text-blue-700 font-mono block">
                      Source ID: {fb.source_document_id} • Verified from unalterable Ministry publication
                    </span>
                  </div>

                  {/* Explanation */}
                  <div className="text-xs text-slate-700 bg-white p-3 rounded-lg border border-slate-200/80 leading-relaxed">
                    <strong className="text-slate-900 font-semibold block mb-0.5">
                      Technical Assessment Rationale:
                    </strong>
                    {fb.explanation}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recommended Capacity Building Courses for this Competency */}
        {assessmentResult.recommended_courses && assessmentResult.recommended_courses.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-blue-800" />
                  Targeted Capacity Building Courses (ACBP 2026-27)
                </h3>
                <p className="text-xs text-slate-500">
                  Recommended courses from the Annual Capacity Building Plan mapped to this competency.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
              {assessmentResult.recommended_courses.slice(0, 4).map((rec) => (
                <div
                  key={rec.course_id}
                  className="p-3.5 rounded-lg border border-slate-200 hover:border-blue-300 transition-all bg-slate-50/50 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1">
                      <span className="font-semibold text-blue-800">{rec.competency_category}</span>
                      <span>{rec.duration}</span>
                    </div>
                    <h4 className="text-xs font-bold text-slate-900 line-clamp-2">
                      {rec.course_name}
                    </h4>
                    <p className="text-[11px] text-slate-600 mt-1 line-clamp-2">
                      {rec.recommendation_reason}
                    </p>
                  </div>
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-200/60">
                    <span className="text-[10px] text-slate-500">By {rec.course_creator}</span>
                    <button
                      onClick={() => navigateTo('course-details', rec.course_id)}
                      className="text-xs font-bold text-blue-700 hover:text-blue-900 flex items-center gap-1"
                    >
                      <span>Explore Course</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-white rounded-xl border border-slate-200">
          <button
            onClick={() => {
              resetDiagnosticAssessment();
            }}
            className="px-4 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 border border-slate-200 rounded-lg hover:bg-slate-50 flex items-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Select Another Competency</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={() => startDiagnosticAssessment(assessmentResult.competency_id)}
              className="px-4 py-2 text-xs font-bold text-blue-900 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors flex items-center gap-1.5 shadow-2xs"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Re-assess This Competency</span>
            </button>
            <button
              onClick={returnDashboard}
              className="px-5 py-2 text-xs font-extrabold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow transition-colors flex items-center gap-1.5"
            >
              <span>View Updated Dashboard & Gaps</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // =========================================================================
  // VIEW 2: Active Quiz Taking View
  // =========================================================================
  if (activeAssessment) {
    const currentQ = activeAssessment.questions[currentQuestionIndex];
    const totalQ = activeAssessment.questions.length;
    const answeredCount = Object.keys(userAnswers).length;

    return (
      <div className="space-y-6 max-w-3xl mx-auto">
        {/* Assessment Active Header */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider bg-blue-100 text-blue-900 px-2.5 py-0.5 rounded">
              {activeAssessment.competency_name}
            </span>
            <span className="text-xs font-mono font-medium text-slate-500">
              {activeAssessment.attempt_id}
            </span>
          </div>

          <h1 className="text-xl font-extrabold text-slate-900">
            Diagnostic Assessment — {activeAssessment.competency_name}
          </h1>

          <div className="flex items-center gap-2 mt-2 text-xs text-slate-600">
            <BookOpen className="w-4 h-4 text-blue-700 shrink-0" />
            <span>
              Grounded in: <strong>{activeAssessment.source_title}</strong> ({activeAssessment.source_document_id})
            </span>
          </div>

          <p className="text-xs text-slate-500 mt-2 bg-slate-50 p-2.5 rounded border border-slate-200">
            {activeAssessment.instructions}
          </p>
        </div>

        {/* Question Navigation Bar */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-sm flex items-center justify-between gap-2 overflow-x-auto">
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Question {currentQuestionIndex + 1} of {totalQ}
            </span>
            <span className="text-[11px] text-slate-500">
              ({answeredCount} of {totalQ} answered)
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            {activeAssessment.questions.map((q, idx) => {
              const isCurrent = currentQuestionIndex === idx;
              const hasAnswered = !!userAnswers[q.question_id];

              return (
                <button
                  key={q.question_id}
                  onClick={() => setCurrentQuestionIndex(idx)}
                  className={`w-8 h-8 rounded-lg text-xs font-bold transition-all flex items-center justify-center ${
                    isCurrent
                      ? 'bg-blue-900 text-white ring-2 ring-blue-400'
                      : hasAnswered
                      ? 'bg-blue-50 text-blue-800 border border-blue-300 font-bold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {idx + 1}
                </button>
              );
            })}
          </div>
        </div>

        {/* Validation Error Alert if unsubmitted items exist */}
        {validationError && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs font-semibold flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{validationError}</span>
          </div>
        )}

        {/* Main Question Card */}
        {currentQ && (
          <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-sm">
            <div className="mb-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-blue-700 uppercase tracking-wider">
                  Question {currentQuestionIndex + 1}
                </span>
                <span className="text-[11px] font-semibold text-slate-500 uppercase px-2 py-0.5 bg-slate-100 rounded">
                  Difficulty: {currentQ.difficulty}
                </span>
              </div>
              <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                {currentQ.question_text}
              </h2>
            </div>

            {/* Answer Options */}
            <div className="space-y-3 mb-6">
              {Object.entries(currentQ.options).map(([optKey, optText]) => {
                const isSelected = userAnswers[currentQ.question_id] === optKey;

                return (
                  <button
                    key={optKey}
                    onClick={() => handleSelectOption(currentQ.question_id, optKey)}
                    className={`w-full text-left p-4 rounded-xl border transition-all flex items-center gap-3.5 ${
                      isSelected
                        ? 'border-blue-700 bg-blue-50/70 text-blue-950 font-bold ring-1 ring-blue-600 shadow-2xs'
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-800'
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                        isSelected
                          ? 'bg-blue-800 text-white'
                          : 'bg-slate-100 text-slate-700 border border-slate-300'
                      }`}
                    >
                      {optKey}
                    </div>
                    <span className="text-sm">{optText}</span>
                  </button>
                );
              })}
            </div>

            {/* Navigation & Submit */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-200">
              <button
                onClick={handlePrev}
                disabled={currentQuestionIndex === 0}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Previous</span>
              </button>

              <div className="flex items-center gap-3">
                {currentQuestionIndex < totalQ - 1 ? (
                  <button
                    onClick={handleNext}
                    className="px-5 py-2 text-xs font-bold text-white bg-blue-800 hover:bg-blue-700 rounded-lg flex items-center gap-1.5 transition-colors shadow-2xs"
                  >
                    <span>Next</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : null}

                <button
                  onClick={handleSubmit}
                  disabled={isAssessmentLoading}
                  className="px-6 py-2 text-xs font-extrabold text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 rounded-lg shadow flex items-center gap-1.5 transition-all transform hover:scale-105"
                >
                  {isAssessmentLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Grading Submission...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Submit Assessment ({answeredCount}/{totalQ})</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Back to topic selection */}
        <div className="flex justify-start">
          <button
            onClick={() => resetDiagnosticAssessment()}
            className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 underline underline-offset-2"
          >
            ← Cancel and select another competency topic
          </button>
        </div>
      </div>
    );
  }

  // =========================================================================
  // VIEW 3: Competency Selection & Overview
  // =========================================================================
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="bg-linear-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-xl p-6 text-white shadow-md border border-blue-800">
        <div className="max-w-2xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs uppercase tracking-wider font-extrabold px-2.5 py-0.5 rounded bg-blue-400 text-slate-950 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Source-Grounded Prototype
            </span>
            <span className="text-xs text-blue-200">
              • MoSPI & Karmayogi Documentation
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">
            Diagnostic Competency Assessment
          </h1>
          <p className="text-xs text-blue-100 mt-2 leading-relaxed">
            Select a civil service competency below to take an authentic diagnostic quiz. All questions are rigorously grounded in official Ministry publications with exact page references. Performance produces an explainable provisional Level 1–5 assessment.
          </p>
        </div>

        {/* Transparency note */}
        <div className="mt-4 pt-3 border-t border-blue-800/80 flex items-center gap-2 text-[11px] text-blue-200">
          <HelpCircle className="w-4 h-4 text-blue-300 shrink-0" />
          <span>
            Demonstration assumptions: Provisional Level 1–5 scale with 3-question evidence sufficiency rule. Does not claim psychometric validation.
          </span>
        </div>
      </div>

      {/* Assessment Error Alert */}
      {assessmentError && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
          <div className="flex-1">
            <strong>Assessment Error: </strong>
            <span>{assessmentError}</span>
          </div>
          <button
            onClick={() => resetDiagnosticAssessment()}
            className="text-xs font-bold underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Current Learner Context Banner */}
      <div className="p-4 bg-white rounded-xl border border-slate-200/90 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-900 font-bold flex items-center justify-center text-xs">
            {userProfile.name.split(' ').map((n) => n[0]).join('')}
          </div>
          <div>
            <span className="text-xs font-bold text-slate-900 block">
              Assessing Learner: {userProfile.name} ({selectedLearnerId})
            </span>
            <span className="text-[11px] text-slate-500">
              {userProfile.department} • {userProfile.designation}
            </span>
          </div>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-md">
          Ready for Assessment
        </span>
      </div>

      {/* Topics Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Target className="w-4 h-4 text-blue-700" />
            Available Competency Assessment Topics
          </h2>
          <span className="text-xs text-slate-500 font-medium">
            {assessmentTopics.length} grounded topics available
          </span>
        </div>

        {isAssessmentLoading && (
          <div className="p-12 text-center bg-white rounded-xl border border-slate-200">
            <Loader2 className="w-8 h-8 animate-spin text-blue-700 mx-auto mb-3" />
            <span className="text-xs font-semibold text-slate-700 block">
              Loading source-grounded questions...
            </span>
          </div>
        )}

        {!isAssessmentLoading && assessmentTopics.length === 0 && (
          <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200">
            <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <h3 className="text-sm font-bold text-slate-700">No Assessment Topics Available</h3>
            <p className="text-xs text-slate-500 mt-1">
              Verify that the backend competency engine is running and questions are loaded.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {assessmentTopics.map((topic) => {
            const isSelected = selectedAssessmentTopicId === topic.competency_id;

            return (
              <div
                key={topic.competency_id}
                className={`p-5 rounded-xl border transition-all bg-white flex flex-col justify-between ${
                  isSelected
                    ? 'border-blue-600 ring-1 ring-blue-500 shadow-md'
                    : 'border-slate-200 hover:border-slate-300 shadow-2xs'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span
                      className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                        topic.competency_type === 'functional'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-purple-100 text-purple-800'
                      }`}
                    >
                      {topic.competency_type}
                    </span>
                    <span className="text-[11px] font-mono text-slate-500 font-medium">
                      {topic.competency_id}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 leading-snug mb-1">
                    {topic.competency_name}
                  </h3>

                  <p className="text-xs text-slate-600 leading-relaxed line-clamp-2 mb-3">
                    {topic.description}
                  </p>

                  {/* Grounded Source Tag */}
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/80 text-[11px] text-slate-600 space-y-1">
                    <div className="flex items-center gap-1.5 font-semibold text-slate-800">
                      <BookOpen className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                      <span className="line-clamp-1">{topic.source_title}</span>
                    </div>
                    <div className="flex items-center justify-between text-slate-500 text-[10px]">
                      <span>Document: {topic.source_document_id}</span>
                      <span className="font-bold text-blue-700">
                        {topic.available_questions_count} Questions
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500 font-medium">
                    Diagnostic Quiz: 4 Items
                  </span>
                  <button
                    onClick={() => {
                      setSelectedAssessmentTopicId(topic.competency_id);
                      startDiagnosticAssessment(topic.competency_id);
                    }}
                    disabled={isAssessmentLoading}
                    className="px-4 py-2 text-xs font-bold text-white bg-blue-900 hover:bg-blue-800 rounded-lg shadow-2xs flex items-center gap-1.5 transition-all transform hover:scale-102"
                  >
                    <span>Start Assessment</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
