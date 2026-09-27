import { Layers, Camera, TrendingUp, ShieldCheck } from 'lucide-react';

export default function PlatformPillars() {
  const pillars = [
    {
      num: '01',
      title: 'Multi-Tier Project Monitoring',
      icon: Layers,
      description:
        'Unified oversight across government departments, districts, and contractors with structured milestone recording, financial disbursement reconciliation, and physical status tracking.',
      badge: 'Core Monitoring',
    },
    {
      num: '02',
      title: 'AI-Assisted Visual Verification',
      icon: Camera,
      description:
        'Image processing pipeline analyzing geotagged site photographs against reported physical completion to detect work discrepancies and flag progress anomalies.',
      badge: 'Computer Vision',
    },
    {
      num: '03',
      title: 'Predictive Risk Intelligence',
      icon: TrendingUp,
      description:
        'Machine learning classification models assessing cost escalation ratios, schedule elapsed variances, and milestone delay probabilities to provide proactive early warnings.',
      badge: 'Predictive ML',
    },
    {
      num: '04',
      title: 'Audit-Ready Project Tracking',
      icon: ShieldCheck,
      description:
        'Comprehensive audit log tracing every status transition, evidence submission, and administrative action with automated executive PDF report generation.',
      badge: 'Governance & Compliance',
    },
  ];

  return (
    <section id="features" className="py-20 bg-white border-y border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center space-x-2 bg-[#EAF3FF] text-[#1769D2] px-3.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
            <span>Platform Pillars</span>
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-[#14213D] tracking-tight">
            Integrated Capabilities for End-to-End Monitoring
          </h2>
          <p className="text-base text-[#64748B]">
            Engineered to transform infrastructure monitoring from passive paper-based reporting to evidence-backed, risk-intelligent governance.
          </p>
        </div>

        {/* 4 Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {pillars.map((pillar) => {
            const IconComponent = pillar.icon;
            return (
              <div
                key={pillar.num}
                className="bg-[#F5F7FA] rounded-xl p-6 border border-gray-200 flex flex-col justify-between hover:border-[#1769D2]/40 hover:shadow-md transition-all group"
              >
                <div className="space-y-4">
                  {/* Top Bar: Number & Icon */}
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-extrabold text-[#1769D2] font-mono">
                      {pillar.num}
                    </span>
                    <div className="w-10 h-10 rounded-lg bg-[#EAF3FF] text-[#1769D2] flex items-center justify-center group-hover:bg-[#1769D2] group-hover:text-white transition-colors">
                      <IconComponent className="w-5 h-5" />
                    </div>
                  </div>

                  {/* Title & Badge */}
                  <div className="space-y-1.5">
                    <span className="inline-block text-[11px] font-semibold text-[#64748B] uppercase tracking-wider">
                      {pillar.badge}
                    </span>
                    <h3 className="text-lg font-bold text-[#14213D] group-hover:text-[#1769D2] transition-colors leading-snug">
                      {pillar.title}
                    </h3>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-[#64748B] leading-relaxed">
                    {pillar.description}
                  </p>
                </div>

                {/* Bottom Decorative Line */}
                <div className="pt-4 mt-4 border-t border-gray-200/60 flex items-center text-[11px] font-medium text-[#1769D2] group-hover:underline">
                  <span>Explore Architecture</span>
                  <span className="ml-1">→</span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
