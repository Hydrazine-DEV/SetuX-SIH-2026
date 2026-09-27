import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  BrainCircuit, CheckCircle, AlertTriangle, ShieldCheck, 
  Activity, Clock, ChevronRight, FileText, BarChart2, ShieldAlert
} from 'lucide-react';
import { HealthScoreGauge, Spinner, CheckRow, DelayBadge } from '../components/ui';
import { DEMO_PROJECTS } from '../data/demoProjects';

// Simulated delay prediction queue
const DELAY_QUEUE = [
  { id: 'MH-PN-009', reason: 'Pothole density mismatch', delay: 25, risk: 'HIGH' },
  { id: 'MH-NK-001', reason: 'Bridge girder absent', delay: 50, risk: 'HIGH' },
  { id: 'MH-PN-011', reason: 'No active machinery detected', delay: 45, risk: 'MEDIUM' }
];

export default function AIVerification() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const projectId = searchParams.get('project') || 'MH-PN-001';
  
  const [analyzing, setAnalyzing] = useState(true);
  const [stage, setStage] = useState(0);

  const project = DEMO_PROJECTS.find(p => p.project_id === projectId) || DEMO_PROJECTS[0];

  useEffect(() => {
    if (!analyzing) return;
    const stages = [
      { t: 1000, s: 1 }, // Extracting Metadata
      { t: 2500, s: 2 }, // GPS & Temporal Check
      { t: 4500, s: 3 }, // Object Detection (CV)
      { t: 6500, s: 4 }, // Progress Estimation
      { t: 8000, s: 5 }, // Generating Report
    ];
    stages.forEach(({ t, s }) => setTimeout(() => setStage(s), t));
    setTimeout(() => setAnalyzing(false), 8500);
  }, [analyzing]);

  const PIPELINE_STAGES = [
    'Initializing Engine...',
    'Extracting EXIF Metadata...',
    'Geofence & Temporal Validation...',
    'Computer Vision Infrastructure Detection...',
    'AI Progress & Delay Estimation...',
    'Compiling Intelligence Report...'
  ];

  if (analyzing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-6 bg-gray-50 font-sans">
        <div className="w-24 h-24 relative mb-8">
          <div className="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-primary-900 rounded-full border-t-transparent animate-spin"></div>
          <div className="absolute inset-0 flex items-center justify-center text-primary-900">
            <BrainCircuit size={32} className="animate-pulse" />
          </div>
        </div>
        
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Engine Active</h2>
        <p className="text-gray-500 mb-8 max-w-sm text-center text-sm">
          Processing field evidence for {project.project_id}
        </p>

        <div className="w-full max-w-md space-y-3">
          {PIPELINE_STAGES.map((text, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 transition-colors duration-500
                ${stage > i ? 'bg-green-500 text-white' : stage === i ? 'bg-primary-900 text-white animate-pulse' : 'bg-gray-200 text-gray-400'}
              `}>
                {stage > i ? <CheckCircle size={12} /> : <div className="w-1.5 h-1.5 rounded-full bg-current" />}
              </div>
              <span className={`text-sm font-medium transition-colors duration-500
                ${stage >= i ? 'text-gray-900' : 'text-gray-400'}
              `}>
                {text}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto space-y-6 font-sans animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2 tracking-tight">
            <BrainCircuit className="text-primary-900" /> AI & Project Analytics
          </h1>
          <p className="text-sm text-gray-500 mt-1">Automated progress verification and delay prediction</p>
        </div>
        <div className="bg-amber-50 text-amber-800 text-xs font-bold px-3 py-1.5 rounded-lg border border-amber-200 flex items-center gap-1.5">
          <AlertTriangle size={14} /> AI-Assisted Estimate
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Analysis Column */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Progress Estimation Card */}
          <div className="card p-5">
            <h3 className="section-title mb-4 flex items-center gap-2">
              <BarChart2 size={18} /> AI Progress Estimation
            </h3>
            
            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 mb-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex-1">
                  <div className="text-xs text-gray-500 font-semibold uppercase mb-1">Contractor Reported</div>
                  <div className="text-3xl font-bold text-gray-900">{project.reported_progress}%</div>
                </div>
                <div className="hidden md:block w-px h-16 bg-gray-200"></div>
                <div className="flex-1">
                  <div className="text-xs text-primary-600 font-semibold uppercase mb-1 flex items-center gap-1">
                    <BrainCircuit size={12} /> AI Verified Progress
                  </div>
                  <div className="text-3xl font-bold text-primary-900">{project.ai_estimated_progress}%</div>
                </div>
                <div className="hidden md:block w-px h-16 bg-gray-200"></div>
                <div className="flex-1">
                  <div className="text-xs text-gray-500 font-semibold uppercase mb-1">Difference</div>
                  <div className={`text-2xl font-bold ${project.reported_progress - project.ai_estimated_progress > 10 ? 'text-red-600' : 'text-green-600'}`}>
                    {project.reported_progress - project.ai_estimated_progress}%
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <CheckRow label="Geotag Distance Check (Limit: 500m)" value="12.4m" status="ok" />
              <CheckRow label="EXIF Timestamp Authenticity" value="Verified Original" status="ok" />
              <CheckRow label="Image Manipulation / Deepfake" value="No Alterations" status="ok" />
              <CheckRow label="Progress Consistency" value={`Mismatch: ${project.reported_progress - project.ai_estimated_progress}% gap`} status={project.reported_progress - project.ai_estimated_progress > 10 ? 'error' : 'ok'} />
            </div>
          </div>

          {/* Infrastructure Detection */}
          <div className="card p-5">
            <h3 className="section-title mb-4">Detected Infrastructure</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {['Asphalt Layer', 'Road Markers', 'Sidewalk Base', 'Drainage Cover'].map((item, i) => (
                <div key={i} className="bg-white border border-gray-200 rounded-lg p-3 text-center shadow-sm">
                  <div className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center mx-auto mb-2">
                    <CheckCircle size={16} />
                  </div>
                  <div className="text-xs font-semibold text-gray-700">{item}</div>
                </div>
              ))}
            </div>
            
            <div className="mt-5 p-4 bg-gray-50 rounded-xl border border-gray-100">
              <div className="text-xs font-bold text-gray-900 uppercase mb-2">AI Diagnostic Summary</div>
              <p className="text-sm text-gray-600 leading-relaxed font-mono">
                Model detected {project.project_type} features with 94% confidence. However, volume estimation 
                indicates only {project.ai_estimated_progress}% completion vs {project.reported_progress}% claimed. 
                Top layer finishing is completely absent. Base course appears incomplete in sector 2.
              </p>
            </div>
          </div>

        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          
          {/* Delay Risk & Health */}
          <div className="card p-5 text-center">
            <h3 className="text-sm font-bold text-gray-900 uppercase mb-4 tracking-wider">Project Health Score</h3>
            <HealthScoreGauge score={project.health_score} />
            
            <div className="mt-6 pt-6 border-t border-gray-100">
               <h4 className="text-xs font-bold text-gray-900 uppercase mb-3 flex items-center justify-center gap-1">
                 <Clock size={14} className="text-saffron-500" /> AI Delay Prediction
               </h4>
               <div className="bg-saffron-50 border border-saffron-100 rounded-lg p-3 text-left">
                  <div className="text-saffron-900 text-sm font-semibold mb-1">Expected Delay: {project.delay_days} Days</div>
                  <div className="text-xs text-saffron-700">Based on current trajectory and historical contractor performance.</div>
               </div>
            </div>
          </div>

          {/* Action Panel */}
          <div className="card p-5 border-t-4 border-t-primary-900">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Recommendation</h3>
            {project.health_score < 50 ? (
              <div className="text-red-700 text-sm font-semibold bg-red-50 p-3 rounded-lg mb-4 border border-red-100 flex items-start gap-2">
                 <ShieldAlert size={16} className="mt-0.5 shrink-0" />
                 FIELD INSPECTION REQUIRED
              </div>
            ) : (
              <div className="text-green-700 text-sm font-semibold bg-green-50 p-3 rounded-lg mb-4 border border-green-100 flex items-start gap-2">
                 <CheckCircle size={16} className="mt-0.5 shrink-0" />
                 CONTINUE MONITORING
              </div>
            )}
            
            <button 
              className="w-full btn-primary py-2.5 text-sm flex items-center justify-center gap-2"
              onClick={() => navigate(`/projects/${project.project_id}`)}
            >
              Update Project Profile <ChevronRight size={16} />
            </button>
          </div>

          {/* Priority Queue (Global context) */}
          <div className="card p-5">
             <h3 className="text-sm font-bold text-gray-900 uppercase mb-3 flex items-center gap-1">
               <Activity size={14} className="text-red-600" /> AI Priority Queue
             </h3>
             <div className="space-y-3">
               {DELAY_QUEUE.map(q => (
                 <div key={q.id} className="p-2 bg-gray-50 rounded border border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors" onClick={() => navigate(`/projects/${q.id}`)}>
                    <div className="flex justify-between items-center mb-1">
                       <span className="text-xs font-bold text-primary-900">{q.id}</span>
                       <DelayBadge days={q.delay} />
                    </div>
                    <div className="text-[10px] text-gray-500 truncate">{q.reason}</div>
                 </div>
               ))}
             </div>
             <button className="w-full mt-3 text-xs font-semibold text-primary-900 hover:underline">View All At-Risk</button>
          </div>

        </div>
      </div>
    </div>
  );
}
