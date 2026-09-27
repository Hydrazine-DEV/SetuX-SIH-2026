import { FileCheck2 } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import EmptyState from '../components/common/EmptyState';

export default function Issues() {
  return (
    <div className="min-h-full pb-12">
      <PageHeader
        title="Field Issues & Site Evidence"
        subtitle="Site inspection logs, contractor discrepancies, and photographic evidence submissions."
        badge="Evidence Module"
        breadcrumbs={['SetuX', 'Issues & Evidence']}
      />

      <EmptyState
        icon={FileCheck2}
        title="Issues & Site Evidence Workspace"
        description="Field inspection reports, geo-tagged image uploads, and milestone verification audit tools are being prepared for live integration."
        phaseTag="Module Ready"
        actionLink="/dashboard"
        actionText="Return to Command Center"
        secondaryActionLink="/projects"
        secondaryActionText="View Projects"
      />
    </div>
  );
}
