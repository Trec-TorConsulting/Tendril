"use client";

import { useEffect } from "react";
import { useChat } from "@/components/chat-provider";
import { PageHeader } from "@/components/page-header";

export default function AiChatPage() {
  const { openChat } = useChat();

  useEffect(() => {
    openChat();
  }, [openChat]);

  return (
    <>
      <PageHeader
        title="AI Chat"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "AI", href: "/dashboard/ai" },
          { label: "Chat" },
        ]}
      />
      <div className="flex flex-1 items-center justify-center p-6">
        <p className="text-sm text-muted-foreground">
          Chat is open in the side panel →
        </p>
      </div>
    </>
  );
}
