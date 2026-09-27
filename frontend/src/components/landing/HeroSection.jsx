import { Link } from 'react-router-dom';
import { ShieldCheck, Eye, ArrowRight, Activity, Cpu } from 'lucide-react';

export default function HeroSection() {
  return (
    <section id="home" className="relative bg-[#0B2A4A] overflow-hidden text-white min-h-[580px] lg:min-h-[640px] flex items-center">
      {/* Background Image Container with Overlay */}
      <div className="absolute inset-0 z-0">
        <img
          src="/assets/hero/infrastructure-bridge.jpg"
          alt="Infrastructure Bridge Monitoring"
          className="w-full h-full object-cover object-center"
        />
        {/* Multilayer Dark Navy Gradients for Crisp Contrast */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#0B2A4A] via-[#0B2A4A]/90 to-[#0B2A4A]/60"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-[#0B2A4A] via-transparent to-[#0B2A4A]/40"></div>
      </div>

      {/* Hero Content Container */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="max-w-3xl space-y-6">
          
          {/* Tagline Badge */}
          <div className="inline-flex items-center space-x-2.5 bg-[#1769D2]/30 backdrop-blur-sm border border-blue-400/30 px-3.5 py-1.5 rounded-full text-xs font-semibold text-[#EAF3FF]">
            <Cpu className="w-3.5 h-3.5 text-blue-300 animate-pulse" />
            <span className="tracking-wide">Integrated Government Project Monitoring & Intelligence Platform</span>
          </div>

          {/* Primary Headline */}
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
            From Reported Progress to <br className="hidden sm:block" />
            <span className="text-[#EAF3FF] underline decoration-[#1769D2] decoration-4 underline-offset-8">
              Verified Progress
            </span>
          </h1>

          {/* Product Description */}
          <p className="text-base sm:text-lg text-gray-200 leading-relaxed font-normal max-w-2xl">
            Empowering infrastructure governance with AI-assisted visual evidence verification, 
            predictive cost and timeline overrun modeling, early warning risk intelligence, and 
            audit-ready project tracking across state departments.
          </p>

          {/* Action CTAs */}
          <div className="pt-4 flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
            <Link
              to="/officer-login"
              className="inline-flex items-center justify-center space-x-2 bg-[#1769D2] hover:bg-[#1459b8] text-white px-7 py-3.5 rounded-lg font-semibold text-base shadow-lg hover:shadow-xl transition-all border border-blue-400/20"
            >
              <ShieldCheck className="w-5 h-5" />
              <span>Officer Login</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>

            <Link
              to="/citizen-login"
              className="inline-flex items-center justify-center space-x-2 bg-white/10 hover:bg-white/20 text-white border border-white/30 px-7 py-3.5 rounded-lg font-semibold text-base backdrop-blur-sm transition-all"
            >
              <Eye className="w-5 h-5 text-blue-200" />
              <span>Citizen Portal</span>
            </Link>
          </div>

          {/* Feature Highlight Pills */}
          <div className="pt-8 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-medium text-gray-200 border-t border-white/10">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>Multi-Tier Monitoring</span>
            </div>
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span>Predictive Overrun Risk Engine</span>
            </div>
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-indigo-400 flex-shrink-0" />
              <span>Audit Trail Verification</span>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
