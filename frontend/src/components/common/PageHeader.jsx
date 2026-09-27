export default function PageHeader({
  title,
  subtitle,
  badge,
  actions,
  breadcrumbs,
}) {
  return (
    <div className="bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 px-4 sm:px-6 lg:px-8 py-5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="space-y-1">
          {breadcrumbs && (
            <div className="flex items-center space-x-2 text-xs text-[#64748B] dark:text-slate-400 font-medium mb-1">
              {breadcrumbs.map((crumb, idx) => (
                <span key={idx} className="flex items-center space-x-1.5">
                  {idx > 0 && <span className="text-gray-300 dark:text-slate-600">/</span>}
                  <span>{crumb}</span>
                </span>
              ))}
            </div>
          )}

          <div className="flex items-center space-x-3">
            <h1 className="text-xl sm:text-2xl font-bold text-[#14213D] dark:text-slate-100 tracking-tight">
              {title}
            </h1>
            {badge && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#EAF3FF] dark:bg-blue-950/50 text-[#1769D2] dark:text-blue-400 border border-blue-200 dark:border-blue-800/50">
                {badge}
              </span>
            )}
          </div>

          {subtitle && (
            <p className="text-xs sm:text-sm text-[#64748B] dark:text-slate-400 max-w-3xl leading-relaxed">
              {subtitle}
            </p>
          )}
        </div>

        {actions && (
          <div className="flex items-center space-x-3 shrink-0">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
