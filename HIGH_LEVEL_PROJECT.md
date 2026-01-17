Nexus - AI-Native Event Production Platform

Executive Summary

Event production for student clubs is fragmented. Teams waste 30% of planning time context-switching between tools and scrolling through Slack. Partnership teams live in Google Sheets, Logistics in Google Docs, Developers in GitHub, Marketing in Figma. Nexus connects these silos with AI agents that execute tasks autonomously.

Target User: Student club organizing committees running 7 events/year. Structure: Team POCs → Leaders → Co-Presidents. Communication in Slack, weekly meeting docs in Google Docs.

Agent Teams & Tools

1. Partnerships (Outreach & Sponsorship) Goal: Secure sponsors, judges, mentors, and student mentors for each event.

search_partnership_sheet(event_name, category): Query Google Sheets for partners.
draft_linkedin_outreach(profile_url, template): Generate personalized LinkedIn message.
draft_email_outreach(recipient, template, event_name): Generate outreach email.
log_partnership_status(event_name, partner_name, category, status): Update Google Sheet status.
prepare_calendly_link(assignee, meeting_type): Generate Calendly link for assigned team member.
get_partnership_summary(event_name): Aggregate status of all partners.

2. Marketing (Growth & Design) Goal: Social media presence, content creation, and visual design.

create_content_timeline(event_name, launch_date): Generate posting schedule.
draft_social_post(platform, topic, campaign_name): Create Instagram/LinkedIn copy.
check_figma_asset(file_id): Verify design status.
schedule_instagram_post(content, image_url, publish_time): Queue Instagram post.
schedule_linkedin_post(content, publish_time): Queue LinkedIn post.
get_campaign_ideas(event_name): Retrieve campaign concepts.
update_sponsor_in_content(event_name, sponsor_name, tier): Update marketing files with sponsor.

3. Finance (Budgeting & Documentation) Goal: MOUs, invoices, and budget management.

draft_mou(sponsor_name, amount, deliverables): Generate MOU from template.
generate_invoice(sponsor_name, amount, due_date): Create invoice.
update_budget_sheet(event_name, category, amount, type): Log expense/income.
check_budget_status(event_name): Return remaining budget by category.
get_sponsorship_financials(event_name): Summarize secured vs pending amounts.

4. Events (Logistics & Operations) Goal: Venue, room bookings, food, theme, schedule, and team coordination.

send_availability_poll(attendees, duration, date_range, slack_channel): Post When2Meet/LettuceMeet to Slack.
update_logistics_sheet(event_name, category, details): Update venue/food/schedule.
get_logistics_summary(event_name): Pull all logistics info.
create_room_booking_request(building, room, date, time): Draft booking request.
generate_event_schedule(event_name): Build run-of-show.
send_team_reminder(team, message): Post to team's Slack channel.
announce_to_slack(channel, message, mention_team): Post announcement to Slack.

5. Developers (Platform & Features) Goal: Build features for event websites, dashboards, and apps.

create_github_issue(repo, title, description, labels): Create GitHub issue.
check_pr_status(repo): Summarize open PRs.
get_repo_updates(repo, days): Summarize recent commits.
assign_issue(repo, issue_number, assignee): Assign team member.

Integrations

Google Workspace (Sheets, Docs, Calendar)
Slack
GitHub
Figma
Calendly
LinkedIn/Instagram

Demo Flow

Prompt: "Just finished a meeting with a sponsor, Google, who agreed to pay $1,000 in exchange for boothing at Blueprint."

Agents execute in parallel:

Partnerships Agent:
- log_partnership_status → Updates Google Sheet with "verbal confirmation"

Finance Agent:
- draft_mou → Generates MOU (queued for approval)
- generate_invoice → Creates invoice (queued for approval)

Marketing Agent:
- update_sponsor_in_content → Updates marketing files, flags posts

Events Agent:
- update_logistics_sheet → Adds Google to boothing schedule
- announce_to_slack → Posts to #blueprint-team

See TECHNICAL_ARCHITECTURE.md for: system architecture, folder structure, UI layout, testing checkpoints, dependencies, and implementation details.


