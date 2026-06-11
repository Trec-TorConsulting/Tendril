# Privacy Policy

**Tendril — Open-Source Grow Monitoring & Automation Platform**

*Effective Date: June 11, 2026 | Last Updated: June 11, 2026*

---

**Geek Info LLC**, a New Jersey limited liability company managed by Trec-Tor Consulting ("Company," "we," "us," or "our"), operates the Tendril platform at tendrilgrow.com and related services. This Privacy Policy describes how we collect, use, disclose, retain, and protect your personal information when you access or use the Tendril platform, website, mobile applications, APIs, hardware, and related services (collectively, the "Service").

**BY CREATING AN ACCOUNT OR USING THE SERVICE, YOU ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND CONSENT TO THE PRACTICES DESCRIBED IN THIS PRIVACY POLICY. IF YOU DO NOT AGREE, DO NOT USE THE SERVICE.**

This Privacy Policy is designed to comply with the European Union General Data Protection Regulation (GDPR), the California Consumer Privacy Act as amended by the California Privacy Rights Act (CCPA/CPRA), the New Jersey Data Privacy Act (NJDPA), the Virginia Consumer Data Protection Act (VCDPA), the Colorado Privacy Act (CPA), the Connecticut Data Privacy Act (CTDPA), and other applicable data protection laws.

---

## 1. Information We Collect

### 1.1 Information You Provide Directly

| Category | Data Elements | Purpose |
|----------|--------------|---------|
| Account Information | Email address, display name, organization name, password (hashed with bcrypt, never stored in plaintext) | Account creation, authentication, communication |
| Billing Information | Name, billing address, payment method (processed and stored exclusively by Stripe; we never receive or store full card numbers, CVVs, or bank account details) | Payment processing, tax compliance |
| Grow Data | Grow cycle information, plant types, growth stages, dates, notes, strain information, yield records | Core service functionality |
| Journal Content | Text entries, feeding logs, observations, expense records | Grow journaling features |
| Photos & Media | Plant photos, environment images, documents | Health analysis, grow records, AI features |
| Automation Configuration | Rules, schedules, thresholds, notification preferences | Automation and alerting features |
| Support Communications | Emails, chat messages, feedback submitted to us | Customer support, product improvement |

### 1.2 Information Collected Automatically

| Category | Data Elements | Purpose |
|----------|--------------|---------|
| Sensor/Telemetry Data | Temperature, humidity, soil moisture, pH, EC/TDS, dissolved oxygen, water level, VPD, CO2, light intensity, and other environmental measurements from connected IoT devices | Environmental monitoring, alerting, AI analysis |
| Device Information | ESP32 device identifiers, MAC addresses, firmware versions, hardware configuration, MQTT connection metadata | Device management, troubleshooting |
| Network Information | IP addresses, request headers, TLS fingerprints | Security, rate limiting, fraud prevention |
| Usage Data | Pages visited, features used, click patterns, session duration, referral source | Product improvement, analytics |
| Technical Data | Browser type, operating system, screen resolution, device type, timezone | Compatibility, debugging |
| API Logs | Request paths, response codes, timestamps, latency | Debugging, performance monitoring, security |
| Error Data | Error messages, stack traces, application state at time of error | Bug fixing, stability improvement |

### 1.3 Information from Third Parties

| Source | Data | Purpose |
|--------|------|---------|
| OAuth Providers (Google, GitHub) | Email, name, profile picture (only if you choose OAuth login) | Account authentication |
| Stripe | Payment status, subscription state, invoice history | Billing management |
| Weather Services (OpenWeather, Open-Meteo, Ecowitt) | Weather data associated with your configured locations | Environmental context for grows |
| Integration Connectors (Pulse Grow, Ecowitt) | Device data, sensor readings from connected third-party systems | Unified monitoring dashboard |

### 1.4 Sensitive Information

We do **not** intentionally collect sensitive personal information such as racial or ethnic origin, political opinions, religious beliefs, health data, sexual orientation, genetic data, or biometric data. If you voluntarily include such information in journal entries, photos, or other Content, you do so at your own discretion.

---

## 2. Legal Bases for Processing (GDPR)

For users in the European Economic Area (EEA), United Kingdom, and Switzerland, we process your personal data under the following legal bases:

| Processing Activity | Legal Basis |
|--------------------|-------------|
| Providing the Service, processing sensor data, storing Content | Performance of contract (Art. 6(1)(b) GDPR) |
| Processing payments, tax compliance | Performance of contract & legal obligation (Art. 6(1)(b), (c)) |
| Security monitoring, fraud prevention, rate limiting | Legitimate interest (Art. 6(1)(f)) — security of Service |
| Product improvement via anonymized analytics | Legitimate interest (Art. 6(1)(f)) — improving the Service |
| Sending transactional emails (alerts, receipts, security notices) | Performance of contract (Art. 6(1)(b)) |
| Sending optional product updates or newsletters | Consent (Art. 6(1)(a)) — opt-in only |
| AI analysis of photos and grow data | Performance of contract (Art. 6(1)(b)) — you request analysis |
| Responding to legal requests, law enforcement | Legal obligation (Art. 6(1)(c)) |
| Retaining billing records | Legal obligation (Art. 6(1)(c)) — tax law |

---

## 3. How We Use Your Information

We use collected information for the following purposes:

- **Service Delivery:** Store, process, display, and transmit your grow data; process sensor readings; execute automations; deliver alerts and notifications;
- **AI Features:** Provide AI-powered grow recommendations, plant health analysis, and insights based on your data (only when you actively use AI features);
- **Billing & Payments:** Process subscriptions, calculate usage, collect taxes, issue invoices and receipts via Stripe;
- **Communication:** Send transactional messages (account verification, password resets, billing receipts, security alerts, threshold notifications);
- **Security & Integrity:** Detect and prevent fraud, abuse, unauthorized access, and DDoS attacks; enforce rate limits; maintain audit logs;
- **Debugging & Support:** Diagnose and fix technical issues, respond to support requests;
- **Product Improvement:** Analyze anonymized, aggregated usage patterns to improve features, performance, and reliability;
- **Legal Compliance:** Comply with applicable laws, regulations, legal processes, and governmental requests;
- **Safety:** Protect the rights, property, or safety of our users, the public, or ourselves.

---

## 4. What We Do NOT Do

We make the following commitments regarding your data:

- We do **NOT** sell, rent, lease, or trade your personal information to any third party for monetary or other valuable consideration;
- We do **NOT** share your personal information for cross-context behavioral advertising;
- We do **NOT** use your grow data, sensor readings, photos, or journal entries for advertising or marketing purposes;
- We do **NOT** share identifiable data with other tenants or users (multi-tenant isolation is enforced via PostgreSQL Row Level Security);
- We do **NOT** train AI/ML models on your private data without your explicit, informed, opt-in consent;
- We do **NOT** use tracking pixels, advertising beacons, or third-party analytics cookies;
- We do **NOT** fingerprint your browser or device for tracking purposes;
- We do **NOT** build behavioral profiles of you for sale to data brokers;
- We do **NOT** monetize your data in any way other than providing the Service to you.

---

## 5. Disclosure of Information

We may disclose your information only in the following limited circumstances:

### 5.1 Service Providers (Data Processors)

We share data with third-party service providers who process it on our behalf under written data processing agreements:

| Provider | Purpose | Data Shared | Location |
|----------|---------|-------------|----------|
| Stripe, Inc. | Payment processing, billing, tax calculation | Email, name, billing address, payment method tokens | United States |
| Google LLC (Gemini AI) | AI plant health analysis | Plant photos submitted for analysis (ephemeral — not retained by Google per our DPA) | United States |
| Resend | Transactional email delivery | Email address, notification content | United States |
| OpenWeather Ltd. | Weather data retrieval | Geographic coordinates (if you configure outdoor grows) | United Kingdom |
| Open-Meteo | Weather data (free baseline) | Geographic coordinates | Germany |
| Infrastructure provider (Kubernetes) | Hosting, compute, storage | All Service data (encrypted at rest and in transit) | United States |

All service providers are contractually bound to process data only as instructed by us and to implement appropriate security measures.

### 5.2 Legal Requirements

We may disclose your information if required to do so by law or if we believe in good faith that disclosure is necessary to:

- Comply with a legal obligation, court order, subpoena, or valid legal process;
- Protect and defend our rights, property, or safety;
- Protect the personal safety of users or the public;
- Prevent or investigate possible wrongdoing in connection with the Service;
- Cooperate with law enforcement investigations.

Where legally permitted, we will attempt to notify you of such requests before disclosing your data.

### 5.3 Business Transfers

In the event of a merger, acquisition, reorganization, bankruptcy, asset sale, or similar business transaction, your information may be transferred as a business asset. We will notify you via email and/or prominent notice on the Service before your information becomes subject to a different privacy policy.

### 5.4 With Your Consent

We may share your information with third parties when you provide explicit consent to do so (e.g., connecting a third-party integration).

### 5.5 Aggregated/De-identified Data

We may share aggregated, anonymized, or de-identified data that cannot reasonably be used to identify you. Such data is not subject to this Privacy Policy.

---

## 6. Data Storage, Security, and Retention

### 6.1 Storage Location

Your data is stored and processed in the **United States** on private Kubernetes clusters. We do not store data on shared/public cloud infrastructure.

### 6.2 Security Measures

We implement industry-standard technical and organizational security measures including:

- **Encryption in transit:** All connections use TLS 1.3. No unencrypted connections are accepted.
- **Encryption at rest:** Sensitive fields (API keys, integration secrets, payment credentials) are encrypted with AES-256-GCM.
- **Database isolation:** Multi-tenant data isolation enforced at the database level via PostgreSQL Row Level Security (RLS).
- **Authentication security:** Passwords hashed with bcrypt (cost factor 12). httpOnly, Secure, SameSite cookies. CSRF protection on all state-changing requests.
- **Access controls:** Role-based access control (RBAC). Principle of least privilege for all internal systems.
- **Audit logging:** All administrative actions and data access are logged with immutable audit trails.
- **Infrastructure security:** Network policies, pod security standards, automated vulnerability scanning, regular security updates.
- **Incident response:** Documented incident response procedures with defined notification timelines (see Section 6.5).

### 6.3 Data Retention Schedule

| Data Type | Retention Period | Justification |
|-----------|-----------------|---------------|
| Active account data | Life of account | Contract performance |
| Sensor data (Free plan) | 90 days | Plan limitation |
| Sensor data (Paid plans) | Unlimited (life of account) | Contract performance |
| API/access logs | 30 days | Security, debugging |
| Audit logs | 7 years | Legal compliance, security |
| Billing records | 7 years after last transaction | Tax law (IRS, state requirements) |
| Deleted account data | 30 days (recovery) + 60 days (purge from backups) | Recovery window, then permanent deletion |
| Support communications | 3 years | Legitimate interest (dispute resolution) |
| Anonymized analytics | Indefinite | Not personal data after de-identification |

### 6.4 Data Minimization

We collect only data that is necessary for the stated purposes. We periodically review our data collection practices and delete data that is no longer necessary.

### 6.5 Breach Notification

In the event of a data breach that poses a risk to your rights and freedoms:

- We will notify affected users via email within **72 hours** of confirming the breach (as required by GDPR Art. 33);
- We will notify the relevant supervisory authority within 72 hours where required;
- We will notify the California Attorney General if the breach affects more than 500 California residents;
- Notification will include: nature of the breach, categories of data affected, likely consequences, and measures taken or proposed.

---

## 7. Your Privacy Rights

We provide the following rights to **all users regardless of location**. Additional jurisdiction-specific rights are detailed in subsequent sections.

### 7.1 Universal Rights

| Right | Description | How to Exercise |
|-------|-------------|-----------------|
| **Access** | Obtain a copy of all personal data we hold about you | Account Settings → Export Data, or email privacy@tendrilgrow.com |
| **Rectification** | Correct inaccurate or incomplete personal data | Edit your profile, or email us for data we cannot edit in-app |
| **Deletion** | Request permanent deletion of your account and data | Account Settings → Delete Account, or email privacy@tendrilgrow.com |
| **Portability** | Receive your data in a structured, machine-readable format (JSON) | Account Settings → Export Data, or via API |
| **Restriction** | Request that we limit processing of your data | Email privacy@tendrilgrow.com |
| **Objection** | Object to processing based on legitimate interests | Email privacy@tendrilgrow.com |
| **Withdraw Consent** | Withdraw previously given consent at any time | Notification preferences, or email privacy@tendrilgrow.com |

### 7.2 Response Timeline

- We will acknowledge your request within **3 business days**.
- We will fulfill verified requests within **30 days** (extendable to 45 days for complex requests with notice).
- We will not charge a fee for exercising your rights unless requests are manifestly unfounded or excessive.

### 7.3 Verification

To protect your privacy, we may need to verify your identity before fulfilling requests. Verification methods include confirming account ownership via email confirmation or providing account-specific details.

### 7.4 Non-Discrimination

We will not discriminate against you for exercising any of your privacy rights. You will not receive different pricing, a different quality of service, or be denied service for making privacy requests.

---

## 8. GDPR-Specific Provisions (EEA, UK, Switzerland)

If you are located in the European Economic Area, United Kingdom, or Switzerland, the following additional provisions apply:

### 8.1 Data Controller

Geek Info LLC is the data controller for your personal data. Contact: privacy@tendrilgrow.com.

### 8.2 Data Protection Officer

For GDPR-related inquiries, contact our designated privacy representative at: dpo@tendrilgrow.com

### 8.3 International Data Transfers

Your data is transferred to and processed in the United States. We rely on the following transfer mechanisms:

- EU-U.S. Data Privacy Framework (where applicable);
- Standard Contractual Clauses (SCCs) approved by the European Commission (Commission Implementing Decision (EU) 2021/914);
- Supplementary measures including encryption, access controls, and contractual commitments.

You may request a copy of our Standard Contractual Clauses by emailing privacy@tendrilgrow.com.

### 8.4 Right to Lodge a Complaint

You have the right to lodge a complaint with your local data protection supervisory authority if you believe our processing of your personal data violates the GDPR.

### 8.5 Automated Decision-Making

We do not make decisions that produce legal or similarly significant effects based solely on automated processing. AI recommendations are informational only and do not result in automated decisions affecting your legal rights.

---

## 9. CCPA/CPRA-Specific Provisions (California Residents)

If you are a California resident, the following additional disclosures and rights apply under the California Consumer Privacy Act as amended by the California Privacy Rights Act (Cal. Civ. Code § 1798.100 et seq.):

### 9.1 Categories of Personal Information Collected

In the preceding 12 months, we have collected the following categories of personal information as defined by the CCPA:

| CCPA Category | Examples | Collected? | Sold? | Shared for Advertising? |
|---------------|----------|-----------|-------|------------------------|
| A. Identifiers | Email, name, IP address, device IDs | Yes | No | No |
| B. Personal information (Cal. Civ. Code § 1798.80(e)) | Name, address (billing only via Stripe) | Yes | No | No |
| D. Commercial information | Subscription history, transaction records | Yes | No | No |
| F. Internet/network activity | Browsing history on Service, API logs | Yes | No | No |
| G. Geolocation data | Approximate location (if outdoor grows configured) | Yes (optional) | No | No |
| H. Sensory data | Photos uploaded for AI analysis | Yes | No | No |
| K. Inferences | AI-generated grow recommendations | Yes | No | No |

### 9.2 Sale and Sharing

**We do NOT sell your personal information.** We have not sold personal information in the preceding 12 months. We do NOT share personal information for cross-context behavioral advertising.

### 9.3 California-Specific Rights

- **Right to Know:** You may request disclosure of the categories and specific pieces of personal information we have collected, the purposes, and the third parties with whom we share it.
- **Right to Delete:** You may request deletion of your personal information, subject to legal exceptions.
- **Right to Correct:** You may request correction of inaccurate personal information.
- **Right to Opt-Out of Sale/Sharing:** Not applicable — we do not sell or share your data. However, we honor Global Privacy Control (GPC) signals.
- **Right to Limit Use of Sensitive Personal Information:** We do not use sensitive personal information for purposes beyond what is necessary to provide the Service.
- **Right to Non-Discrimination:** We will not discriminate against you for exercising CCPA rights.

### 9.4 Authorized Agents

You may designate an authorized agent to submit requests on your behalf. We require written authorization and may verify your identity directly.

### 9.5 "Do Not Sell or Share My Personal Information"

We do not sell or share personal information. We honor GPC browser signals as a valid opt-out mechanism. No "Do Not Sell" link is required because we do not engage in selling or sharing.

### 9.6 Financial Incentives

We do not offer financial incentives for the collection, sale, or deletion of personal information.

---

## 10. Additional U.S. State Privacy Rights

### 10.1 New Jersey Data Privacy Act (NJDPA)

New Jersey residents have the right to: access, correct, delete, and obtain a portable copy of their personal data; opt out of targeted advertising, sale, and profiling. We do not engage in targeted advertising, sale, or profiling. To exercise rights, contact privacy@tendrilgrow.com. We will respond within 45 days.

### 10.2 Virginia (VCDPA), Colorado (CPA), Connecticut (CTDPA)

Residents of Virginia, Colorado, and Connecticut have similar rights including: access, correction, deletion, portability, and opt-out of targeted advertising/sale/profiling. We provide these rights universally. Appeals may be submitted to privacy@tendrilgrow.com and will be resolved within 60 days.

### 10.3 Appeal Process

If we decline a privacy request, you may appeal by emailing privacy@tendrilgrow.com with "Privacy Appeal" in the subject line. We will respond to appeals within the timeframes required by applicable law (typically 45-60 days). If unsatisfied, you may contact your state's Attorney General.

---

## 11. Cookies, Tracking, and Similar Technologies

### 11.1 Cookies We Use

| Cookie Name | Type | Purpose | Duration | Party |
|-------------|------|---------|----------|-------|
| access_token | Strictly Necessary | Authentication session | 15 minutes | First-party |
| refresh_token | Strictly Necessary | Session renewal | 7 days | First-party |
| csrf_token | Strictly Necessary | CSRF protection | Session | First-party |
| tos_accepted | Strictly Necessary | Record of Terms acceptance | Persistent | First-party |

### 11.2 What We Do NOT Use

- No third-party analytics cookies (no Google Analytics, no Mixpanel, no Amplitude);
- No advertising cookies or pixels (no Meta Pixel, no Google Ads, no TikTok Pixel);
- No cross-site tracking technologies;
- No browser fingerprinting;
- No invisible tracking pixels in emails (we do not track email opens).

### 11.3 Do Not Track / Global Privacy Control

We honor the Global Privacy Control (GPC) signal. Since we do not engage in tracking, selling, or sharing personal data for advertising, the practical effect is already built into our architecture. We also respect Do Not Track (DNT) browser headers.

---

## 12. AI-Specific Privacy Disclosures

### 12.1 How AI Processes Your Data

When you use AI features (grow assistant, plant health analysis), the following occurs:

- Your query, relevant sensor data, and/or photos are sent to the AI model provider (Google Gemini or local Ollama instance);
- For Google Gemini: data is processed under our API agreement which prohibits Google from using your data for model training;
- For local Ollama: data never leaves your server (self-hosted only);
- AI responses are generated and stored in your conversation history;
- We do NOT use your private conversations or data to train or fine-tune any AI model without explicit opt-in consent.

### 12.2 AI Data Retention

- AI conversation history is retained as part of your account data;
- Photos sent to Google Gemini for analysis are processed ephemerally and not retained by Google;
- You may delete your AI conversation history at any time from the AI assistant interface.

### 12.3 Opting Out of AI Features

AI features are opt-in. You are never required to use AI features and can use the full Platform without engaging any AI functionality.

---

## 13. Children's Privacy

The Service is not directed to and is not intended for individuals under the age of eighteen (18). We do not knowingly collect personal information from children under 18. If we discover that we have collected personal information from a child under 18, we will promptly delete that information. If you believe a child has provided us with personal information, please contact privacy@tendrilgrow.com.

---

## 14. International Data Transfers

The Service is operated from and data is stored in the **United States**. If you access the Service from outside the United States, your data will be transferred to, stored in, and processed in the United States.

For transfers from the EEA/UK, see Section 8.3. For all other international users, by using the Service you consent to such transfer and processing. We implement the following safeguards:

- Encryption of all data in transit (TLS 1.3) and sensitive data at rest (AES-256-GCM);
- Contractual data protection commitments with all service providers;
- Access controls limiting who can access personal data;
- Regular security assessments and penetration testing.

---

## 15. Third-Party Links and Integrations

The Service may contain links to third-party websites or integrate with third-party services. This Privacy Policy applies only to the Tendril Service. We are not responsible for the privacy practices of third-party websites or services. We encourage you to review the privacy policies of any third-party service you connect to the Platform.

---

## 16. Data Processing for Self-Hosted Instances

If you self-host Tendril using our open-source software:

- We do NOT receive, process, or store any data from your self-hosted instance;
- YOU are the data controller for all data in your self-hosted instance;
- You are solely responsible for your own privacy compliance, data security, backup, and breach notification;
- This Privacy Policy does not apply to self-hosted instances except where you voluntarily connect to our hosted services (e.g., telemetry opt-in, marketplace, or support channels).

---

## 17. Changes to This Privacy Policy

We may update this Privacy Policy periodically to reflect changes in our practices, legal requirements, or the Service. When we make changes:

- **Material changes:** We will notify you via email and/or prominent in-app notification at least **30 days** before the effective date;
- **Non-material changes:** We will update the "Last Updated" date at the top of this page;
- Your continued use of the Service after the effective date constitutes acceptance of the updated policy;
- If you do not agree to any update, your sole remedy is to delete your account before the effective date.

---

## 18. Contact Information

For all privacy-related questions, data requests, complaints, or concerns:

| Contact | Details |
|---------|---------|
| Privacy inquiries | privacy@tendrilgrow.com |
| Data Protection Officer (GDPR) | dpo@tendrilgrow.com |
| Legal inquiries | legal@tendrilgrow.com |
| Entity | Geek Info LLC |
| Management | Trec-Tor Consulting |
| Jurisdiction | New Jersey, United States |

For California residents: You may also contact the California Attorney General at [oag.ca.gov/privacy](https://oag.ca.gov/privacy) if you believe your CCPA rights have been violated.

---

*This Privacy Policy is effective as of June 11, 2026.*
