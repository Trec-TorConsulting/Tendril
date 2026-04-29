"use client";

import { PageHeader } from "@/components/page-header";
import { CameraGrid } from "@/components/camera-grid";

export default function CamerasPage() {
  return (
    <>
      <PageHeader title="Cameras" />
      <div className="p-4">
        <CameraGrid />
      </div>
    </>
  );
}
