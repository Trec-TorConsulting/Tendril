import * as React from "react"

const MOBILE_BREAKPOINT = 768

function subscribe(onChange: () => void): () => void {
  if (typeof window === "undefined") return () => {}
  const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)
  mql.addEventListener("change", onChange)
  return () => mql.removeEventListener("change", onChange)
}

export function useIsMobile() {
  // useSyncExternalStore is the idiomatic way to read a browser store
  // (matchMedia / innerWidth) without setting state inside an effect, and it
  // is SSR-safe: the server snapshot is always false until the client mounts.
  return React.useSyncExternalStore(
    subscribe,
    () => window.innerWidth < MOBILE_BREAKPOINT,
    () => false,
  )
}
