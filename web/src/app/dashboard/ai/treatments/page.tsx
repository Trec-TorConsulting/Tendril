"use client";

import { TreatmentDatabase } from "@/components/treatment-database";
import { PageHeader } from "@/components/page-header";
import { useGrow } from "@/hooks/use-grow";

export default function TreatmentsPage() {
  const { grow } = useGrow();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Treatment Guide"
        description="Comprehensive reference for diagnosing and treating cannabis plant issues — deficiencies, pests, diseases, and environmental stress."
      />
      <TreatmentDatabase growType={grow?.grow_type} />
    </div>
  );
}
