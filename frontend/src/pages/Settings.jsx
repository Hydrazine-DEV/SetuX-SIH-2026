import { Settings as SettingsIcon } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import EmptyState from '../components/common/EmptyState';

export default function Settings() {
  return (
    <div className="min-h-full pb-12">
      <PageHeader
        title="Department Settings & Officer Profile"
        subtitle="Departmental preferences, system access controls, and notification subscriptions."
        badge="Settings"
        breadcrumbs={['SetuX', 'Settings']}
      />

      <EmptyState
        icon={SettingsIcon}
        title="Settings & Configuration Workspace"
        description="Departmental configuration, officer notification settings, and access control management are being prepared for integration."
        phaseTag="Module Ready"
        actionLink="/dashboard"
        actionText="Return to Command Center"
      />
    </div>
  );
}
