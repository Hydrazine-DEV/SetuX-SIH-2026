import { Link } from 'react-router-dom';
import { Shield, ArrowLeft, ArrowRight } from 'lucide-react';

export default function EmptyState({
  icon: Icon = Shield,
  title,
  description,
  phaseTag = 'Module Workspace Ready',
  actionLink = '/dashboard',
  actionText = 'Return to Command Center',
  secondaryActionLink,
  secondaryActionText,
}) {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 sm:p-12 text-center flex flex-col items-center space-y-6">
        
        {/* Icon Container */}
        <div className="w-16 h-16 rounded-2xl bg-[#EAF3FF] border border-blue-100 flex items-center justify-center text-[#1769D2] shadow-sm">
          <Icon className="w-8 h-8" />
        </div>

        {/* Phase Badge */}
        {phaseTag && (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#F5F7FA] text-[#1769D2] border border-gray-200">
            <span className="w-2 h-2 rounded-full bg-[#1769D2]"></span>
            <span>{phaseTag}</span>
          </span>
        )}

        {/* Text Content */}
        <div className="space-y-2 max-w-lg">
          <h2 className="text-xl sm:text-2xl font-bold text-[#14213D] tracking-tight">
            {title}
          </h2>
          <p className="text-xs sm:text-sm text-[#64748B] leading-relaxed">
            {description}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
          {actionLink && (
            <Link
              to={actionLink}
              className="inline-flex items-center space-x-2 bg-[#1769D2] hover:bg-[#1459b8] text-white px-5 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-[#1769D2] focus:ring-offset-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{actionText}</span>
            </Link>
          )}

          {secondaryActionLink && secondaryActionText && (
            <Link
              to={secondaryActionLink}
              className="inline-flex items-center space-x-2 bg-white hover:bg-gray-50 text-[#14213D] border border-gray-200 px-5 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all shadow-sm"
            >
              <span>{secondaryActionText}</span>
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </Link>
          )}
        </div>

      </div>
    </div>
  );
}
