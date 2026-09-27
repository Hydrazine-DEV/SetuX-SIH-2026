import { Link } from 'react-router-dom';
import { ShieldCheck, Eye, Layers } from 'lucide-react';

export default function GovernmentFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-[#0B2A4A] text-white border-t border-navy-800">
      
      {/* Top Main Footer Area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10">
          
          {/* Column 1: Branding & Product Identity */}
          <div className="lg:col-span-4 space-y-4">
            <div className="flex items-center space-x-3">
              <img
                src="/assets/branding/govt-emblem.png"
                alt="Government Emblem"
                className="h-10 w-auto object-contain brightness-0 invert opacity-90"
              />
              <div className="h-7 w-px bg-white/20"></div>
              <img
                src="/assets/branding/setux-wordmark.png"
                alt="SetuX Platform"
                className="h-7 w-auto object-contain brightness-0 invert"
              />
            </div>
            <p className="text-xs text-gray-300 leading-relaxed max-w-sm">
              SetuX is an integrated project monitoring and intelligence platform engineered by Team VeriX for SIH Problem Statement SIH26103. Designed to enable evidence-backed visual progress verification and predictive overrun risk analysis.
            </p>
            <div className="pt-2 text-xs text-gray-400 flex items-center space-x-2">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>Platform Status: System Operational</span>
            </div>
          </div>

          {/* Column 2: Quick Links */}
          <div className="lg:col-span-3 space-y-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-white border-b border-white/10 pb-2">
              Navigation & Portals
            </h4>
            <ul className="space-y-2 text-xs text-gray-300">
              <li>
                <a href="#home" className="hover:text-blue-300 transition-colors flex items-center space-x-1">
                  <span>Home</span>
                </a>
              </li>
              <li>
                <Link to="/citizen-login" className="hover:text-blue-300 transition-colors flex items-center space-x-1">
                  <Eye className="w-3.5 h-3.5 text-blue-400" />
                  <span>Public Citizen Transparency Portal</span>
                </Link>
              </li>
              <li>
                <Link to="/officer-login" className="hover:text-blue-300 transition-colors flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                  <span>Department Officer Portal Login</span>
                </Link>
              </li>
              <li>
                <a href="#features" className="hover:text-blue-300 transition-colors flex items-center space-x-1">
                  <Layers className="w-3.5 h-3.5 text-blue-400" />
                  <span>Platform Monitoring Features</span>
                </a>
              </li>
              <li>
                <a href="#impact" className="hover:text-blue-300 transition-colors flex items-center space-x-1">
                  <span>Statewide Impact & Sectors</span>
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Monitored Sectors */}
          <div className="lg:col-span-3 space-y-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-white border-b border-white/10 pb-2">
              Infrastructure Scope
            </h4>
            <ul className="space-y-2 text-xs text-gray-300">
              <li>Roads, Bridges & Highways</li>
              <li>Water Supply & Drainage Networks</li>
              <li>Public Works & Institutional Buildings</li>
              <li>Zilla Parishad Education Infrastructure</li>
              <li>Urban & Industrial Zone Developments</li>
            </ul>
          </div>

          {/* Column 4: Institutional Attribution */}
          <div className="lg:col-span-2 space-y-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-white border-b border-white/10 pb-2">
              Project Info
            </h4>
            <div className="space-y-2 text-xs text-gray-300">
              <p><strong className="text-white">Team:</strong> Team VeriX</p>
              <p><strong className="text-white">Problem Code:</strong> SIH26103</p>
              <p className="text-[11px] text-gray-400 pt-1">
                Integrated Government Project Monitoring & Intelligence Architecture
              </p>
            </div>
          </div>

        </div>
      </div>

      {/* Bottom Copyright Bar */}
      <div className="border-t border-white/10 bg-[#071d33] py-4 px-4 sm:px-6 lg:px-8 text-xs text-gray-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0 text-center sm:text-left">
          <div>
            <span>© {currentYear} SetuX Platform — Developed by Team VeriX for SIH26103. All rights reserved.</span>
          </div>
          <div className="flex items-center space-x-4 text-[11px] text-gray-400">
            <span>Privacy Policy</span>
            <span>|</span>
            <span>Terms of Use</span>
            <span>|</span>
            <span>Security Specifications</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
