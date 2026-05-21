import Link from "next/link";

export const metadata = {
  title: "Terms of Service — Tendril",
  description: "Terms of Service for the Tendril grow monitoring platform",
};

export default function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Nav */}
      <nav className="border-b border-neutral-800 bg-neutral-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link href="/" className="text-xl font-bold text-green-500">🌿 Tendril</Link>
          <div className="flex gap-4">
            <Link href="/login" className="rounded px-4 py-2 text-sm text-neutral-300 hover:text-white">Log In</Link>
            <Link href="/register" className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">Sign Up Free</Link>
          </div>
        </div>
      </nav>

      <article className="mx-auto max-w-3xl px-4 py-16 prose prose-invert prose-neutral">
        <h1>Terms of Service</h1>
        <p className="text-neutral-400"><strong>Last updated:</strong> May 6, 2026</p>

        <p>These Terms of Service (&ldquo;Terms&rdquo;) govern your use of the Tendril platform (&ldquo;Service&rdquo;), operated by <strong>Geek Info LLC</strong>, managed by Trec-Tor Consulting, located in New Jersey, USA.</p>
        <p>By creating an account or using the Service, you agree to be bound by these Terms. If you do not agree, do not use the Service.</p>

        <h2>1. Definitions</h2>
        <ul>
          <li><strong>&ldquo;Service&rdquo;</strong> means the Tendril web application, API, mobile experience, and related services at tendrilgrow.com.</li>
          <li><strong>&ldquo;User&rdquo;</strong> or <strong>&ldquo;You&rdquo;</strong> means any individual or entity accessing the Service.</li>
          <li><strong>&ldquo;Account&rdquo;</strong> means your registered Tendril account including all associated Tenants and data.</li>
          <li><strong>&ldquo;Content&rdquo;</strong> means any data, images, sensor readings, grow logs, or other information you submit.</li>
        </ul>

        <h2>2. Account Registration</h2>
        <p>You must provide accurate information when creating an account. You are responsible for maintaining the security of your credentials. You must be at least 18 years old to use the Service.</p>
        <p>One person or legal entity may not maintain more than one free account.</p>

        <h2>3. Acceptable Use</h2>
        <p>You agree not to:</p>
        <ul>
          <li>Use the Service for any illegal purpose or in violation of any local, state, or federal law</li>
          <li>Attempt to reverse engineer, decompile, or extract source code from the Service</li>
          <li>Use automated systems (bots, scrapers) to access the Service beyond the documented API</li>
          <li>Interfere with or disrupt the Service or servers/networks connected to the Service</li>
          <li>Impersonate another person or entity</li>
          <li>Upload malware, viruses, or other malicious code</li>
          <li>Exceed your plan&rsquo;s usage limits through circumvention or abuse</li>
        </ul>

        <h2>4. Subscription Plans & Billing</h2>
        <ul>
          <li>Paid plans are billed monthly in advance via Stripe or other supported payment providers.</li>
          <li>All fees are exclusive of taxes. Applicable sales tax is calculated and collected automatically via Stripe Tax based on your billing address.</li>
          <li>You may upgrade or downgrade at any time. Upgrades take effect immediately; downgrades take effect at the end of the current billing period.</li>
          <li>If payment fails, we provide a 14-day grace period with automatic retries before downgrading your account to the Free plan.</li>
          <li>No refunds are provided for partial months of service except within 7 days of the initial charge upon request.</li>
        </ul>

        <h2>5. Cancellation & Termination</h2>
        <ul>
          <li>You may cancel your subscription at any time from the billing dashboard.</li>
          <li>Upon cancellation, you retain access until the end of the current billing period.</li>
          <li>After your subscription ends, your account reverts to the Free plan. Your data is preserved.</li>
          <li>We reserve the right to suspend or terminate accounts that violate these Terms.</li>
        </ul>

        <h2>6. Data Ownership & License</h2>
        <p>You retain full ownership of all Content you submit to the Service. By using the Service, you grant us a limited license to store, process, and display your Content solely to provide the Service to you.</p>
        <p>We do not sell, share, or use your grow data for advertising or any purpose other than operating the Service.</p>

        <h2>7. Data Retention & Deletion</h2>
        <ul>
          <li>You may request account deletion at any time from account settings.</li>
          <li>Upon deletion request, your data is retained for 30 days (recovery window), then permanently purged.</li>
          <li>You may cancel a pending deletion by logging in during the 30-day window.</li>
          <li>We may retain anonymized, aggregated analytics data that cannot identify you.</li>
        </ul>

        <h2>8. Service Availability</h2>
        <p>We aim for 99.9% uptime but do not guarantee uninterrupted service. We are not liable for any downtime, data loss, or service interruption. Enterprise and Dedicated plans include SLA guarantees as specified in their service agreements.</p>

        <h2>9. Limitation of Liability</h2>
        <p>TO THE MAXIMUM EXTENT PERMITTED BY LAW, GEEK INFO LLC SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUE, WHETHER INCURRED DIRECTLY OR INDIRECTLY.</p>
        <p>Our total liability for any claim arising from these Terms or the Service shall not exceed the amount you paid us in the 12 months preceding the claim.</p>

        <h2>10. Indemnification</h2>
        <p>You agree to indemnify and hold harmless Geek Info LLC, Trec-Tor Consulting, and their officers, directors, and employees from any claims arising from your use of the Service or violation of these Terms.</p>

        <h2>11. Intellectual Property</h2>
        <p>The Service, including its design, code, branding, and documentation, is owned by Geek Info LLC. Nothing in these Terms grants you any right to use our trademarks, logos, or brand assets without written permission.</p>

        <h2>12. Third-Party Services</h2>
        <p>The Service integrates with third-party providers (Stripe, Google, GitHub, EMQX, OpenWeather, etc.). Your use of those services is governed by their respective terms. We are not responsible for third-party service availability or data handling.</p>

        <h2>13. Modifications</h2>
        <p>We may modify these Terms at any time. Material changes will be communicated via email or in-app notification at least 30 days before taking effect. Continued use after modifications constitutes acceptance.</p>

        <h2>14. Governing Law</h2>
        <p>These Terms are governed by the laws of the State of New Jersey, USA, without regard to conflict of law principles. Any disputes shall be resolved in the courts of New Jersey.</p>

        <h2>15. Contact</h2>
        <p>For questions about these Terms, contact us at <a href="mailto:legal@tendrilgrow.com" className="text-green-500">legal@tendrilgrow.com</a>.</p>

        <div className="mt-12 border-t border-neutral-800 pt-6 text-sm text-neutral-500">
          <p>Powered by <a href="https://www.trector.com" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-300">Trec-Tor Consulting</a></p>
        </div>
      </article>
    </div>
  );
}
