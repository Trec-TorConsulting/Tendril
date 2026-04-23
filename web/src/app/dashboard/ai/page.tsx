"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useChat } from "@/components/chat-provider";

export default function AiChatPage() {
  const router = useRouter();
  const { openChat } = useChat();

  useEffect(() => {
    openChat();
    router.replace("/dashboard");
  }, [openChat, router]);

  return null;
}
