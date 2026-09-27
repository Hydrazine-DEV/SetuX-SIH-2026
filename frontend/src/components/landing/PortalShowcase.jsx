import { Link } from 'react-router-dom';
import { ShieldCheck, Eye, CheckCircle2, ArrowRight, Building2, Users } from 'lucide-react';

export default function PortalShowcase() {
  return (
    <section className="py-20 bg-[#F5F7FA]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-2 bg-[#EAF3FF] text-[#1769D2] px-3.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
            <span>Platform Entry Portals</span>
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-[#14213D] tracking-tight">
            Tailored Gateways for Officers & Citizens
          </h2>
          <p className="text-base text-[#64748B]">
            Dedicated interfaces engineered for specialized decision support, executive project oversight, and open public transparency.
          </p>
        </div>

        {/* Dual Portal Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10">
          
          {/* Portal 1: Department Officer Portal */}
          <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
            <div>
              {/* Image Frame */}
              <div className="relative h-64 overflow-hidden bg-gray-100">
                <img
                  src="/assets/sections/officer-portal.jpg.png"
                  alt="Department Officer Portal"
                  className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0B2A4A]/80 via-transparent to-transparent"></div>
                <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-white">
                  <div className="flex items-center space-x-2 bg-[#0B2A4A]/80 backdrop-blur-md px-3 py-1 rounded-lg border border-white/20">
                    <Building2 className="w-4 h-4 text-blue-400" />
                    <span className="text-xs font-semibold">Executive & Field Officers</span>
                  </div>
                  <span className="text-xs font-medium bg-[#1769D2] px-2.5 py-0.5 rounded text-white">Restricted Access</span>
                </div>
              </div>

              {/* Body Content */}
              <div className="p-6 sm:p-8 space-y-5">
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-[#14213D] group-hover:text-[#1769D2] transition-colors">
                    Department Officer Portal
                  </h3>
                  <p className="text-sm text-[#64748B] leading-relaxed">
                    Authorized workspace for executive engineers, monitoring officers, and department leadership to manage project lifecycles, review AI verification outputs, evaluate cost overrun risks, and generate audit reports.
                  </p>
                </div>

                {/* Key Capabilities List */}
                <div className="space-y-2.5 pt-2">
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-[#1769D2] flex-shrink-0 mt-0.5" />
                    <span>Real-time physical & financial progress update tracking</span>
                  </div>
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-[#1769D2] flex-shrink-0 mt-0.5" />
                    <span>AI-assisted visual evidence verification & anomaly scoring</span>
                  </div>
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-[#1769D2] flex-shrink-0 mt-0.5" />
                    <span>Predictive Machine Learning models for cost & schedule overruns</span>
                  </div>
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-[#1769D2] flex-shrink-0 mt-0.5" />
                    <span>Automated early warning notifications & executive PDF downloads</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Action CTA */}
            <div className="px-6 pb-6 sm:px-8 sm:pb-8 pt-4 border-t border-gray-100">
              <Link
                to="/officer-login"
                className="w-full inline-flex items-center justify-center space-x-2 bg-[#1769D2] hover:bg-[#1459b8] text-white py-3 px-5 rounded-xl font-semibold text-sm transition-all shadow-sm"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Officer Portal Login</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>

          {/* Portal 2: Public Citizen Transparency Portal */}
          <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
            <div>
              {/* Image Frame */}
              <div className="relative h-64 overflow-hidden bg-gray-100">
                <img
                  src="/assets/sections/citizen-portal.jpg.png"
                  alt="Public Citizen Transparency Portal"
                  className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0B2A4A]/80 via-transparent to-transparent"></div>
                <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-white">
                  <div className="flex items-center space-x-2 bg-[#0B2A4A]/80 backdrop-blur-md px-3 py-1 rounded-lg border border-white/20">
                    <Users className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-semibold">Public Access Gateway</span>
                  </div>
                  <span className="text-xs font-medium bg-emerald-600 px-2.5 py-0.5 rounded text-white">Open Access</span>
                </div>
              </div>

              {/* Body Content */}
              <div className="p-6 sm:p-8 space-y-5">
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-[#14213D] group-hover:text-[#1769D2] transition-colors">
                    Public Citizen Transparency Portal
                  </h3>
                  <p className="text-sm text-[#64748B] leading-relaxed">
                    Public transparency hub allowing citizens, researchers, and community members to inspect active infrastructure projects, track district-level expenditure, and verify development milestones.
                  </p>
                </div>

                {/* Key Capabilities List */}
                <div className="space-y-2.5 pt-2">
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>Open public directory of state infrastructure developments</span>
                  </div>
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>Geospatial map exploration by district, sector, and status</span>
                  </div>
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>Transparent milestone completion records and progress updates</span>
                  </div>
                  <div className="flex items-start space-x-2.5 text-xs text-[#14213D] font-medium">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>Verified public information fostering civic trust and accountability</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Action CTA */}
            <div className="px-6 pb-6 sm:px-8 sm:pb-8 pt-4 border-t border-gray-100">
              <Link
                to="/citizen-login"
                className="w-full inline-flex items-center justify-center space-x-2 bg-[#EAF3FF] hover:bg-blue-100 text-[#1769D2] py-3 px-5 rounded-xl font-semibold text-sm transition-all border border-blue-200"
              >
                <Eye className="w-4 h-4" />
                <span>Explore Citizen Portal</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
