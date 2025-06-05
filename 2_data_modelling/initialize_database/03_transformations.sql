/* -----------------------------------------------------------
   03_transformations.sql
   - Percentage-Strings ("98%", "<1%") to DECIMAL(5,2) 
   - fill fields with entry of "<1%" from remaining percentages
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
-- 3) distribute remaining percentages
----------------------------------------------------------------
WITH sums AS (
  SELECT  website,
          COALESCE(star_5_pct,0) + COALESCE(star_4_pct,0) +
          COALESCE(star_3_pct,0) + COALESCE(star_2_pct,0) +
          COALESCE(star_1_pct,0) AS pct_sum,
          (CASE WHEN star_5_pct IS NULL THEN 1 ELSE 0 END +
           CASE WHEN star_4_pct IS NULL THEN 1 ELSE 0 END +
           CASE WHEN star_3_pct IS NULL THEN 1 ELSE 0 END +
           CASE WHEN star_2_pct IS NULL THEN 1 ELSE 0 END +
           CASE WHEN star_1_pct IS NULL THEN 1 ELSE 0 END) AS null_cnt
  FROM rating
)
UPDATE rating r
SET star_5_pct = COALESCE(star_5_pct,
                          ROUND( (100 - s.pct_sum) / s.null_cnt, 2)),
    star_4_pct = COALESCE(star_4_pct,
                          ROUND( (100 - s.pct_sum) / s.null_cnt, 2)),
    star_3_pct = COALESCE(star_3_pct,
                          ROUND( (100 - s.pct_sum) / s.null_cnt, 2)),
    star_2_pct = COALESCE(star_2_pct,
                          ROUND( (100 - s.pct_sum) / s.null_cnt, 2)),
    star_1_pct = COALESCE(star_1_pct,
                          ROUND( (100 - s.pct_sum) / s.null_cnt, 2))
FROM sums s
WHERE r.website = s.website
  AND s.null_cnt > 0;         

----------------------------------------------------------------
-- 4) (Optional) old TEXT-columns cleaned
----------------------------------------------------------------
-- ALTER TABLE rating
--   DROP COLUMN "5_star_percentage",
--   DROP COLUMN "4_star_percentage",
--   DROP COLUMN "3_star_percentage",
--   DROP COLUMN "2_star_percentage",
--   DROP COLUMN "1_star_percentage";

COMMIT;
