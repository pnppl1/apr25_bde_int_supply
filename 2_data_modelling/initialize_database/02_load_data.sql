
-- 02_load_data.sql


-- 0.  STAGING-TABLE  
CREATE TEMP TABLE raw_review (
  name                  TEXT,
  country               TEXT,
  rating_x              SMALLINT,
  title                 TEXT,
  text                  TEXT,
  date_of_experience    DATE,
  has_reply             SMALLINT,
  company_x             TEXT,
  company_y             TEXT,
  website               TEXT,
  rating_y              NUMERIC,         -- TrustScore 
  number_review         FLOAT,
  domain                TEXT,            -- Python-List as String
  "5_star_percentage"   TEXT,
  "4_star_percentage"   TEXT,
  "3_star_percentage"   TEXT,
  "2_star_percentage"   TEXT,
  "1_star_percentage"   TEXT
);

\copy raw_review FROM '/import/all_data.csv' DELIMITER ',' CSV HEADER;

-- 1.  COMPANY  (website = PK)  
INSERT INTO company (website, company, trust_score, number_review)
SELECT DISTINCT
       website,
       COALESCE(NULLIF(company_y, ''), company_x)            AS company_name,
       rating_y                                              AS trust_score,
       number_review
FROM   raw_review;

-- 2.  RATING  (1:1 COMPANY, PK = FK)  
INSERT INTO rating (website, 
"5_star_percentage",
"4_star_percentage",
"3_star_percentage",
"2_star_percentage",
"1_star_percentage")
SELECT DISTINCT
       website,
       "5_star_percentage",
"4_star_percentage",
"3_star_percentage",
"2_star_percentage",
"1_star_percentage"
       -- CAST(regexp_replace("5_star_percentage", '%', '', 'g') AS TEXT),
       -- CAST(regexp_replace("4_star_percentage", '%', '', 'g') AS TEXT),
       -- CAST(regexp_replace("3_star_percentage", '%', '', 'g') AS TEXT),
       -- CAST(regexp_replace("2_star_percentage", '%', '', 'g') AS TEXT),
       -- CAST(regexp_replace("1_star_percentage", '%', '', 'g') AS TEXT)
FROM   raw_review;


-- 3.  DOMAIN  +  COMPANY_DOMAIN  (M:N)  

-- 3.1  Domains extracting and list creation
WITH domain_tokens AS (
    SELECT DISTINCT
           website,
           -- delete brackets and spaces
           string_to_array(
             regexp_replace(trim(both '[]' FROM domain), '''', '', 'g'), ','
           ) AS domain_arr
    FROM raw_review
), exploded AS (
    SELECT website, trim(both ' ' FROM unnest(domain_arr)) AS domain_name
    FROM   domain_tokens
)
-- 3.2  register DOMAIN-table 
INSERT INTO domain (domain)
SELECT DISTINCT domain_name
FROM   exploded
ON CONFLICT (domain) DO NOTHING;

-- 3.3  Bridgetable filling 
INSERT INTO company_domain (website, domain_id)
SELECT DISTINCT
       e.website,
       d.domain_id
FROM   (
         SELECT website,
                trim(both ' ' FROM unnest(
                    string_to_array(
                      regexp_replace(trim(both '[]' FROM domain), '''', '', 'g'),
                      ','
                    )
                )) AS domain_name
         FROM raw_review
       ) AS e
JOIN   domain d ON d.domain = e.domain_name
ON CONFLICT DO NOTHING;   -- 

-- 4.  REVIEW  
INSERT INTO review (website, name, country, rating,
                    title, text, date_of_experience, has_reply)
SELECT
       website,
       name,
       country,
       rating_x,
       title,
       text,
       date_of_experience,
       (has_reply = 1)      -- INTEGER → BOOLEAN
FROM   raw_review;


-- 5.  Clean up
DROP TABLE IF EXISTS raw_review;
