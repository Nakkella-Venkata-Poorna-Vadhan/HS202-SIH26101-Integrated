import React, { useState, useEffect, useRef } from 'react';
import {
  Upload,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Sparkles,
  BookOpen,
  Send,
  Eye,
  Edit3,
  Layers,
  ArrowRight,
  ShieldCheck,
  RotateCw,
  Cpu,
  FileCheck,
  Hash
} from 'lucide-react';
import { api } from '../../services/api';
import { UploadedDocument, DraftQuestion, ProviderStatus } from '../../types';
import { useApp } from '../../context/AppContext';

export const TrainerStudio: React.FC = () => {
  const { navigateTo } = useApp();

  // State
  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [drafts, setDrafts] = useState<DraftQuestion[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [generating, setGenerating] = useState<boolean>(false);
  const [publishing, setPublishing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Upload Form State
  const [uploadTitle, setUploadTitle] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Generation Modal / Panel State
  const [selectedDocId, setSelectedDocId] = useState<string>('');
  const [genCount, setGenCount] = useState<number>(2);
  const [genDifficulty, setGenDifficulty] = useState<'foundation' | 'operational' | 'advanced'>('operational');
  const [genCompetencyId, setGenCompetencyId] = useState<string>('KCM-001');

  // Edit Modal State
  const [editingDraft, setEditingDraft] = useState<DraftQuestion | null>(null);
  const [editQuestionText, setEditQuestionText] = useState<string>('');
  const [editExplanation, setEditExplanation] = useState<string>('');

  // Initial Load
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const [statusRes, docsRes, draftsRes] = await Promise.all([
        api.getProviderStatus().catch(() => null),
        api.getUploadedDocuments().catch(() => []),
        api.getDraftQuestions().catch(() => []),
      ]);
      setProviderStatus(statusRes);
      setDocuments(docsRes);
      setDrafts(draftsRes);
      if (docsRes.length > 0 && !selectedDocId) {
        setSelectedDocId(docsRes[0].document_id);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load trainer studio data.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage('Please select a PDF or TXT file to upload.');
      return;
    }

    setUploading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const result = await api.uploadMaterial(selectedFile, uploadTitle || selectedFile.name);
      setSuccessMessage(`Document '${result.filename}' (${result.page_count} page(s), ${result.character_count.toLocaleString()} chars) successfully processed.`);
      setSelectedFile(null);
      setUploadTitle('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      await loadAllData();
      setSelectedDocId(result.document_id);
    } catch (err: any) {
      setErrorMessage(err.message || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateQuestions = async () => {
    if (!selectedDocId) {
      setErrorMessage('Please select an uploaded document.');
      return;
    }

    setGenerating(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const result = await api.generateQuestions({
        documentId: selectedDocId,
        questionCount: genCount,
        difficulty: genDifficulty,
        competencyId: genCompetencyId,
      });

      setSuccessMessage(
        `Generated ${result.generated_count} source-grounded question(s). ${result.verification_status}`
      );
      if (result.rejections && result.rejections.length > 0) {
        console.warn('Rejections during generation:', result.rejections);
      }
      await loadAllData();
      setStatusFilter('draft');
    } catch (err: any) {
      setErrorMessage(err.message || 'Question generation failed.');
    } finally {
      setGenerating(false);
    }
  };

  const handleReviewAction = async (
    questionId: string,
    action: 'approve' | 'reject',
    reason?: string
  ) => {
    try {
      await api.reviewDraftQuestion(questionId, action, {
        reviewedBy: 'trainer_admin',
        rejectionReason: reason,
      });
      await loadAllData();
    } catch (err: any) {
      setErrorMessage(err.message || `Failed to ${action} question.`);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingDraft) return;
    try {
      await api.reviewDraftQuestion(editingDraft.question_id, 'edit', {
        reviewedBy: 'trainer_admin',
        editedQuestion: {
          question_text: editQuestionText,
          explanation: editExplanation,
        },
      });
      setEditingDraft(null);
      await loadAllData();
      setSuccessMessage(`Question ${editingDraft.question_id} updated and marked approved.`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to edit question.');
    }
  };

  const handlePublishApproved = async () => {
    setPublishing(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const result = await api.publishApprovedQuestions({
        publishedBy: 'trainer_lead',
      });
      setSuccessMessage(result.message);
      await loadAllData();
      setStatusFilter('published');
    } catch (err: any) {
      setErrorMessage(err.message || 'Publication failed.');
    } finally {
      setPublishing(false);
    }
  };

  // Filtered drafts
  const filteredDrafts = drafts.filter((d) => {
    if (statusFilter === 'all') return true;
    return d.status === statusFilter;
  });

  const approvedCount = drafts.filter((d) => d.status === 'approved').length;
  const draftCount = drafts.filter((d) => d.status === 'draft').length;
  const publishedCount = drafts.filter((d) => d.status === 'published').length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-md border border-slate-800">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider bg-amber-400 text-slate-950 px-2.5 py-0.5 rounded-full">
                Trainer Studio
              </span>
              <span className="text-xs text-slate-300 font-medium">
                Stage 4.7 • Dynamic Source-Grounded Pipeline
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Learning Material Ingestion & AI Question Generation
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Upload official learning materials (PDF/TXT), extract verified text chunks with page-level provenance, generate MCQs with strict source grounding, and review drafts before publishing into live diagnostic assessments.
            </p>
          </div>

          {/* Provider Status Pill */}
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl p-4 min-w-[240px]">
            <div className="flex items-center justify-between gap-2 mb-2">
              <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                Generator Mode
              </span>
              <span
                className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                  providerStatus?.configured
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                }`}
              >
                {providerStatus?.mode === 'openai_compatible' ? 'LLM Provider Active' : 'Deterministic Heuristic'}
              </span>
            </div>
            <div className="text-xs font-mono text-slate-200 truncate">
              Model: {providerStatus?.model || 'deterministic_source_extractor'}
            </div>
            <div className="text-[11px] text-slate-400 mt-1 line-clamp-2">
              {providerStatus?.demonstration_notice || 'Grounded extraction directly from authentic document chunks.'}
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {errorMessage && (
        <div className="bg-red-50 border border-red-200 text-red-900 rounded-xl p-4 flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <XCircle className="w-5 h-5 text-red-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-xs font-bold text-red-700 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {successMessage && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-xl p-4 flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-xs font-bold text-emerald-700 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Two-Column Grid: Upload & Generator Control */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload New Material (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Upload className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-bold text-slate-900">Upload Learning Material</h3>
            </div>
            <p className="text-xs text-slate-600 mb-4 leading-relaxed">
              Upload official training publications, circulars, or course notes in PDF or TXT format (up to 20 MB). Cryptographic SHA-256 hash and 1-based page numbers are preserved.
            </p>

            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Publication Title
                </label>
                <input
                  type="text"
                  placeholder="e.g. NSSTA Advance Training Calendar or National Accounts Note"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Select File (.pdf, .txt)
                </label>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".pdf,.txt"
                  onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                />
                {selectedFile && (
                  <p className="text-[11px] text-slate-500 mt-1">
                    Selected: {selectedFile.name} ({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
                  </p>
                )}
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-[11px] text-slate-600 space-y-1">
                <div className="flex items-center gap-1.5 font-semibold text-slate-800">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>Security & Untrusted Input Protection:</span>
                </div>
                <p>
                  Documents are parsed as static text content only. Embedded instructions or prompt injection attempts are neutralized before chunk analysis.
                </p>
              </div>

              <button
                type="submit"
                disabled={uploading || !selectedFile}
                className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 shadow-2xs"
              >
                {uploading ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    <span>Extracting & Hashing Material...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    <span>Ingest Learning Material</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Generation Controls (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <h3 className="text-lg font-bold text-slate-900">Generate Source-Grounded MCQs</h3>
              </div>
              <button
                onClick={loadAllData}
                disabled={loading}
                className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1"
                title="Refresh inventory"
              >
                <RotateCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
            <p className="text-xs text-slate-600 mb-4 leading-relaxed">
              Synthesize 4-option multiple-choice questions grounded strictly in the chosen document. The verifier enforces schema validity, verbatim page excerpt citations, and duplicate rejection.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
              {/* Document Select */}
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Source Material Document
                </label>
                {documents.length === 0 ? (
                  <div className="text-xs text-amber-800 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
                    No documents uploaded yet. Ingest a PDF or TXT on the left to begin.
                  </div>
                ) : (
                  <select
                    value={selectedDocId}
                    onChange={(e) => setSelectedDocId(e.target.value)}
                    className="w-full px-3.5 py-2 text-xs font-medium border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  >
                    {documents.map((doc) => (
                      <option key={doc.document_id} value={doc.document_id}>
                        {doc.title || doc.filename} ({doc.page_count} pg, {doc.file_type.toUpperCase()}) — {doc.document_id}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Question Count */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Questions to Generate
                </label>
                <select
                  value={genCount}
                  onChange={(e) => setGenCount(Number(e.target.value))}
                  className="w-full px-3 py-2 text-xs font-medium border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value={1}>1 Question</option>
                  <option value={2}>2 Questions</option>
                  <option value={3}>3 Questions</option>
                  <option value={5}>5 Questions</option>
                </select>
              </div>

              {/* Difficulty */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Difficulty Level
                </label>
                <select
                  value={genDifficulty}
                  onChange={(e) => setGenDifficulty(e.target.value as any)}
                  className="w-full px-3 py-2 text-xs font-medium border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value="foundation">Foundation (Recall & Basics)</option>
                  <option value="operational">Operational (Standard Procedures)</option>
                  <option value="advanced">Advanced (Analytical & Diagnostic)</option>
                </select>
              </div>

              {/* Target Competency */}
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Target Competency Association
                </label>
                <select
                  value={genCompetencyId}
                  onChange={(e) => setGenCompetencyId(e.target.value)}
                  className="w-full px-3 py-2 text-xs font-medium border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value="KCM-001">KCM-001 • Official Statistics Methodology</option>
                  <option value="KCM-002">KCM-002 • Sample Survey Design and Estimation</option>
                  <option value="KCM-003">KCM-003 • National Accounts Compilation</option>
                  <option value="KCM-004">KCM-004 • Price Statistics and Index Compilation</option>
                  <option value="KCM-005">KCM-005 • Data Quality Assurance and Auditing</option>
                  <option value="KCM-UNRESOLVED">Mark as Unresolved Competency (Manual Mapping)</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerateQuestions}
              disabled={generating || documents.length === 0}
              className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-amber-300 font-extrabold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 shadow-2xs"
            >
              {generating ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin text-amber-300" />
                  <span>Synthesizing & Verifying Drafts...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Generate Grounded Drafts</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Uploaded Documents Inventory */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Uploaded Document Provenance Register</h3>
          </div>
          <span className="text-xs text-slate-500 font-semibold">
            {documents.length} Document(s) Registered
          </span>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            No training documents registered yet. Upload a document above to begin question generation.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3 font-bold">Document ID / Title</th>
                  <th className="py-2.5 px-3 font-bold">Type</th>
                  <th className="py-2.5 px-3 font-bold">Pages</th>
                  <th className="py-2.5 px-3 font-bold">Characters</th>
                  <th className="py-2.5 px-3 font-bold">Extraction Status</th>
                  <th className="py-2.5 px-3 font-bold">SHA-256 Checksum</th>
                  <th className="py-2.5 px-3 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {documents.map((doc) => (
                  <tr key={doc.document_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-bold text-slate-900">{doc.title}</div>
                      <div className="font-mono text-[11px] text-slate-500">{doc.document_id}</div>
                    </td>
                    <td className="py-3 px-3 uppercase font-semibold text-slate-600">
                      {doc.file_type}
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-800">
                      {doc.page_count}
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-800">
                      {doc.character_count.toLocaleString()}
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                          doc.extraction_status === 'extracted'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : doc.extraction_status === 'ocr_required'
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-red-50 text-red-700 border border-red-200'
                        }`}
                      >
                        {doc.extraction_status === 'extracted' && <CheckCircle2 className="w-3 h-3" />}
                        {doc.extraction_status === 'ocr_required' && <AlertTriangle className="w-3 h-3" />}
                        {doc.extraction_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-[11px] text-slate-500">
                      {doc.sha256 ? `${doc.sha256.substring(0, 10)}...` : 'N/A'}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => {
                          setSelectedDocId(doc.document_id);
                          window.scrollTo({ top: 300, behavior: 'smooth' });
                        }}
                        className="px-2.5 py-1 text-[11px] font-bold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded border border-indigo-200"
                      >
                        Select for Generation
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review Queue & Publication Control */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-bold text-slate-900">Trainer Question Review Queue</h3>
            </div>
            <p className="text-xs text-slate-600 mt-1">
              Inspect generated options, correct answers, and verbatim excerpts. Unapproved drafts never enter diagnostic quizzes.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Status Filter Tabs */}
            <div className="flex items-center bg-slate-100 p-1 rounded-lg text-xs font-semibold">
              <button
                onClick={() => setStatusFilter('all')}
                className={`px-3 py-1 rounded-md transition-all ${
                  statusFilter === 'all' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                All ({drafts.length})
              </button>
              <button
                onClick={() => setStatusFilter('draft')}
                className={`px-3 py-1 rounded-md transition-all ${
                  statusFilter === 'draft' ? 'bg-white text-amber-800 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Pending ({draftCount})
              </button>
              <button
                onClick={() => setStatusFilter('approved')}
                className={`px-3 py-1 rounded-md transition-all ${
                  statusFilter === 'approved' ? 'bg-white text-emerald-800 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Approved ({approvedCount})
              </button>
              <button
                onClick={() => setStatusFilter('published')}
                className={`px-3 py-1 rounded-md transition-all ${
                  statusFilter === 'published' ? 'bg-white text-blue-800 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Published ({publishedCount})
              </button>
            </div>

            {/* Publish Action Button */}
            <button
              onClick={handlePublishApproved}
              disabled={publishing || approvedCount === 0}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-1.5 shadow-2xs"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Publish Approved ({approvedCount}) to Live Assessment</span>
            </button>
          </div>
        </div>

        {/* Drafts Cards List */}
        {filteredDrafts.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-500">
            No draft questions match the selected filter ('{statusFilter}').
          </div>
        ) : (
          <div className="space-y-4">
            {filteredDrafts.map((draft, idx) => (
              <div
                key={draft.question_id}
                className={`border rounded-xl p-5 transition-all ${
                  draft.status === 'approved'
                    ? 'border-emerald-200 bg-emerald-50/20'
                    : draft.status === 'published'
                    ? 'border-blue-200 bg-blue-50/20'
                    : draft.status === 'rejected'
                    ? 'border-red-200 bg-red-50/20 opacity-70'
                    : 'border-slate-200 bg-white'
                }`}
              >
                {/* Top Badges */}
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-600">
                      #{idx + 1} • {draft.question_id}
                    </span>
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-800 border border-indigo-200">
                      {draft.competency_name} ({draft.competency_id})
                    </span>
                    <span className="text-[11px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {draft.difficulty}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                        draft.status === 'published'
                          ? 'bg-blue-100 text-blue-900 border border-blue-300'
                          : draft.status === 'approved'
                          ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                          : draft.status === 'rejected'
                          ? 'bg-red-100 text-red-900 border border-red-300'
                          : 'bg-amber-100 text-amber-900 border border-amber-300'
                      }`}
                    >
                      Status: {draft.status.toUpperCase()}
                    </span>
                    <span className="text-[11px] text-slate-500">
                      Page {draft.source_page}
                    </span>
                  </div>
                </div>

                {/* Question Text */}
                <h4 className="text-sm font-extrabold text-slate-900 mb-3 leading-snug">
                  {draft.question_text}
                </h4>

                {/* Options Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
                  {(['A', 'B', 'C', 'D'] as const).map((key) => {
                    const isCorrect = draft.correct_answer === key;
                    return (
                      <div
                        key={key}
                        className={`p-2.5 rounded-lg text-xs flex items-start gap-2 border ${
                          isCorrect
                            ? 'bg-emerald-50 border-emerald-300 text-emerald-950 font-semibold'
                            : 'bg-slate-50 border-slate-200 text-slate-700'
                        }`}
                      >
                        <span
                          className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                            isCorrect ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {key}
                        </span>
                        <div className="flex-1">
                          <span>{draft.options[key]}</span>
                          {isCorrect && (
                            <span className="ml-1.5 text-[10px] font-extrabold text-emerald-700 uppercase">
                              (Correct Answer)
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Source Excerpt & Explanation Box */}
                <div className="bg-amber-50/60 border-l-4 border-amber-400 p-3 rounded-r-lg text-xs space-y-1 mb-4">
                  <div className="flex items-center gap-1.5 font-bold text-amber-950">
                    <FileText className="w-3.5 h-3.5 text-amber-700" />
                    <span>Verbatim Source Excerpt (Page {draft.source_page}):</span>
                  </div>
                  <p className="italic text-slate-800">
                    "{draft.source_excerpt}"
                  </p>
                  <p className="text-[11px] text-slate-600 pt-1">
                    <span className="font-semibold text-slate-700">Rationale:</span> {draft.explanation}
                  </p>
                </div>

                {/* Reviewer Action Buttons */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
                  <div className="text-[11px] text-slate-500">
                    {draft.reviewed_by && (
                      <span>Reviewed by <span className="font-semibold">{draft.reviewed_by}</span></span>
                    )}
                    {draft.rejection_reason && (
                      <span className="text-red-700 ml-2">Reason: {draft.rejection_reason}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {draft.status !== 'approved' && draft.status !== 'published' && (
                      <button
                        onClick={() => handleReviewAction(draft.question_id, 'approve')}
                        className="px-3 py-1.5 text-xs font-bold text-emerald-800 bg-emerald-100 hover:bg-emerald-200 rounded-md transition-colors flex items-center gap-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                        <span>Approve</span>
                      </button>
                    )}

                    {draft.status !== 'rejected' && draft.status !== 'published' && (
                      <button
                        onClick={() => {
                          const reason = prompt('Enter rejection reason for this draft:');
                          if (reason !== null) {
                            handleReviewAction(draft.question_id, 'reject', reason || 'Rejected by trainer.');
                          }
                        }}
                        className="px-3 py-1.5 text-xs font-bold text-red-800 bg-red-100 hover:bg-red-200 rounded-md transition-colors flex items-center gap-1"
                      >
                        <XCircle className="w-3.5 h-3.5 text-red-700" />
                        <span>Reject</span>
                      </button>
                    )}

                    {draft.status !== 'published' && (
                      <button
                        onClick={() => {
                          setEditingDraft(draft);
                          setEditQuestionText(draft.question_text);
                          setEditExplanation(draft.explanation);
                        }}
                        className="px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors flex items-center gap-1"
                      >
                        <Edit3 className="w-3.5 h-3.5 text-slate-600" />
                        <span>Edit</span>
                      </button>
                    )}

                    {draft.status === 'published' && (
                      <button
                        onClick={() => navigateTo('quiz')}
                        className="px-3 py-1.5 text-xs font-extrabold text-blue-900 bg-blue-100 hover:bg-blue-200 rounded-md transition-colors flex items-center gap-1"
                      >
                        <Send className="w-3.5 h-3.5 text-blue-700" />
                        <span>Test in Diagnostic Assessment</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Edit Modal */}
      {editingDraft && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-indigo-600" />
                <span>Edit Question: {editingDraft.question_id}</span>
              </h3>
              <button
                onClick={() => setEditingDraft(null)}
                className="text-slate-400 hover:text-slate-600 font-bold"
              >
                ✕
              </button>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Question Text
              </label>
              <textarea
                rows={3}
                value={editQuestionText}
                onChange={(e) => setEditQuestionText(e.target.value)}
                className="w-full text-xs p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Explanation & Supporting Rationale
              </label>
              <textarea
                rows={3}
                value={editExplanation}
                onChange={(e) => setEditExplanation(e.target.value)}
                className="w-full text-xs p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div className="bg-amber-50 p-3 rounded-lg text-xs text-amber-900">
              <span className="font-semibold">Note:</span> Saving edits will mark this question as <span className="font-bold text-emerald-800">Approved</span>, ready for publication to live assessments.
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setEditingDraft(null)}
                className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-2xs"
              >
                Save & Approve
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
