import { MapPin, Shield, CheckCircle, FileCheck, Landmark } from 'lucide-react';

export default function StateImpact() {
  const highlights = [
    {
      title: 'Multi-Sector Visibility',
      icon: Landmark,
      description: 'Unified tracking across Roads & Bridges, Water Pipeline Networks, Urban Infrastructure, School Facilities, and Drainage Systems.',
    },
    {
      title: 'Risk-Aware Monitoring',
      icon: Shield,
      description: 'Proactive early warning engine identifying delay risks, cost escalation indicators, and milestone schedule variances.',
    },
    {
      title: 'Evidence-Backed Progress',
      icon: FileCheck,
      description: 'Transitioning from unverified paper assertions to geotagged visual site evidence and structured verification workflows.',
    },
    {
      title: 'Institutional Accountability',
      icon: CheckCircle,
      description: 'Strengthening department decision support while providing open public access for civic transparency.',
    },
  ];

  return (
    <section id="impact" className="py-20 bg-[#0B2A4A] text-white relative overflow-hidden">
      {/* Background Decorative Pattern */}
      <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#EAF3FF_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-2 bg-blue-500/20 text-[#EAF3FF] border border-blue-400/30 px-3.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
            <MapPin className="w-3.5 h-3.5 text-blue-400" />
            <span>Statewide Infrastructure Reach</span>
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight">
            Integrated Governance & Visibility Across Sectors
          </h2>
          <p className="text-base text-gray-300">
            Providing Maharashtra with standardized digital oversight, objective verification standards, and actionable project intelligence.
          </p>
        </div>

        {/* 2-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          
          {/* Left Column: Image Showcase */}
          <div className="lg:col-span-5 relative">
            <div className="relative rounded-2xl overflow-hidden border border-white/20 shadow-2xl bg-navy-800">
              <img
                src="/assets/sections/infrastructure-india.jpg"
                alt="Maharashtra Infrastructure Regional View"
                className="w-full h-auto object-cover rounded-2xl"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#0B2A4A] via-transparent to-transparent"></div>
              <div className="absolute bottom-4 left-4 right-4 bg-[#0B2A4A]/90 backdrop-blur-md p-4 rounded-xl border border-white/10">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></div>
                  <div>
                    <p className="text-xs font-bold text-white">Geospatial Regional Oversight</p>
                    <p className="text-[11px] text-gray-300">Active monitoring across districts & execution zones</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Qualitative Impact Pillars */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-6">
            {highlights.map((item, idx) => {
              const IconComp = item.icon;
              return (
                <div
                  key={idx}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:border-blue-400/40 transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    <div className="w-10 h-10 rounded-lg bg-[#1769D2]/30 border border-blue-400/30 text-blue-300 flex items-center justify-center">
                      <IconComp className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold text-white leading-snug">
                      {item.title}
                    </h3>
                    <p className="text-xs text-gray-300 leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                  <div className="text-[11px] font-medium text-blue-300 uppercase tracking-wider">
                    Governance Standard
                  </div>
                </div>
              );
            })}
          </div>

        </div>

      </div>
    </section>
  );
}
