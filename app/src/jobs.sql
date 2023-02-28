CREATE TABLE IF NOT EXISTS jobs (
    job_position_id INT,
    position_title TEXT,
    job_publish_date TIMESTAMP NOT NULL,
    org_name TEXT,
    position_location_display TEXT,
    job_location Text,
    job_url TEXT,
    min_salary_range FLOAT,
    max_salary_range FLOAT,
    record_created_date TIMESTAMP NOT NULL,
    search_parameters TEXT,
    created_by TEXT,
    UNIQUE (job_position_id, search_parameters)
);

CREATE VIEW chicago_jobs
AS
SELECT
    job_position_id,
    position_title,
    job_publish_date,
    org_name,
    position_location_display,
    job_location,
    job_url,
    min_salary_range,
    max_salary_range,
    record_created_date,
    search_parameters
FROM jobs
WHERE job_location LIKE '%Chicago%';