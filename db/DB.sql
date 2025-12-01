CREATE TABLE "admin_users" (
  "id" BIGSERIAL PRIMARY KEY
);

CREATE TABLE "departments" (
  "id" BIGSERIAL PRIMARY KEY
);

CREATE TABLE "targets" (
  "id" BIGSERIAL PRIMARY KEY,
  "department_id" BIGINT
);

CREATE TABLE "target_lists" (
  "id" BIGSERIAL PRIMARY KEY,
  "created_by_id" BIGINT
);

CREATE TABLE "target_list_members" (
  "id" BIGSERIAL PRIMARY KEY,
  "target_list_id" BIGINT,
  "target_id" BIGINT
);

CREATE TABLE "email_templates" (
  "id" BIGSERIAL PRIMARY KEY,
  "created_by_id" BIGINT
);

CREATE TABLE "landing_pages" (
  "id" BIGSERIAL PRIMARY KEY,
  "created_by_id" BIGINT
);

CREATE TABLE "campaigns" (
  "id" BIGSERIAL PRIMARY KEY,
  "created_by_id" BIGINT,
  "email_template_id" BIGINT,
  "landing_page_id" BIGINT
);

CREATE TABLE "campaign_target_lists" (
  "id" BIGSERIAL PRIMARY KEY,
  "campaign_id" BIGINT,
  "target_list_id" BIGINT
);

CREATE TABLE "campaign_targets" (
  "id" BIGSERIAL PRIMARY KEY,
  "campaign_id" BIGINT,
  "target_id" BIGINT,
  "email_template_id" BIGINT,
  "landing_page_id" BIGINT
);

CREATE TABLE "email_jobs" (
  "id" BIGSERIAL PRIMARY KEY,
  "campaign_target_id" BIGINT
);

CREATE TABLE "event_types" (
  "id" BIGSERIAL PRIMARY KEY
);

CREATE TABLE "events" (
  "id" BIGSERIAL PRIMARY KEY,
  "campaign_target_id" BIGINT,
  "event_type_id" BIGINT
);

CREATE TABLE "form_templates" (
  "id" BIGSERIAL PRIMARY KEY,
  "landing_page_id" BIGINT,
  "created_by_id" BIGINT
);

CREATE TABLE "form_questions" (
  "id" BIGSERIAL PRIMARY KEY,
  "form_template_id" BIGINT
);

CREATE TABLE "form_submissions" (
  "id" BIGSERIAL PRIMARY KEY,
  "campaign_target_id" BIGINT,
  "form_template_id" BIGINT
);

CREATE TABLE "form_answers" (
  "id" BIGSERIAL PRIMARY KEY,
  "form_submission_id" BIGINT,
  "form_question_id" BIGINT
);

CREATE UNIQUE INDEX ON "target_list_members" ("target_list_id", "target_id");

CREATE UNIQUE INDEX ON "campaign_target_lists" ("campaign_id", "target_list_id");

CREATE UNIQUE INDEX ON "campaign_targets" ("campaign_id", "target_id");

ALTER TABLE "targets" ADD FOREIGN KEY ("department_id") REFERENCES "departments" ("id");

ALTER TABLE "target_lists" ADD FOREIGN KEY ("created_by_id") REFERENCES "admin_users" ("id");

ALTER TABLE "target_list_members" ADD FOREIGN KEY ("target_list_id") REFERENCES "target_lists" ("id");

ALTER TABLE "target_list_members" ADD FOREIGN KEY ("target_id") REFERENCES "targets" ("id");

ALTER TABLE "email_templates" ADD FOREIGN KEY ("created_by_id") REFERENCES "admin_users" ("id");

ALTER TABLE "landing_pages" ADD FOREIGN KEY ("created_by_id") REFERENCES "admin_users" ("id");

ALTER TABLE "campaigns" ADD FOREIGN KEY ("created_by_id") REFERENCES "admin_users" ("id");

ALTER TABLE "campaigns" ADD FOREIGN KEY ("email_template_id") REFERENCES "email_templates" ("id");

ALTER TABLE "campaigns" ADD FOREIGN KEY ("landing_page_id") REFERENCES "landing_pages" ("id");

ALTER TABLE "campaign_target_lists" ADD FOREIGN KEY ("campaign_id") REFERENCES "campaigns" ("id");

ALTER TABLE "campaign_target_lists" ADD FOREIGN KEY ("target_list_id") REFERENCES "target_lists" ("id");

ALTER TABLE "campaign_targets" ADD FOREIGN KEY ("campaign_id") REFERENCES "campaigns" ("id");

ALTER TABLE "campaign_targets" ADD FOREIGN KEY ("target_id") REFERENCES "targets" ("id");

ALTER TABLE "campaign_targets" ADD FOREIGN KEY ("email_template_id") REFERENCES "email_templates" ("id");

ALTER TABLE "campaign_targets" ADD FOREIGN KEY ("landing_page_id") REFERENCES "landing_pages" ("id");

ALTER TABLE "email_jobs" ADD FOREIGN KEY ("campaign_target_id") REFERENCES "campaign_targets" ("id");

ALTER TABLE "events" ADD FOREIGN KEY ("campaign_target_id") REFERENCES "campaign_targets" ("id");

ALTER TABLE "events" ADD FOREIGN KEY ("event_type_id") REFERENCES "event_types" ("id");

ALTER TABLE "form_templates" ADD FOREIGN KEY ("landing_page_id") REFERENCES "landing_pages" ("id");

ALTER TABLE "form_templates" ADD FOREIGN KEY ("created_by_id") REFERENCES "admin_users" ("id");

ALTER TABLE "form_questions" ADD FOREIGN KEY ("form_template_id") REFERENCES "form_templates" ("id");

ALTER TABLE "form_submissions" ADD FOREIGN KEY ("campaign_target_id") REFERENCES "campaign_targets" ("id");

ALTER TABLE "form_submissions" ADD FOREIGN KEY ("form_template_id") REFERENCES "form_templates" ("id");

ALTER TABLE "form_answers" ADD FOREIGN KEY ("form_submission_id") REFERENCES "form_submissions" ("id");

ALTER TABLE "form_answers" ADD FOREIGN KEY ("form_question_id") REFERENCES "form_questions" ("id");
