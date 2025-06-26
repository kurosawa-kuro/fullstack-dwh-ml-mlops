{{
  config(
    materialized='table',
    tags=['intermediate', 'cleaning']
  )
}}

-- Intermediate Layer: データクリーニングと標準化
-- 仕様書に基づくデータ検証、クリーニング、派生フィールド計算

WITH cleaned_data AS (
  SELECT 
    id,
    
    -- 基本データクリーニング（仕様書 1.1）
    CASE 
      WHEN price > 0 THEN price 
      ELSE NULL 
    END as price,
    
    CASE 
      WHEN sqft > 0 THEN sqft 
      ELSE NULL 
    END as sqft,
    
    CASE 
      WHEN bedrooms > 0 THEN bedrooms 
      ELSE NULL 
    END as bedrooms,
    
    CASE 
      WHEN bathrooms > 0 THEN bathrooms 
      ELSE NULL 
    END as bathrooms,
    
    CASE 
      WHEN year_built >= 1900 AND year_built <= EXTRACT(YEAR FROM CURRENT_DATE)
      THEN year_built 
      ELSE NULL 
    END as year_built,
    
    -- 文字列列のトリム＆大文字化
    TRIM(UPPER(location)) as location,
    TRIM(UPPER(condition)) as condition,
    
    created_at
    
  FROM {{ ref('stg_house_data') }}
),

derived_data AS (
  SELECT 
    *,
    
    -- 派生カラム（仕様書 1.2）
    CASE 
      WHEN price > 0 AND sqft > 0 THEN price / sqft 
      ELSE NULL 
    END as price_per_sqft,
    
    CASE 
      WHEN year_built > 0 THEN EXTRACT(YEAR FROM CURRENT_DATE) - year_built 
      ELSE NULL 
    END as house_age,
    
    CASE 
      WHEN bedrooms > 0 AND bathrooms > 0 THEN bedrooms / bathrooms 
      ELSE NULL 
    END as bed_bath_ratio
    
  FROM cleaned_data
),

final_data AS (
  SELECT 
    *,
    
    -- 品質フラグ（仕様書 1.3）
    CASE 
      WHEN price IS NOT NULL 
        AND sqft IS NOT NULL 
        AND bedrooms IS NOT NULL 
        AND bathrooms IS NOT NULL 
        AND year_built IS NOT NULL 
        AND location IS NOT NULL 
        AND condition IS NOT NULL 
      THEN TRUE 
      ELSE FALSE 
    END as is_complete_record,
    
    -- 外れ値検出（仕様書 2.2）
    CASE 
      WHEN price_per_sqft > 1000 OR price_per_sqft < 50 THEN TRUE 
      ELSE FALSE 
    END as is_price_outlier,
    
    CASE 
      WHEN house_age > 100 OR house_age < 0 THEN TRUE 
      ELSE FALSE 
    END as is_age_outlier
    
  FROM derived_data
)

SELECT * FROM final_data 