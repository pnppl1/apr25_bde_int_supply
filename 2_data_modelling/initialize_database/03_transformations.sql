/* -----------------------------------------------------------
   03_transformations.sql
   - Adjust numeric columns
   - Transform raw values to numbers
   - Percentage-Strings ("98%", "<1%") to DECIMAL(5,2) 
   - Fill fields with entry of "<1%" from remaining percentages
   - Remove extra fields in reviews table (filled with NULL)
   - Fill missing 'name' field in review table
   - Delete empty ratings (one row)
   - 
   ----------------------------------------------------------- */

BEGIN;

----------------------------------------------------------------
-- 1) Adjust numeric columns
----------------------------------------------------------------
DO $$
BEGIN
  IF NOT EXISTS (
       SELECT 1 FROM information_schema.columns
       WHERE table_name = 'rating' AND column_name = 'star_5_pct'
  ) THEN
    ALTER TABLE rating
      ADD COLUMN star_5_pct DECIMAL(5,2),
      ADD COLUMN star_4_pct DECIMAL(5,2),
      ADD COLUMN star_3_pct DECIMAL(5,2),
      ADD COLUMN star_2_pct DECIMAL(5,2),
      ADD COLUMN star_1_pct DECIMAL(5,2);
  END IF;
END$$;

----------------------------------------------------------------
-- 2) Transform raw values to numbers
----------------------------------------------------------------
UPDATE rating
SET star_5_pct = NULLIF(regexp_replace("5_star_percentage", '[%<]', '', 'g'), '')::DECIMAL,
    star_4_pct = NULLIF(regexp_replace("4_star_percentage", '[%<]', '', 'g'), '')::DECIMAL,
    star_3_pct = NULLIF(regexp_replace("3_star_percentage", '[%<]', '', 'g'), '')::DECIMAL,
    star_2_pct = NULLIF(regexp_replace("2_star_percentage", '[%<]', '', 'g'), '')::DECIMAL,
    star_1_pct = NULLIF(regexp_replace("1_star_percentage", '[%<]', '', 'g'), '')::DECIMAL;

----------------------------------------------------------------
-- 3) Distribute remaining percentages
----------------------------------------------------------------
WITH base AS (
  SELECT website,
         CASE WHEN TRIM("5_star_percentage") LIKE '<%' THEN NULL ELSE regexp_replace("5_star_percentage", '[%<]', '', 'g')::DECIMAL END AS star_5,
         CASE WHEN TRIM("4_star_percentage") LIKE '<%' THEN NULL ELSE regexp_replace("4_star_percentage", '[%<]', '', 'g')::DECIMAL END AS star_4,
         CASE WHEN TRIM("3_star_percentage") LIKE '<%' THEN NULL ELSE regexp_replace("3_star_percentage", '[%<]', '', 'g')::DECIMAL END AS star_3,
         CASE WHEN TRIM("2_star_percentage") LIKE '<%' THEN NULL ELSE regexp_replace("2_star_percentage", '[%<]', '', 'g')::DECIMAL END AS star_2,
         CASE WHEN TRIM("1_star_percentage") LIKE '<%' THEN NULL ELSE regexp_replace("1_star_percentage", '[%<]', '', 'g')::DECIMAL END AS star_1,

         CASE WHEN TRIM("5_star_percentage") LIKE '<%' THEN 1 ELSE 0 END AS is_5_less,
         CASE WHEN TRIM("4_star_percentage") LIKE '<%' THEN 1 ELSE 0 END AS is_4_less,
         CASE WHEN TRIM("3_star_percentage") LIKE '<%' THEN 1 ELSE 0 END AS is_3_less,
         CASE WHEN TRIM("2_star_percentage") LIKE '<%' THEN 1 ELSE 0 END AS is_2_less,
         CASE WHEN TRIM("1_star_percentage") LIKE '<%' THEN 1 ELSE 0 END AS is_1_less
  FROM rating
), calc AS (
  SELECT *,
         COALESCE(star_5, 0) + COALESCE(star_4, 0) + COALESCE(star_3, 0) + COALESCE(star_2, 0) + COALESCE(star_1, 0) AS sum_known,
         (is_5_less + is_4_less + is_3_less + is_2_less + is_1_less) AS null_count
  FROM base
), final AS (
  SELECT website,
         COALESCE(star_5, CASE WHEN is_5_less = 1 THEN ROUND((100 - sum_known)::NUMERIC / NULLIF(null_count, 0), 2) END) AS star_5_pct,
         COALESCE(star_4, CASE WHEN is_4_less = 1 THEN ROUND((100 - sum_known)::NUMERIC / NULLIF(null_count, 0), 2) END) AS star_4_pct,
         COALESCE(star_3, CASE WHEN is_3_less = 1 THEN ROUND((100 - sum_known)::NUMERIC / NULLIF(null_count, 0), 2) END) AS star_3_pct,
         COALESCE(star_2, CASE WHEN is_2_less = 1 THEN ROUND((100 - sum_known)::NUMERIC / NULLIF(null_count, 0), 2) END) AS star_2_pct,
         COALESCE(star_1, CASE WHEN is_1_less = 1 THEN ROUND((100 - sum_known)::NUMERIC / NULLIF(null_count, 0), 2) END) AS star_1_pct
  FROM calc
)
UPDATE rating r
SET star_5_pct = f.star_5_pct,
    star_4_pct = f.star_4_pct,
    star_3_pct = f.star_3_pct,
    star_2_pct = f.star_2_pct,
    star_1_pct = f.star_1_pct
FROM final f
WHERE r.website = f.website;
-- FROM sums s
-- WHERE r.website = s.website
--   AND s.null_cnt > 0;         

----------------------------------------------------------------
-- 4) (Optional) old TEXT-columns cleaned
----------------------------------------------------------------
-- ALTER TABLE rating
--   DROP COLUMN "5_star_percentage",
--   DROP COLUMN "4_star_percentage",
--   DROP COLUMN "3_star_percentage",
--   DROP COLUMN "2_star_percentage",
--   DROP COLUMN "1_star_percentage";

----------------------------------------------------------------
-- 5) Remove extra fields in reviews table
----------------------------------------------------------------
DELETE FROM review
WHERE name IS NULL AND date_of_experience IS NULL;

----------------------------------------------------------------
-- 6) Fill missing 'name' field in review table
----------------------------------------------------------------
UPDATE review                            
SET name = 'customer'
WHERE name IS NULL;

----------------------------------------------------------------
-- 7) Delete empty ratings (one row)
----------------------------------------------------------------
DELETE FROM rating 
WHERE star_5_pct IS NULL
  AND star_4_pct IS NULL
  AND star_3_pct IS NULL
  AND star_2_pct IS NULL
  AND star_1_pct IS NULL;



COMMIT;
