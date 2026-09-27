import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogIn, Menu, X, ShieldCheck } from 'lucide-react';

export default function GovernmentHeader() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleNavClick = (id) => {
    setMobileMenuOpen(false);
    if (id.startsWith('/')) {
      navigate(id);
    } else {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      {/* Top Institutional Banner */}
      <div className="bg-[#0B2A4A] text-white py-1.5 px-4 text-xs font-medium border-b border-navy-800">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="tracking-wide">Government Infrastructure Monitoring Platform</span>
          </div>
          <div className="hidden sm:flex items-center space-x-4 text-gray-300">
            <span>Team VeriX — SIH26103</span>
            <span>|</span>
            <span className="text-gray-200">Public & Officer Gateway</span>
          </div>
        </div>
      </div>

      {/* Main Header Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          
          {/* Left Branding Group */}
          <div className="flex items-center space-x-3 sm:space-x-4">
            <img 
              src="/assets/branding/govt-emblem.png" 
              alt="Government Emblem" 
              className="h-10 sm:h-12 w-auto object-contain"
            />
            <div className="h-8 w-px bg-gray-300 hidden sm:block"></div>
            <Link to="/" className="flex flex-col">
              <img 
                src="/assets/branding/setux-logo.png" 
                alt="SetuX Platform" 
                className="h-8 sm:h-9 w-auto object-contain"
              />
              <span className="text-[10px] uppercase tracking-wider font-semibold text-[#64748B] -mt-0.5 hidden md:block">
                Project Monitoring & Intelligence Platform
              </span>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-8">
            <button
              onClick={() => handleNavClick('home')}
              className="text-[#14213D] hover:text-[#1769D2] font-medium text-sm transition-colors py-1"
            >
              Home
            </button>
            <button
              onClick={() => handleNavClick('/citizen-login')}
              className="text-[#14213D] hover:text-[#1769D2] font-medium text-sm transition-colors py-1"
            >
              Citizen Portal
            </button>
            <button
              onClick={() => handleNavClick('features')}
              className="text-[#14213D] hover:text-[#1769D2] font-medium text-sm transition-colors py-1"
            >
              Monitoring Features
            </button>
            <button
              onClick={() => handleNavClick('impact')}
              className="text-[#14213D] hover:text-[#1769D2] font-medium text-sm transition-colors py-1"
            >
              State Impact
            </button>
          </nav>

          {/* Desktop Right Action CTA */}
          <div className="hidden lg:flex items-center space-x-4">
            <Link
              to="/officer-login"
              className="inline-flex items-center space-x-2 bg-[#1769D2] hover:bg-[#1459b8] text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-[#1769D2] focus:ring-offset-2"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Officer Login</span>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex lg:hidden items-center space-x-3">
            <Link
              to="/officer-login"
              className="inline-flex items-center space-x-1.5 bg-[#1769D2] text-white px-3 py-1.5 rounded-md text-xs font-medium"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Login</span>
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-700 hover:text-gray-900 p-2 focus:outline-none"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-gray-200 bg-white px-4 pt-3 pb-6 space-y-3 shadow-lg">
          <button
            onClick={() => handleNavClick('home')}
            className="block w-full text-left py-2 text-[#14213D] font-medium text-sm hover:text-[#1769D2]"
          >
            Home
          </button>
          <button
            onClick={() => handleNavClick('/citizen-login')}
            className="block w-full text-left py-2 text-[#14213D] font-medium text-sm hover:text-[#1769D2]"
          >
            Public Citizen Portal
          </button>
          <button
            onClick={() => handleNavClick('features')}
            className="block w-full text-left py-2 text-[#14213D] font-medium text-sm hover:text-[#1769D2]"
          >
            Monitoring Features
          </button>
          <button
            onClick={() => handleNavClick('impact')}
            className="block w-full text-left py-2 text-[#14213D] font-medium text-sm hover:text-[#1769D2]"
          >
            State Impact
          </button>
          <div className="pt-2 border-t border-gray-100 flex flex-col space-y-2">
            <Link
              to="/officer-login"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-center space-x-2 bg-[#1769D2] text-white py-2.5 rounded-lg font-semibold text-sm"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Officer Login</span>
            </Link>
            <Link
              to="/citizen-login"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-center space-x-2 bg-[#EAF3FF] text-[#1769D2] py-2.5 rounded-lg font-semibold text-sm border border-blue-100"
            >
              <span>Explore Public Citizen Portal</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
