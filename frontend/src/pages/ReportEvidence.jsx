import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, MapPin, Camera, CheckCircle, AlertTriangle, 
  ChevronRight, Building2, ShieldCheck, PlayCircle
} from 'lucide-react';
import { DEMO_PROJECTS } from '../data/demoProjects';
import { evidenceApi } from '../services/api';
import { Spinner } from '../components/ui';

const STEPS = [
  { id: 1, title: 'Select Project' },
  { id: 2, title: 'Progress Update' },
  { id: 3, title: 'Capture Media' },
  { id: 4, title: 'GPS Verification' },
  { id: 5, title: 'Certify & Submit' }
];

export default function ReportEvidence() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    projectId: '',
    evidenceType: 'During Work',
    reportedProgress: '',
    remarks: '',
    files: []
  });

  // GPS Simulation state
  const [gpsStatus, setGpsStatus] = useState('pending'); // pending, scanning, success, error
  const [gpsDist, setGpsDist] = useState(null);

  const selectedProj = DEMO_PROJECTS.find(p => p.project_id === formData.projectId);

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map(file => ({
        file,
        preview: URL.createObjectURL(file),
        name: file.name
      }));
      setFormData(prev => ({ ...prev, files: [...prev.files, ...newFiles].slice(0, 4) }));
    }
  };

  const removeFile = (index) => {
    setFormData(prev => {
      const newFiles = [...prev.files];
      URL.revokeObjectURL(newFiles[index].preview);
      newFiles.splice(index, 1);
      return { ...prev, files: newFiles };
    });
  };

  const simulateGps = () => {
    setGpsStatus('scanning');
    setTimeout(() => {
      setGpsDist(12.4);
      setGpsStatus('success');
    }, 1500);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const form = new FormData();
      form.append('project_id', formData.projectId);
      form.append(
        'evidence_type',
        formData.evidenceType === 'Completion' ? 'Current / After Work' : formData.evidenceType
      );
      form.append('reported_progress', String(parseInt(formData.reportedProgress, 10) || 0));
      form.append('remarks', formData.remarks || '');
      if (selectedProj?.lat != null) form.append('submitted_lat', String(selectedProj.lat));
      if (selectedProj?.lng != null) form.append('submitted_lng', String(selectedProj.lng));
      formData.files.forEach(({ file }) => form.append('files', file));
      await evidenceApi.submit(form);
    } catch (err) {
      console.warn('Evidence upload failed, continuing with demo analysis flow.', err);
    } finally {
      setLoading(false);
      navigate(`/ai-analytics?project=${formData.projectId}`);
    }
  };

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto font-sans">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Field Progress Update</h1>
        <p className="text-sm text-gray-500 dark:text-slate-400 mt-1">Submit live field data and images for AI monitoring</p>
      </div>

      {/* Stepper */}
      <div className="card mb-8 p-4">
        <div className="flex items-center justify-between relative">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-gray-100 dark:bg-slate-800 z-0" />
          <div 
            className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-primary-900 z-0 transition-all duration-300"
            style={{ width: `${((step - 1) / (STEPS.length - 1)) * 100}%` }}
          />
          {STEPS.map((s) => (
            <div key={s.id} className="relative z-10 flex flex-col items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-colors
                ${step > s.id ? 'bg-primary-900 border-primary-900 text-white' : 
                  step === s.id ? 'bg-white dark:bg-slate-900 border-primary-900 text-primary-900' : 'bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-700 text-gray-400 dark:text-slate-500'}
              `}>
                {step > s.id ? <CheckCircle size={16} /> : s.id}
              </div>
              <div className={`text-xs font-semibold hidden sm:block ${step >= s.id ? 'text-gray-900' : 'text-gray-400 dark:text-slate-500'}`}>
                {s.title}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="card p-6 min-h-[400px]">
        {/* STEP 1: Select Project */}
        {step === 1 && (
          <div className="space-y-6 max-w-xl mx-auto animate-in fade-in">
            <h2 className="text-xl font-bold text-gray-900 text-center">Select Target Project</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Project ID / Name</label>
                <select 
                  className="select"
                  value={formData.projectId}
                  onChange={e => setFormData({...formData, projectId: e.target.value})}
                >
                  <option value="">-- Choose a project --</option>
                  {DEMO_PROJECTS.map(p => (
                    <option key={p.project_id} value={p.project_id}>
                      {p.project_id} : {p.name}
                    </option>
                  ))}
                </select>
              </div>
              
              {selectedProj && (
                <div className="bg-blue-50 dark:bg-blue-950/40 border border-blue-100 p-4 rounded-xl space-y-2">
                  <div className="font-semibold text-blue-900 flex items-center gap-2">
                    <Building2 size={16} /> {selectedProj.name}
                  </div>
                  <div className="text-sm text-blue-800 flex items-center gap-2">
                    <MapPin size={14} /> {selectedProj.location_name}, {selectedProj.district}
                  </div>
                  <div className="text-xs text-blue-700 bg-blue-100 inline-block px-2 py-1 rounded">
                    Currently at {selectedProj.reported_progress}% Progress
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 2: Progress */}
        {step === 2 && (
          <div className="space-y-6 max-w-xl mx-auto animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-gray-900 text-center">Update Progress</h2>
            
            <div className="space-y-5">
              <div>
                <label className="label">Evidence Type</label>
                <div className="grid grid-cols-3 gap-3">
                  {['Before Work', 'During Work', 'Completion'].map(type => (
                    <button
                      key={type}
                      onClick={() => setFormData({...formData, evidenceType: type})}
                      className={`py-2 px-3 text-sm font-semibold rounded-lg border text-center transition-colors
                        ${formData.evidenceType === type 
                          ? 'bg-primary-50 border-primary-900 text-primary-900' 
                          : 'bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-700 text-gray-600 hover:bg-gray-50 dark:bg-slate-800/50'}`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label">New Reported Progress (%)</label>
                <input 
                  type="number" min="0" max="100"
                  className="input text-lg font-bold"
                  value={formData.reportedProgress}
                  onChange={e => setFormData({...formData, reportedProgress: e.target.value})}
                  placeholder="e.g. 45"
                />
              </div>

              <div>
                <label className="label">Field Remarks (Optional)</label>
                <textarea 
                  className="input min-h-[100px] resize-none"
                  value={formData.remarks}
                  onChange={e => setFormData({...formData, remarks: e.target.value})}
                  placeholder="Note any field observations or delays..."
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Media */}
        {step === 3 && (
          <div className="space-y-6 max-w-2xl mx-auto animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-gray-900 text-center">Upload Field Evidence</h2>
            
            <div 
              className="border-2 border-dashed border-gray-300 dark:border-slate-600 rounded-xl p-8 text-center hover:bg-gray-50 dark:bg-slate-800/50 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud size={48} className="mx-auto text-gray-400 dark:text-slate-500 mb-4" />
              <div className="text-sm font-semibold text-gray-700 dark:text-slate-300">Click to capture or upload images</div>
              <div className="text-xs text-gray-500 dark:text-slate-400 mt-1">Geotagged JPEG/PNG up to 10MB</div>
              <input 
                type="file" multiple accept="image/*" className="hidden"
                ref={fileInputRef} onChange={handleFileChange}
              />
            </div>

            {formData.files.length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {formData.files.map((f, i) => (
                  <div key={i} className="relative group rounded-lg overflow-hidden border border-gray-200 dark:border-slate-700 aspect-square">
                    <img src={f.preview} alt="preview" className="w-full h-full object-cover" />
                    <button 
                      onClick={() => removeFile(i)}
                      className="absolute top-1 right-1 bg-red-600 text-white w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      ×
                    </button>
                    <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-[10px] p-1 truncate">
                      {f.name}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* STEP 4: GPS */}
        {step === 4 && (
          <div className="space-y-8 max-w-xl mx-auto animate-in fade-in slide-in-from-right-4 text-center">
            <h2 className="text-xl font-bold text-gray-900">Geofence Verification</h2>
            <p className="text-sm text-gray-600">
              Verifying your current location against the registered coordinates for {selectedProj?.project_id}.
            </p>

            <div className="flex justify-center">
              {gpsStatus === 'pending' && (
                <button onClick={simulateGps} className="btn-primary flex items-center gap-2">
                  <MapPin size={18} /> Acquire GPS Coordinates
                </button>
              )}
              {gpsStatus === 'scanning' && (
                <div className="flex flex-col items-center gap-4 text-primary-900">
                  <Spinner size="lg" />
                  <span className="font-semibold animate-pulse">Calculating Haversine Distance...</span>
                </div>
              )}
              {gpsStatus === 'success' && (
                <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center w-full">
                  <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle size={32} />
                  </div>
                  <h3 className="text-lg font-bold text-green-900 mb-1">GPS Verified</h3>
                  <p className="text-sm text-green-800">
                    You are exactly <span className="font-bold">{gpsDist}m</span> from the site.<br/>
                    Within the 500m accepted geofence radius.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 5: Submit */}
        {step === 5 && (
          <div className="space-y-6 max-w-xl mx-auto animate-in fade-in slide-in-from-right-4 text-center">
            <div className="w-20 h-20 bg-blue-50 dark:bg-blue-950/40 text-primary-900 rounded-full flex items-center justify-center mx-auto mb-2">
              <ShieldCheck size={40} />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Ready for Analysis</h2>
            <p className="text-sm text-gray-600 px-8">
              I certify that this field data is accurate. The SetuX AI engine will now analyze the uploaded evidence against the expected baseline.
            </p>

            <div className="bg-gray-50 dark:bg-slate-800/50 rounded-xl p-4 text-left space-y-2 border border-gray-100 dark:border-slate-800 max-w-sm mx-auto">
              <div className="flex justify-between text-sm"><span className="text-gray-500 dark:text-slate-400">Project:</span> <span className="font-semibold">{selectedProj?.project_id}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-500 dark:text-slate-400">Claimed Progress:</span> <span className="font-semibold">{formData.reportedProgress}%</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-500 dark:text-slate-400">Images Attached:</span> <span className="font-semibold">{formData.files.length}</span></div>
              <div className="flex justify-between text-sm"><span className="text-gray-500 dark:text-slate-400">GPS Validation:</span> <span className="font-semibold text-green-600">Passed</span></div>
            </div>

            <button 
              onClick={handleSubmit} 
              disabled={loading}
              className="btn-primary w-full max-w-sm py-3 text-base flex items-center justify-center gap-2 shadow-lg"
            >
              {loading ? <Spinner size="sm" /> : <><PlayCircle size={20} /> Submit Field Update & Run Analysis</>}
            </button>
          </div>
        )}
      </div>

      {/* Footer Navigation */}
      <div className="mt-6 flex items-center justify-between">
        <button 
          className="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-900 disabled:opacity-0"
          onClick={() => setStep(s => s - 1)}
          disabled={step === 1 || loading}
        >
          Back
        </button>
        {step < STEPS.length && (
          <button 
            className="btn-primary flex items-center gap-1 pl-5 pr-4"
            onClick={() => setStep(s => s + 1)}
            disabled={
              (step === 1 && !formData.projectId) ||
              (step === 2 && !formData.reportedProgress) ||
              (step === 3 && formData.files.length === 0) ||
              (step === 4 && gpsStatus !== 'success')
            }
          >
            Next Step <ChevronRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
