"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function CamerasPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/dashboard/devices?tab=cameras");
  }, [router]);

  return null;
}
