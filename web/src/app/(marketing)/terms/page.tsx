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
        <p className="text-neutral-400"><strong>Effective Date:</strong> June 11, 2026 &nbsp;|&nbsp; <strong>Last Updated:</strong> June 11, 2026</p>

        <p>These Terms of Service (&ldquo;Terms&rdquo; or &ldquo;Agreement&rdquo;) constitute a legally binding contract between you (&ldquo;User,&rdquo; &ldquo;you,&rdquo; or &ldquo;your&rdquo;) and <strong>Geek Info LLC</strong>, a New Jersey limited liability company managed by Trec-Tor Consulting (&ldquo;Company,&rdquo; &ldquo;we,&rdquo; &ldquo;us,&rdquo; or &ldquo;our&rdquo;), governing your access to and use of the Tendril platform.</p>
        <p><strong>BY CREATING AN ACCOUNT, CHECKING THE &ldquo;I AGREE&rdquo; BOX, ACCESSING, OR USING ANY PART OF THE SERVICE, YOU ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND AGREE TO BE BOUND BY THESE TERMS AND OUR <Link href="/privacy" className="text-green-500">PRIVACY POLICY</Link>. IF YOU DO NOT AGREE TO ALL OF THESE TERMS, YOU ARE NOT AUTHORIZED TO USE THE SERVICE AND MUST IMMEDIATELY CEASE ALL USE.</strong></p>

        <h2>1. Definitions</h2>
        <ul>
          <li><strong>&ldquo;Service&rdquo;</strong> means the Tendril web application, mobile application, APIs, hosted infrastructure, firmware, AI features, documentation, hardware products, and all related services accessible at tendrilgrow.com or any subdomains thereof.</li>
          <li><strong>&ldquo;Platform&rdquo;</strong> means the Service together with any self-hosted deployments of our open-source software, hardware products, and all associated materials.</li>
          <li><strong>&ldquo;User&rdquo;</strong> or <strong>&ldquo;You&rdquo;</strong> means any individual or entity that accesses, registers for, or uses any portion of the Platform.</li>
          <li><strong>&ldquo;Account&rdquo;</strong> means your registered Tendril account including all associated Tenants, organizations, and data.</li>
          <li><strong>&ldquo;Content&rdquo;</strong> means any data, images, sensor readings, grow logs, journal entries, photos, configuration data, automation rules, or other information you submit, upload, or generate through the Platform.</li>
          <li><strong>&ldquo;Hardware&rdquo;</strong> means any physical products including but not limited to ESP32 sensor boards, pre-assembled kits, components, and accessories distributed by or through us.</li>
          <li><strong>&ldquo;AI Features&rdquo;</strong> means any artificial intelligence, machine learning, algorithmic analysis, or automated recommendation capabilities provided through the Platform.</li>
          <li><strong>&ldquo;Sensor Data&rdquo;</strong> means any measurements, readings, or telemetry data collected by IoT hardware and transmitted to or processed by the Platform.</li>
        </ul>

        <h2>2. Eligibility and Acceptance</h2>
        <h3>2.1 Age Requirement</h3>
        <p>You must be at least eighteen (18) years of age or the age of legal majority in your jurisdiction, whichever is greater, to use the Service. By using the Service, you represent and warrant that you meet this requirement.</p>
        <h3>2.2 Binding Agreement</h3>
        <p>These Terms form a binding legal agreement. If you are accepting on behalf of a company, organization, or other entity, you represent and warrant that you have authority to bind that entity to these Terms.</p>
        <h3>2.3 Mandatory Acceptance</h3>
        <p><strong>You may not access or use any part of the Service without first expressly agreeing to these Terms. Your affirmative acceptance during account registration constitutes your digital signature and agreement to be bound.</strong></p>
        <h3>2.4 One Free Account Per Entity</h3>
        <p>One person or legal entity may not maintain more than one free account. Violation may result in immediate termination without notice.</p>

        <h2>3. Account Registration and Security</h2>
        <p>You must provide accurate, current, and complete information when creating an account. You are solely responsible for:</p>
        <ul>
          <li>Maintaining the confidentiality and security of your credentials;</li>
          <li>All activities that occur under your account;</li>
          <li>Notifying us immediately of any unauthorized use.</li>
        </ul>
        <p>We are not liable for any loss arising from unauthorized access to your account, whether or not you have notified us.</p>

        <h2>4. Acceptable Use Policy</h2>
        <h3>4.1 Prohibited Conduct</h3>
        <p>You agree not to:</p>
        <ul>
          <li>Use the Service for any purpose that violates applicable local, state, national, or international law or regulation;</li>
          <li>Use the Service in connection with any activity that is illegal in your jurisdiction;</li>
          <li>Reverse engineer, decompile, disassemble, or attempt to derive source code from any non-open-source portion of the Service;</li>
          <li>Use automated systems (bots, scrapers, crawlers) to access the Service beyond the documented API;</li>
          <li>Interfere with, disrupt, or impose an unreasonable burden on the Service or its underlying infrastructure;</li>
          <li>Impersonate any person or entity or misrepresent your affiliation;</li>
          <li>Upload or transmit malware, viruses, worms, Trojan horses, or other malicious code;</li>
          <li>Circumvent, disable, or interfere with security features or usage limits;</li>
          <li>Use the Service to store or transmit material that infringes third-party intellectual property rights;</li>
          <li>Resell, sublicense, or commercially exploit the Service without written authorization;</li>
          <li>Use AI Features to generate content that is harmful, deceptive, or violates third-party rights;</li>
          <li>Attempt to access other users&rsquo; data or accounts.</li>
        </ul>
        <h3>4.2 Enforcement</h3>
        <p>We reserve the right to investigate and take appropriate action against violations, including immediate termination, removal of content, and cooperation with law enforcement where required by law.</p>

        <h2>5. Subscription Plans, Billing, and Payment</h2>
        <h3>5.1 Plans and Pricing</h3>
        <ul>
          <li>Paid plans are billed monthly or annually in advance via Stripe or other supported payment processors.</li>
          <li>All fees are exclusive of applicable taxes. Sales tax, VAT, or GST is calculated and collected automatically based on your billing address.</li>
          <li>Prices are subject to change with 30 days&rsquo; advance notice.</li>
        </ul>
        <h3>5.2 Upgrades and Downgrades</h3>
        <ul>
          <li>Upgrades take effect immediately with prorated billing.</li>
          <li>Downgrades take effect at the end of the current billing period.</li>
        </ul>
        <h3>5.3 Payment Failure</h3>
        <ul>
          <li>If payment fails, we provide a fourteen (14) day grace period with automatic retries.</li>
          <li>After the grace period, your account is downgraded to the Free plan. We are not liable for any data loss resulting from plan downgrades.</li>
        </ul>
        <h3>5.4 Refund Policy</h3>
        <p>No refunds are provided for partial months or unused service, except:</p>
        <ul>
          <li>Within seven (7) days of your initial paid subscription charge, upon written request;</li>
          <li>Where required by applicable consumer protection law.</li>
        </ul>
        <h3>5.5 Free Tier</h3>
        <p>The free tier is provided at our sole discretion and may be modified, limited, or discontinued at any time without notice or liability.</p>

        <h2>6. Cancellation and Termination</h2>
        <h3>6.1 Cancellation by You</h3>
        <ul>
          <li>You may cancel your subscription at any time from the billing dashboard.</li>
          <li>Upon cancellation, you retain access until the end of the current billing period.</li>
          <li>After your subscription ends, your account reverts to the Free plan and your data is preserved subject to Free plan limitations.</li>
        </ul>
        <h3>6.2 Termination by Us</h3>
        <ul>
          <li>We may suspend or terminate your account immediately, without prior notice, for any violation of these Terms or for any reason at our sole discretion.</li>
          <li>We may terminate the Service entirely upon thirty (30) days&rsquo; notice.</li>
        </ul>
        <h3>6.3 Effect of Termination</h3>
        <p>Upon termination: (a) all rights granted to you under these Terms immediately cease; (b) you must cease all use of the Service; (c) we may delete your data after thirty (30) days. Sections 8 through 16 and 18 through 23 survive termination.</p>

        <h2>7. Data Ownership and License</h2>
        <h3>7.1 Your Content</h3>
        <p>You retain full ownership of all Content you submit to the Service. By using the Service, you grant us a limited, non-exclusive, worldwide, royalty-free license to store, process, display, and transmit your Content solely as necessary to provide and improve the Service.</p>
        <h3>7.2 Restrictions</h3>
        <p>We do not sell, share, rent, or use your grow data for advertising, marketing to third parties, or any purpose other than operating and improving the Service.</p>
        <h3>7.3 Aggregated Data</h3>
        <p>We may create anonymized, aggregated, de-identified data derived from your use of the Service. Such data does not identify you and is not subject to these restrictions.</p>

        <h2>8. Data Retention and Deletion</h2>
        <ul>
          <li>You may request account deletion at any time from account settings or by emailing privacy@tendrilgrow.com.</li>
          <li>Upon deletion request, your data is retained for thirty (30) days (recovery window), then permanently and irreversibly purged from all systems including backups within sixty (60) additional days.</li>
          <li>You may cancel a pending deletion by logging in during the 30-day window.</li>
          <li>We may retain anonymized, aggregated analytics data that cannot identify you.</li>
          <li>We retain billing records as required by tax law (typically seven years).</li>
        </ul>

        <h2>9. DISCLAIMER OF WARRANTIES</h2>
        <p className="uppercase font-bold text-sm">TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE PLATFORM IS PROVIDED &ldquo;AS IS,&rdquo; &ldquo;AS AVAILABLE,&rdquo; AND &ldquo;WITH ALL FAULTS.&rdquo; GEEK INFO LLC, TREC-TOR CONSULTING, AND THEIR RESPECTIVE OFFICERS, DIRECTORS, EMPLOYEES, AGENTS, AFFILIATES, LICENSORS, AND SUPPLIERS (COLLECTIVELY, &ldquo;RELEASED PARTIES&rdquo;) EXPRESSLY DISCLAIM ALL WARRANTIES OF ANY KIND, WHETHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE, INCLUDING BUT NOT LIMITED TO:</p>
        <ul className="uppercase font-bold text-sm">
          <li>IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT;</li>
          <li>WARRANTIES ARISING FROM COURSE OF DEALING, COURSE OF PERFORMANCE, OR USAGE OF TRADE;</li>
          <li>ANY WARRANTY THAT THE PLATFORM WILL BE UNINTERRUPTED, TIMELY, SECURE, ERROR-FREE, OR FREE OF VIRUSES, DEFECTS, OR HARMFUL COMPONENTS;</li>
          <li>ANY WARRANTY REGARDING THE ACCURACY, RELIABILITY, COMPLETENESS, OR CURRENCY OF ANY DATA, CONTENT, SENSOR READINGS, AI RECOMMENDATIONS, OR INFORMATION;</li>
          <li>ANY WARRANTY THAT THE PLATFORM WILL MEET YOUR REQUIREMENTS OR EXPECTATIONS;</li>
          <li>ANY WARRANTY REGARDING RESULTS OBTAINED FROM USE OF THE PLATFORM.</li>
        </ul>

        <h3>9.1 Sensor Data Disclaimer</h3>
        <p><strong>ALL SENSOR DATA PROVIDED THROUGH THE PLATFORM (INCLUDING BUT NOT LIMITED TO TEMPERATURE, HUMIDITY, SOIL MOISTURE, PH, EC/TDS, DISSOLVED OXYGEN, WATER LEVEL, VPD, CO2, LIGHT INTENSITY, AND ANY OTHER ENVIRONMENTAL MEASUREMENTS) IS PROVIDED FOR GENERAL INFORMATIONAL PURPOSES ONLY. WE DO NOT WARRANT THE ACCURACY, PRECISION, CALIBRATION, RELIABILITY, OR TIMELINESS OF ANY SENSOR DATA.</strong> Sensor hardware may malfunction, lose calibration, experience connectivity issues, report incorrect values, suffer from electromagnetic interference, or fail catastrophically without warning. You must independently verify all sensor readings before relying on them for any decision or action.</p>

        <h3>9.2 AI and Recommendation Disclaimer</h3>
        <p><strong>THE AI GROW ASSISTANT AND ALL RECOMMENDATIONS, SUGGESTIONS, ANALYSES, OR INSIGHTS PROVIDED BY THE PLATFORM (WHETHER GENERATED BY ARTIFICIAL INTELLIGENCE, MACHINE LEARNING, ALGORITHMS, OR OTHERWISE) ARE FOR GENERAL INFORMATIONAL AND ENTERTAINMENT PURPOSES ONLY AND DO NOT CONSTITUTE PROFESSIONAL ADVICE OF ANY KIND.</strong> AI-generated content may be inaccurate, incomplete, outdated, misleading, or wholly inappropriate for your specific conditions, environment, jurisdiction, or circumstances. The Platform does not provide and is not a substitute for professional agricultural, horticultural, botanical, legal, financial, medical, or any other professional advice. You assume all risk from acting or failing to act on any recommendation or output provided by the Platform.</p>

        <h3>9.3 Automation Disclaimer</h3>
        <p><strong>AUTOMATED WORKFLOWS, RULES, SCHEDULES, ALERTS, TRIGGERS, AND ALL AUTOMATION FEATURES ARE PROVIDED WITHOUT ANY WARRANTY OF RELIABLE, TIMELY, OR CORRECT EXECUTION.</strong> Automations may fail to trigger, trigger at incorrect times, trigger incorrectly, execute with unintended parameters, experience delays, or produce unintended or harmful results. You are solely responsible for maintaining independent monitoring of your grow environment and must never rely exclusively on Platform automations for critical environmental controls, safety systems, or any system where failure could result in property damage, crop loss, or personal harm.</p>

        <h2>10. LIMITATION OF LIABILITY</h2>
        <h3>10.1 Exclusion of Damages</h3>
        <p className="uppercase font-bold text-sm">TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL ANY OF THE RELEASED PARTIES BE LIABLE TO YOU OR ANY THIRD PARTY FOR ANY:</p>
        <ul className="uppercase font-bold text-sm">
          <li>INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, PUNITIVE, OR EXEMPLARY DAMAGES;</li>
          <li>LOSS OF PROFITS, REVENUE, INCOME, BUSINESS, SAVINGS, OR GOODWILL;</li>
          <li>LOSS OF DATA, DATA CORRUPTION, OR INABILITY TO ACCESS DATA;</li>
          <li>CROP LOSS, CROP DAMAGE, YIELD REDUCTION, PLANT DEATH, OR AGRICULTURAL LOSSES OF ANY KIND;</li>
          <li>EQUIPMENT DAMAGE, WATER DAMAGE, FIRE DAMAGE, ELECTRICAL DAMAGE, OR ANY PROPERTY DAMAGE;</li>
          <li>PERSONAL INJURY, BODILY HARM, OR ADVERSE HEALTH EFFECTS;</li>
          <li>LOSS ARISING FROM POWER OUTAGES, INTERNET FAILURES, CONNECTIVITY DISRUPTIONS, OR HARDWARE MALFUNCTION;</li>
          <li>LOSS ARISING FROM RELIANCE ON AI RECOMMENDATIONS, SENSOR DATA, AUTOMATED ACTIONS, OR ANY PLATFORM OUTPUT;</li>
          <li>REGULATORY FINES, PENALTIES, LEGAL FEES, COMPLIANCE COSTS, OR GOVERNMENT ACTIONS;</li>
          <li>LOSS ARISING FROM UNAUTHORIZED ACCESS TO YOUR ACCOUNT, SYSTEMS, OR DATA;</li>
          <li>COST OF PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;</li>
          <li>LOSS OF USE, INTERRUPTION OF BUSINESS, OR PRODUCTION DOWNTIME;</li>
          <li>ANY DAMAGES RESULTING FROM THE USE, INABILITY TO USE, OR PERFORMANCE OF THE PLATFORM;</li>
        </ul>
        <p className="uppercase font-bold text-sm">WHETHER BASED ON WARRANTY, CONTRACT, TORT (INCLUDING NEGLIGENCE AND STRICT LIABILITY), PRODUCT LIABILITY, OR ANY OTHER LEGAL THEORY, AND WHETHER OR NOT ANY RELEASED PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES, AND EVEN IF A LIMITED REMEDY SET FORTH HEREIN IS FOUND TO HAVE FAILED ITS ESSENTIAL PURPOSE.</p>

        <h3>10.2 Maximum Liability Cap</h3>
        <p><strong>IN NO EVENT SHALL THE TOTAL AGGREGATE LIABILITY OF ALL RELEASED PARTIES FOR ALL CLAIMS ARISING OUT OF OR RELATING TO THESE TERMS, THE SERVICE, THE PLATFORM, OR ANY HARDWARE PRODUCT EXCEED THE GREATER OF: (A) THE TOTAL AMOUNT YOU ACTUALLY PAID TO US IN THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO THE CLAIM, OR (B) FIFTY UNITED STATES DOLLARS ($50.00 USD).</strong></p>

        <h3>10.3 Essential Basis of the Bargain</h3>
        <p>You acknowledge and agree that we have set our prices, offered free tiers, and made the Platform available in reliance upon the limitations of liability and disclaimers of warranties set forth herein, and that the same form an essential basis of the bargain between the parties. The Platform would not be provided to you without these limitations.</p>

        <h3>10.4 Jurisdictional Limitations</h3>
        <p>Some jurisdictions do not allow the exclusion or limitation of certain damages. In such jurisdictions, our liability shall be limited to the maximum extent permitted by applicable law.</p>

        <h2>11. Hardware Products</h2>
        <h3>11.1 Hardware Disclaimer</h3>
        <p>Any Hardware products (including but not limited to ESP32 sensor boards, pre-assembled kits, components, and accessories) are provided <strong>&ldquo;AS IS&rdquo;</strong> and <strong>&ldquo;WITH ALL FAULTS&rdquo;</strong> without warranty of any kind. We disclaim all warranties regarding hardware fitness, durability, accuracy, precision, calibration, electrical safety, waterproofing, weather resistance, and compatibility with any environment or use case.</p>
        <h3>11.2 Assumption of Hardware Risk</h3>
        <p><strong>YOU EXPRESSLY ACKNOWLEDGE AND ASSUME ALL RISKS ASSOCIATED WITH IOT SENSOR HARDWARE INCLUDING BUT NOT LIMITED TO: ELECTRICAL HAZARDS, FIRE RISK, SHORT CIRCUITS, WATER EXPOSURE, ELECTROMAGNETIC INTERFERENCE, RADIO FREQUENCY EMISSIONS, COMPONENT DEGRADATION, BATTERY FAILURE, AND CATASTROPHIC COMPONENT FAILURE.</strong> You are solely responsible for the assembly, installation, operation, maintenance, and safe disposal of all Hardware. You must ensure all installations comply with applicable electrical codes, building codes, and safety standards.</p>
        <h3>11.3 No Safety Certification</h3>
        <p>Unless explicitly stated in writing for a specific product, Hardware is NOT UL-listed, CE-marked, FCC-certified, RoHS-compliant, or certified by any safety, regulatory, or standards body. Hardware is provided as experimental/hobbyist products intended for use by technically competent individuals who understand and accept the associated risks.</p>
        <h3>11.4 Environmental Limitations</h3>
        <p>Hardware is not warranted for use in extreme temperatures, high humidity, direct water contact, outdoor conditions, corrosive environments, or any conditions beyond standard indoor residential environments (15-35&deg;C, &lt;80% RH) unless explicitly rated and documented for such use.</p>
        <h3>11.5 No Life-Safety Use</h3>
        <p><strong>THE HARDWARE AND PLATFORM ARE NOT DESIGNED, INTENDED, OR CERTIFIED FOR USE IN LIFE-SAFETY APPLICATIONS, CRITICAL INFRASTRUCTURE, MEDICAL DEVICES, OR ANY APPLICATION WHERE FAILURE COULD RESULT IN DEATH, PERSONAL INJURY, OR SEVERE PROPERTY DAMAGE.</strong></p>

        <h2>12. Indemnification</h2>
        <p><strong>TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, YOU AGREE TO INDEMNIFY, DEFEND, AND HOLD HARMLESS ALL RELEASED PARTIES FROM AND AGAINST ANY AND ALL CLAIMS, ACTIONS, PROCEEDINGS, LIABILITIES, DAMAGES, LOSSES, JUDGMENTS, SETTLEMENTS, COSTS, AND EXPENSES (INCLUDING REASONABLE ATTORNEYS&rsquo; FEES, EXPERT WITNESS FEES, AND COURT COSTS) ARISING OUT OF OR RELATING TO:</strong></p>
        <ol>
          <li>Your access to or use of the Platform, Service, or Hardware;</li>
          <li>Your violation or breach of these Terms or any applicable law;</li>
          <li>Your violation of any third-party right, including intellectual property, privacy, or publicity rights;</li>
          <li>Your cultivation, possession, processing, distribution, transport, sale, or use of any plant, substance, or product (whether legal or illegal in your jurisdiction);</li>
          <li>Any crop loss, property damage, environmental damage, or personal injury arising from your use of the Platform or Hardware;</li>
          <li>Any claims by third parties (including employees, contractors, customers, regulators, or government entities) related to your use of the Platform;</li>
          <li>Your negligence, recklessness, or willful misconduct;</li>
          <li>Any Content you upload, transmit, store, or generate through the Platform;</li>
          <li>Your failure to comply with applicable safety, building, electrical, or environmental codes;</li>
          <li>Your failure to maintain adequate insurance for your operations;</li>
          <li>Any regulatory investigation, audit, enforcement action, or penalty arising from your activities;</li>
          <li>Your reliance on AI recommendations, sensor data, or automated actions.</li>
        </ol>
        <p>This indemnification obligation shall survive termination of these Terms and is in addition to (not in lieu of) any other indemnities provided by law.</p>

        <h2>13. Assumption of Risk</h2>
        <h3>13.1 Agricultural and Horticultural Risk</h3>
        <p><strong>YOU EXPRESSLY ACKNOWLEDGE AND ASSUME ALL RISKS INHERENT IN AGRICULTURAL AND HORTICULTURAL ACTIVITIES.</strong> Growing plants involves inherent and unavoidable risks including but not limited to: crop failure, pest infestation, disease, mold, contamination, environmental damage, water damage, nutrient deficiency or toxicity, light stress, heat stress, equipment failure, and financial loss. The Platform does not eliminate, reduce, or mitigate these risks. The Platform is a monitoring and informational tool only; all outcomes and consequences of your growing activities are solely your responsibility.</p>
        <h3>13.2 Technology Reliance Risk</h3>
        <p><strong>YOU ACKNOWLEDGE THAT RELIANCE ON TECHNOLOGY FOR ENVIRONMENTAL MONITORING AND AUTOMATION CARRIES INHERENT AND SUBSTANTIAL RISKS.</strong> Electronic systems fail. Software contains bugs. Networks experience outages. Sensors degrade and lose calibration. Automations malfunction. You agree to maintain independent, manual monitoring procedures and to never rely exclusively on the Platform for any critical environmental control, safety system, or time-sensitive operation.</p>
        <h3>13.3 Financial and Business Risk</h3>
        <p>You assume all financial and business risk associated with your operations. We make no representations, warranties, or guarantees regarding potential yields, returns, profitability, cost savings, or any other financial outcome. Past performance data shown in the Platform does not predict future results.</p>
        <h3>13.4 Voluntary Participation</h3>
        <p>Your use of the Platform is entirely voluntary. You are free to cease using the Platform at any time. By continuing to use the Platform, you reaffirm your assumption of all associated risks.</p>

        <h2>14. Cannabis and Controlled Substance Disclaimers</h2>
        <h3>14.1 General-Purpose Agricultural Tool</h3>
        <p><strong>THE PLATFORM IS A GENERAL-PURPOSE AGRICULTURAL MONITORING AND AUTOMATION TOOL. IT IS NOT DESIGNED FOR, MARKETED TOWARD, OR INTENDED EXCLUSIVELY FOR THE CULTIVATION OF ANY CONTROLLED SUBSTANCE.</strong> The Platform can be used for monitoring any plant, crop, or growing environment. Any references to cannabis in documentation, marketing materials, community forums, or AI outputs are solely for the convenience of users operating in jurisdictions where such activity is fully legal and licensed.</p>
        <h3>14.2 Federal Law Notice (United States)</h3>
        <p><strong>CANNABIS REMAINS A SCHEDULE I CONTROLLED SUBSTANCE UNDER UNITED STATES FEDERAL LAW (21 U.S.C. &sect; 841 et seq.). STATE OR LOCAL LEGALIZATION DOES NOT PREEMPT FEDERAL LAW.</strong> You acknowledge that the legal status of cannabis varies dramatically by jurisdiction and is subject to change. It is YOUR sole responsibility to understand and comply with ALL applicable laws in your jurisdiction before, during, and after using the Platform.</p>
        <h3>14.3 Non-Legal Jurisdictions</h3>
        <p><strong>IF YOU ARE LOCATED IN A JURISDICTION WHERE THE CULTIVATION, POSSESSION, OR USE OF CANNABIS (OR ANY OTHER SUBSTANCE YOU INTEND TO GROW) IS ILLEGAL, YOU USE THE PLATFORM ENTIRELY AT YOUR OWN RISK AND SOLELY FOR LAWFUL PURPOSES.</strong> The availability of the Platform in your jurisdiction does NOT constitute legal advice, an invitation to break the law, or any representation that your intended use is lawful. We expressly disclaim any responsibility for your decision to use the Platform for any illegal purpose.</p>
        <h3>14.4 No Facilitation of Illegal Activity</h3>
        <p>We do not knowingly encourage, facilitate, endorse, promote, or condone any illegal activity. The Platform is provided as a neutral technology tool. YOUR ACTIONS AND THEIR LEGAL CONSEQUENCES ARE SOLELY YOUR RESPONSIBILITY.</p>
        <h3>14.5 No Legal Advice</h3>
        <p>Nothing in the Platform, its documentation, AI recommendations, community forums, support communications, or any output of any kind constitutes legal advice. You must consult a qualified attorney licensed in your jurisdiction regarding the legality of your activities.</p>
        <h3>14.6 Compliance Data Not Certified</h3>
        <p>Any data generated by the Platform (including but not limited to audit logs, yield records, environmental data, chain-of-custody records, and compliance reports) is NOT certified for regulatory submission to any government body. You must independently verify whether Platform data meets applicable regulatory standards and requirements before submitting it to any authority.</p>
        <h3>14.7 Cooperation with Law Enforcement</h3>
        <p>We will comply with valid legal process including subpoenas, court orders, and lawful requests from government authorities. We may disclose your information and data as required by law without prior notice to you.</p>

        <h2>15. Service Availability</h2>
        <h3>15.1 No Uptime Guarantee</h3>
        <p>Unless you have a separate written Enterprise SLA, we do not guarantee any specific level of availability, uptime, response time, or performance. The Service may be interrupted at any time for maintenance, updates, security patches, or due to factors beyond our reasonable control.</p>
        <h3>15.2 Modification and Discontinuation</h3>
        <p>We reserve the right to modify, suspend, deprecate, or permanently discontinue any feature, API endpoint, integration, or the entire Service at any time with or without notice and without liability to you.</p>
        <h3>15.3 Self-Hosted Deployments</h3>
        <p>If you self-host the Platform using our open-source software, you are solely and exclusively responsible for its operation, security, patching, backups, availability, compliance, and all aspects of its deployment. We bear no responsibility whatsoever for self-hosted instances.</p>

        <h2>16. Intellectual Property</h2>
        <h3>16.1 Ownership</h3>
        <p>The Service, including its design, user interface, branding, documentation, proprietary algorithms, and all non-open-source components, is owned by Geek Info LLC and protected by U.S. and international copyright, trademark, patent, trade secret, and other intellectual property laws.</p>
        <h3>16.2 Open-Source Components</h3>
        <p>Certain components of the Platform are licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) for server software and the MIT License for ESP32 firmware. These Terms do not modify or supersede those open-source licenses. In the event of conflict between these Terms and the applicable open-source license regarding the software source code, the open-source license prevails for that component.</p>
        <h3>16.3 Trademarks</h3>
        <p>&ldquo;Tendril,&rdquo; the Tendril logo, and associated branding are trademarks of Geek Info LLC. No open-source license grants you any right to use our trademarks, trade names, logos, or brand assets without express written permission.</p>
        <h3>16.4 Feedback</h3>
        <p>Any feedback, suggestions, or ideas you provide regarding the Service are provided voluntarily and we may use them without obligation, compensation, or attribution to you.</p>

        <h2>17. Third-Party Services and Integrations</h2>
        <p>The Service integrates with third-party providers including but not limited to Stripe, Google (Gemini AI), GitHub, EMQX, OpenWeather, Ecowitt, Pulse Grow, and Ollama. Your use of any third-party service is governed by that service&rsquo;s own terms and privacy policy. We are not responsible for:</p>
        <ul>
          <li>Third-party service availability, accuracy, or data handling;</li>
          <li>Changes to third-party APIs, pricing, or terms;</li>
          <li>Data processed by third parties once transmitted to their systems;</li>
          <li>Any loss arising from third-party service failures or discontinuation.</li>
        </ul>

        <h2>18. Dispute Resolution</h2>
        <h3>18.1 Informal Resolution</h3>
        <p>Before initiating formal proceedings, you agree to first contact us at legal@tendrilgrow.com and attempt to resolve the dispute informally for at least thirty (30) days.</p>
        <h3>18.2 Binding Arbitration</h3>
        <p><strong>ANY DISPUTE, CLAIM, OR CONTROVERSY ARISING OUT OF OR RELATING TO THESE TERMS, THE PLATFORM, OR THE RELATIONSHIP BETWEEN YOU AND US (INCLUDING CLAIMS THAT AROSE BEFORE THESE TERMS) SHALL BE RESOLVED BY FINAL AND BINDING INDIVIDUAL ARBITRATION</strong> administered by the American Arbitration Association (&ldquo;AAA&rdquo;) under its Consumer Arbitration Rules or Commercial Arbitration Rules (as applicable based on the claim amount). The arbitration shall be conducted in the English language. The seat of arbitration shall be the State of New Jersey.</p>
        <h3>18.3 Class Action Waiver</h3>
        <p><strong>YOU AND GEEK INFO LLC AGREE THAT EACH MAY BRING CLAIMS AGAINST THE OTHER ONLY IN YOUR OR ITS INDIVIDUAL CAPACITY AND NOT AS A PLAINTIFF, CLASS MEMBER, OR PARTICIPANT IN ANY PURPORTED CLASS ACTION, COLLECTIVE ACTION, CONSOLIDATED ACTION, MASS ARBITRATION, OR REPRESENTATIVE PROCEEDING.</strong> The arbitrator may not consolidate proceedings or preside over any form of representative or class proceeding. If this waiver is found unenforceable, the entire arbitration provision shall be void.</p>
        <h3>18.4 Jury Trial Waiver</h3>
        <p><strong>TO THE EXTENT PERMITTED BY LAW, YOU AND GEEK INFO LLC EACH WAIVE THE RIGHT TO A JURY TRIAL IN ANY COURT PROCEEDING.</strong></p>
        <h3>18.5 Small Claims Exception</h3>
        <p>Either party may bring an individual action in small claims court for disputes within that court&rsquo;s jurisdictional and monetary limits.</p>
        <h3>18.6 Opt-Out Right</h3>
        <p>You may opt out of the arbitration and class action waiver provisions by sending written notice to legal@tendrilgrow.com within thirty (30) days of first accepting these Terms. If you opt out, disputes will be resolved in the courts specified in Section 19.</p>
        <h3>18.7 Statute of Limitations</h3>
        <p><strong>ANY CLAIM OR CAUSE OF ACTION ARISING OUT OF OR RELATED TO THESE TERMS OR THE PLATFORM MUST BE FILED WITHIN ONE (1) YEAR AFTER THE CLAIM AROSE, OR BE PERMANENTLY BARRED.</strong></p>

        <h2>19. Governing Law and Jurisdiction</h2>
        <p>These Terms shall be governed by and construed in accordance with the laws of the <strong>State of New Jersey, United States</strong>, without regard to its conflict of law provisions or the United Nations Convention on Contracts for the International Sale of Goods. If arbitration does not apply, you irrevocably consent to the exclusive personal jurisdiction and venue of the state and federal courts located in New Jersey for any proceedings arising from these Terms.</p>

        <h2>20. Modifications to Terms</h2>
        <p>We reserve the right to modify these Terms at any time. Material changes will be communicated via email or prominent in-app notification at least thirty (30) days before taking effect. Non-material changes (e.g., formatting, clarifications) may take effect immediately. Your continued use of the Service after the effective date of any modification constitutes acceptance of the modified Terms. If you do not agree to any modification, your sole remedy is to terminate your account.</p>

        <h2>21. Export Controls and Sanctions</h2>
        <p>You represent and warrant that you are not located in, organized under the laws of, or a resident of any country or territory subject to comprehensive U.S. economic sanctions, and that you are not a Specially Designated National or on any other U.S. government restricted party list. You will comply with all applicable export control and sanctions laws.</p>

        <h2>22. Force Majeure</h2>
        <p>We shall not be liable for any failure or delay in performance due to causes beyond our reasonable control, including but not limited to: acts of God, natural disasters, earthquakes, floods, hurricanes, pandemics, epidemics, war, terrorism, civil unrest, government actions, embargoes, sanctions, strikes, power failures, internet outages, telecommunications failures, supply chain disruptions, semiconductor shortages, or cyberattacks.</p>

        <h2>23. General Provisions</h2>
        <h3>23.1 Entire Agreement</h3>
        <p>These Terms, together with the <Link href="/privacy" className="text-green-500">Privacy Policy</Link> and any applicable Enterprise SLA or order form, constitute the entire agreement between you and Geek Info LLC regarding the Platform. These Terms supersede all prior or contemporaneous proposals, agreements, negotiations, representations, warranties, and communications.</p>
        <h3>23.2 Severability</h3>
        <p>If any provision is held invalid, illegal, or unenforceable, that provision shall be modified to the minimum extent necessary to make it enforceable (or severed if modification is not possible), and all remaining provisions remain in full force and effect.</p>
        <h3>23.3 Waiver</h3>
        <p>Our failure to enforce any right or provision shall not constitute a waiver of that right or provision. Any waiver must be in writing and signed by us.</p>
        <h3>23.4 Assignment</h3>
        <p>We may assign, transfer, or delegate these Terms and our rights and obligations without restriction, including in connection with a merger, acquisition, reorganization, or sale of assets. You may not assign these Terms without our prior written consent.</p>
        <h3>23.5 No Third-Party Beneficiaries</h3>
        <p>These Terms do not create any third-party beneficiary rights except as expressly provided herein.</p>
        <h3>23.6 Notices</h3>
        <p>Legal notices to us must be sent to legal@tendrilgrow.com. Notices to you will be sent to the email address associated with your account or displayed in the Service.</p>
        <h3>23.7 Headings</h3>
        <p>Section headings are for convenience only and have no legal effect.</p>
        <h3>23.8 Relationship of Parties</h3>
        <p>Nothing in these Terms creates a partnership, joint venture, employment, or agency relationship between you and us.</p>
        <h3>23.9 Electronic Communications</h3>
        <p>You consent to receive communications from us electronically. Electronic communications satisfy any legal requirement that such communications be in writing.</p>

        <h2>24. Contact Information</h2>
        <p>For questions, concerns, or legal notices regarding these Terms:</p>
        <ul>
          <li><strong>Entity:</strong> Geek Info LLC</li>
          <li><strong>Management:</strong> Trec-Tor Consulting</li>
          <li><strong>Email:</strong> <a href="mailto:legal@tendrilgrow.com" className="text-green-500">legal@tendrilgrow.com</a></li>
          <li><strong>Jurisdiction:</strong> New Jersey, United States</li>
        </ul>

        <div className="mt-12 border-t border-neutral-800 pt-6 text-sm text-neutral-500">
          <p>Powered by <a href="https://www.trector.com" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-300">Trec-Tor Consulting</a></p>
        </div>
      </article>
    </div>
  );
}
